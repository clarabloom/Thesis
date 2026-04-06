import pandas as pd
from pathlib import Path
import shutil

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

LOWNG_DIR  = FUTURES_DIR / "lowng"
HIGHNG_DIR = FUTURES_DIR / "highng"

# ==================================================
# SETTINGS
# ==================================================

MULTIPLIERS = {
    "lowng": 0.7,
    "highng": 1.3
}

PERIODS = ["p1", "p2", "p3"]

# ==================================================
# COLUMN HELPERS
# ==================================================

def get_cols(df):
    ng_cols   = [c for c in df.columns if "naturalgas" in c.lower()]
    coal_cols = [c for c in df.columns if "coal" in c.lower()]
    return ng_cols, coal_cols


# ==================================================
# UPDATE TDR FILE
# ==================================================

def update_tdr(base_path, target_path, multiplier):
    base_df = pd.read_csv(base_path)
    target_df = pd.read_csv(target_path)

    ng_cols, coal_cols = get_cols(base_df)

    print(f"\n  [TDR] {target_path}")

    # --- NATURAL GAS ---
    for col in ng_cols:
        if col in target_df.columns:
            target_df[col] = base_df[col].values * multiplier
        else:
            print(f"    ⚠ Missing NG column: {col}")

    # --- COAL ---
    for col in coal_cols:
        if col in target_df.columns:
            target_df[col] = base_df[col].values
        else:
            print(f"    ⚠ Missing coal column: {col}")

    target_df.to_csv(target_path, index=False)


# ==================================================
# UPDATE SYSTEM FILE (SAFE)
# ==================================================

def update_system(base_path, target_path, multiplier):
    base_df = pd.read_csv(base_path)

    print(f"  [SYSTEM] {target_path}")

    # If system file is missing → copy from base
    if not target_path.exists():
        print("    → Missing system file, copying from base")
        shutil.copy(base_path, target_path)
        target_df = pd.read_csv(target_path)
    else:
        target_df = pd.read_csv(target_path)

    # Check for corruption
    if (
        base_df.shape != target_df.shape or
        set(base_df.columns) != set(target_df.columns) or
        "None" in target_df.columns
    ):
        print("    ⚠ Corrupted system file detected → replacing with base")
        shutil.copy(base_path, target_path)
        target_df = pd.read_csv(target_path)

    ng_cols, coal_cols = get_cols(base_df)

    # --- NATURAL GAS ---
    for col in ng_cols:
        if col in target_df.columns:
            target_df[col] = base_df[col].values * multiplier

    # --- COAL ---
    for col in coal_cols:
        if col in target_df.columns:
            target_df[col] = base_df[col].values

    target_df.to_csv(target_path, index=False)


# ==================================================
# PROCESS FUTURE
# ==================================================

def process_future(future_dir, multiplier):

    if not future_dir.exists():
        print(f"⚠ Missing directory: {future_dir}")
        return

    for case in future_dir.iterdir():
        if not case.is_dir():
            continue

        print(f"\n=== Processing {case.name} ===")

        base_case_name = case.name.replace("lowng_", "").replace("highng_", "")
        base_case = BASE_DIR / f"base_{base_case_name}"

        if not base_case.exists():
            print(f"  ⚠ Missing base case: {base_case}")
            continue

        for p in PERIODS:

            # --- TDR FILE ---
            base_tdr = base_case / f"inputs/inputs_{p}/TDR_results/Fuels_data.csv"
            target_tdr = case / f"inputs/inputs_{p}/TDR_results/Fuels_data.csv"

            if base_tdr.exists() and target_tdr.exists():
                update_tdr(base_tdr, target_tdr, multiplier)
            else:
                print(f"  ⚠ Missing TDR file for {p}")

            # --- SYSTEM FILE ---
            base_sys = base_case / f"inputs/inputs_{p}/system/Fuels_data.csv"
            target_sys = case / f"inputs/inputs_{p}/system/Fuels_data.csv"

            if base_sys.exists():
                update_system(base_sys, target_sys, multiplier)
            else:
                print(f"  ⚠ Missing system base file for {p}")


# ==================================================
# MAIN
# ==================================================

def main():

    print("\n=== FIXING LOW NG FUTURES ===")
    process_future(LOWNG_DIR, MULTIPLIERS["lowng"])

    print("\n=== FIXING HIGH NG FUTURES ===")
    process_future(HIGHNG_DIR, MULTIPLIERS["highng"])

    print("\nDone! All fuels corrected (TDR + system).")


if __name__ == "__main__":
    main()