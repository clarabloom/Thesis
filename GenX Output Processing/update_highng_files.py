#!/usr/bin/env python3

import shutil
import pandas as pd
from pathlib import Path

# ==========================================================
# USER SETTINGS
# ==========================================================

SCENARIO_ROOT = Path(
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng"
)

# IMPORTANT: point directly to the files you manually verified
SOURCE_FILES = {
    "inputs_p1": Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/Fuels_highng_p1.csv"),
    "inputs_p2": Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/Fuels_highng_p2.csv"),
    "inputs_p3": Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/Fuels_highng_p3.csv"),
}

CASE_PREFIX = "base_"
TARGET_FILENAME = "Fuels_data.csv"

# ==========================================================
# MAIN
# ==========================================================

updated_count = 0

for case_dir in SCENARIO_ROOT.iterdir():

    if not case_dir.is_dir():
        continue

    if not case_dir.name.startswith(CASE_PREFIX):
        continue

    print(f"\nProcessing case: {case_dir.name}")

    for period, src_file in SOURCE_FILES.items():

        if not src_file.exists():
            raise FileNotFoundError(f"Source file missing:\n{src_file}")

        for subfolder in ["TDR_results", "system"]:

            target_path = (
                case_dir
                / "inputs"
                / period
                / subfolder
                / TARGET_FILENAME
            )

            if not target_path.exists():
                print(f"   ⚠ Missing: {target_path}")
                continue

            print(f"   Updating:")
            print(f"      FROM: {src_file}")
            print(f"      TO  : {target_path}")

            # Read old and new for verification
            old_df = pd.read_csv(target_path)
            new_df = pd.read_csv(src_file)

            # Compare one fuel row as a sanity check
            if "NaturalGas" in old_df.iloc[:,0].astype(str).values:
                old_val = old_df.loc[
                    old_df.iloc[:,0].astype(str).str.contains("NaturalGas"),
                    old_df.columns[1]
                ].values[0]
            else:
                old_val = old_df.iloc[0,1]

            shutil.copy2(src_file, target_path)

            check_df = pd.read_csv(target_path)

            if check_df.equals(old_df):
                print("      ⚠ File did not change after copy.")
            else:
                print("      ✓ File successfully updated.")
                updated_count += 1

print("\n--------------------------------------------------")

if updated_count == 0:
    raise RuntimeError("No files were updated. Check paths carefully.")

print(f"SUCCESS: {updated_count} files updated.")