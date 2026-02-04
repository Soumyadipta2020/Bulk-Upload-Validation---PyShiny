import pandas as pd


def create_sample_file(file_type):
    if file_type == "attrition":
        return pd.DataFrame(
            {
                "week": ["2025-01-06", "2025-01-13", "2025-01-20"],
                "job_type": ["A", "B", "C"],
                "attrition_count": [5.2, 2.1, 4.8],
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
        return pd.DataFrame({"wmis": ["A", "B", "C"], "region": ["North", "South", "East"]})
    elif file_type == "demand":
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
