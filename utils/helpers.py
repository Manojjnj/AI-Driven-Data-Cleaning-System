def format_number(num):
    """
    Format large numbers with commas.
    Example: 10000 -> 10,000
    """
    try:
        return "{:,}".format(num)
    except:
        return num


def get_data_quality_score(df):
    """
    Calculate a simple data quality score (0-100)
    based on missing values and duplicates.
    """
    if df is None or len(df) == 0:
        return 0

    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()

    missing_score = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
    duplicate_score = 1 - (duplicate_rows / len(df)) if len(df) > 0 else 0

    final_score = (missing_score * 0.6 + duplicate_score * 0.4) * 100

    return round(final_score, 2)
import pandas as pd
import numpy as np

def format_number(number):
    """Format large numbers with commas"""
    return f"{number:,}"

def get_data_quality_score(data):
    """Calculate a simple data quality score"""
    if data.empty:
        return 0.0
    
    total_cells = data.shape[0] * data.shape[1]
    missing_cells = data.isnull().sum().sum()
    duplicate_rows = data.duplicated().sum()
    
    # Calculate score
    missing_penalty = (missing_cells / total_cells) * 100
    duplicate_penalty = (duplicate_rows / data.shape[0]) * 10 if data.shape[0] > 0 else 0
    
    quality_score = 100 - missing_penalty - duplicate_penalty
    return max(0, min(100, quality_score))

def detect_file_encoding(file_path):
    """Detect file encoding"""
    try:
        import chardet
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except:
        return 'utf-8'

def safe_convert_numeric(series):
    """Safely convert series to numeric"""
    try:
        return pd.to_numeric(series, errors='coerce')
    except:
        return series

def get_memory_usage(data):
    """Get detailed memory usage information"""
    memory_usage = data.memory_usage(deep=True)
    return {
        'total_mb': memory_usage.sum() / 1024**2,
        'by_column': memory_usage.to_dict()
    }

def suggest_sample_size(data_shape, target_mb=100):
    """Suggest appropriate sample size for large datasets"""
    total_rows, total_cols = data_shape
    estimated_mb = (total_rows * total_cols * 8) / (1024**2)  # Rough estimate
    
    if estimated_mb <= target_mb:
        return total_rows
    else:
        suggested_rows = int((target_mb * 1024**2) / (total_cols * 8))
        return min(suggested_rows, total_rows)
