import pandas as pd
from pathlib import Path

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base"
)

FUTURES_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios"
)

# Cases we want to modify
TARGET_CASE_STRINGS = [
    "cesincccstech",
    "cesincccstechinstate"
]

# Value to set
NEW_VALUE = -0.476


# ==================================================
# FUNCTION TO MODIFY FILE
# ==================================================

def update_incremental_constraint(file_path):

    df = pd.read_csv(file_path)

    # Identify zone column automatically
    zone_col = None
    for col in df.columns:
        if "zone" in col.lower():
            zone_col = col
            break

    if zone_col is None:
        print(f"⚠ Could not find zone column in {file_path}")
        return

    # Modify value
    mask = df[zone_col].astype(str) == "z10"

    if "CapRes_8" not in df.columns:
        print(f"⚠ CapRes_8 not found in {file_path}")
        return

    df.loc[mask, "CapRes_8"] = NEW_VALUE

    df.to_csv(file_path, index=False)

    print(f"✓ Updated {file_path}")


# ==================================================
# PROCESS BASE CASES
# ==================================================

print("\nProcessing BASE cases\n")

for case_dir in BASE_DIR.iterdir():

    if not case_dir.is_dir():
        continue

    case_name = case_dir.name

    if not any(key in case_name for key in TARGET_CASE_STRINGS):
        continue

    policy_file = case_dir / "inputs" / "inputs_p3" / "policies" / "Capacity_reserve_margin.csv"

    if policy_file.exists():
        update_incremental_constraint(policy_file)


# ==================================================
# PROCESS FUTURES CASES
# ==================================================

print("\nProcessing FUTURES cases\n")

for scenario_dir in FUTURES_DIR.iterdir():

    if not scenario_dir.is_dir():
        continue

    for case_dir in scenario_dir.iterdir():

        if not case_dir.is_dir():
            continue

        case_name = case_dir.name

        if not any(key in case_name for key in TARGET_CASE_STRINGS):
            continue

        policy_file = case_dir / "inputs" / "inputs_p3" / "policies" / "Capacity_reserve_margin.csv"

        if policy_file.exists():
            update_incremental_constraint(policy_file)

print("\nAll incremental CCS constraints updated.")