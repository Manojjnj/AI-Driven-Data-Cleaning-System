import pandas as pd
import numpy as np
from datetime import datetime


class ReportGenerator:
    """Generate comprehensive cleaning reports"""

    def __init__(self):
        pass

    def generate_report(self, original_data, cleaned_data, cleaning_report):
        """Generate comprehensive cleaning report"""

        # Safe extraction (prevents KeyError)
        missing_values_handled = cleaning_report.get("missing_values_handled", 0)
        duplicates_removed = cleaning_report.get("duplicates_removed", 0)
        outliers_handled = cleaning_report.get("outliers_handled", 0)
        operations_performed = cleaning_report.get(
            "operations_performed",
            cleaning_report.get("operations", [])
        )

        # Quality score
        original_quality = self._calculate_quality_score(original_data)
        final_quality = self._calculate_quality_score(cleaned_data)
        quality_improvement = final_quality - original_quality

        # Memory usage
        original_memory = original_data.memory_usage(deep=True).sum() / 1024**2
        final_memory = cleaned_data.memory_usage(deep=True).sum() / 1024**2

        memory_reduction = 0
        if original_memory > 0:
            memory_reduction = ((original_memory - final_memory) / original_memory) * 100

        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_shape": original_data.shape,
            "final_shape": cleaned_data.shape,
            "rows_removed": original_data.shape[0] - cleaned_data.shape[0],
            "columns_removed": original_data.shape[1] - cleaned_data.shape[1],
            "missing_values_handled": missing_values_handled,
            "duplicates_removed": duplicates_removed,
            "outliers_handled": outliers_handled,
            "operations_performed": operations_performed,
            "quality_improvement": {
                "original_score": original_quality,
                "final_score": final_quality,
                "improvement": quality_improvement,
            },
            "memory_reduction": {
                "original_mb": original_memory,
                "final_mb": final_memory,
                "reduction_percent": memory_reduction,
            },
        }

        return report

    def _calculate_quality_score(self, data):
        """Simple quality score"""
        if data.empty:
            return 0.0

        total_cells = data.shape[0] * data.shape[1]
        missing_cells = data.isnull().sum().sum()
        duplicate_rows = data.duplicated().sum()

        missing_penalty = (missing_cells / total_cells) * 100
        duplicate_penalty = (duplicate_rows / data.shape[0]) * 10 if data.shape[0] > 0 else 0

        quality_score = 100 - missing_penalty - duplicate_penalty
        return max(0, min(100, quality_score))
