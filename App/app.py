# ============================================================================ #
# Importing necessary libraries
# ============================================================================ #

from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
import io
from datetime import datetime
from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
import io
from datetime import datetime

# Local modules
from helpers import create_modal_with_loading, close_modal
from samples import create_sample_file
from validation import validate_file, validation_rules

# Validation Rules
# ============================================================================ #

"""
Validation rules (overview)
This dictionary maps a logical file type (key) to a rules object that
describes how uploaded data for that type should be validated, transformed
and exported. The `validate_file` and `validate_single_file` functions use
these entries to perform schema/type checks, date parsing and range checks,
value validations, and optional wide->long transformations before calling
the configured export function.

Supported top-level keys for each file-type rule object:
- `columns` (list): For long-format files, the expected column names or
    the set of id/base columns used when transforming from wide->long.
- `types` (dict): Mapping of column name -> type. Supported types:
    `numeric`, `string`, `date`. When a column is `date` the validator
    will attempt to parse values (optionally using per-column formats).
- `date_columns` (dict): Optional per-column configuration for date
    columns. Each key is a column name and the value may include:
      - `format`: user-friendly pattern (e.g. `yyyy-mm-dd`, `dd/mm/yyyy`,
          `mmm-yy`, `mm/dd/yy`) — converted internally to strptime.
      - `range`: dict with `start`, `end` (ISO strings) and optional
          `freq` (e.g. `W-MON` for weekly Mondays). Used for range checks.
          The `range` dict may also include separate offsets for the start and
          end dates to shift the allowed window. Offsets are specified as
          integer days using the keys `start_offset` and `end_offset`.
          Example:
            "range": {
                "start": "2025-01-06",
                "end": "2025-01-20",
                "start_offset": -7,
                "end_offset": 3,
                "freq": "W-MON"
            }
- `date_range` (dict): Legacy / top-level date range that applies when a
    single date axis is implied (used for wide-format week columns).
    This dict also supports `start_offset` and `end_offset` (integers,
    days) to adjust the inclusive window used for validation.
- `value_checks` (dict): Rules for values per column. Supported forms:
      - `'not_null'` — column must not contain nulls
      - list of allowed values — column values must be one of the list
- `transform_config` (dict): Controls transformations applied by
    `validate_file` before export. The key `type` selects behavior:
      - `none`: no transform
      - `column`: long-format where a single column contains dates (inferred
          from `date_columns`) — used by attrition/recruitment/fte
      - `columns`: wide-format where date labels are column headers. When
          used provide `column_format` (user format) and optional
          `require_monday` (bool) to enforce weekly Mondays.
      - `multi_ids`: special wide-format where a set of ID columns are
          date fields (e.g., `date_1`, `date_2`, `date_3`) and remaining
          columns are value dimensions (melted to long). Provide
          `id_columns` listing those date ID columns.
- `names_to` / `values_to` (str): Column names to use for the melted
    variable and value columns when performing wide->long (`melt`). For
    example `names_to: 'week'` and `values_to: 'fte_count'`.
- `id_columns` (list): For `multi_ids` transformations, the list of
    columns that contain date IDs and should be kept as id_vars during melt.
- `export_path` (str) and `export_func` (str | callable): Where to write
    the exported CSV and which function (or function-name) to call.
- `sheets` (dict): For multi-sheet Excel files, `validation_rules` may
    contain a `sheets` mapping; each sheet has its own sub-rule object.

Notes & examples:
- `attrition` uses `transform_config: {'type': 'column'}` and a
   `date_columns` entry for `week` so the validator infers the date axis.
- `fte_wide` uses `transform_config: {'type': 'columns', 'column_format':
   'yyyy-mm-dd', 'require_monday': True}` because dates are encoded in
   the column headers and must be parsed and validated as Mondays.
- `resource_allocation` uses `transform_config: {'type': 'multi_ids'}`
   with `id_columns: ['date_1','date_2','date_3']` and per-column
   `date_columns` formats; remaining columns are treated as city value
   dimensions and are melted to long on export.

Keep this block updated whenever new rule keys or transform types are
introduced so validators and UI help text remain accurate.
"""
validation_rules = {
    "attrition": {
        "skiprows": 1,
        # Add an extra date column `hire_date` to demonstrate multiple date formats
        "columns": ["week", "job_type", "attrition_count", "hire_date"],
        "types": {
            "week": "date",
            "job_type": "string",
            "attrition_count": "numeric",
            "hire_date": "date",
        },
        # per-column date formats and ranges. `week` uses yyyy-mm-dd weekly (W-MON),
        # `hire_date` uses yyyy/mm/dd and has its own (non-weekly) range.
        "date_columns": {
            "week": {
                "format": "yyyy-mm-dd",
                "range": {"start": "2025-01-06", "end": "2025-01-20", "freq": "W-MON"},
            },
            "hire_date": {
                "format": "yyyy/mm/dd",
                "range": {
                    "start": "2025-01-05",
                    "end": "2025-01-18",
                    "start_offset": 0,
                    "end_offset": -1,
                    "freq": "W-MON",
                },
            },
        },
        "value_checks": {
            "week": "not_null",
            "job_type": ["A", "B", "C"],
            "attrition_count": "not_null",
            "hire_date": "not_null",
        },
        "transform_config": {"type": "column"},
        "export_path": "./exports/attrition.csv",
        "export_func": "export_attrition",
    },
    "recruitment": {
        "columns": ["week", "job_type", "recruitment_count"],
        "types": {"week": "date", "job_type": "string", "recruitment_count": "numeric"},
        "date_columns": {
            "week": {
                "format": "yyyy-mm-dd",
                "range": {"start": "2025-01-06", "end": "2025-01-20", "freq": "W-MON"},
            }
        },
        "value_checks": {
            "week": "not_null",
            "job_type": ["A", "B", "C"],
            "recruitment_count": "not_null",
        },
        "transform_config": {"type": "column"},
        "export_path": "./exports/recruitment.csv",
        "export_func": "export_recruitment",
    },
    "fte": {
        "columns": ["week", "job_type", "fte_count"],
        "types": {"week": "date", "job_type": "string", "fte_count": "numeric"},
        "date_columns": {
            "week": {
                "format": "yyyy-mm-dd",
                "range": {"start": "2025-01-06", "end": "2025-01-20", "freq": "W-MON"},
            }
        },
        "value_checks": {
            "week": "not_null",
            "job_type": ["A", "B", "C"],
            "fte_count": "not_null",
        },
        "transform_config": {"type": "column"},
        "export_path": "./exports/fte.csv",
        "export_func": "export_fte",
    },
    "fte_wide": {
        "columns": ["job_type"],
        "types": {"job_type": "string"},
        # For wide-format files the date columns are column names; specify column_format
        "date_range": {"start": "2025-01-06", "end": "2025-01-20", "freq": "W-MON"},
        "value_checks": {"job_type": ["A", "B", "C"]},
        "transform_config": {
            "type": "columns",
            "column_format": "yyyy-mm-dd",
            "require_monday": True,
        },
        "names_to": "week",
        "values_to": "fte_count",
        "export_path": "./exports/fte_wide.csv",
        "export_func": "export_fte_wide",
    },
    "patch_mapping": {
        "columns": ["wmis", "region"],
        "types": {"wmis": "string", "region": "string"},
        "value_checks": {
            "wmis": ["A", "B", "C"],
            "region": ["North", "South", "East", "West"],
        },
        "transform_config": {"type": "none"},
        "export_path": "./exports/patch_mapping.csv",
        "export_func": "export_patch_mapping",
    },
    "resource_allocation": {
        # 3 date ID columns with different formats; city columns are dimensions (value columns)
        "columns": [
            "date_1", 
            "date_2", 
            "date_3", 
            "skill"
        ],
        "types": {
            "date_1": "date",
            "date_2": "date",
            "date_3": "date",
            "skill": "string",
        },
        # per-column date formats for the 3 date ID columns
        "date_columns": {
            "date_1": {"format": "dd/mm/yyyy"},
            "date_2": {"format": "mmm-yy"},
            "date_3": {"format": "mm/dd/yy"},
        },
        "value_checks": {
            "date_1": "not_null",
            "date_2": "not_null",
            "date_3": "not_null",
            "skill": ["MS", "SS"],
        },
        # wide format: multiple date ID columns; other columns are value dimensions
        "transform_config": {"type": "multi_ids"},
        "id_columns": [
            "date_1", 
            "date_2", 
            "date_3", 
            "skill"
        ],
        "names_to": "city_name",
        "values_to": "allocation_value",
        "export_path": "./exports/resource_allocation.csv",
        "export_func": "export_resource_allocation",
    },
    "demand": {
        "sheets": {
            "Volume": {
                "columns": ["job_type"],
                "types": {"job_type": "string", "demand_jobs": "numeric"},
                "transform_config": {
                    "type": "columns",
                    "column_format": "yyyy-mm-dd",
                    "require_monday": True,
                },
                "names_to": "week",
                "values_to": "demand_jobs",
                "date_range": {
                    "start": "2025-01-06",
                    "end": "2025-01-20",
                    "freq": "W-MON",
                },
                "value_checks": {"job_type": ["A", "B", "C"]},
                "export_path": "./exports/demand_volume.csv",
                "export_func": "export_demand_volume",
            },
            "Mix": {
                "columns": ["job_type"],
                "types": {"job_type": "string", "demand_hours": "numeric"},
                "transform_config": {
                    "type": "columns",
                    "column_format": "yyyy-mm-dd",
                    "require_monday": True,
                },
                "names_to": "week",
                "values_to": "demand_hours",
                "date_range": {
                    "start": "2025-01-06",
                    "end": "2025-01-20",
                    "freq": "W-MON",
                },
                "value_checks": {"job_type": ["A", "B", "C"]},
                "export_path": "./exports/demand_mix.csv",
                "export_func": "export_demand_mix",
            },
        },
    },
}


