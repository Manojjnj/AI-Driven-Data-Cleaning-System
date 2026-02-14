
import pandas as pd
import numpy as np


class DataCleaner:

    def __init__(self):
        pass

    def clean_data(self, data, config):
        """
        Main cleaning function
        """
        cleaned_data = data.copy()
        full_report = {
            "operations": []
        }

        # -------------------------------
        # 1️⃣ Handle Missing Values
        # -------------------------------
        if config.get("handle_missing", False):
            cleaned_data, missing_report = self._handle_missing(cleaned_data)
            full_report["operations"].extend(missing_report["operations"])

        # -------------------------------
        # 2️⃣ Remove Duplicates
        # -------------------------------
        if config.get("remove_duplicates", False):
            before = len(cleaned_data)
            cleaned_data = cleaned_data.drop_duplicates()
            after = len(cleaned_data)

            if before != after:
                full_report["operations"].append(
                    f"Removed {before - after} duplicate rows"
                )

        # -------------------------------
        # 3️⃣ Standardize Text Columns
        # -------------------------------
        if config.get("standardize_text", False):
            case_type = config.get("text_case", "lower")
            cleaned_data, text_report = self._standardize_text(
                cleaned_data,
                case_type=case_type
            )
            full_report["operations"].extend(text_report["operations"])

        return {
    "cleaned_data": cleaned_data,
    "report": full_report
}


    # ==========================================================
    # 🔹 Handle Missing Values
    # ==========================================================
    def _handle_missing(self, data):
        report = {"operations": []}

        for col in data.columns:
            missing_count = data[col].isna().sum()

            if missing_count > 0:

                # Numeric column → fill with median
                if pd.api.types.is_numeric_dtype(data[col]):
                    median_value = data[col].median()
                    data[col].fillna(median_value, inplace=True)

                    report["operations"].append(
                        f"Filled {missing_count} missing values in '{col}' with median"
                    )

                # Categorical column → fill with mode
                else:
                    mode_value = data[col].mode()[0]
                    data[col].fillna(mode_value, inplace=True)

                    report["operations"].append(
                        f"Filled {missing_count} missing values in '{col}' with mode"
                    )

        return data, report

    # ==========================================================
    # 🔹 Advanced Text Standardization
    # ==========================================================
    def _standardize_text(self, data, case_type="lower"):
        """
        case_type: 'lower' or 'title'
        """
        report = {"operations": []}
        categorical_cols = data.select_dtypes(include=["object"]).columns

        for col in categorical_cols:
            original_values = data[col].copy()

            # Convert to string
            data[col] = data[col].astype(str)

            # Remove leading/trailing spaces
            data[col] = data[col].str.strip()

            # Remove multiple spaces
            data[col] = data[col].str.replace(r"\s+", " ", regex=True)

            # Normalize case
            if case_type == "lower":
                data[col] = data[col].str.lower()
            elif case_type == "title":
                data[col] = data[col].str.title()

            # Replace string "nan" back to actual NaN
            data[col] = data[col].replace("nan", np.nan)

            # Count changes
            changes_count = (original_values != data[col]).sum()

            if changes_count > 0:
                report["operations"].append(
                    f"Standardized {changes_count} values in '{col}' (whitespace cleaned + {case_type} case)"
                )

        return data, report
def detect_case_inconsistencies(self, data):
    issues = {}

    categorical_cols = data.select_dtypes(include=["object"]).columns

    for col in categorical_cols:
        unique_values = data[col].dropna().unique()

        lower_map = {}

        for val in unique_values:
            val_str = str(val)
            lower_val = val_str.lower()

            if lower_val not in lower_map:
                lower_map[lower_val] = [val_str]
            else:
                lower_map[lower_val].append(val_str)

        # If multiple versions exist → inconsistency
        for key, variations in lower_map.items():
            if len(variations) > 1:
                issues[col] = variations

    return issues


