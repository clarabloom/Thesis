import os
import pandas as pd
import numpy as np

# =====================================================
# USER SETTINGS
# =====================================================

CASE_DIRS = [
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_base",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_ces",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesccstech",
    "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base/base_cesincccstech",
]

PERIODS = [1, 2, 3]
NJ_ZONE = "NJ1"
NJ_DEMAND_COL = "Demand_MW_z10"

OUTFILE = "NJ_Clean_Energy_Metrics_by_Case_and_Period.csv"

# Technologies considered clean
CLEAN_TECH_KEYWORDS = [
    "solar", "pv", "wind", "nuclear", "hydro", "bio", "geothermal"
]

# =====================================================
# HELPERS
# =====================================================

def build_hourly_weights(demand_df):
    """
    Convert GenX sub-weights into per-hour weights.
    """
    weights = demand_df["Sub_Weights"].dropna().values
    return np.repeat(weights / 168, 168)


def select_columns(df, zone, tech_keywords=None):
    """
    Select generation columns by zone and optional tech filters.
    Excludes storage / charging by default.
    """
    cols = df.columns.str.contains(zone, case=False)

    if tech_keywords is not None:
        tech_mask = df.columns.str.contains("|".join(tech_keywords), case=False)
        cols = cols & tech_mask

    storage_mask = df.columns.str.contains("stor|batt|charge", case=False)
    cols = cols & ~storage_mask

    return df.columns[cols]


def compute_period_metrics(case_dir, period):
    """
    Compute NJ load, generation, clean generation,
    production clean share, and consumption clean share.
    """

    power_path = os.path.join(
        case_dir, f"results/results_p{period}/power.csv"
    )
    demand_path = os.path.join(
        case_dir, f"inputs/inputs_p{period}/TDR_results/Demand_data.csv"
    )

    power = pd.read_csv(power_path, index_col=0)
    demand = pd.read_csv(demand_path)

    hourly_weights = build_hourly_weights(demand)

    # -------------------------
    # Load
    # -------------------------
    load = (demand[NJ_DEMAND_COL].values * hourly_weights).sum()

    # -------------------------
    # Generation (production)
    # -------------------------
    total_cols = select_columns(power, NJ_ZONE)
    clean_cols = select_columns(power, NJ_ZONE, CLEAN_TECH_KEYWORDS)

    hourly_rows = len(hourly_weights)

    gen_hourly = power.iloc[:hourly_rows]

    total_generation = (
        gen_hourly[total_cols].sum(axis=1).values
        * hourly_weights
    ).sum()

    clean_generation = (
        gen_hourly[clean_cols].sum(axis=1).values
        * hourly_weights
    ).sum()


    production_clean_fraction = (
        clean_generation / total_generation
        if total_generation > 0 else 0
    )

    # -------------------------
    # Consumption accounting
    # -------------------------
    clean_serving_load = min(clean_generation, load)
    consumption_clean_fraction = clean_serving_load / load

    return {
        f"Total_NJ_Load_p{period}": load,
        f"Total_NJ_Generation_p{period}": total_generation,
        f"NJ_Clean_Generation_p{period}": clean_generation,
        f"Production_Clean_Fraction_p{period}": production_clean_fraction,
        f"Consumption_Clean_Fraction_p{period}": consumption_clean_fraction,
    }


# =====================================================
# MAIN
# =====================================================

def main():
    rows = []

    for case_dir in CASE_DIRS:
        if not os.path.isdir(case_dir):
            print(f"⚠ Skipping missing case: {case_dir}")
            continue

        case_name = os.path.basename(os.path.normpath(case_dir))
        row = {"CaseName": case_name}

        print(f"Processing {case_name}")

        for p in PERIODS:
            metrics = compute_period_metrics(case_dir, p)
            row.update(metrics)

        rows.append(row)

    df_out = pd.DataFrame(rows)
    df_out = df_out.round(4)

    df_out.to_csv(OUTFILE, index=False)
    print(f"\n✓ Wrote output to {OUTFILE}")


if __name__ == "__main__":
    main()