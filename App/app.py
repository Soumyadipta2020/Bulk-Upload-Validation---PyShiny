# ============================================================================ #
# Importing necessary libraries
# ============================================================================ #

from shiny import App, render, ui, reactive
import pandas as pd
from pathlib import Path
import io
from datetime import datetime

# ============================================================================ #
# Modal window
# ============================================================================ #


def create_modal_with_loading(text: str):
    """
    Create a modal window with custom text and a loading animation

    Args:
        text: The text to display in the modal

    Returns:
        A Shiny modal object
    """
    animations = {
        "spinner": """
            <div class="spinner" style="display: inline-block; width: 16px; height: 16px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        """,
        "dots": """
            <div class="dots" style="display: inline-block;">
                <span style="animation: blink 1.4s infinite both; animation-delay: 0s;">.</span>
                <span style="animation: blink 1.4s infinite both; animation-delay: 0.2s;">.</span>
                <span style="animation: blink 1.4s infinite both; animation-delay: 0.4s;">.</span>
            </div>
            <style>
                @keyframes blink {
                    0%, 80%, 100% { opacity: 0; }
                    40% { opacity: 1; }
                }
            </style>
        """,
        "pulse": """
            <div class="pulse" style="display: inline-block; width: 16px; height: 16px; background-color: #3498db; border-radius: 50%; animation: pulse 1.5s ease-in-out infinite;"></div>
            <style>
                @keyframes pulse {
                    0% { transform: scale(0); opacity: 1; }
                    100% { transform: scale(1); opacity: 0; }
                }
            </style>
        """,
        "bars": """
            <div class="bars" style="display: inline-block;">
                <div style="display: inline-block; width: 3px; height: 16px; background-color: #3498db; margin: 0 1px; animation: bars 1.2s infinite ease-in-out; animation-delay: -1.1s;"></div>
                <div style="display: inline-block; width: 3px; height: 16px; background-color: #3498db; margin: 0 1px; animation: bars 1.2s infinite ease-in-out; animation-delay: -1.0s;"></div>
                <div style="display: inline-block; width: 3px; height: 16px; background-color: #3498db; margin: 0 1px; animation: bars 1.2s infinite ease-in-out; animation-delay: -0.9s;"></div>
            </div>
            <style>
                @keyframes bars {
                    0%, 40%, 100% { transform: scaleY(0.4); }
                    20% { transform: scaleY(1.0); }
                }
            </style>
        """,
    }

    animation_html = animations.get("bars", "spinner")

    ui.modal_show(
        ui.modal(
            ui.div(
                ui.HTML(f"""
                <div style="font-size: 16px; text-align: center; padding: 20px;">
                    <span>{text}</span>
                    <span style="margin-left: 10px;">
                        {animation_html}
                    </span>
                </div>
            """)
            ),
            easy_close=False,
            footer=None,
        )
    )


def close_modal():
    import time

    time.sleep(2)  # Simulate a delay for demonstration purposes
    ui.modal_remove()


