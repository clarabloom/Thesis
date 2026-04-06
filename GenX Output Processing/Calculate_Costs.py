#!/usr/bin/env python3

# Multi-case runner to Caculate Costs

import os
import pandas as pd

# === CASE DIRECTORIES ===
CASE_DIRS = [
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesinstate100"
]

NJ_ZONE_COL = "Zone10"   # NJ zone in GenX

def read_costs_for_period(base_dir, period):
    costs_path = os.path.join(
        base_dir,
        "results",
        f"results_p{period}",
        "costs.csv"
    )

    if not os.path.isfile(costs_path):
        raise FileNotFoundError(costs_path)

    costs = pd.read_csv(costs_path)

    # Row with total system cost
    row = costs.loc[costs["Costs"] == "cTotal"].iloc[0]

    return {
        f"System_Cost_p{period}": row["Total"],
        f"NJ_Cost_p{period}": row.get(NJ_ZONE_COL, float("nan")),
    }

def build_single_case_row(base_dir):
    out = {}

    for p in [1, 2, 3]:
        out.update(read_costs_for_period(base_dir, p))

    return out

def main():
    rows = []

    for case_dir in CASE_DIRS:
        case_name = os.path.basename(os.path.normpath(case_dir))

        if not os.path.isdir(case_dir):
            print(f"Skipping missing case: {case_name}")
            continue

        print(f"Processing {case_name}")
        row = build_single_case_row(case_dir)
        row["CaseName"] = case_name
        rows.append(row)

    if not rows:
        print("No cases processed.")
        return

    df = pd.DataFrame(rows)
    df = df[["CaseName"] + [c for c in df.columns if c != "CaseName"]]

    out_path = os.path.join(
        os.path.dirname(__file__),
        "Costs_by_Case_and_Period_ALL_CASES.csv"
    )
    df.to_csv(out_path, index=False)

    print(f"\nWrote {len(df)} cases to:\n{out_path}")

if __name__ == "__main__":
    main()