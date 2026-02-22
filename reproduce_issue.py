import pandas as pd
import io
import os

def read_csv_robust(content: bytes) -> pd.DataFrame:
    """
    Attempts to read CSV with multiple encodings and separators.
    """
    encodings = ["utf-8", "cp1252", "latin1", "iso-8859-2"]
    separators = [",", ";", "`t"]
    
    last_error = None
    candidate_df = None
    
    for encoding in encodings:
        for sep in separators:
            try:
                # Try reading
                df = pd.read_csv(io.BytesIO(content), encoding=encoding, sep=sep)
                
                # Heuristic: If we have only 1 column, it might be the wrong separator
                # unless the file genuinely has 1 column.
                # But if we have >1 columns, it is a strong signal we found the right one.
                if len(df.columns) > 1:
                    return df
                
                # If 1 column, keep it as a candidate but keep trying other separators
                candidate_df = df
                
            except Exception as e:
                last_error = e
                continue
    
    # If we found a candidate (even with 1 column), return it
    if candidate_df is not None:
        return candidate_df
        
    raise last_error or Exception("Could not read CSV file")

def test_read_files():
    folder = "test_upload_files"
    if not os.path.exists(folder):
        print(f"Folder {folder} not found")
        return

    files = [f for f in os.listdir(folder) if f.endswith((".csv", ".xlsx", ".xls"))]
    
    for filename in files:
        filepath = os.path.join(folder, filename)
        print(f"\nTesting {filename}...")
        
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            
            if filename.endswith(".csv"):
                try:
                    df = read_csv_robust(content)
                    print(f"  SUCCESS (Robust): Read {len(df)} rows. Columns: {list(df.columns)}")
                except Exception as e:
                    print(f"  FAILED (Robust): {e}")
            else:
                df = pd.read_excel(io.BytesIO(content))
                print(f"  SUCCESS (Excel): Read {len(df)} rows. Columns: {list(df.columns)}")
                
        except Exception as e:
            print(f"  FATAL ERROR: {e}")

if __name__ == "__main__":
    test_read_files()