# ============================================================================ #
# Sample Files
# ============================================================================ #


# Sample file generators
# create_sample_file(file_type)
# - Returns a small example DataFrame used for download templates and testing.
def create_sample_file(file_type):
    # Return a small example DataFrame that matches the schema defined in
    # `validation_rules` for the given `file_type`. These are used by the
    # download handlers to provide CSV templates for users.
    if file_type == "attrition":
        return pd.DataFrame(
            {
                "week": ["2025-01-06", "2025-01-13", "2025-01-20"],
                "job_type": ["A", "B", "C"],
                "attrition_count": [5.2, 2.1, 4.8],
                # hire_date uses a different format (yyyy/mm/dd) per new rules
                "hire_date": ["2025/01/13", "2025/01/13", "2025/01/06"],
            }
        )
    elif file_type == "recruitment":
        return pd.DataFrame(
            {
                "week": ["2025-01-06", "2025-01-13", "2025-01-20"],
                "job_type": ["A", "B", "C"],
                "recruitment_count": [15, 8, 12],
            }
        )
    elif file_type == "fte":
        return pd.DataFrame(
            {
                "week": ["2025-01-06", "2025-01-13", "2025-01-20"],
                "job_type": ["A", "B", "C"],
                "fte_count": [120.5, 85.2, 95.8],
            }
        )
    elif file_type == "fte_wide":
        return pd.DataFrame(
            {
                "job_type": ["A", "B", "C"],
                "2025-01-06": [120.5, 85.2, 95.8],
                "2025-01-13": [121.0, 86.0, 96.5],
                "2025-01-20": [119.8, 84.5, 94.0],
            }
        )
    elif file_type == "patch_mapping":
        return pd.DataFrame(
            {
                "wmis": ["A", "B", "C"],
                "region": ["North", "South", "East"],
            }
        )
    elif file_type == "demand":
        # return a dict of sample sheets so callers can generate Excel templates if needed
        return {
            "Volume": pd.DataFrame(
                {
                    "job_type": ["A", "B", "C"],
                    "2025-01-06": [100, 80, 90],
                    "2025-01-13": [105, 82, 92],
                    "2025-01-20": [98, 78, 95],
                }
            ),
            "Mix": pd.DataFrame(
                {
                    "job_type": ["A", "B", "C"],
                    "2025-01-06": [8.0, 7.5, 8.2],
                    "2025-01-13": [8.1, 7.6, 8.3],
                    "2025-01-20": [7.9, 7.4, 8.0],
                }
            ),
        }
    elif file_type == "resource_allocation":
        # 3 date ID columns with different formats; cities as value dimensions
        return pd.DataFrame(
            {
                "date_1": ["15/01/2025", "15/02/2025", "15/03/2025"],
                "date_2": ["Jan-25", "Feb-25", "Mar-25"],
                "date_3": ["01/15/25", "02/15/25", "03/15/25"],
                "skill": ["MS", "SS", "MS"],
                "New York": [100.5, 105.2, 98.8],
                "Los Angeles": [85.0, 88.5, 90.2],
                "Chicago": [75.5, 78.0, 82.3],
            }
        )


