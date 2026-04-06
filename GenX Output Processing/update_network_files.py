import shutil
from pathlib import Path

import hashlib

def checksum(path):
    return hashlib.md5(path.read_bytes()).hexdigest()

ROOT_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
SOURCE_FILE = ROOT_DIR / "Network_updated.csv"

CASE_PREFIX = "base_"   # only update cases starting with base_
PERIODS = ["inputs_p1", "inputs_p2", "inputs_p3"]

# =========================
# SAFETY CHECKS
# =========================

if not SOURCE_FILE.exists():
    raise FileNotFoundError(f"Source file not found: {SOURCE_FILE}")

print(f"Using source network file:\n  {SOURCE_FILE}\n")

# =========================
# MAIN LOGIC
# =========================

updated_files = []

for case_dir in ROOT_DIR.iterdir():
    if not case_dir.is_dir():
        continue
    if not case_dir.name.startswith(CASE_PREFIX):
        continue

    for period in PERIODS:
        target = (
            case_dir
            / "inputs"
            / period
            / "system"
            / "Network.csv"
        )
        
        print("Checking:", target)

        if target.exists():
            before = checksum(target)
            shutil.copy2(SOURCE_FILE, target)
            after = checksum(target)
        
            if before == after:
                print(f"⚠ NO CHANGE (identical): {target}")
            else:
                print(f"✓ UPDATED: {target}")
        
            updated_files.append(target)

if not updated_files:
    raise RuntimeError("No Network.csv files were updated!")

print(f"\nTotal files updated: {len(updated_files)}")