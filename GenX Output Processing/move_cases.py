import shutil
from pathlib import Path

# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

DEST_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/PROGRESS")

TARGET_KEY = "cesincccsinstate"

# Ensure destination exists
DEST_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# HELPER
# ==================================================

def move_case(case_path):
    name = case_path.name

    if TARGET_KEY not in name:
        return

    dest_path = DEST_DIR / name

    # Avoid overwriting existing folders
    if dest_path.exists():
        i = 1
        while (DEST_DIR / f"{name}_{i}").exists():
            i += 1
        dest_path = DEST_DIR / f"{name}_{i}"

    print(f"Moving: {case_path} → {dest_path}")
    shutil.move(str(case_path), str(dest_path))

# ==================================================
# PROCESS BASE CASES
# ==================================================

print("=== BASE CASES ===")

for case in BASE_DIR.iterdir():
    if case.is_dir():
        move_case(case)

# ==================================================
# PROCESS FUTURE CASES
# ==================================================

print("\n=== FUTURE CASES ===")

for scenario in FUTURES_DIR.iterdir():
    if not scenario.is_dir():
        continue

    for case in scenario.iterdir():
        if case.is_dir():
            move_case(case)

print("\nDONE: All cesincccsinstate cases moved.")