import pandas as pd
import os

file_path = r"C:\Users\Slavko\SanctionDefenderV2\sanction list comparison.xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    # Try to find it in the current directory just in case
    file_path = "sanction list comparison.xlsx"
    if not os.path.exists(file_path):
        print(f"File not found in current dir either.")
        exit(1)

print(f"Reading {file_path}...")
try:
    df = pd.read_excel(file_path, header=None)
    
    # Row 27 (index 26) seems to be the header for the second block
    header_row_idx = 26
    print(f"\nHeaders at Row {header_row_idx+1} (Index {header_row_idx}):")
    headers = df.iloc[header_row_idx]
    for i, val in enumerate(headers):
        if pd.notna(val):
            print(f"Col {i}: {val}")

    # Check UK mapping at index 31
    print(f"\nUK Mapping at Row 32 (Index 31):")
    uk_map = df.iloc[31]
    for i in [2, 3, 9]:
        val = uk_map[i]
        if pd.notna(val):
            print(f"Col {i}: {val}")

    # Check US mapping at index 36
    print(f"\nUS Mapping at Row 37 (Index 36):")
    us_map = df.iloc[36]
    for i in [2, 3, 9]:
        val = us_map[i]
        if pd.notna(val):
            print(f"Col {i}: {val}")





    # Print a slice of the dataframe to see the structure better
    print("\nData Slice (Rows 2-15, Cols 0-15):")
    # print(df.iloc[2:15, 0:15].to_string())

except Exception as e:
    print(f"Error reading excel: {e}")
