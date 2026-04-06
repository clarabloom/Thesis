import shutil
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


# ==================================================
# FUNCTION TO DELETE RESULTS FOLDERS
# ==================================================

def delete_results_dirs(case_dir):

    for item in case_dir.iterdir():

        if item.is_dir() and item.name.startswith("results"):

            shutil.rmtree(item)

            print(f"Deleted: {item}")


# ==================================================
# BASE CASES
# ==================================================

# print("\nCleaning BASE cases\n")

# for case_dir in BASE_DIR.iterdir():

#    if not case_dir.is_dir():
#        continue

   # delete_results_dirs(case_dir)


# ==================================================
# FUTURES CASES
# ==================================================

print("\nCleaning FUTURES cases\n")

for scenario_dir in FUTURES_DIR.iterdir():

    if not scenario_dir.is_dir():
        continue

    for case_dir in scenario_dir.iterdir():

        if not case_dir.is_dir():
            continue

        delete_results_dirs(case_dir)


print("\nAll results folders removed.")