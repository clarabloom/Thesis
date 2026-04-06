import os

BASE_DIR = "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base"
FUTURES_DIR = "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios"

TARGET_POLICIES = ["cesincccstech", "cesincccstechinstate"]

def matches_policy(case_name):
    suffix = case_name.split("_", 1)[-1]
    return suffix in TARGET_POLICIES

def fix_results(case_dir):
    results = os.path.join(case_dir, "results")
    results_1 = os.path.join(case_dir, "results_1")

    if os.path.isdir(results_1):
        print(f"Fixing {case_dir}")

        # Rename old results if exists
        if os.path.isdir(results):
            i = "old"
            new_name = os.path.join(case_dir, f"results_{i}")
            while os.path.isdir(new_name):
                i += "_1"
                new_name = os.path.join(case_dir, f"results_{i}")

            os.rename(results, new_name)
            print(f"  Renamed results → {os.path.basename(new_name)}")

        # Promote results_1 → results
        os.rename(results_1, results)
        print("  Renamed results_1 → results")


# BASE
print("Processing BASE cases...")
for case in os.listdir(BASE_DIR):
    case_path = os.path.join(BASE_DIR, case)
    if os.path.isdir(case_path) and matches_policy(case):
        fix_results(case_path)

# FUTURES
print("Processing FUTURE cases...")
for scenario in os.listdir(FUTURES_DIR):
    scenario_path = os.path.join(FUTURES_DIR, scenario)
    if not os.path.isdir(scenario_path):
        continue

    for case in os.listdir(scenario_path):
        case_path = os.path.join(scenario_path, case)
        if os.path.isdir(case_path) and matches_policy(case):
            fix_results(case_path)

print("Done.")