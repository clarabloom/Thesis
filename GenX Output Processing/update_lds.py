#!/usr/bin/env python3

import pandas as pd
from pathlib import Path

# ==================================================
# PATHS
# ==================================================

FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lds")

# ==================================================
# CONFIG
# ==================================================

LDS_NAME = "LDS"
FOM_PERCENT = 0.025  # 2.5% of CAPEX

# ==================================================
# FIX FUNCTION
# ==================================================

def fix_lds_costs(storage_path):
    df = pd.read_csv(storage_path)

    lds_mask = df["Resource"].str.contains(LDS_NAME, case=False, na=False)

    if not lds_mask.any():
        print(f"  ⚠ No LDS in {storage_path.name}")
        return

    print(f"  Fixing {storage_path.name}")

    # Ensure numeric
    for col in ["capex_mw", "Inv_Cost_per_MWyr"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for idx in df[lds_mask].index:

        capex = df.at[idx, "capex_mw"]

        # ----------------------------
        # FIXED O&M (advisor suggestion)
        # ----------------------------

        if "Fixed_OM_Cost_per_MWyr" in df.columns:
            df.at[idx, "Fixed_OM_Cost_per_MWyr"] = round(capex * FOM_PERCENT, 2)

        if "Fixed_OM_Cost_per_MWhyr" in df.columns:
            df.at[idx, "Fixed_OM_Cost_per_MWhyr"] = 0

        # ----------------------------
        # INVESTMENT COST CLEANUP
        # ----------------------------

        # Remove any energy-side investment cost
        if "Inv_Cost_per_MWhyr" in df.columns:
            df.at[idx, "Inv_Cost_per_MWhyr"] = 0

        # DO NOT modify Inv_Cost_per_MWyr here
        # (assumes it's already correct capital recovery)

    df.to_csv(storage_path, index=False)


# ==================================================
# APPLY TO ALL CASES
# ==================================================

def apply_fix():

    for case in sorted(FUTURES_DIR.iterdir()):
        if not case.is_dir():
            continue

        print(f"\nUpdating {case.name}")

        for period in ["p1", "p2", "p3"]:
            storage = case / f"inputs/inputs_{period}/resources/Storage.csv"

            if storage.exists():
                fix_lds_costs(storage)
            else:
                print(f"  ⚠ Missing: {storage}")


# ==================================================
# MAIN
# ==================================================

def main():
    print("=== Fixing LDS cost structure (FULL) ===")
    apply_fix()
    print("\nDone!")

if __name__ == "__main__":
    main()