import pandas as pd
from pathlib import Path
import shutil

# ==================================================
# PATHS
# ==================================================

ROOT = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

# UNDOING OLD SCALING 

SCENARIOS = {
    "highnuclearcost": 1.1,   # +10% to leave +100%
    "lownuclearcost":  0.9  # -10% to leave -25%
}

PERIODS = ["p1", "p2", "p3"]

# ==================================================
# HELPERS
# ==================================================

def update_thermal_file(file_path, multiplier):
    df = pd.read_csv(file_path)

    if "Resource" not in df.columns or "Inv_Cost_per_MWyr" not in df.columns:
        print(f"⚠ Skipping (missing columns): {file_path}")
        return

    mask = df["Resource"].str.lower().str.contains("nuclear", na=False)

    if mask.sum() == 0:
        print(f"⚠ No nuclear rows found: {file_path}")
        return

    # Apply multiplier
    df.loc[mask, "Inv_Cost_per_MWyr"] *= (1 / multiplier)

    df.to_csv(file_path, index=False)

    print(f"✓ Updated nuclear costs in {file_path.name}")

def rename_results(case_dir):
    for folder in case_dir.glob("results*"):

        if not folder.is_dir():
            continue

        new_name = case_dir / "results_old"

        # Avoid overwrite
        i = 1
        while new_name.exists():
            new_name = case_dir / f"results_old_{i}"
            i += 1

        shutil.move(str(folder), str(new_name))
        print(f"✓ Renamed {folder.name} → {new_name.name}")

# ==================================================
# MAIN LOOP
# ==================================================

for scenario, multiplier in SCENARIOS.items():

    scenario_dir = ROOT / scenario

    if not scenario_dir.exists():
        print(f"⚠ Missing scenario: {scenario}")
        continue

    print(f"\n=== Processing {scenario} (×{multiplier}) ===")

    for case in scenario_dir.iterdir():

        if not case.is_dir():
            continue

        print(f"\n--- Case: {case.name} ---")

        # 1. Update Thermal.csv
        for p in PERIODS:

            thermal_file = (
                case
                / "inputs"
                / f"inputs_{p}"
                / "resources"
                / "Thermal.csv"
            )

            if thermal_file.exists():
                update_thermal_file(thermal_file, multiplier)
            else:
                print(f"⚠ Missing file: {thermal_file}")

        # 2. Rename results folders
        rename_results(case)

print("\nDONE: Nuclear cost updates + results cleared.")