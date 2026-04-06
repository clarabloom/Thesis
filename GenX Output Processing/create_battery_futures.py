import shutil
import pandas as pd
from pathlib import Path

# ==================================================
# PATHS (match your reference)
# ==================================================

BASE_DIR    = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

# ==================================================
# CONFIG
# ==================================================

COST_MULTIPLIERS = {
    "batterieslow":  0.7,
    "batterieshigh": 1.3,
}

# ==================================================
# STEP 1: COPY AND RENAME CASES (IDENTICAL LOGIC)
# ==================================================

def create_future_cases():
    for future_name in COST_MULTIPLIERS:
        future_dir = FUTURES_DIR / future_name
        future_dir.mkdir(exist_ok=True)

        for base_case in BASE_DIR.iterdir():
            if not base_case.is_dir():
                continue

            old_name = base_case.name

            if old_name.startswith("base_"):
                new_name = future_name + "_" + old_name[len("base_"):]
            else:
                new_name = old_name

            new_case_path = future_dir / new_name

            if not new_case_path.exists():
                shutil.copytree(base_case, new_case_path)
                print(f"Copied {old_name} → {new_name}")

# ==================================================
# STEP 2: MODIFY STORAGE COSTS
# ==================================================

def update_storage_costs(storage_path, multiplier):
    df = pd.read_csv(storage_path)

    if "Inv_Cost_per_MWyr" not in df.columns:
        print(f"⚠ Missing column in {storage_path}")
        return

    # Apply multiplier to ALL storage rows
    df["Inv_Cost_per_MWyr"] *= multiplier

    df.to_csv(storage_path, index=False)
    print(f"  ✓ Updated costs in {storage_path.name}")

# ==================================================
# STEP 3: APPLY TO ALL CASES + PERIODS
# ==================================================

def apply_updates():
    for future_name, multiplier in COST_MULTIPLIERS.items():
        future_dir = FUTURES_DIR / future_name

        if not future_dir.exists():
            print(f"⚠ Missing future dir: {future_dir}")
            continue

        for case in sorted(future_dir.iterdir()):
            if not case.is_dir():
                continue

            print(f"\nUpdating {case.name}")

            for period in ["p1", "p2", "p3"]:
                storage = case / f"inputs/inputs_{period}/resources/Storage.csv"

                if storage.exists():
                    update_storage_costs(storage, multiplier)
                else:
                    print(f"  ⚠ Missing: {storage}")

# ==================================================
# MAIN
# ==================================================

def main():
    print("=== Creating battery futures ===")
    create_future_cases()

    print("\n=== Applying cost updates ===")
    apply_updates()

    print("\nDone!")

if __name__ == "__main__":
    main()