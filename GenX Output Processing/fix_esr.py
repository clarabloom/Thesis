import shutil
from pathlib import Path

BASE_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base"
)

FUTURES_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios"
)

PERIODS = ["p1","p2","p3"]


def get_policy_suffix(case_name):
    """
    Extract policy suffix from futures case name.
    Example:
        highsolar_cesccs -> cesccs
        highsolar_base -> base
    """
    return case_name.split("_",1)[1]


for scenario_dir in FUTURES_DIR.iterdir():

    if not scenario_dir.is_dir():
        continue

    print(f"\nProcessing scenario: {scenario_dir.name}")

    for case_dir in scenario_dir.iterdir():

        if not case_dir.is_dir():
            continue

        case_name = case_dir.name

        try:
            policy_suffix = get_policy_suffix(case_name)
        except:
            print(f"Skipping {case_name}")
            continue

        base_case = BASE_DIR / f"base_{policy_suffix}"

        if not base_case.exists():
            print(f"Base case not found for {case_name}")
            continue

        for period in PERIODS:

            src = base_case / "inputs" / f"inputs_{period}" / "policies" / "Energy_share_requirement.csv"

            dst = case_dir / "inputs" / f"inputs_{period}" / "policies" / "Energy_share_requirement.csv"

            if not src.exists():
                print(f"Missing source: {src}")
                continue

            shutil.copy2(src, dst)

            print(f"✓ {case_name} {period} ← base_{policy_suffix}")

print("\nAll ESR files corrected.")