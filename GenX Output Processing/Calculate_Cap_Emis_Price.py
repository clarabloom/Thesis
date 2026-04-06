#!/usr/bin/env python3
"""
Multi-case runner for Calculate_Capacity.

How to use:
1) Put this script alongside your case folders (or use absolute paths).
2) Edit the CASE_DIRS list below to include the directories for each case.
3) Run this script. It will:
   - run the existing revenue calculations for periods 1–3 for each case,
   - add a first column "CaseName" with the case folder name,
   - vertically concatenate all cases, and
   - write the result to 'Capacity_by_Zone_by_Year_ALL_CASES.csv' next to this script.
   
       "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesinstate50"
    
           "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highnuclearcost/highnuclear_cesinstate50"
    
        "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_cesinstate50"
   
           "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highambition/highambition_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowambition/lowambition_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowsolarcost/lowsolar_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highsolarcost/highsolar_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highng/highng_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowng/lowng_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lowdemand/lowdemand_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highdemand/highdemand_cesinstate50"
    
            "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition/highestamb_cesinstate50"
"""

import os
import pandas as pd
import numpy as np

# === 1) HARD-CODE YOUR CASE DIRECTORIES HERE ===
# You can use relative names (folders next to this script) or absolute paths.
CASE_DIRS = [       "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccs",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstech",
   "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstechnuc35",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstechnuc45",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesccstechret",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesincccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesincccstechinstate",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/lownuclearcost/lownuclear_cesinstate50"
    ]

def get_start_cap(df, zone, tech):
    return df.loc[df.Resource.str.contains(zone)&df.Resource.str.contains(tech),"StartCap"].sum()
def get_start_energy_cap(df, zone, tech):
    return df.loc[df.Resource.str.contains(zone)&df.Resource.str.contains(tech),"StartEnergyCap"].sum()
def get_cap(df, zone, tech):
    return df.loc[df.Resource.str.contains(zone)&df.Resource.str.contains(tech),"EndCap"].sum()
def get_energy_cap(df, zone, tech):
    return df.loc[df.Resource.str.contains(zone)&df.Resource.str.contains(tech),"EndEnergyCap"].sum()

# === Existing function, modified only to read from a given base_dir ===
def calculate_revenue(df, period, base_dir):
    p = period
    start = 0
    if period == 0:
        start = 1
        period = 1
    cap_path = os.path.join(base_dir, "results", f"results_p{period}", "capacity.csv")

    cap_in = pd.read_csv(cap_path, header='infer')


    zones = ["NJ1"]

    minorcap = []
    hydrocap = []
    exnukecap = []
    newnukecap = []
    coalcap = []
    solarcap = []
    windcap = []
    gascap = []
    battcap = []
    battencap = []
    for zone in zones:
        if start == 0:
            minorcap.append(get_cap(cap_in,zone,"geothermal")+get_cap(cap_in,zone,"biomass")+get_cap(cap_in,zone,"petroleum"))
            hydrocap.append(get_cap(cap_in,zone,"conventional_hydro"))
            exnukecap.append(get_cap(cap_in,zone,"nuclear_1"))
            newnukecap.append(get_cap(cap_in,zone,"nuclear_nuclear"))
            coalcap.append(get_cap(cap_in,zone,"coal"))
            solarcap.append(get_cap(cap_in,zone,"solar")+get_cap(cap_in,zone,"pv")+get_cap(cap_in,zone,"distributed"))
            windcap.append(get_cap(cap_in,zone,"wind"))
            gascap.append(get_cap(cap_in,zone,"gas"))
            battcap.append(get_cap(cap_in,zone,"batt"))
            battencap.append(get_energy_cap(cap_in,zone,"batt"))
        else:
            minorcap.append(get_start_cap(cap_in,zone,"geothermal")+get_start_cap(cap_in,zone,"biomass")+get_start_cap(cap_in,zone,"petroleum"))
            hydrocap.append(get_start_cap(cap_in,zone,"conventional_hydro"))
            exnukecap.append(get_start_cap(cap_in,zone,"nuclear_1"))
            newnukecap.append(get_start_cap(cap_in,zone,"nuclear_nuclear"))
            coalcap.append(get_start_cap(cap_in,zone,"coal"))
            solarcap.append(get_start_cap(cap_in,zone,"solar")+get_start_cap(cap_in,zone,"pv")+get_start_cap(cap_in,zone,"distributed"))
            windcap.append(get_start_cap(cap_in,zone,"wind"))
            gascap.append(get_start_cap(cap_in,zone,"gas"))
            battcap.append(get_start_cap(cap_in,zone,"batt"))
            battencap.append(get_start_energy_cap(cap_in,zone,"batt"))

    df[f"Minor_Techs_p{p}"] = minorcap
    df[f"Hydropower_p{p}"] = hydrocap
    df[f"Existing_Nuclear_p{p}"] = exnukecap
    df[f"New_Nuclear_p{p}"] = newnukecap
    df[f"Coal_p{p}"] = coalcap
    df[f"Solar_p{p}"] = solarcap
    df[f"Wind_p{p}"] = windcap
    df[f"Natural_Gas_p{p}"] = gascap
    df[f"Battery_Power_p{p}"] = battcap
    df[f"Battery_Energy_p{p}"] = battencap
    return df

def build_single_case_df(base_dir):
    # Base Zone frame (same as your original script)
    df = pd.DataFrame({"Zone": [
        "NJ1"
    ]})
    # Run for periods 1–3 (same as original)
    df = calculate_revenue(df, 0, base_dir)
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
    out_path = os.path.join(script_dir, "Capacities_by_Zone_by_Tech_by_Year_ALL_CASES.csv")
    combined.to_csv(out_path, index=False)
    print(f"\nWrote {len(all_case_dfs)} cases to: {out_path}")

if __name__ == "__main__":
    main()
    
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