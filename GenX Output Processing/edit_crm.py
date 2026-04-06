import pandas as pd
from pathlib import Path

# ==================================================
# USER PATHS
# ==================================================

BASE_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base"
)

FUTURES_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios"
)

# ==================================================
# FUNCTION TO MODIFY FILE
# ==================================================

def update_crm_file(file_path):

    df = pd.read_csv(file_path)

    # Modify numeric columns only
    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        df[col] = df[col].apply(lambda x: 0.0001 if x != 0 else 0)

    df.to_csv(file_path, index=False)

    print(f"✓ Updated {file_path}")


# ==================================================
# SEARCH BASE CASES
# ==================================================

print("\nProcessing BASE cases\n")

for case_dir in BASE_DIR.iterdir():

    if not case_dir.is_dir():
        continue

    for policy_file in case_dir.glob("inputs/inputs_p*/policies/Capacity_reserve_margin.csv"):
        update_crm_file(policy_file)


# ==================================================
# SEARCH FUTURES CASES
# ==================================================

print("\nProcessing FUTURES cases\n")

for scenario_dir in FUTURES_DIR.iterdir():

    if not scenario_dir.is_dir():
        continue

    for case_dir in scenario_dir.iterdir():

        if not case_dir.is_dir():
            continue

        for policy_file in case_dir.glob("inputs/inputs_p*/policies/Capacity_reserve_margin.csv"):
            update_crm_file(policy_file)


print("\nAll CRM files updated successfully.")