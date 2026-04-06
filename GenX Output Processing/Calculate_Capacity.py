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

def get_start_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_")&df.Resource.str.contains(tech),"StartCap"].sum()
def get_start_energy_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_")&df.Resource.str.contains(tech),"StartEnergyCap"].sum()
def get_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_")&df.Resource.str.contains(tech),"EndCap"].sum()
def get_energy_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_")&df.Resource.str.contains(tech),"EndEnergyCap"].sum()

def calculate_revenue(df, period, base_dir):
    p = period
    start = 0
    if period == 0:
        start = 1
        period = 1
    cap_path = os.path.join(base_dir, "results", f"results_p{period}", "capacity.csv")
    cap_in = pd.read_csv(cap_path, header='infer')

PJM_ZONES = ["DE1", "IL1", "KY3", "KY4", "MD1", "MD2", "MI", "MISC",
             "NJ1", "OH1", "OH2", "OH3", "OH4", "PA1", "PA2",
             "PA3", "PA4", "VA1", "VA2", "VA3", "VA4", "WV1", "WV2"]

def get_start_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_") & df.Resource.str.contains(tech), "StartCap"].sum()
def get_start_energy_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_") & df.Resource.str.contains(tech), "StartEnergyCap"].sum()
def get_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_") & df.Resource.str.contains(tech), "EndCap"].sum()
def get_energy_cap(df, zone, tech):
    return df.loc[df.Resource.str.startswith(zone + "_") & df.Resource.str.contains(tech), "EndEnergyCap"].sum()


def calculate_revenue(df, period, base_dir):
    p = period
    start = 0
    if period == 0:
        start = 1
        period = 1
    cap_path = os.path.join(base_dir, "results", f"results_p{period}", "capacity.csv")
    cap_in = pd.read_csv(cap_path, header='infer')

    def get_tech_caps(zone=None):
        def cap(tech):
            if zone:
                if start == 0:
                    return cap_in.loc[cap_in.Resource.str.startswith(zone + "_") & cap_in.Resource.str.contains(tech), "EndCap"].sum()
                else:
                    return cap_in.loc[cap_in.Resource.str.startswith(zone + "_") & cap_in.Resource.str.contains(tech), "StartCap"].sum()
            else:
                if start == 0:
                    return cap_in.loc[cap_in.Resource.str.contains(tech), "EndCap"].sum()
                else:
                    return cap_in.loc[cap_in.Resource.str.contains(tech), "StartCap"].sum()

        def energy_cap(tech):
            if zone:
                if start == 0:
                    return cap_in.loc[cap_in.Resource.str.startswith(zone + "_") & cap_in.Resource.str.contains(tech), "EndEnergyCap"].sum()
                else:
                    return cap_in.loc[cap_in.Resource.str.startswith(zone + "_") & cap_in.Resource.str.contains(tech), "StartEnergyCap"].sum()
            else:
                if start == 0:
                    return cap_in.loc[cap_in.Resource.str.contains(tech), "EndEnergyCap"].sum()
                else:
                    return cap_in.loc[cap_in.Resource.str.contains(tech), "StartEnergyCap"].sum()

        return {
            f"Minor_Techs_p{p}":     cap("geothermal") + cap("biomass") + cap("petroleum"),
            f"Hydropower_p{p}":       cap("conventional_hydro"),
            f"Existing_Nuclear_p{p}": cap("nuclear_1"),
            f"New_Nuclear_p{p}":      cap("nuclear_nuclear"),
            f"Coal_p{p}":             cap("coal"),
            f"Solar_p{p}":            cap("solar") + cap("pv") + cap("distributed"),
            f"Wind_p{p}":             cap("wind"),
            f"Natural_Gas_p{p}":      cap("gas"),
            f"Battery_Power_p{p}":    cap("batt"),
            f"Battery_Energy_p{p}":   energy_cap("batt"),
        }

    def get_tech_caps_pjm():
        def cap(tech):
            mask = cap_in.Resource.str.contains(tech)
            zone_mask = pd.Series(False, index=cap_in.index)
            for z in PJM_ZONES:
                zone_mask |= cap_in.Resource.str.startswith(z + "_")
            if start == 0:
                return cap_in.loc[mask & zone_mask, "EndCap"].sum()
            else:
                return cap_in.loc[mask & zone_mask, "StartCap"].sum()

        def energy_cap(tech):
            mask = cap_in.Resource.str.contains(tech)
            zone_mask = pd.Series(False, index=cap_in.index)
            for z in PJM_ZONES:
                zone_mask |= cap_in.Resource.str.startswith(z + "_")
            if start == 0:
                return cap_in.loc[mask & zone_mask, "EndEnergyCap"].sum()
            else:
                return cap_in.loc[mask & zone_mask, "StartEnergyCap"].sum()

        return {
            f"Minor_Techs_p{p}":     cap("geothermal") + cap("biomass") + cap("petroleum"),
            f"Hydropower_p{p}":       cap("conventional_hydro"),
            f"Existing_Nuclear_p{p}": cap("nuclear_1"),
            f"New_Nuclear_p{p}":      cap("nuclear_nuclear"),
            f"Coal_p{p}":             cap("coal"),
            f"Solar_p{p}":            cap("solar") + cap("pv") + cap("distributed"),
            f"Wind_p{p}":             cap("wind"),
            f"Natural_Gas_p{p}":      cap("gas"),
            f"Battery_Power_p{p}":    cap("batt"),
            f"Battery_Energy_p{p}":   energy_cap("batt"),
        }

    rows = [
        {"Zone": "NJ1", **get_tech_caps(zone="NJ1")},
        {"Zone": "PJM", **get_tech_caps_pjm()},
    ]

    period_df = pd.DataFrame(rows)
    df = period_df if df.empty else df.merge(period_df, on="Zone", how="outer")
    return df


def build_single_case_df(base_dir):
    df = pd.DataFrame(columns=["Zone"])
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
            print(f"WARNING: Skipping '{case_name}': folder not found at {case_path}")
            continue
        df_case = build_single_case_df(case_path)
        df_case.insert(0, "CaseName", case_name)
        all_case_dfs.append(df_case)

    if not all_case_dfs:
        print("No valid case directories found.")
        return

    combined = pd.concat(all_case_dfs, axis=0, ignore_index=True, sort=False)
    out_path = os.path.join(script_dir, "Capacities_by_Zone_by_Tech_by_Year_ALL_CASES.csv")
    combined.to_csv(out_path, index=False)
    print(f"\nWrote {len(all_case_dfs)} cases to: {out_path}")

if __name__ == "__main__":
    main()