import shutil
from pathlib import Path

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

SOURCE_POLICY = "cesincccstech"
NEW_POLICY = "cesincccs"

PERIODS = ["p1", "p2", "p3"]

BASE_BASE = BASE_DIR / "base_base"

# ==================================================
# HELPERS
# ==================================================

def get_mincap_source(period):
    return (
        BASE_BASE
        / "inputs"
        / f"inputs_{period}"
        / "policies"
        / "Minimum_capacity_requirement.csv"
    )

def process_case(case_path):
    name = case_path.name

    # Only process relevant policy cases
    if SOURCE_POLICY not in name:
        return

    new_name = name.replace(SOURCE_POLICY, NEW_POLICY)
    new_path = case_path.parent / new_name

    print(f"\n--- Creating {new_name} ---")

    # ==========================================
    # 1. COPY CASE
    # ==========================================
    if not new_path.exists():
        shutil.copytree(case_path, new_path)
        print("✓ Copied case")
    else:
        print("⚠ Case already exists")

    # ==========================================
    # 2. REMOVE OLD RESULTS
    # ==========================================
    for folder in new_path.glob("results*"):
        shutil.rmtree(folder, ignore_errors=True)
    print("✓ Cleared old results")

    # ==========================================
    # 3. REPLACE MINCAP FILES
    # ==========================================
    for p in PERIODS:

        src = get_mincap_source(p)

        dst = (
            new_path
            / "inputs"
            / f"inputs_{p}"
            / "policies"
            / "Minimum_capacity_requirement.csv"
        )

        if not src.exists():
            print(f"⚠ Missing source: {src}")
            continue

        if not dst.exists():
            print(f"⚠ Missing target: {dst}")
            continue

        shutil.copy2(src, dst)
        print(f"✓ Updated MinCap ({p})")

# ==================================================
# RUN BASE CASES
# ==================================================

print("=== BASE CASES ===")

for case in BASE_DIR.iterdir():
    if case.is_dir():
        process_case(case)

# ==================================================
# RUN FUTURE CASES
# ==================================================

print("\n=== FUTURE SCENARIOS ===")

for scenario in FUTURES_DIR.iterdir():

    if not scenario.is_dir():
        continue

    print(f"\nScenario: {scenario.name}")

    for case in scenario.iterdir():
        if case.is_dir():
            process_case(case)

print("\nDONE: cesincccs cases created.")