# ============================================================================ #
# UI
# ============================================================================ #

# Application UI
# - `app_ui` defines the page layout, file upload controls, download
#   template buttons, and placeholders for assignment/validation cards.
# - This is passed to `App` together with `server` to run the app.
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("File Upload"),
        ui.div(
            ui.h5("Download Sample Templates"),
            ui.download_button(
                "download_attrition",
                "Download Attrition Template",
                class_="btn-outline-primary btn-sm me-2 mb-2",
            ),
            ui.download_button(
                "download_recruitment",
                "Download Recruitment Template",
                class_="btn-outline-primary btn-sm me-2 mb-2",
            ),
            ui.download_button(
                "download_fte",
                "Download FTE Template",
                class_="btn-outline-primary btn-sm me-2 mb-2",
            ),
            ui.download_button(
                "download_fte_wide",
                "Download FTE Wide Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            ui.download_button(
                "download_patch_mapping",
                "Download Patch Mapping Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            ui.download_button(
                "download_demand",
                "Download Demand Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            ui.download_button(
                "download_resource_allocation",
                "Download Resource Allocation Template",
                class_="btn-outline-primary btn-sm mb-2",
            ),
            class_="mb-3",
        ),
        ui.hr(),
        ui.input_file(
            "uploaded_files",
            "Upload Files (CSV or Excel)",
            accept=[".csv", ".xlsx", ".xls", ".xlsm"],
            multiple=True,
        ),
        ui.br(),
        ui.output_ui("file_assignment_ui"),
    ),
    ui.card(ui.card_header("File Assignment"), ui.output_ui("file_assignment_display")),
    ui.card(
        ui.card_header("File Validation Results"), ui.output_ui("validation_results")
    ),
    ui.card(ui.card_header("Uploaded Files Preview"), ui.output_ui("file_previews")),
)


