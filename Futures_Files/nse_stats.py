import pandas as pd

# ============================
# SETTINGS
# ============================

INPUT_FILE = "ALL_CASE_NSE.csv"
OUTPUT_FILE = "BASE_NSE_SUMMARY.csv"

CORE_CASES = [
    "base",
    "ces",
    "cesinstate50",
    "cesccs",
    "cesincccs",
    "cesccsret",
    "cesccstechnuc35"
]

# ============================
# HELPERS
# ============================

def split_case(case):
    if "_" in case:
        scenario, policy = case.split("_", 1)
    else:
        scenario, policy = "base", case
    return scenario, policy


# ============================
# MAIN
# ============================

def main():

    df = pd.read_csv(INPUT_FILE)

    # Extract scenario + policy
    df[["ScenarioClean", "Policy"]] = df["CaseName"].apply(
        lambda x: pd.Series(split_case(x))
    )

    # Keep only base future
    df = df[df["ScenarioClean"] == "base"]

    # Keep only core policies
    df = df[df["Policy"].isin(CORE_CASES)]

    # ============================
    # SELECT + CLEAN COLUMNS
    # ============================

    cols = [
        "Policy",
        "NSE_MWh_System_p1",
        "NSE_MWh_System_p2",
        "NSE_MWh_System_p3",
        "NSE_pct_System_p1",
        "NSE_pct_System_p2",
        "NSE_pct_System_p3",
    ]

    df_out = df[cols].copy()

    # Convert % to percent scale
    for col in df_out.columns:
        if "pct" in col:
            df_out[col] = df_out[col] * 100

    # Sort nicely
    df_out = df_out.sort_values("Policy")

    # ============================
    # PRINT SUMMARY
    # ============================

    print("\n=== BASE FUTURE NSE SUMMARY ===\n")

    print(df_out.to_string(index=False, float_format="%.4f"))

    # ============================
    # ADD AGGREGATE STATS
    # ============================

    print("\n=== AGGREGATE STATISTICS ===\n")

    for period in ["p1", "p2", "p3"]:
        pct_col = f"NSE_pct_System_{period}"
        mwh_col = f"NSE_MWh_System_{period}"

        print(f"{period.upper()}:")

        # --- Percent NSE ---
        mean_pct = df_out[pct_col].mean()
        std_pct  = df_out[pct_col].std()

        print(f"  Mean NSE (%): {mean_pct:.4f}")
        print(f"  Std  NSE (%): {std_pct:.4f}")
        print(f"  Max  NSE (%): {df_out[pct_col].max():.4f}")
        print(f"  Min  NSE (%): {df_out[pct_col].min():.4f}")

        # --- MWh NSE ---
        mean_mwh = df_out[mwh_col].mean()
        std_mwh  = df_out[mwh_col].std()

        print(f"  Mean NSE (MWh): {mean_mwh:.2f}")
        print(f"  Std  NSE (MWh): {std_mwh:.2f}")

        # --- Worst case ---
        worst_policy = df_out.loc[df_out[pct_col].idxmax(), "Policy"]
        print(f"  Worst policy: {worst_policy}")

        print("")

    # ============================
    # SAVE
    # ============================

    df_out.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved summary to {OUTPUT_FILE}")

def compare_nse_across_futures():

    df = pd.read_csv(INPUT_FILE)

    # Extract scenario + policy
    df[["ScenarioClean", "Policy"]] = df["CaseName"].apply(
        lambda x: pd.Series(split_case(x))
    )

    # Keep only core policies
    df = df[df["Policy"].isin(CORE_CASES)]

    # Convert % to percent scale
    for col in df.columns:
        if "NSE_pct_System" in col:
            df[col] = df[col] * 100

    print("\n=== NSE COMPARISON ACROSS FUTURES ===\n")

    results = []

    for scenario, group in df.groupby("ScenarioClean"):

        row = {"Scenario": scenario}

        for period in ["p1", "p2", "p3"]:
            pct_col = f"NSE_pct_System_{period}"
            mwh_col = f"NSE_MWh_System_{period}"

            if pct_col not in group.columns:
                continue

            row[f"{period}_mean_pct"] = group[pct_col].mean()
            row[f"{period}_std_pct"]  = group[pct_col].std()
            row[f"{period}_max_pct"]  = group[pct_col].max()
            row[f"{period}_min_pct"]  = group[pct_col].min()

            row[f"{period}_mean_mwh"] = group[mwh_col].mean()
            row[f"{period}_std_mwh"]  = group[mwh_col].std()

        results.append(row)

    results_df = pd.DataFrame(results)

    # Sort for readability
    results_df = results_df.sort_values("Scenario")

    print(results_df.to_string(index=False, float_format="%.4f"))

    # Save
    results_df.to_csv("NSE_COMPARISON_ACROSS_FUTURES.csv", index=False)

    print("\nSaved to NSE_COMPARISON_ACROSS_FUTURES.csv")


if __name__ == "__main__":
    main()
    compare_nse_across_futures()