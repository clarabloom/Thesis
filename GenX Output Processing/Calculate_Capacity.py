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
    "Basecase_RGGI",
    "Updated_RGGI_noprocurement",
    "Updated_RGGI_noprocurement_noOOS",
    "Updated_RGGI_procurement_noOOS",
    "Basecase_RGGI_solarderate",
    "Updated_RGGI_noprocurement_solarderate",
    "Updated_RGGI_noprocurement_noOOS_solarderate",
    "Updated_RGGI_procurement_noOOS_solarderate",  
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


    zones = ["NJ1", "DE1", "PA3", "PA4"]

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
        "NJ1", "DE1", "PA3", "PA4"
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
