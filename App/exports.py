from pathlib import Path
import pandas as pd
from typing import Callable


def export_demand_volume(df: pd.DataFrame, export_file: Path, file_id: str):
    try:
        df.to_csv(export_file, index=False)
        return True
    except Exception:
        return False


def export_demand_mix(df: pd.DataFrame, export_file: Path, file_id: str):
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


def export_validated_file(df, export_path, file_id, export_func: Callable | str = None):
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
