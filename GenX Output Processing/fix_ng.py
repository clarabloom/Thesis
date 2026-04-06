import pandas as pd
from pathlib import Path

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

# ==================================================
# CORE FUNCTION
# ==================================================

def update_fuels(base_path, target_path, multiplier):
    base_df = pd.read_csv(base_path)
    target_df = pd.read_csv(target_path)

    # Identify natural gas columns
    ng_cols = [c for c in base_df.columns if "naturalgas" in c.lower()]

    if not ng_cols:
        print(f"⚠ No natural gas columns found in {base_path}")
        return

    # Apply scaling from BASE (not from target!)
    for col in ng_cols:
        if col in target_df.columns:
            target_df[col] = base_df[col] * multiplier
        else:
            print(f"  ⚠ Missing column {col} in target")

    target_df.to_csv(target_path, index=False)


# ==================================================
# APPLY TO ALL CASES
# ==================================================

def process_future(future_dir, multiplier):

    if not future_dir.exists():
        print(f"⚠ Missing directory: {future_dir}")
        return

    for case in future_dir.iterdir():
        if not case.is_dir():
            continue

        print(f"\nUpdating {case.name}")

        # Find corresponding base case
        base_case_name = case.name.replace("lowng_", "").replace("highng_", "")
        base_case = BASE_DIR / f"base_{base_case_name}"

        if not base_case.exists():
            print(f"  ⚠ Missing base case: {base_case}")
            continue

        for period in ["p1", "p2", "p3"]:
            base_fuels = base_case / f"inputs/inputs_{period}/TDR_results/Fuels_data.csv"
            target_fuels = case / f"inputs/inputs_{period}/TDR_results/Fuels_data.csv"

            if not base_fuels.exists():
                print(f"  ⚠ Missing base file: {base_fuels}")
                continue

            if not target_fuels.exists():
                print(f"  ⚠ Missing target file: {target_fuels}")
                continue

            update_fuels(base_fuels, target_fuels, multiplier)

            print(f"  ✓ Updated {period}")


# ==================================================
# MAIN
# ==================================================

def main():
    print("=== Fixing LOW NG futures ===")
    process_future(LOWNG_DIR, MULTIPLIERS["lowng"])

    print("\n=== Fixing HIGH NG futures ===")
    process_future(HIGHNG_DIR, MULTIPLIERS["highng"])

    print("\nDone!")

if __name__ == "__main__":
    main()