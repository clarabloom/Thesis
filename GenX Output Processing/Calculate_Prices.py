#!/usr/bin/env python3
"""
Multi-case runner for Calculate_cost.

How to use:
1) Put this script alongside your case folders (or use absolute paths).
2) Edit the CASE_DIRS list below to include the directories for each case.
3) Run this script. It will:
   - run the existing cost calculations for periods 1–3 for each case,
   - add a first column "CaseName" with the case folder name,
   - vertically concatenate all cases, and
   - write the result to 'costs_by_Zone_by_Year_ALL_CASES.csv' next to this script.
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
def calculate_cost(df, period, base_dir):
    dem_path   = os.path.join(base_dir, "inputs", f"inputs_p{period}", "TDR_results", "Demand_data.csv")
    capres_path   = os.path.join(base_dir, "inputs", f"inputs_p{period}", "policies", "Capacity_reserve_margin.csv")
    prices_path = os.path.join(base_dir, "results", f"results_p{period}", "prices.csv")
    resmar_path = os.path.join(base_dir, "results", f"results_p{period}", "ReserveMargin_w.csv")
    esr_path    = os.path.join(base_dir, "results", f"results_p{period}", "ESR_prices_and_penalties.csv")
    mincap_path = os.path.join(base_dir, "results", f"results_p{period}", "MinCapReq_prices_and_penalties.csv")

    dem_in = pd.read_csv(dem_path, header='infer')
    hourly_demand = dem_in["Demand_MW_z10"].values
    weights = dem_in["Sub_Weights"].dropna().values
    print(f"[{os.path.basename(os.path.normpath(base_dir))}] p{period}: {len(weights)} sub-weights")
    hourly_weights = [w/168 for w in weights for _ in range(168)]

    capres = pd.read_csv(capres_path, header='infer')

    prices = pd.read_csv(prices_path, header='infer')
    resmar = pd.read_csv(resmar_path, header='infer')
    esr = pd.read_csv(esr_path, header='infer')
    mincap = pd.read_csv(mincap_path, header='infer')

    energyrev = []
    caprev_pjm = []
    caprev_nj = []
    energyrev.append(round((prices['10'].values * hourly_weights * hourly_demand).sum()/(hourly_weights * hourly_demand).sum()))
    caprev_pjm.append(round((resmar['CapRes_5'].values*1.177 * hourly_weights * hourly_demand).sum()/(hourly_weights * hourly_demand).sum()))
    if ("case" in base_dir.lower()) | (period == 1):
        caprev_nj.append(0)
    else:
        try:
            captarget = capres.loc[capres['Network_zones'] == 'z10', 'CapRes_8'].values[0]
        except KeyError:
            captarget = 0
        if captarget != 0:
            captarget = captarget + 1
            
        try:
            if 'CapRes_8' in resmar.columns and not pd.isna(captarget):
                numerator = (
                    resmar['CapRes_8'].fillna(0).values
                    * captarget
                    * hourly_weights
                    * hourly_demand
                ).sum()
        
                denominator = (hourly_weights * hourly_demand).sum()
        
                if denominator > 0:
                    value = numerator / denominator
                else:
                    value = 0
        
                caprev_nj.append(round(value, 4))
            else:
                caprev_nj.append(0)

        except Exception:
            caprev_nj.append(0)

    df[f"Energy_Price_p{period}"] = energyrev
    df[f"PJM_Capacity_Price_p{period}"] = caprev_pjm
    df[f"NJ_Clean_Capacity_Price_p{period}"] = caprev_nj

    esrrev = []
    if "case" in base_dir.lower():
        esrrev.append(esr['ESR_Price'].values[2]*0.512 + esr['ESR_Price'].values[7]*0.512)
    elif period == 1:
        esrrev.append(esr['ESR_Price'].values[2]*0.534 + esr['ESR_Price'].values[7]*0.85)
    elif period == 2:
        esrrev.append(esr['ESR_Price'].values[2]*0.534 + esr['ESR_Price'].values[7]*1)
    elif period == 3:
        esrrev.append(esr['ESR_Price'].values[2]*0.534 + esr['ESR_Price'].values[7]*1)

    df[f"EAC_Price_p{period}"] = esrrev

    mincaprev = []
    if "_procurement_" in base_dir.lower():
        if period == 1:
            mincaprev.append(round((mincap['Price'].values[9]*3000+mincap['Price'].values[10]*0)/(hourly_weights * hourly_demand).sum()))
        elif period == 2:
            mincaprev.append(round((mincap['Price'].values[9]*6000+mincap['Price'].values[10]*10000)/(hourly_weights * hourly_demand).sum()))
        elif period == 3:
            mincaprev.append(round((mincap['Price'].values[9]*6000+mincap['Price'].values[10]*14000)/(hourly_weights * hourly_demand).sum()))
    else:
        mincaprev.append(round((mincap['Price'].values[9]*2000+mincap['Price'].values[10]*0)/(hourly_weights * hourly_demand).sum()))

    df[f"MinCap_Price_p{period}"] = mincaprev

    df[f"Total_Price_p{period}"] = (
        df[f"Energy_Price_p{period}"]
        + df[f"PJM_Capacity_Price_p{period}"]
        + df[f"NJ_Clean_Capacity_Price_p{period}"]
        + df[f"EAC_Price_p{period}"]
        + df[f"MinCap_Price_p{period}"]
    )
    return df

def build_single_case_df(base_dir):
    # Base Zone frame (same as your original script)
    df = pd.DataFrame({"Zone": [
        "NJ"
    ]})
    # Run for periods 1–3 (same as original)
    df = calculate_cost(df, 1, base_dir)
    df = calculate_cost(df, 2, base_dir)
    df = calculate_cost(df, 3, base_dir)
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
    out_path = os.path.join(script_dir, "Prices_by_Zone_by_Year_ALL_CASES.csv")
    combined.to_csv(out_path, index=False)
    print(f"\nWrote {len(all_case_dfs)} cases to: {out_path}")

if __name__ == "__main__":
    main()
