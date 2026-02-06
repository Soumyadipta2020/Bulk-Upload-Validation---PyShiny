from shiny import render, reactive, ui
import pandas as pd
from pathlib import Path
import io
from datetime import datetime

# Local modules
from App.helpers import create_modal_with_loading, close_modal
from App.samples import create_sample_file
from App.validation import validate_file, validation_rules


def server(input, output, session):
    # Server manages reactive state for uploaded files, user assignments,
    # and validation results. It wires up handlers for file downloads,
    # file reading, assignment UI, and running validations.
    uploaded_files_data = reactive.value({})
    assigned_files = reactive.value({})
    validation_results_val = reactive.value({})

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
                all_sheets = pd.read_excel(file_path, sheet_name=None)
                if len(all_sheets) == 1:
                    return next(iter(all_sheets.values()))
                else:
                    return all_sheets
            else:
                return None
        except Exception:
            return None

    # Download handlers
    @render.download(filename="attrition_template.xlsx")
    def download_attrition():
        buffer = io.BytesIO()
        df = create_sample_file("attrition")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="recruitment_template.xlsx")
    def download_recruitment():
        buffer = io.BytesIO()
        df = create_sample_file("recruitment")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="fte_template.xlsx")
    def download_fte():
        buffer = io.BytesIO()
        df = create_sample_file("fte")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="fte_wide_template.xlsx")
    def download_fte_wide():
        buffer = io.BytesIO()
        df = create_sample_file("fte_wide")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="patch_mapping_template.xlsx")
    def download_patch_mapping():
        buffer = io.BytesIO()
        df = create_sample_file("patch_mapping")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="demand_template.xlsx")
    def download_demand():
        sample = create_sample_file("demand")
        buffer = io.BytesIO()
        if isinstance(sample, dict):
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                for sheet_name, df in sample.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="resource_allocation_template.xlsx")
    def download_resource_allocation():
        buffer = io.BytesIO()
        df = create_sample_file("resource_allocation")
        if isinstance(df, pd.DataFrame):
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    # Process uploads
    @reactive.effect
    @reactive.event(input.uploaded_files)
    def _():
        create_modal_with_loading("Uploading files")
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

    @render.ui
    def file_assignment_ui():
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
            ui.input_action_button("submit_assignment", "Submit Assignment", class_="btn-success mt-3")
        )
        return ui.div(*assignment_inputs)

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
        assigned_files.set(assignments)
        validate_assigned_files()
        close_modal()

    def validate_assigned_files():
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

    @render.ui
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
                previews.append(
                    ui.div(
                        ui.h5(f"{ft.capitalize()} File Preview ({fi['filename']})"),
                        ui.pre(str(data.head())),
                        ui.hr(),
                    )
                )
        return ui.div(*previews)
