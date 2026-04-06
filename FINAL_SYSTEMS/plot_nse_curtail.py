import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============================
# SETTINGS
# ============================

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


def build_grouped_positions(pivot, group_gap=2):
    x_positions = []
    labels = []
    scenario_centers = []

    current_x = 0

    for scenario, group in pivot.groupby(level=0):
        group_start = current_x

        for policy in group.index.get_level_values(1):
            x_positions.append(current_x)
            labels.append(policy)
            current_x += 1

        group_end = current_x - 1
        scenario_centers.append((group_start + group_end) / 2)

        current_x += group_gap

    return x_positions, labels, scenario_centers


def plot_grouped_bars(pivot, ylabel, title):
    pivot_reset = pivot.reset_index(drop=True)

    x_positions, labels, scenario_centers = build_grouped_positions(pivot)

    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(16, 6))

    for i, p in enumerate(["p1", "p2", "p3"]):
        if p in pivot.columns:
            ax.bar(
                [x + i * bar_width for x in x_positions],
                pivot_reset[p],
                bar_width,
                label=p
            )

    ax.set_xticks([x + bar_width for x in x_positions])
    ax.set_xticklabels(labels, rotation=45, ha="right")

    # Vertical separators
    for center in scenario_centers[:-1]:
        ax.axvline(center + 0.5, linestyle="--", alpha=0.3)

    # Scenario labels
    ymax = ax.get_ylim()[1]
    for center, scenario in zip(scenario_centers, pivot.index.levels[0]):
        ax.text(center, ymax * 0.9, scenario, ha='center', fontsize=7)

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(title="Period")

    plt.tight_layout()
    plt.show()


# ============================
# CURTAILMENT PLOT (FIXED)
# ============================

def plot_curtailment_pct():

    df = pd.read_csv("ALL_CASE_CURTAILMENT_RE.csv")

    df[["ScenarioClean", "Policy"]] = df["CaseName"].apply(
        lambda x: pd.Series(split_case(x))
    )

    df = df[df["ScenarioClean"] == "base"]

    df = df[df["Policy"].isin(CORE_CASES)]
    df = df.sort_values(["ScenarioClean", "Policy"])

    # Reshape
    pct_cols = [
        "Curtailment_pct_RE_p1",
        "Curtailment_pct_RE_p2",
        "Curtailment_pct_RE_p3"
    ]

    df_long = df.melt(
        id_vars=["ScenarioClean", "Policy"],
        value_vars=pct_cols,
        var_name="Period",
        value_name="Curtailment_pct_RE"
    )

    df_long["Period"] = df_long["Period"].str.replace("Curtailment_pct_RE_", "")

    pivot = df_long.pivot_table(
        index=["ScenarioClean", "Policy"],
        columns="Period",
        values="Curtailment_pct_RE"
    )

    # Convert to %
    pivot = pivot * 100

    plot_grouped_bars(
        pivot,
        ylabel="Curtailment (% of Renewable Generation)",
        title="Curtailment Efficiency by Scenario and Policy"
    )

def plot_lds_vs_base_curtailment():

    df = pd.read_csv("ALL_CASE_CURTAILMENT_RE.csv")

    # Extract scenario + policy
    df[["ScenarioClean", "Policy"]] = df["CaseName"].apply(
        lambda x: pd.Series(split_case(x))
    )

    df = df[df["Policy"].isin(CORE_CASES)]

    # Keep only base and lds
    df = df[df["ScenarioClean"].isin(["base", "lds"])]

    # Focus on p3 (most important)
    df_plot = df[[
        "ScenarioClean",
        "Policy",
        "Curtailment_pct_RE_p3"
    ]].copy()

    # Pivot for side-by-side comparison
    pivot = df_plot.pivot(
        index="Policy",
        columns="ScenarioClean",
        values="Curtailment_pct_RE_p3"
    )

    # Convert to %
    pivot = pivot * 100

    # Plot
    x = np.arange(len(pivot.index))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.bar(x - width/2, pivot["base"], width, label="Base")
    ax.bar(x + width/2, pivot["lds"], width, label="LDS")

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=45, ha="right")

    ax.set_ylabel("Curtailment (% of Renewable Generation)")
    ax.set_title("Base vs LDS Curtailment (2045)")

    ax.legend()

    plt.tight_layout()
    plt.show()

# ============================
# NSE PLOT (GROUPED)
# ============================

def plot_nse():

    df = pd.read_csv("ALL_CASE_NSE.csv")

    df[["ScenarioClean", "Policy"]] = df["CaseName"].apply(
        lambda x: pd.Series(split_case(x))
    )

    df = df[df["Policy"].isin(CORE_CASES)]
    df = df.sort_values(["ScenarioClean", "Policy"])

    df = df[df["ScenarioClean"] == "base"]

    # Reshape NSE %
    nse_cols = [
        "NSE_pct_System_p1",
        "NSE_pct_System_p2",
        "NSE_pct_System_p3"
    ]

    df_long = df.melt(
        id_vars=["ScenarioClean", "Policy"],
        value_vars=nse_cols,
        var_name="Period",
        value_name="NSE_pct"
    )

    df_long["Period"] = df_long["Period"].str.replace("NSE_pct_System_", "")

    pivot = df_long.pivot_table(
        index=["ScenarioClean", "Policy"],
        columns="Period",
        values="NSE_pct"
    )

    # Convert to %
    pivot = pivot * 100

    plot_grouped_bars(
        pivot,
        ylabel="NSE (% of Load)",
        title="System Reliability (NSE) by Scenario and Policy"
    )


# ============================
# NSE vs EMISSIONS SCATTER
# ============================

def plot_nse_vs_emissions():

    nse = pd.read_csv("ALL_CASE_NSE.csv")
    emis = pd.read_csv("FINAL_SYSTEMS/ALL_CASE_load_emissions.csv")

    # Merge on CaseName
    df = nse.merge(emis, on="CaseName", how="inner")

    # Use p3 (2045)
    x = df["Total_System_Emissions_p3"]
    y = df["NSE_pct_System_p3"] * 100

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y)

    # Label a few points (optional)
    for i in range(len(df)):
        if i % 5 == 0:
            plt.text(x.iloc[i], y.iloc[i], df["CaseName"].iloc[i], fontsize=6)

    plt.xlabel("System Emissions (p3)")
    plt.ylabel("NSE (% of Load)")
    plt.title("Reliability vs Emissions (2045)")

    plt.tight_layout()
    plt.show()


# ============================
# MAIN
# ============================

if __name__ == "__main__":
    plot_curtailment_pct()
    plot_nse()
    plot_nse_vs_emissions()
    plot_lds_vs_base_curtailment()