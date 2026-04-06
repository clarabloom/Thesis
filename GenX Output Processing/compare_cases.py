import os
import pandas as pd
import filecmp
import difflib

BASE_CASE = "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccstech/inputs"
POLICY_CASE = "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesccstech/inputs"

# ---------------------------------------------------
# Helper: get all files under a directory
# ---------------------------------------------------
def get_all_files(root):
    files = {}
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            rel_path = os.path.relpath(full_path, root)
            files[rel_path] = full_path
    return files


# ---------------------------------------------------
# Helper: compare CSVs
# ---------------------------------------------------
def compare_csv(file1, file2, rel_path):
    try:
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
    except Exception as e:
        print(f"⚠️ Could not read CSV {rel_path}: {e}")
        return

    if df1.shape != df2.shape:
        print(f"❗ CSV shape differs in {rel_path}: {df1.shape} vs {df2.shape}")

    # Column comparison
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)

    if cols1 != cols2:
        print(f"❗ Column mismatch in {rel_path}")
        print("  Only in base:", cols1 - cols2)
        print("  Only in policy:", cols2 - cols1)

    # Numeric differences
    common_cols = cols1 & cols2
    common_cols = cols1 & cols2

    for col in common_cols:
        s1_full = df1[col].reset_index(drop=True)
        s2_full = df2[col].reset_index(drop=True)
    
        min_len = min(len(s1_full), len(s2_full))
        s1 = s1_full.iloc[:min_len]
        s2 = s2_full.iloc[:min_len]
    
        # Boolean columns
        if pd.api.types.is_bool_dtype(s1):
            mismatches = (s1 != s2).sum()
            if mismatches > 0:
                print(f"** {rel_path} | column '{col}': {mismatches} boolean mismatches")
    
        # Numeric columns
        elif pd.api.types.is_numeric_dtype(s1):
            diff = (s1.astype(float) - s2.astype(float)).abs()
            if diff.max() > 0:
                print(f"** {rel_path} | column '{col}': max abs diff = {diff.max():.4g}")
    
        # Strings / others
        else:
            mismatches = (s1 != s2).sum()
            if mismatches > 0:
                print(f"** {rel_path} | column '{col}': {mismatches} differing entries")


# ---------------------------------------------------
# Helper: compare text files
# ---------------------------------------------------
def compare_text(file1, file2, rel_path):
    with open(file1) as f1, open(file2) as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    if lines1 != lines2:
        print(f"❗ Text file differs: {rel_path}")
        diff = difflib.unified_diff(
            lines1, lines2,
            fromfile="base",
            tofile="policy",
            lineterm=""
        )
        for line in list(diff)[:10]:  # limit output
            print(line)
        print("  ... (diff truncated)")


# ---------------------------------------------------
# Main comparison
# ---------------------------------------------------
base_files = get_all_files(BASE_CASE)
policy_files = get_all_files(POLICY_CASE)

all_files = set(base_files.keys()) | set(policy_files.keys())

print("\n===== FILE EXISTENCE CHECK =====\n")

for f in sorted(all_files):
    if f not in base_files:
        print(f"➕ Only in policy case: {f}")
    elif f not in policy_files:
        print(f"➖ Only in base case: {f}")

print("\n===== CONTENT COMPARISON =====\n")

for rel_path in sorted(base_files.keys() & policy_files.keys()):
    f1 = base_files[rel_path]
    f2 = policy_files[rel_path]

    if filecmp.cmp(f1, f2, shallow=False):
        continue  # identical

    if rel_path.endswith(".csv"):
        print(f"\n CSV differs: {rel_path}")
        compare_csv(f1, f2, rel_path)

    elif rel_path.endswith((".yml", ".yaml")):
        print(f"\n YAML differs: {rel_path}")
        compare_text(f1, f2, rel_path)

    else:
        print(f"\n File differs: {rel_path}")
        compare_text(f1, f2, rel_path)