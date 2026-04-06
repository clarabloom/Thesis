#!/usr/bin/env python3

import pandas as pd
from pathlib import Path

# =====================================================
# ROOT DIRECTORIES
# =====================================================

BASE_DIR    = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

# Toggle debug prints
DEBUG = False

# =====================================================
# FIND ALL CASES
# =====================================================

def find_all_cases():
    cases = []

    # Base cases
    for case in BASE_DIR.iterdir():
        if case.is_dir():
            cases.append(case)

    # All futures (auto-detect all scenarios)
    for scenario in FUTURES_DIR.iterdir():
        if scenario.is_dir():
            for case in scenario.iterdir():
                if case.is_dir():
                    cases.append(case)

    print(f"Found {len(cases)} total cases.")
    return cases

# =====================================================
# NSE CALCULATION
# =====================================================

def calculate_nse(case_dir):
    df = pd.DataFrame({"Zone": ["NJ"]})

    for period in [1, 2, 3]:

        nse_path = case_dir / f"results/results_p{period}/nse.csv"
        dem_path = case_dir / f"inputs/inputs_p{period}/TDR_results/Demand_data.csv"

        if not nse_path.exists() or not dem_path.exists():
            print(f"  Missing files for {case_dir.name}, p{period}")
            continue

        # -------------------------------
        # Load data
        # -------------------------------
        nse = pd.read_csv(nse_path)
        dem = pd.read_csv(dem_path)

        if DEBUG:
            print(f"\n--- DEBUG {case_dir.name} p{period} ---")
            print("NSE columns:", nse.columns.tolist())
            print("Demand columns:", dem.columns.tolist())

        # -------------------------------
        # Convert NSE to numeric safely
        # -------------------------------
        nse_cols = [c for c in nse.columns if c.lower() != "time"]

        nse_numeric = nse[nse_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

        # -------------------------------
        # NJ NSE (zone 10)
        # -------------------------------
        if "10" in nse.columns:
            nse_nj = pd.to_numeric(nse["10"], errors="coerce").fillna(0).values
        else:
            nse_nj = pd.Series([0] * len(nse)).values

        # -------------------------------
        # System NSE
        # -------------------------------
        nse_system = nse_numeric.sum(axis=1).values

        # -------------------------------
        # Weights (TDR)
        # -------------------------------
        weights = pd.to_numeric(dem["Sub_Weights"], errors="coerce").dropna().values
        hourly_weights = [w / 168 for w in weights for _ in range(168)]

        # -------------------------------
        # Align lengths
        # -------------------------------
        n = min(len(hourly_weights), len(nse_system))
        hourly_weights = hourly_weights[:n]
        nse_nj         = nse_nj[:n]
        nse_system     = nse_system[:n]

        # -------------------------------
        # TOTAL NSE
        # -------------------------------
        total_nse_nj     = (nse_nj * hourly_weights).sum()
        total_nse_system = (nse_system * hourly_weights).sum()

        # -------------------------------
        # LOAD CALCULATION
        # -------------------------------

        # NJ load
        if "Demand_MW_z10" in dem.columns:
            demand_nj = pd.to_numeric(dem["Demand_MW_z10"], errors="coerce").fillna(0).values[:n]
            total_load_nj = (demand_nj * hourly_weights).sum()
        else:
            total_load_nj = None

        # System load
        demand_cols = [c for c in dem.columns if c.startswith("Demand_MW_z")]

        if demand_cols:
            demand_numeric = dem[demand_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
            demand_system = demand_numeric.sum(axis=1).values[:n]
            total_load_system = (demand_system * hourly_weights).sum()
        else:
            total_load_system = None

        # -------------------------------
        # PERCENTAGES
        # -------------------------------
        nse_pct_nj = (
            total_nse_nj / total_load_nj
            if total_load_nj and total_load_nj > 0 else 0
        )

        nse_pct_system = (
            total_nse_system / total_load_system
            if total_load_system and total_load_system > 0 else 0
        )

        # -------------------------------
        # STORE RESULTS
        # -------------------------------
        df[f"NSE_MWh_NJ_p{period}"]     = [round(total_nse_nj, 2)]
        df[f"NSE_pct_NJ_p{period}"]     = [round(nse_pct_nj, 6)]

        df[f"NSE_MWh_System_p{period}"] = [round(total_nse_system, 2)]
        df[f"NSE_pct_System_p{period}"] = [round(nse_pct_system, 6)]

        if DEBUG:
            print(f"NSE NJ p{period}: {total_nse_nj}")
            print(f"NSE System p{period}: {total_nse_system}")

    return df

# =====================================================
# MAIN
# =====================================================

def main():
    cases = find_all_cases()

    all_rows = []

    for case_path in cases:
        case_name = case_path.name
        print(f"Processing {case_name}")

        try:
            nse_df = calculate_nse(case_path)
            nse_df.insert(0, "CaseName", case_name)

            # Save per-case
            nse_df.to_csv(case_path / f"{case_name}_nse_summary.csv", index=False)

            all_rows.append(nse_df)

        except Exception as e:
            print(f"❌ Error processing {case_name}: {e}")

    # Save combined file
    if all_rows:
        pd.concat(all_rows, ignore_index=True).to_csv("ALL_CASE_NSE.csv", index=False)

    print(f"\n✅ Done. Processed {len(cases)} cases.")

# =====================================================

if __name__ == "__main__":
    main()