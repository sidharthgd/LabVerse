import os
import pandas as pd
import json

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

    return f"{metadata['path']} with columns: {', '.join(metadata['column_descriptions'])}. Sample rows: {sample_text}"

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
                column_descriptions.append(f"{col} (arbitrary values)")

        metadata = {
            "file": os.path.basename(file_path),
            "path": file_path,
            "columns": list(df.columns),
            "column_descriptions": column_descriptions,
            "sample": df.head(2).to_dict(orient="records"),   # Limit to 2 rows for brevity
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
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".csv", ".xlsx", ".xls", ".json")):
                full_path = os.path.join(root, file)
                meta = extract_metadata(full_path)
                if meta:
                    metadata_list.append(meta)
    return metadata_list