# ============================================================================ #
# Server
# ============================================================================ #


# Server function
# - `server` wires up reactives, file reading, download handlers, assignment
#   UI generation, and triggers validation when the user assigns types.
def server(input, output, session):
    # Server manages reactive state for uploaded files, user assignments,
    # and validation results. It wires up handlers for file downloads,
    # file reading, assignment UI, and running validations.
    uploaded_files_data = reactive.value({})
    assigned_files = reactive.value({})
    validation_results_val = reactive.value({})

    # ============================================================================ #
    # Helper: read_file
    # ============================================================================ #

    # - Reads an uploaded file from `file_info['datapath']` and returns a DataFrame.
    # - Supports CSV and Excel; returns None on failure.
    def read_file(file_info):
        """
        Reads uploaded CSV or Excel file and returns:
        - pandas.DataFrame if CSV or Excel with 1 sheet
        - dict of {sheet_name: DataFrame} if Excel with multiple sheets
        """
        file_path = file_info["datapath"]
        file_ext = Path(file_info["name"]).suffix.lower()
        try:
            if file_ext == ".csv":
                return pd.read_csv(file_path)
            elif file_ext in [".xlsx", ".xls", ".xlsm"]:
                # Read all sheets first
                all_sheets = pd.read_excel(file_path, sheet_name=None)
                if len(all_sheets) == 1:
                    # Return only the DataFrame (not a dict) if single sheet
                    return next(iter(all_sheets.values()))
                else:
                    # Multi-sheet Excel — return as dict
                    return all_sheets
            else:
                return None
        except Exception:
            return None

    # ============================================================================ #
    # Download handlers
    # ============================================================================ #

    # - Each decorated `@render.download` returns a CSV template for that file type.
    # - These are lightweight generators used by the UI download buttons.
    @render.download(filename="attrition_template.xlsx")
    def download_attrition():
        # Provide Excel template for attrition
        buffer = io.BytesIO()
        df = create_sample_file("attrition")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="recruitment_template.xlsx")
    def download_recruitment():
        # Provide Excel template for recruitment
        buffer = io.BytesIO()
        df = create_sample_file("recruitment")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="fte_template.xlsx")
    def download_fte():
        # Provide Excel template for FTE (long format)
        buffer = io.BytesIO()
        df = create_sample_file("fte")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="fte_wide_template.xlsx")
    def download_fte_wide():
        # Provide Excel template for FTE (wide format with date columns)
        buffer = io.BytesIO()
        df = create_sample_file("fte_wide")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="patch_mapping_template.xlsx")
    def download_patch_mapping():
        # Provide Excel template for Patch Mapping
        buffer = io.BytesIO()
        df = create_sample_file("patch_mapping")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="demand_template.xlsx")
    def download_demand():
        # Provide Excel template for demand (multi-sheet)
        sample = create_sample_file("demand")  # returns dict of DataFrames
        buffer = io.BytesIO()
        if isinstance(sample, dict):
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:  # use openpyxl
                for sheet_name, df in sample.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="resource_allocation_template.xlsx")
    def download_resource_allocation():
        # Provide Excel template for resource allocation (wide format with 3 date columns)
        buffer = io.BytesIO()
        df = create_sample_file("resource_allocation")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    # ============================================================================ #
    # Process uploads
    # ============================================================================ #
    @reactive.effect
    @reactive.event(input.uploaded_files)
    def _():
        create_modal_with_loading("Uploading files")
        # React to changes in uploaded files. Read each into a DataFrame and
        # store in reactive `uploaded_files_data`.
        files = input.uploaded_files()
        if files:
            files_data = {}
            for file_info in files:
                file_name = file_info["name"]
                df = read_file(file_info)
                if df is not None:
                    files_data[file_name] = df
            uploaded_files_data.set(files_data)
            assigned_files.set({})
            validation_results_val.set({})
        close_modal()

    # ============================================================================ #
    # UI: file assignment builder
    # ============================================================================ #
    @render.ui
    # - Renders inputs to map uploaded filenames to known file types.
    def file_assignment_ui():
        # Build UI allowing the user to assign an uploaded file to a known
        # file type (attrition, recruitment, fte, fte_wide).
        files_data = uploaded_files_data()
        if not files_data:
            return ui.div()
        file_names = list(files_data.keys())
        file_type_options = [""] + list(validation_rules.keys())
        assignment_inputs = [ui.h5("Assign File Types:")]
        for file_name in file_names:
            assignment_inputs.append(
                ui.div(
                    ui.strong(f"{file_name}:"),
                    ui.input_select(
                        f"file_type_{file_name.replace('.', '_').replace(' ', '_')}",
                        "",
                        choices=file_type_options,
                        selected="",
                    ),
                    ui.input_text(
                        f"remarks_{file_name.replace('.', '_').replace(' ', '_')}",
                        label="Remarks (optional)",
                    ),
                    class_="mb-2",
                )
            )
        assignment_inputs.append(
            ui.input_action_button(
                "submit_assignment", "Submit Assignment", class_="btn-success mt-3"
            )
        )
        return ui.div(*assignment_inputs)

    # ============================================================================ #
    # Trigger Validation
    # ============================================================================ #
    @reactive.effect
    @reactive.event(input.submit_assignment)
    def _():
        create_modal_with_loading("Validating assigned files")
        files_data = uploaded_files_data()
        if not files_data:
            return
        assignments = {}
        for file_name in files_data.keys():
            input_id = f"file_type_{file_name.replace('.', '_').replace(' ', '_')}"
            file_type = getattr(input, input_id)()
            input_id = f"remarks_{file_name.replace('.', '_').replace(' ', '_')}"
            remarks = getattr(input, input_id)()
            if file_type:
                assignments[file_type] = {
                    "filename": file_name,
                    "data": files_data[file_name],
                    "remarks": remarks,
                }
        # Persist assignments and trigger validation of all assigned files
        assigned_files.set(assignments)
        validate_assigned_files()
        close_modal()

    # Validation runner
    # - validate_assigned_files runs validations for all currently-assigned files
    #   and stores results in the reactive `validation_results_val`.
    def validate_assigned_files():
        # Validate each file that the user has assigned to a type using the
        # corresponding entry in `validation_rules`.
        assignments = assigned_files()
        results = {}
        for file_type, file_info in assignments.items():
            if file_type in validation_rules:
                results[file_type] = validate_file(
                    file_info["data"],
                    validation_rules[file_type],
                    f"{file_type.capitalize()} ({file_info['filename']})",
                    f"{file_info['filename']}",
                    remarks=file_info.get("remarks", ""),
                )
        validation_results_val.set(results)

    # ============================================================================ #
    # Display assigned files, validation results & previews
    # ============================================================================ #
    @render.ui
    # UI: display assigned files
    # - Shows which uploaded file has been assigned to each known type.
    def file_assignment_display():
        assignments = assigned_files()
        if not assignments:
            return ui.p("No files assigned yet", class_="text-muted")
        return ui.div(
            *[
                ui.div(
                    ui.strong(f"{ft.capitalize()}: "),
                    ui.span(fi["filename"]),
                    class_="mb-1",
                )
                for ft, fi in assignments.items()
            ]
        )

    @render.ui
    # UI: validation results
    # - Shows success, error, or warning messages for validated files.
    def validation_results():
        results = validation_results_val()
        if not results:
            return ui.p(
                "Upload and assign files to see validation results", class_="text-muted"
            )
        content = []
        for _, result in results.items():
            if result["valid"]:
                content.append(
                    ui.div(
                        ui.span("✓ ", class_="text-success fw-bold"),
                        ui.span(result["message"], class_="text-success"),
                        class_="mb-2",
                    )
                )
                if "warning" in result:
                    content.append(
                        ui.div(
                            ui.span("⚠ ", class_="text-warning fw-bold"),
                            ui.span(result["warning"], class_="text-warning"),
                            class_="mb-2",
                        )
                    )
            else:
                content.append(
                    ui.div(
                        ui.span("✗ ", class_="text-danger fw-bold"),
                        ui.span(result["message"], class_="text-danger"),
                        class_="mb-2",
                    )
                )
                if "warning" in result:
                    content.append(
                        ui.div(
                            ui.span("⚠ ", class_="text-warning fw-bold"),
                            ui.span(result["warning"], class_="text-warning"),
                            class_="mb-2",
                        )
                    )
        return ui.div(*content)

    @render.ui
    def file_previews():
        assignments = assigned_files()
        if not assignments:
            return ui.p("No files assigned yet", class_="text-muted")
        previews = []
        for ft, fi in assignments.items():
            data = fi["data"]
            if isinstance(data, dict):
                # Multi-sheet file (e.g., demand)
                sheet_previews = []
                for sheet_name, df in data.items():
                    sheet_previews.append(
                        ui.div(
                            ui.h6(f"Sheet: {sheet_name}"),
                            ui.pre(str(df.head())),
                        )
                    )
                previews.append(
                    ui.div(
                        ui.h5(f"{ft.capitalize()} File Preview ({fi['filename']})"),
                        *sheet_previews,
                        ui.hr(),
                    )
                )
            else:
                # Normal single DataFrame
                previews.append(
                    ui.div(
                        ui.h5(f"{ft.capitalize()} File Preview ({fi['filename']})"),
                        ui.pre(str(data.head())),
                        ui.hr(),
                    )
                )
        return ui.div(*previews)


# App instantiation
# - Create the Shiny `App` from `app_ui` and `server` (commented out when disabling).
app = App(app_ui, server)
