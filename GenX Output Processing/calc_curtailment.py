#!/usr/bin/env python3

import pandas as pd
from pathlib import Path

# =====================================================
# ROOT DIRECTORIES
# =====================================================

BASE_DIR    = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

# Toggle debug
DEBUG = False

# =====================================================
# FIND ALL CASES
# =====================================================

def find_all_cases():
    cases = []

    # Base
    for case in BASE_DIR.iterdir():
        if case.is_dir():
            cases.append(case)

    # Futures
    for scenario in FUTURES_DIR.iterdir():
        if scenario.is_dir():
            for case in scenario.iterdir():
                if case.is_dir():
                    cases.append(case)

    print(f"Found {len(cases)} total cases.")
    return cases

# =====================================================
# MAIN CALCULATION
# =====================================================

def calculate_metrics(case_dir):

    row = {}

    for period in [1, 2, 3]:

        curtail_path = case_dir / f"results/results_p{period}/curtailment.csv"
        power_path   = case_dir / f"results/results_p{period}/power.csv"
        dem_path     = case_dir / f"inputs/inputs_p{period}/TDR_results/Demand_data.csv"

        if not curtail_path.exists() or not dem_path.exists():
            print(f"  Missing data for {case_dir.name}, p{period}")
            continue

        # -------------------------------
        # Load data
        # -------------------------------
        curtail = pd.read_csv(curtail_path)
        dem     = pd.read_csv(dem_path)

        power = None
        if power_path.exists():
            power = pd.read_csv(power_path)

        if DEBUG:
            print(f"\n--- DEBUG {case_dir.name} p{period} ---")
            print("Curtail cols:", curtail.columns[:5])
            if power is not None:
                print("Power cols:", power.columns[:5])

        # -------------------------------
        # Weights
        # -------------------------------
        weights = pd.to_numeric(dem["Sub_Weights"], errors="coerce").dropna().values
        hourly_weights = [w / 168 for w in weights for _ in range(168)]

        # -------------------------------
        # CURTAILMENT
        # -------------------------------
        if "Total" in curtail.columns:
            curtail_vals = pd.to_numeric(curtail["Total"], errors="coerce").fillna(0).values
        else:
            curtail_numeric = curtail.drop(columns=["Resource"], errors="ignore") \
                                     .apply(pd.to_numeric, errors="coerce") \
                                     .fillna(0)
            curtail_vals = curtail_numeric.sum(axis=1).values

        # Remove AnnualSum row if present
        if len(curtail_vals) > len(hourly_weights):
            curtail_vals = curtail_vals[:len(hourly_weights)]

        # -------------------------------
        # RENEWABLE GENERATION
        # -------------------------------
        total_renewable = 0

        if power is not None:

            # Clean
            power_numeric = power.drop(columns=["Time"], errors="ignore") \
                                 .apply(pd.to_numeric, errors="coerce") \
                                 .fillna(0)

            # Identify renewable columns
            renewable_cols = [
                c for c in power_numeric.columns
                if any(x in c.lower() for x in ["solar", "wind", "pv"])
            ]

            if renewable_cols:
                renewable_gen = power_numeric[renewable_cols].sum(axis=1).values
            else:
                renewable_gen = [0] * len(power_numeric)

        else:
            renewable_gen = [0] * len(curtail_vals)

        # -------------------------------
        # ALIGN LENGTHS
        # -------------------------------
        n = min(len(hourly_weights), len(curtail_vals), len(renewable_gen))

        curtail_vals   = curtail_vals[:n]
        renewable_gen  = renewable_gen[:n]
        hourly_weights = hourly_weights[:n]

        # -------------------------------
        # TOTALS
        # -------------------------------
        total_curtailment = (curtail_vals * hourly_weights).sum()
        total_renewable   = (renewable_gen * hourly_weights).sum()

        # -------------------------------
        # METRIC: % OF RENEWABLES
        # -------------------------------
        curtail_pct = (
            total_curtailment / total_renewable
            if total_renewable > 0 else 0
        )

        # -------------------------------
        # STORE
        # -------------------------------
        row[f"Curtailment_MWh_p{period}"] = round(total_curtailment, 2)
        row[f"Renewable_MWh_p{period}"]   = round(total_renewable, 2)
        row[f"Curtailment_pct_RE_p{period}"] = round(curtail_pct, 5)

        if DEBUG:
            print(f"Curtailment p{period}: {total_curtailment}")
            print(f"Renewables p{period}: {total_renewable}")
            print(f"% curtailed: {curtail_pct}")

    return row

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
            metrics = calculate_metrics(case_path)

            metrics["CaseName"] = case_name

            # Save per-case
            pd.DataFrame([metrics]).to_csv(
                case_path / f"{case_name}_curtailment_summary.csv",
                index=False
            )

            all_rows.append(metrics)

        except Exception as e:
            print(f"❌ Error processing {case_name}: {e}")

    # Save combined
    if all_rows:
        pd.DataFrame(all_rows).to_csv("ALL_CASE_CURTAILMENT_RE.csv", index=False)

    print(f"\n✅ Done. Processed {len(cases)} cases.")

# =====================================================

if __name__ == "__main__":
    main()