# ============================================================================ #
# Key Generation Function
# ============================================================================ #
def add_key_column(df: pd.DataFrame | None, filename: str, key: str = None):
    """
    Two modes:
    - If df is None: return a generated key string for the filename (used to
        create a single key for a multi-sheet file).
    - If df is a DataFrame: add/assign the 'key' column. If `key` is None a
        new key will be generated. Returns the DataFrame with the 'key' column.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    generated_key = f"{Path(filename).stem}_{timestamp}"
    if df is None:
        return key or generated_key
    df = df.copy()
    df["key"] = key or generated_key
    return df


# ============================================================================ #
# Individual Export Helpers
# ============================================================================ #


# Helper: export_validated_file
# - Saves a validated DataFrame to an `export/` folder next to this script.
# - Returns (success: bool, message: str) to indicate result.
def export_demand_volume(df: pd.DataFrame, export_file: Path, file_id: str):
    """Export the 'Volume' sheet of demand."""
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_demand_mix(df: pd.DataFrame, export_file: Path, file_id: str):
    """Export the 'Mix' sheet of demand."""
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_attrition(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_recruitment(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_fte(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_fte_wide(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_patch_mapping(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_resource_allocation(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


# ============================================================================ #
# Export Validated File generic function
# ============================================================================ #


def export_validated_file(df, export_path, file_id, export_func=None):
    """
    Export validated DataFrame to 'export/' folder.
    - If df -> DataFrame.
    - export_func may be a string (name of function in globals) or a callable.
    """
    try:
        base_dir = Path(__file__).parent.resolve()
        export_dir = base_dir / "export"
        export_dir.mkdir(parents=True, exist_ok=True)

        export_file = export_dir / Path(export_path).name

        func = None
        if export_func:
            if isinstance(export_func, str):
                func = globals().get(export_func)
            elif callable(export_func):
                func = export_func

        if callable(func):
            success = func(df, export_file, file_id)
            if success:
                return True, f"{file_id}: Successfully validated ✅ and exported ✅"
            else:
                return (
                    False,
                    f"{file_id}: Successfully validated ✅ but export function failed ❌",
                )
        else:
            return (
                False,
                f"{file_id}: Successfully validated ✅ but failed to export ❌",
            )
    except Exception as e:
        return False, f"{file_id}: Validation passed ✅ but export failed ❌ ({str(e)})"


def _convert_user_fmt(fmt_str: str) -> str:
    """Convert a user format like 'yyyy-mm-dd' or 'dd/mm/yyyy' or 'mmm-yy' to Python strptime format."""
    if not fmt_str:
        return None
    # Order matters: replace longer patterns first to avoid double replacements
    return (
        fmt_str.replace("yyyy", "%Y")
        .replace("mmm", "%b")  # month abbreviation before mm
        .replace("mm", "%m")
        .replace("yy", "%y")
        .replace("dd", "%d")
    )


def _normalize_dates_for_export(df: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """Return a copy of df where date columns defined by `rules` are parsed
    and converted to ISO `YYYY-MM-DD` strings for export.

    Rules supported:
    - `date_columns`: mapping col -> {format, range}
    - `types`: mapping col -> 'date'
    - `names_to` / `names_to` used for melted date column name
    """
    df = df.copy()
    date_columns_cfg = rules.get("date_columns", {})

    # Candidate date columns: explicit in date_columns_cfg or in types
    types_map = rules.get("types", {})

    # Determine if a melted date column name is used.
    # Only treat `names_to` as a date column when the transform type is 'columns'
    transform_type = rules.get("transform_config", {}).get("type", "none")
    date_col_name = None
    if transform_type == "columns":
        date_col_name = rules.get("names_to", "date")

    # Build a set of columns to attempt parsing
    cols_to_parse = set()
    for col in df.columns:
        if col in date_columns_cfg:
            cols_to_parse.add(col)
        elif types_map.get(col) == "date":
            cols_to_parse.add(col)
    # Also consider the names_to column if present and it's being used as a date
    if date_col_name and (date_col_name in df.columns):
        cols_to_parse.add(date_col_name)

    for col in list(cols_to_parse):
        if col not in df.columns:
            continue
        # Determine format
        cfg = date_columns_cfg.get(col, {})
        fmt = cfg.get("format") if isinstance(cfg, dict) else None
        py_fmt = _convert_user_fmt(fmt) if fmt else None
        try:
            if py_fmt:
                parsed = pd.to_datetime(
                    df[col].astype(str), format=py_fmt, errors="coerce"
                )
            else:
                parsed = pd.to_datetime(df[col], errors="coerce")
            # Replace column with ISO formatted strings, preserving NaT as empty
            df[col] = parsed.dt.strftime("%Y-%m-%d")
            df.loc[parsed.isna(), col] = ""
        except Exception:
            # on any parse failure, leave column as-is
            continue

    return df


# ============================================================================ #
# Validation Function
# ============================================================================ #


# Helper inner that runs the previous single-DataFrame validation logic
def validate_single_file(df, rules_single, file_id_single):
    # If the rule specifies `skiprows`, ignore those initial rows when
    # performing validation. This only affects which DataFrame rows are
    # validated; existing validation logic and reported row numbers remain
    # unchanged.
    print(df)
    try:
        skiprows = int(rules_single.get("skiprows", 0) or 0)
    except Exception:
        skiprows = 0
    skiprows = skiprows - 1
    if skiprows >= 0:
        df = df.iloc[skiprows:].copy().reset_index(drop=True)
        print(df)
        # Use first row as column names after skipping rows
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)
    
    # Column names validation
    expected_columns = rules_single["columns"]
    transform_config = rules_single.get("transform_config", {"type": "none"})
    if not set(expected_columns).issubset(set(df.columns)):
        return {
            "valid": False,
            "message": f"{file_id_single}: Invalid columns. Expected {expected_columns}, got {list(df.columns)}",
        }

    # Type validation (support per-column date formats)
    expected_types = rules_single["types"]
    # date_columns: optional mapping col -> {format: 'yyyy-mm-dd', range: {...}}
    date_columns_cfg = rules_single.get("date_columns", {})

    def _convert_fmt(fmt_str: str) -> str:
        # convert simple format like 'yyyy-mm-dd' or 'dd/mm/yyyy' or 'mmm-yy' to strptime
        return (
            fmt_str.replace("yyyy", "%Y")
            .replace("mmm", "%b")
            .replace("mm", "%m")
            .replace("yy", "%y")
            .replace("dd", "%d")
        )
    def _expected_len_from_pyfmt(py_fmt: str) -> int | None:
        """Return expected length of a formatted date using `py_fmt` by
        formatting a sample date. Returns None if formatting fails.
        """
        if not py_fmt:
            return None
        try:
            sample = datetime(2000, 11, 22).strftime(py_fmt)
            return len(sample)
        except Exception:
            return None
    
    for col, expected_type in expected_types.items():
        if col in df.columns:
            try:
                if expected_type == "numeric":
                    try:
                        pd.to_numeric(df[col].dropna(how='all'), errors="raise")
                    except Exception:
                        first_bad = df[
                            pd.to_numeric(df[col], errors="coerce").isna()
                            & df[col].notna()
                        ].index[0]
                        row_number = first_bad + 1
                        first_val = df[col].iloc[first_bad]
                        return {
                            "valid": False,
                            "message": (
                                f"{file_id_single}: Column '{col}' has invalid numeric format. "
                                f"Found '{first_val}' at row {row_number}"
                            ),
                        }
                elif expected_type == "string":
                    try:
                        df[col].dropna(how='all').astype(str)
                    except Exception:
                        return {
                            "valid": False,
                            "message": (
                                f"{file_id_single}: Column '{col}' has invalid string format."
                            ),
                        }
                elif expected_type == "date":
                    # If the rules provide a custom format for this column, use it
                    col_cfg = date_columns_cfg.get(col, {})
                    fmt = col_cfg.get("format")
                    if fmt:
                        py_fmt = _convert_fmt(fmt)
                        sample_len = _expected_len_from_pyfmt(py_fmt)
                        # Prepare series trimmed to expected length when possible
                        s_all = df[col].astype(str)
                        s = df[col].dropna(how='all').astype(str)
                        if sample_len:
                            s = s.str.slice(0, sample_len)
                            s_all = s_all.str.slice(0, sample_len)
                        parsed = pd.to_datetime(s, format=py_fmt, errors="coerce")
                        if parsed.isna().any():
                            # find first offending original row and value
                            parsed_all = pd.to_datetime(s_all, format=py_fmt, errors="coerce")
                            mask = parsed_all.isna() & df[col].notna()
                            if mask.any():
                                first_bad = mask[mask].index[0]
                                row_number = first_bad + 1
                                first_val = df.loc[first_bad, col]
                                return {
                                    "valid": False,
                                    "message": (
                                        f"{file_id_single}: Column '{col}' has invalid date format. "
                                        f"Expected format '{fmt}'. Found '{first_val}' at row {row_number}"
                                    ),
                                }
                            else:
                                return {
                                    "valid": False,
                                    "message": (
                                        f"{file_id_single}: Column '{col}' has invalid date format. "
                                        f"Expected format '{fmt}'."
                                    ),
                                }
                    else:
                        # fallback: try to parse using pandas inference
                        pd.to_datetime(df[col].dropna(how='all'), errors="raise")
            except Exception as e:
                return {
                    "valid": False,
                    "message": (
                        f"{file_id_single}: Column '{col}' has invalid type. "
                        f"Expected {expected_type}."
                    ),
                }

    # Week/date column validation (support custom formats and per-column ranges)
    if transform_config["type"] == "column":
        # For "column" type, date column is inferred from date_columns config
        date_col = list(date_columns_cfg.keys())[0] if date_columns_cfg else None
        if date_col in df.columns:
            # determine expected format for this date column from date_columns config
            wc_fmt = date_columns_cfg.get(date_col, {}).get("format")
            py_fmt = _convert_fmt(wc_fmt) if wc_fmt else None
            sample_len = _expected_len_from_pyfmt(py_fmt) if py_fmt else None
            for idx, val in df[date_col].items():
                if pd.isna(val):
                    continue
                val_str = str(val)
                if py_fmt:
                    if sample_len:
                        val_str = val_str[:sample_len]
                    d = pd.to_datetime(val_str, format=py_fmt, errors="coerce")
                else:
                    d = pd.to_datetime(val_str, errors="coerce")
                if pd.isna(d):
                    return {
                        "valid": False,
                        "message": f"{file_id_single}: Column '{date_col}' has invalid date '{val_str}' at row {idx + 2}",
                    }
                # If rules expect weekly Monday values, check weekday when freq specified
                # Use per-column range config to infer weekly expectation if 'freq' == 'W-MON'
                col_range_cfg = date_columns_cfg.get(date_col, {}).get("range")
                freq = None
                if col_range_cfg and isinstance(col_range_cfg, dict):
                    freq = col_range_cfg.get("freq")
                if freq == "W-MON" and d.weekday() != 0:
                    return {
                        "valid": False,
                        "message": f"{file_id_single}: Column '{date_col}' has non-Monday date '{val_str}' at row {idx + 2}",
                    }
    elif transform_config["type"] == "columns":
        # wide-format: date columns are column names; validate that the column names
        # can be parsed as dates in the provided format (transform_config -> 'column_format')
        week_cols = [c for c in df.columns if c not in expected_columns]
        col_fmt = transform_config.get("column_format")
        py_col_fmt = _convert_fmt(col_fmt) if col_fmt else None
        parsed_cols = []
        for col in week_cols:
            col_str = str(col)
            if py_col_fmt:
                d = pd.to_datetime(col_str, format=py_col_fmt, errors="coerce")
            else:
                d = pd.to_datetime(col_str, errors="coerce")
            if d is pd.NaT:
                return {
                    "valid": False,
                    "message": f"{file_id_single}: Invalid date column '{col}'. Expected format {col_fmt or 'ISO'}",
                }
            # If weekly enforcement is desired, default to checking Monday
            if transform_config.get("require_monday", True) and d.weekday() != 0:
                return {
                    "valid": False,
                    "message": f"{file_id_single}: Date column '{col}' is not a valid Monday",
                }
            parsed_cols.append(d.strftime("%Y-%m-%d"))
    elif transform_config["type"] == "multi_date_ids":
        # Multiple date ID columns (e.g., date_1, date_2, date_3); city columns are values
        # Validate each date ID column using its format from date_columns_cfg
        id_columns = rules_single.get("id_columns", [])
        for date_col in id_columns:
            if date_col not in df.columns:
                return {
                    "valid": False,
                    "message": f"{file_id_single}: Missing required ID column '{date_col}'",
                }
            col_cfg = date_columns_cfg.get(date_col, {})
            fmt = col_cfg.get("format") if isinstance(col_cfg, dict) else None
            py_fmt = _convert_fmt(fmt) if fmt else None
            sample_len = _expected_len_from_pyfmt(py_fmt) if py_fmt else None
            for idx, val in df[date_col].items():
                if pd.isna(val):
                    continue
                val_str = str(val)
                if py_fmt:
                    if sample_len:
                        val_str = val_str[:sample_len]
                    d = pd.to_datetime(val_str, format=py_fmt, errors="coerce")
                else:
                    d = pd.to_datetime(val_str, errors="coerce")
                if pd.isna(d):
                    return {
                        "valid": False,
                        "message": f"{file_id_single}: Column '{date_col}' has invalid date '{val_str}' at row {idx + 2}",
                    }

    # Date range validation
    # Parse actual week labels using formats from rules before comparing to
    # expected ISO labels. Use per-column `date_columns[<col>]['format']` if
    # present; for wide `columns` use that format or fall back to
    # transform_config['column_format'].
    week_config = transform_config

    # Iterate per-column ranges first
    for dc_name, dc_cfg in date_columns_cfg.items():
        if not isinstance(dc_cfg, dict):
            continue
        date_range = dc_cfg.get("range")
        if not date_range or week_config.get("type") == "none":
            continue

        # Respect optional start_offset / end_offset in the per-column range
        start = pd.to_datetime(date_range["start"])
        end = pd.to_datetime(date_range["end"])
        start_offset = date_range.get("start_offset", 0) or 0
        end_offset = date_range.get("end_offset", 0) or 0
        start = start + pd.Timedelta(days=int(start_offset))
        end = end + pd.Timedelta(days=int(end_offset))
        expected_weeks = pd.date_range(start, end, freq=date_range.get("freq", "W-MON"))
        expected_labels = [d.strftime("%Y-%m-%d") for d in expected_weeks]

        # Determine parsing format for actual week labels
        col_fmt = dc_cfg.get("format")
        py_col_fmt = _convert_fmt(col_fmt) if col_fmt else None

        if week_config["type"] == "column":
            # Parse values in the date column using provided format
            if dc_name in df.columns:
                if py_col_fmt:
                    sample_len = _expected_len_from_pyfmt(py_col_fmt)
                    s = df[dc_name].astype(str)
                    if sample_len:
                        s = s.str.slice(0, sample_len)
                    parsed = pd.to_datetime(s, format=py_col_fmt, errors="coerce")
                    weeks = parsed.dropna().dt.strftime("%Y-%m-%d").unique().tolist()
                else:
                    parsed = pd.to_datetime(df[dc_name], errors="coerce")
                    weeks = parsed.dropna().dt.strftime("%Y-%m-%d").unique().tolist()
            else:
                weeks = []
        elif week_config["type"] == "columns":
            # Column headers represent weeks; parse each header using the
            # per-column format when provided, else fall back to transform
            # column_format
            candidate_cols = [c for c in df.columns if c not in expected_columns]
            parse_fmt = (
                py_col_fmt
                or (_convert_fmt(transform_config.get("column_format")) if transform_config.get("column_format") else None)
            )
            weeks = []
            for c in candidate_cols:
                c_str = str(c)
                if parse_fmt:
                    c_sample_len = _expected_len_from_pyfmt(parse_fmt)
                    if c_sample_len:
                        c_str = c_str[:c_sample_len]
                    d = pd.to_datetime(c_str, format=parse_fmt, errors="coerce")
                else:
                    d = pd.to_datetime(c_str, errors="coerce")
                if pd.isna(d):
                    # keep original string if unparsable so it shows as extra/missing
                    weeks.append(c_str)
                else:
                    weeks.append(d.strftime("%Y-%m-%d"))
        else:
            weeks = []

        missing = sorted(set(expected_labels) - set(weeks))
        extra = sorted(set(weeks) - set(expected_labels))

        if missing:
            return {
                "valid": False,
                "message": f"{file_id_single}: Missing weeks {missing} from expected range {date_range}",
            }
        elif extra:
            return {
                "valid": False,
                "warning": f"{file_id_single}: Extra weeks {extra} beyond expected {date_range}",
                "message": f"{file_id_single}: Sheet is valid ✅ (with warning)",
            }

    # Fallback to top-level date_range if present
    date_range = rules_single.get("date_range", None)
    if date_range and week_config.get("type") != "none":
        # Honor optional start_offset / end_offset on top-level date_range too
        start = pd.to_datetime(date_range["start"])
        end = pd.to_datetime(date_range["end"])
        start_offset = date_range.get("start_offset", 0) or 0
        end_offset = date_range.get("end_offset", 0) or 0
        start = start + pd.Timedelta(days=int(start_offset))
        end = end + pd.Timedelta(days=int(end_offset))
        expected_weeks = pd.date_range(start, end, freq=date_range.get("freq", "W-MON"))
        expected_labels = [d.strftime("%Y-%m-%d") for d in expected_weeks]

        if week_config["type"] == "column":
            # Try to infer the date column and its format
            inferred_col = (
                list(date_columns_cfg.keys())[0]
                if date_columns_cfg
                else week_config.get("name")
            )
            col_fmt = (
                date_columns_cfg.get(inferred_col, {}).get("format")
                if inferred_col
                else None
            )
            py_col_fmt = _convert_fmt(col_fmt) if col_fmt else None
            if inferred_col and inferred_col in df.columns:
                if py_col_fmt:
                    parsed = pd.to_datetime(
                        df[inferred_col].astype(str), format=py_col_fmt, errors="coerce"
                    )
                    weeks = parsed.dropna().dt.strftime("%Y-%m-%d").unique().tolist()
                else:
                    parsed = pd.to_datetime(df[inferred_col], errors="coerce")
                    weeks = parsed.dropna().dt.strftime("%Y-%m-%d").unique().tolist()
            else:
                weeks = []
        elif week_config["type"] == "columns":
            candidate_cols = [c for c in df.columns if c not in expected_columns]
            parse_fmt = (
                _convert_fmt(transform_config.get("column_format"))
                if transform_config.get("column_format")
                else None
            )
            weeks = []
            for c in candidate_cols:
                c_str = str(c)
                if parse_fmt:
                    c_sample_len = _expected_len_from_pyfmt(parse_fmt)
                    if c_sample_len:
                        c_str = c_str[:c_sample_len]
                    d = pd.to_datetime(c_str, format=parse_fmt, errors="coerce")
                else:
                    d = pd.to_datetime(c_str, errors="coerce")
                if pd.isna(d):
                    weeks.append(c_str)
                else:
                    weeks.append(d.strftime("%Y-%m-%d"))
        else:
            weeks = []

        missing = sorted(set(expected_labels) - set(weeks))
        extra = sorted(set(weeks) - set(expected_labels))

        if missing:
            return {
                "valid": False,
                "message": f"{file_id_single}: Missing weeks {missing} from expected range {date_range}",
            }
        elif extra:
            return {
                "valid": False,
                "warning": f"{file_id_single}: Extra weeks {extra} beyond expected {date_range}",
                "message": f"{file_id_single}: Sheet is valid ✅ (with warning)",
            }

    # Value checks
    value_checks = rules_single.get("value_checks", {})
    for col, check in value_checks.items():
        if col in df.columns:
            if check == "not_null":
                invalid_rows = df[df[col].isnull()]
                if not invalid_rows.empty:
                    first_idx = invalid_rows.index[0]
                    row_number = first_idx + 1
                    return {
                        "valid": False,
                        "message": f"{file_id_single}: Column '{col}' has null value at row {row_number}",
                    }
            elif isinstance(check, list):
                invalid_rows = df[df[col].notna() & ~df[col].isin(check)]
                if not invalid_rows.empty:
                    first_idx = invalid_rows.index[0]
                    first_val = df.loc[first_idx, col]
                    row_number = first_idx + 1
                    return {
                        "valid": False,
                        "message": (
                            f"{file_id_single}: Column '{col}' has invalid value '{first_val}' "
                            f"at row {row_number}. Allowed values: {check}"
                        ),
                    }

    return {"valid": True, "message": f"{file_id_single}: Sheet is valid ✅"}


# Validation: validate_file
# - Validates a pandas.DataFrame against a `rules` specification.
# - Returns a dict with keys: `valid` (bool), `message` (str), and optional `warning`.
def validate_file(df_input, rules, file_id, filename, remarks: str = None):
    """
    Support:
    - Single DataFrame (existing behavior)
    - dict of sheetname->DataFrame when rules defines 'sheets' (per-sheet rules).
    For multi-sheet files we:
    - validate each sheet using its dedicated rules
    - produce a single success message if all sheets valid
    - ensure the same `key` is applied to all exported sheets
    """
    # Multi-sheet handling
    if "sheets" in rules:
        sheet_rules = rules["sheets"]
        if not isinstance(df_input, dict):
            return {
                "valid": False,
                "message": f"{file_id}: Expected an Excel with sheets {list(sheet_rules.keys())}, but uploaded data is not multi-sheet.",
            }

        file_key = add_key_column(None, filename)

        transformed = {}
        for sheet_name, s_rules in sheet_rules.items():
            if sheet_name not in df_input:
                return {
                    "valid": False,
                    "message": f"{file_id}: Missing required sheet '{sheet_name}' in uploaded Excel.",
                }
            df_sheet = df_input[sheet_name]
            res = validate_single_file(df_sheet, s_rules, f"{file_id} - {sheet_name}")
            if not res.get("valid", False):
                return res

            # Transform wide to long if needed
            transform_config = s_rules.get("transform_config", {"type": "none"})
            if transform_config.get("type") == "columns":
                id_vars = s_rules["columns"]
                value_vars = [c for c in df_sheet.columns if c not in id_vars]
                df_melted = df_sheet.melt(
                    id_vars=id_vars,
                    value_vars=value_vars,
                    var_name=s_rules.get("names_to", "date"),
                    value_name=s_rules.get("values_to", "value"),
                )
                transformed[sheet_name] = add_key_column(
                    df_melted, filename, key=file_key
                )
            elif transform_config.get("type") == "multi_date_ids":
                id_columns = s_rules.get("id_columns", [])
                value_vars = [c for c in df_sheet.columns if c not in id_columns]
                df_melted = df_sheet.melt(
                    id_vars=id_columns,
                    value_vars=value_vars,
                    var_name=s_rules.get("names_to", "city_name"),
                    value_name=s_rules.get("values_to", "allocation_value"),
                )
                transformed[sheet_name] = add_key_column(
                    df_melted, filename, key=file_key
                )
            else:
                transformed[sheet_name] = add_key_column(
                    df_sheet, filename, key=file_key
                )

        # Attach Remarks and Last Update timestamp to each transformed sheet
        try:
            lu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for tn, tdf in transformed.items():
                if isinstance(tdf, pd.DataFrame):
                    tdf["Remarks"] = remarks or ""
                    tdf["Last Update"] = lu
                    transformed[tn] = tdf
        except Exception:
            pass

        test_success = {}
        for sheet_name, s_rules in sheet_rules.items():
            export_func = s_rules.get("export_func", None)
            func = None
            if export_func:
                if isinstance(export_func, str):
                    func = globals().get(export_func)
                elif callable(export_func):
                    func = export_func
            if callable(func):
                test_success[sheet_name] = True
            else:
                test_success[sheet_name] = False

        if all(test_success.values()):
            test_success_sheets = {}
            test_success_massage = {}
            for sheet_name, s_rules in sheet_rules.items():
                export_func = s_rules.get("export_func", None)
                export_path = s_rules.get("export_path", None)
                # normalize date columns for export according to sheet rules
                df_for_export = _normalize_dates_for_export(
                    transformed[sheet_name], s_rules
                )
                test_success_sheets[sheet_name], test_success_massage[sheet_name] = (
                    export_validated_file(
                        df_for_export,
                        export_path,
                        file_id,
                        export_func=export_func,
                    )
                )
            sheet_list = ", ".join(sheet_rules.keys())
            if not all(test_success_sheets.values()):
                return {
                    "valid": False,
                    "message": f"{file_id}: Sheets {sheet_list} valid ✅ But some exports failed ❌",
                    "warning": "Export skipped",
                }
            else:
                return {
                    "valid": True,
                    "message": f"{file_id}: Sheets {sheet_list} valid ✅ and exported ✅",
                }
        else:
            return {
                "valid": False,
                "message": f"{file_id}: Sheets valid ✅ but some export functions are not defined ❌",
                "warning": "Export skipped",
            }

    # Single sheet path
    else:
        df = df_input.copy()
        res = validate_single_file(df, rules, file_id)
        if not res.get("valid", False):
            return res

        # Transform if wide format
        transform_config = rules.get("transform_config", {"type": "none"})
        df_to_export = df.copy()
        if transform_config.get("type") == "columns":
            id_vars = rules["columns"]
            value_vars = [c for c in df.columns if c not in id_vars]
            df_to_export = df.melt(
                id_vars=id_vars,
                value_vars=value_vars,
                var_name=rules.get("names_to", "date"),
                value_name=rules.get("values_to", "value"),
            )
        elif transform_config.get("type") == "multi_date_ids":
            # multiple date ID columns; city columns become values
            id_columns = rules.get("id_columns", [])
            value_vars = [c for c in df.columns if c not in id_columns]
            df_to_export = df.melt(
                id_vars=id_columns,
                value_vars=value_vars,
                var_name=rules.get("names_to", "city_name"),
                value_name=rules.get("values_to", "allocation_value"),
            )

        df_to_export = add_key_column(df_to_export, filename)
        # add user remarks and last update timestamp to exported frame
        try:
            df_to_export["Remarks"] = remarks or ""
            df_to_export["Last Update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        export_func = rules.get("export_func", None)
        export_path = rules.get("export_path", None)

        if export_path:
            # normalize date columns for export according to rules
            df_norm = _normalize_dates_for_export(df_to_export, rules)
            success, export_msg = export_validated_file(
                df_norm, export_path, file_id, export_func=export_func
            )
            if success:
                return {"valid": success, "message": export_msg}
            else:
                return {
                    "valid": success,
                    "message": export_msg,
                    "warning": "Export failed",
                }
        else:
            return {
                "valid": False,
                "message": f"{file_id}: File is valid ✅ but no export path defined ❌",
                "warning": "Export skipped",
            }


# ============================================================================ #
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
      - `multi_date_ids`: special wide-format where a set of ID columns are
          date fields (e.g., `date_1`, `date_2`, `date_3`) and remaining
          columns are value dimensions (melted to long). Provide
          `id_columns` listing those date ID columns.
- `names_to` / `values_to` (str): Column names to use for the melted
    variable and value columns when performing wide->long (`melt`). For
    example `names_to: 'week'` and `values_to: 'fte_count'`.
- `id_columns` (list): For `multi_date_ids` transformations, the list of
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
- `resource_allocation` uses `transform_config: {'type': 'multi_date_ids'}`
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
        "columns": ["date_1", "date_2", "date_3"],
        "types": {
            "date_1": "date",
            "date_2": "date",
            "date_3": "date",
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
        },
        # wide format: multiple date ID columns; other columns are value dimensions
        "transform_config": {"type": "multi_date_ids"},
        "id_columns": ["date_1", "date_2", "date_3"],
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
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="recruitment_template.xlsx")
    def download_recruitment():
        # Provide Excel template for recruitment
        buffer = io.BytesIO()
        df = create_sample_file("recruitment")
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="fte_template.xlsx")
    def download_fte():
        # Provide Excel template for FTE (long format)
        buffer = io.BytesIO()
        df = create_sample_file("fte")
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="fte_wide_template.xlsx")
    def download_fte_wide():
        # Provide Excel template for FTE (wide format with date columns)
        buffer = io.BytesIO()
        df = create_sample_file("fte_wide")
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="patch_mapping_template.xlsx")
    def download_patch_mapping():
        # Provide Excel template for Patch Mapping
        buffer = io.BytesIO()
        df = create_sample_file("patch_mapping")
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return buffer

    @render.download(filename="demand_template.xlsx")
    def download_demand():
        # Provide Excel template for demand (multi-sheet)
        sample = create_sample_file("demand")  # returns dict of DataFrames
        buffer = io.BytesIO()
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
                        label="Remarks (optional)"
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
                    "remarks": remarks
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
