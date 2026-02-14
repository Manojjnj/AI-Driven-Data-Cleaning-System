class AISuggestionEngine:
    def __init__(self):
        pass

    def generate_suggestions(self, data, profiling_results):
        suggestions = []

        # Missing values suggestion
        if profiling_results["missing_values"]["total_missing"] > 0:
            suggestions.append({
                "title": "Handle Missing Values",
                "priority": "High",
                "description": "Dataset contains missing values.",
                "recommendation": "Consider imputing or dropping missing values.",
                "type": "missing_values",
                "affected_columns": list(profiling_results["missing_values"]["by_column"].keys())
            })

        # Duplicate rows suggestion
        if profiling_results["duplicates"]["count"] > 0:
            suggestions.append({
                "title": "Remove Duplicate Rows",
                "priority": "Medium",
                "description": "Dataset contains duplicate rows.",
                "recommendation": "Consider removing duplicate records.",
                "type": "duplicates",
                "count": profiling_results["duplicates"]["count"]
            })

        return suggestions
import pandas as pd
import numpy as np

class AISuggestionEngine:
    """AI-powered suggestion engine for data cleaning"""
    
    def __init__(self):
        self.suggestion_rules = {
            'missing_threshold_low': 0.10,
            'missing_threshold_high': 0.40,
            'outlier_threshold': 0.05,
            'duplicate_threshold': 0.01
        }
    
    def generate_suggestions(self, data, profiling_results):
        """Generate AI-powered cleaning suggestions"""
        suggestions = []
        
        # Missing values suggestions
        suggestions.extend(self._suggest_missing_values_handling(data, profiling_results))
        
        # Duplicate suggestions
        suggestions.extend(self._suggest_duplicate_handling(data, profiling_results))
        
        # Outlier suggestions
        suggestions.extend(self._suggest_outlier_handling(data, profiling_results))
        
        # Data type suggestions
        suggestions.extend(self._suggest_data_type_optimization(data, profiling_results))
        
        # Categorical cleaning suggestions
        suggestions.extend(self._suggest_categorical_cleaning(data, profiling_results))
        
        # Sort suggestions by priority
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        suggestions.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return suggestions
    
    def _suggest_missing_values_handling(self, data, profiling_results):
        """Suggest handling for missing values"""
        suggestions = []
        missing_info = profiling_results['missing_values']
        
        if missing_info['total_missing'] == 0:
            return suggestions
        
        # Analyze each column with missing values
        high_missing_cols = []
        low_missing_cols = []
        medium_missing_cols = []
        
        for col, info in missing_info['by_column'].items():
            percentage = info['percentage'] / 100
            
            if percentage > self.suggestion_rules['missing_threshold_high']:
                high_missing_cols.append(col)
            elif percentage < self.suggestion_rules['missing_threshold_low']:
                low_missing_cols.append(col)
            else:
                medium_missing_cols.append(col)
        
        # High missing values - suggest removal
        if high_missing_cols:
            suggestions.append({
                'type': 'missing_values',
                'priority': 'High',
                'title': f'Remove columns with >40% missing values',
                'description': f'Columns {high_missing_cols} have more than 40% missing values',
                'recommendation': 'Consider removing these columns as imputation may not be reliable',
                'affected_columns': high_missing_cols,
                'action': 'remove_columns'
            })
        
        # Low missing values - suggest imputation
        if low_missing_cols:
            numeric_cols = [col for col in low_missing_cols 
                          if data[col].dtype in ['int64', 'float64']]
            categorical_cols = [col for col in low_missing_cols 
                              if col not in numeric_cols]
            
            if numeric_cols:
                suggestions.append({
                    'type': 'missing_values',
                    'priority': 'Medium',
                    'title': f'Impute missing values in numeric columns',
                    'description': f'Numeric columns {numeric_cols} have <10% missing values',
                    'recommendation': 'Use mean/median imputation or KNN imputation',
                    'affected_columns': numeric_cols,
                    'action': 'impute_numeric'
                })
            
            if categorical_cols:
                suggestions.append({
                    'type': 'missing_values',
                    'priority': 'Medium',
                    'title': f'Impute missing values in categorical columns',
                    'description': f'Categorical columns {categorical_cols} have <10% missing values',
                    'recommendation': 'Use mode imputation or create "Unknown" category',
                    'affected_columns': categorical_cols,
                    'action': 'impute_categorical'
                })
        
        # Medium missing values - suggest careful consideration
        if medium_missing_cols:
            suggestions.append({
                'type': 'missing_values',
                'priority': 'Medium',
                'title': f'Carefully handle moderate missing values',
                'description': f'Columns {medium_missing_cols} have 10-40% missing values',
                'recommendation': 'Consider advanced imputation techniques or domain knowledge',
                'affected_columns': medium_missing_cols,
                'action': 'careful_imputation'
            })
        
        return suggestions
    
    def _suggest_duplicate_handling(self, data, profiling_results):
        """Suggest handling for duplicate rows"""
        suggestions = []
        duplicate_info = profiling_results['duplicates']
        
        if duplicate_info['count'] > 0:
            percentage = duplicate_info['percentage']
            priority = 'High' if percentage > 5 else 'Medium' if percentage > 1 else 'Low'
            
            suggestions.append({
                'type': 'duplicates',
                'priority': priority,
                'title': f'Remove duplicate rows',
                'description': f'Found {duplicate_info["count"]} duplicate rows ({percentage:.2f}%)',
                'recommendation': 'Remove duplicate rows to avoid bias in analysis',
                'count': duplicate_info['count'],
                'action': 'remove_duplicates'
            })
        
        return suggestions
    
    def _suggest_outlier_handling(self, data, profiling_results):
        """Suggest handling for outliers"""
        suggestions = []
        outliers_info = profiling_results['outliers']
        
        if not outliers_info:
            return suggestions
        
        high_outlier_cols = []
        moderate_outlier_cols = []
        
        for col, info in outliers_info.items():
            percentage = info['percentage'] / 100
            
            if percentage > self.suggestion_rules['outlier_threshold']:
                high_outlier_cols.append(col)
            else:
                moderate_outlier_cols.append(col)
        
        if high_outlier_cols:
            suggestions.append({
                'type': 'outliers',
                'priority': 'Medium',
                'title': f'Handle outliers in columns with high outlier percentage',
                'description': f'Columns {high_outlier_cols} have >5% outliers',
                'recommendation': 'Consider capping, transformation, or removal based on domain knowledge',
                'affected_columns': high_outlier_cols,
                'action': 'handle_outliers'
            })
        
        if moderate_outlier_cols:
            suggestions.append({
                'type': 'outliers',
                'priority': 'Low',
                'title': f'Review outliers in columns',
                'description': f'Columns {moderate_outlier_cols} have moderate outliers',
                'recommendation': 'Review outliers manually - they might be valid extreme values',
                'affected_columns': moderate_outlier_cols,
                'action': 'review_outliers'
            })
        
        return suggestions
    
    def _suggest_data_type_optimization(self, data, profiling_results):
        """Suggest data type optimizations"""
        suggestions = []
        type_info = profiling_results['data_types']
        
        optimizable_cols = []
        for col, info in type_info.items():
            if info['suggestions']:
                optimizable_cols.append(col)
        
        if optimizable_cols:
            suggestions.append({
                'type': 'data_types',
                'priority': 'Low',
                'title': f'Optimize data types for memory efficiency',
                'description': f'Columns {optimizable_cols} can be optimized',
                'recommendation': 'Convert to more efficient data types to reduce memory usage',
                'affected_columns': optimizable_cols,
                'action': 'optimize_types'
            })
        
        return suggestions
    
    def _suggest_categorical_cleaning(self, data, profiling_results):
        """Suggest categorical data cleaning"""
        suggestions = []
        categorical_issues = profiling_results['categorical_issues']
        
        if not categorical_issues:
            return suggestions
        
        case_issue_cols = []
        whitespace_issue_cols = []
        
        for col, issues in categorical_issues.items():
            if issues['case_issues']:
                case_issue_cols.append(col)
            if issues['whitespace_issues']:
                whitespace_issue_cols.append(col)
        
        if case_issue_cols:
            suggestions.append({
                'type': 'categorical_cleaning',
                'priority': 'Medium',
                'title': f'Standardize text case in categorical columns',
                'description': f'Columns {case_issue_cols} have case inconsistencies',
                'recommendation': 'Standardize text case (e.g., lowercase) for consistency',
                'affected_columns': case_issue_cols,
                'action': 'standardize_case'
            })
        
        if whitespace_issue_cols:
            suggestions.append({
                'type': 'categorical_cleaning',
                'priority': 'Low',
                'title': f'Remove whitespace from categorical columns',
                'description': f'Columns {whitespace_issue_cols} have whitespace issues',
                'recommendation': 'Strip leading/trailing whitespace',
                'affected_columns': whitespace_issue_cols,
                'action': 'strip_whitespace'
            })
        
        return suggestions
