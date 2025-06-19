import os
import pandas as pd
import json
import re
from datetime import datetime
from typing import Dict, List, Any

def _extract_lab_metadata(df: pd.DataFrame, file_path: str) -> Dict[str, Any]:
    """
    Extract laboratory-specific metadata from dataframes.
    """
    metadata = {
        "data_type": "unknown",
        "patient_count": 0,
        "date_range": None,
        "lab_parameters": [],
        "units": {},
        "reference_ranges": {}
    }
    
    # Detect data type based on column patterns
    columns_lower = [col.lower() for col in df.columns]
    
    if any('patient' in col or 'subject' in col for col in columns_lower):
        metadata["data_type"] = "patient_data"
        # Count unique patients
        patient_cols = [col for col in df.columns if 'patient' in col.lower() or 'subject' in col.lower()]
        if patient_cols:
            metadata["patient_count"] = df[patient_cols[0]].nunique()
    
    elif any('test' in col or 'assay' in col for col in columns_lower):
        metadata["data_type"] = "lab_results"
        # Extract lab parameters
        test_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['test', 'assay', 'parameter', 'analyte'])]
        metadata["lab_parameters"] = test_cols
    
    # Extract date ranges
    date_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp'])]
    if date_cols:
        try:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            valid_dates = df[date_col].dropna()
            if not valid_dates.empty:
                metadata["date_range"] = {
                    "start": valid_dates.min().strftime('%Y-%m-%d'),
                    "end": valid_dates.max().strftime('%Y-%m-%d')
                }
        except:
            pass
    
    # Extract units and reference ranges from column names or data
    for col in df.columns:
        # Look for units in parentheses or brackets
        unit_match = re.search(r'\(([^)]+)\)|\[([^\]]+)\]', col)
        if unit_match:
            unit = unit_match.group(1) or unit_match.group(2)
            metadata["units"][col] = unit
        
        # Look for reference ranges in column names
        ref_match = re.search(r'ref[:\s]*([^,\s]+)', col, re.IGNORECASE)
        if ref_match:
            metadata["reference_ranges"][col] = ref_match.group(1)
    
    return metadata

def _build_description(metadata):
    """
    Generate a human-readable description for embedding and LLM reasoning.
    Includes column descriptions and sample rows.
    """
    # Format sample rows compactly
    sample_rows = []
    for row in metadata["sample"]:
        row_str = ", ".join(f"{k}: {v}" for k, v in row.items())
        sample_rows.append(f"[{row_str}]")
    sample_text = "; ".join(sample_rows)

    # Enhanced description with lab-specific metadata
    lab_info = ""
    if metadata.get("lab_metadata"):
        lab_meta = metadata["lab_metadata"]
        if lab_meta["data_type"] != "unknown":
            lab_info = f" Data type: {lab_meta['data_type']}"
        if lab_meta["patient_count"] > 0:
            lab_info += f" ({lab_meta['patient_count']} patients)"
        if lab_meta["date_range"]:
            lab_info += f" Date range: {lab_meta['date_range']['start']} to {lab_meta['date_range']['end']}"
        if lab_meta["lab_parameters"]:
            lab_info += f" Lab parameters: {', '.join(lab_meta['lab_parameters'][:3])}"

    return f"{metadata['path']} with columns: {', '.join(metadata['column_descriptions'])}.{lab_info} Sample rows: {sample_text}"

def extract_metadata(file_path):
    ext = os.path.splitext(file_path)[1]
    print("metadata for file: ", file_path)
    try:
        # Load dataframe based on file extension
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif ext == ".json":
            with open(file_path) as f:
                sample = json.load(f)
                df = pd.json_normalize(sample if isinstance(sample, list) else [sample])
        elif ext in [".txt", ".tsv"]:
            # Handle tab-separated and other text formats
            try:
                df = pd.read_csv(file_path, sep='\t')
            except:
                df = pd.read_csv(file_path, sep=None, engine='python')
        else:
            return None

        # Build column descriptions
        column_descriptions = []
        for col in df.columns:
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) <= 6:
                preview = ', '.join([str(v) for v in unique_vals[:6]])
                column_descriptions.append(f"{col} (values: {preview})")
            else:
                # For numeric columns, provide statistics
                if pd.api.types.is_numeric_dtype(df[col]):
                    stats = df[col].describe()
                    column_descriptions.append(f"{col} (numeric, mean: {stats['mean']:.2f}, range: {stats['min']:.2f}-{stats['max']:.2f})")
                else:
                    column_descriptions.append(f"{col} (arbitrary values)")

        # Extract laboratory-specific metadata
        lab_metadata = _extract_lab_metadata(df, file_path)

        metadata = {
            "file": os.path.basename(file_path),
            "path": file_path,
            "columns": list(df.columns),
            "column_descriptions": column_descriptions,
            "sample": df.head(2).to_dict(orient="records"),   # Limit to 2 rows for brevity
            "lab_metadata": lab_metadata,
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size": os.path.getsize(file_path),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }

        # Add rich description
        metadata["description"] = _build_description(metadata)

        return metadata

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def scan_directory(root_dir):
    """
    Scan a directory for supported data files and extract metadata.
    """
    metadata_list = []
    supported_extensions = (".csv", ".xlsx", ".xls", ".json", ".txt", ".tsv")
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(supported_extensions):
                full_path = os.path.join(root, file)
                meta = extract_metadata(full_path)
                if meta:
                    metadata_list.append(meta)
    return metadata_list
