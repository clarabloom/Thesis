#!/usr/bin/env python3
"""
Multi-case runner for Calculate_Revenue.

How to use:
1) Put this script alongside your case folders (or use absolute paths).
2) Edit the CASE_DIRS list below to include the directories for each case.
3) Run this script. It will:
   - run the existing revenue calculations for periods 1–3 for each case,
   - add a first column "CaseName" with the case folder name,
   - vertically concatenate all cases, and
   - write the result to 'Revenues_by_Zone_by_Year_ALL_CASES.csv' next to this script.
"""

import os
import pandas as pd
import numpy as np

# === 1) HARD-CODE YOUR CASE DIRECTORIES HERE ===
# You can use relative names (folders next to this script) or absolute paths.
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
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesinstate50"
    ]

# === Existing function, modified only to read from a given base_dir ===
def calculate_revenue(df, period, base_dir):
    import os
    import pandas as pd

    dem_path       = os.path.join(base_dir, "inputs", f"inputs_p{period}", "TDR_results", "Demand_data.csv")
    emissions_path = os.path.join(base_dir, "results", f"results_p{period}", "emissions.csv")

    # Load demand & weights
    dem_in = pd.read_csv(dem_path, header='infer')
    hourly_demand = dem_in["Demand_MW_z10"].values
    weights = dem_in["Sub_Weights"].dropna().values
    print(f"[{os.path.basename(os.path.normpath(base_dir))}] p{period}: {len(weights)} sub-weights")
    hourly_weights = [w/168 for w in weights for _ in range(168)]

    # Load emissions
    emissions = pd.read_csv(emissions_path, header='infer')

    # Existing totals
    loadmax = [max(hourly_demand)]
    loadtot = [(hourly_demand * hourly_weights).sum()]
    total_system_emissions = [emissions['Total'].iloc[1]]

    # --- New: NJ total emissions (same calc position as 'Total', using column '10') ---
    # Try numeric column name first; fall back to 'z10' if that’s how the file is labeled.
    if '10' in emissions.columns:
        nj_total = emissions['10'].iloc[1]
    elif 'z10' in emissions.columns:
        nj_total = emissions['z10'].iloc[1]
    else:
        raise KeyError("Neither '10' nor 'z10' found in emissions.csv for NJ emissions.")

    # --- New: RGGI total emissions (sum of listed zones; column names without the 'z') ---
    rggi_numeric_cols = ['1','3','6','7','10','11','12']
    rggi_z_cols       = [f"z{x}" for x in rggi_numeric_cols]

    # Prefer numeric columns if present; otherwise use 'z*' columns.
    present_numeric = [c for c in rggi_numeric_cols if c in emissions.columns]
    present_z       = [c for c in rggi_z_cols if c in emissions.columns]

    if present_numeric:
        rggi_total = emissions.loc[:, present_numeric].iloc[1].sum()
    elif present_z:
        rggi_total = emissions.loc[:, present_z].iloc[1].sum()
    else:
        missing_list = ", ".join(rggi_numeric_cols + rggi_z_cols)
        raise KeyError(f"None of the RGGI columns are present. Looked for: {missing_list}")

    # Write results to df
    df[f"Maximum_NJ_Load_p{period}"]          = loadmax
    df[f"Total_NJ_Load_p{period}"]            = loadtot
    df[f"Total_System_Emissions_p{period}"]   = total_system_emissions
    df[f"Total_NJ_Emissions_p{period}"]       = [nj_total]
    df[f"Total_RGGI_Emissions_p{period}"]     = [rggi_total]

    return df


def build_single_case_df(base_dir):
    # Base Zone frame (same as your original script)
    df = pd.DataFrame({"Zone": [
        "NJ"
    ]})
    # Run for periods 1–3 (same as original)
    df = calculate_revenue(df, 1, base_dir)
    df = calculate_revenue(df, 2, base_dir)
    df = calculate_revenue(df, 3, base_dir)
    df = df.round(2)
    return df

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    case_paths = [
        p if os.path.isabs(p) else os.path.join(script_dir, p)
        for p in CASE_DIRS
    ]

    all_case_dfs = []
    for case_path in case_paths:
        case_name = os.path.basename(os.path.normpath(case_path))
        if not os.path.isdir(case_path):
            print(f"WARNING: Skipping '{case_name}' because the folder was not found at: {case_path}")
            continue

        df_case = build_single_case_df(case_path)
        # Insert CaseName as the FIRST column
        df_case.insert(0, "CaseName", case_name)
        all_case_dfs.append(df_case)

    if not all_case_dfs:
        print("No valid case directories were provided. Please edit CASE_DIRS and try again.")
        return

    combined = pd.concat(all_case_dfs, axis=0, ignore_index=True, sort=False)
    out_path = os.path.join(script_dir, "Load_and_Emissions.csv")
    combined.to_csv(out_path, index=False)
    print(f"\nWrote {len(all_case_dfs)} cases to: {out_path}")

if __name__ == "__main__":
    main()
