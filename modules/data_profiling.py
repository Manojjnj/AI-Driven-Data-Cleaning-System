class DataProfiler:
    def __init__(self):
        pass

    def generate_profile(self, data):
        return {
            "missing_values": {
                "total_missing": data.isnull().sum().sum(),
                "by_column": {
                    col: [
                        int(data[col].isnull().sum()),
                        float(data[col].isnull().mean() * 100)
                    ]
                    for col in data.columns
                }
            },
            "duplicates": {
                "count": int(data.duplicated().sum()),
                "percentage": float(data.duplicated().mean() * 100)
            },
            "outliers": {},
            "categorical_issues": {}
        }
import pandas as pd
import numpy as np
from scipy import stats
from collections import Counter
import re

class DataProfiler:
    """Comprehensive data profiling and analysis"""
    
    def __init__(self):
        self.numeric_threshold = 0.8  # Threshold for considering a column numeric
    
    def generate_profile(self, data):
        """Generate comprehensive data profile"""
        profile = {
            'basic_info': self._get_basic_info(data),
            'missing_values': self._analyze_missing_values(data),
            'duplicates': self._analyze_duplicates(data),
            'data_types': self._analyze_data_types(data),
            'outliers': self._detect_outliers(data),
            'categorical_issues': self._detect_categorical_issues(data),
            'correlation_issues': self._detect_correlation_issues(data)
        }
        return profile
    
    def _get_basic_info(self, data):
        """Get basic dataset information"""
        return {
            'shape': data.shape,
            'memory_usage': data.memory_usage(deep=True).sum(),
            'column_count': len(data.columns),
            'row_count': len(data)
        }
    
    def _analyze_missing_values(self, data):
        """Analyze missing values patterns"""
        missing_count = data.isnull().sum()
        missing_percentage = (missing_count / len(data)) * 100
        
        by_column = {}
        for col in data.columns:
            if missing_count[col] > 0:
                by_column[col] = {
                    'count': int(missing_count[col]),
                    'percentage': float(missing_percentage[col])
                }
        
        return {
            'total_missing': int(missing_count.sum()),
            'columns_with_missing': int((missing_count > 0).sum()),
            'by_column': by_column,
            'missing_patterns': self._find_missing_patterns(data)
        }
    
    def _find_missing_patterns(self, data):
        """Find patterns in missing data"""
        patterns = {}
        
        # Find columns that are missing together
        missing_matrix = data.isnull()
        for col1 in data.columns:
            for col2 in data.columns:
                if col1 != col2:
                    correlation = missing_matrix[col1].corr(missing_matrix[col2])
                    if correlation > 0.5:  # High correlation in missingness
                        if col1 not in patterns:
                            patterns[col1] = []
                        patterns[col1].append(col2)
        
        return patterns
    
    def _analyze_duplicates(self, data):
        """Analyze duplicate rows"""
        duplicate_count = data.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(data)) * 100
        
        return {
            'count': int(duplicate_count),
            'percentage': float(duplicate_percentage),
            'duplicate_indices': data[data.duplicated()].index.tolist()
        }
    
    def _analyze_data_types(self, data):
        """Analyze data types and suggest optimizations"""
        type_analysis = {}
        
        for col in data.columns:
            col_type = str(data[col].dtype)
            unique_count = data[col].nunique()
            
            suggestions = []
            
            # Integer optimization
            if col_type.startswith('int') or col_type.startswith('float'):
                min_val = data[col].min()
                max_val = data[col].max()
                
                if col_type.startswith('int64') and min_val >= -128 and max_val <= 127:
                    suggestions.append('int8')
                elif col_type.startswith('int64') and min_val >= -32768 and max_val <= 32767:
                    suggestions.append('int16')
                elif col_type.startswith('float64') and data[col].apply(float.is_integer).all():
                    suggestions.append('int32')
            
            # Categorical optimization
            if col_type == 'object' and unique_count < len(data) * 0.5:
                suggestions.append('category')
            
            type_analysis[col] = {
                'current_type': col_type,
                'unique_values': int(unique_count),
                'suggestions': suggestions
            }
        
        return type_analysis
    
    def _detect_outliers(self, data):
        """Detect outliers using IQR method"""
        outliers = {}
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if data[col].notna().sum() > 0:  # Skip if all NaN
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (data[col] < lower_bound) | (data[col] > upper_bound)
                outlier_count = outlier_mask.sum()
                
                if outlier_count > 0:
                    outliers[col] = {
                        'count': int(outlier_count),
                        'percentage': float((outlier_count / len(data)) * 100),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'outlier_indices': data[outlier_mask].index.tolist()
                    }
        
        return outliers
    
    def _detect_categorical_issues(self, data):
        """Detect issues in categorical columns"""
        issues = {}
        categorical_cols = data.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            col_issues = {
                'unique_values': int(data[col].nunique()),
                'case_issues': [],
                'whitespace_issues': [],
                'encoding_issues': []
            }
            
            # Check for case inconsistencies
            if data[col].dtype == 'object':
                values = data[col].dropna().astype(str)
                lower_values = values.str.lower()
                
                # Find potential case issues
                value_counts = lower_values.value_counts()
                for lower_val in value_counts.index:
                    original_variations = values[lower_values == lower_val].unique()
                    if len(original_variations) > 1:
                        col_issues['case_issues'].extend(original_variations.tolist())
            
            # Check for whitespace issues
            if data[col].dtype == 'object':
                has_leading_space = data[col].astype(str).str.startswith(' ').any()
                has_trailing_space = data[col].astype(str).str.endswith(' ').any()
                
                if has_leading_space or has_trailing_space:
                    col_issues['whitespace_issues'].append('whitespace_found')
            
            if any(col_issues.values()):
                issues[col] = col_issues
        
        return issues
    
    def _detect_correlation_issues(self, data):
        """Detect highly correlated features"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.shape[1] < 2:
            return {}
        
        correlation_matrix = numeric_data.corr().abs()
        
        # Find pairs with correlation > 0.9
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                if correlation_matrix.iloc[i, j] > 0.9:
                    high_corr_pairs.append({
                        'feature1': correlation_matrix.columns[i],
                        'feature2': correlation_matrix.columns[j],
                        'correlation': float(correlation_matrix.iloc[i, j])
                    })
        
        return {'high_correlation_pairs': high_corr_pairs}
