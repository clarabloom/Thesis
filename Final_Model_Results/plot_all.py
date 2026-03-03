import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# ********************************
# CONFIGURATION
# ********************************

FUTURES_BASE = "/Users/clarabloom/Thesis/Final_Model_Results/Future_Scenarios"

SCENARIOS = [
    # "HIGHEST_AMBITION",
    # "HIGH_AMBITION",
    # "LOW_AMBITION",
    # "HIGH_DEMAND",
    # "LOW_DEMAND",
    # "HIGH_NG",
    # "LOW_NG",
    "HIGH_NUCLEAR",
    "LOW_NUCLEAR",
    # "HIGH_SOLAR",
    # "LOW_SOLAR",
]

TECH_COLORS = {
    "Battery_Energy":   "#8172B2",
    "Battery_Power":    "#DE8647",
    "Existing_Nuclear": "#F598B8",
    "Hydropower":       "#369CE0",
    "Minor_Techs":      "#61C272",
    "Natural_Gas":      "#A8A8A8",
    "New_Nuclear":      "#EB5E78",
    "Solar":            "#EBBB52",
    "Wind":             "#87D4D4",
}

DOT_COLORS = [
    '#48ABE8', '#F29D13', '#77B053', '#F5867F', '#9368B3',
    '#9E5139', '#F291C7', '#393E41', '#B7C480', '#7CC5CC'
]

PRICE_COMPONENTS = {
    "PJM Capacity Price":      ("PJM_Capacity_Price_p1",     "PJM_Capacity_Price_p2",     "PJM_Capacity_Price_p3"),
    "NJ Clean Capacity Price": ("NJ_Clean_Capacity_Price_p1","NJ_Clean_Capacity_Price_p2","NJ_Clean_Capacity_Price_p3"),
}

PRICE_COLORS = {
    "PJM Capacity Price":      "#F29D13",
    "NJ Clean Capacity Price": "#77B053",
}

PRICE_LINE_STYLES = {
    "PJM Capacity Price":      "--",
    "NJ Clean Capacity Price": "-",
}

COMPARE_CASES_SUFFIX = ["base", "cesccs", "cesccstechret", "cesincccstech"]
COMPARE_LABELS       = ["Base", "CES + CCS", "CES + CCS + Tech + Retirement", "CES + Incremental CCS + Tech"]

YEARS = [2030, 2035, 2045]

# ********************************
# HELPER: build a CASE_LABELS dict
# from whatever cases are in the file
# ********************************
POLICY_LABELS = {
    "base":                 "Base",
    "ces":                  "CES",
    "cesccs":               "CES + CCS",
    "cesccstech":           "CES + CCS + Renewable Tech",
    "cesccstechnuc35":      "CES + CCS + Renewable Tech + 2035 Nuclear",
    "cesccstechnuc45":      "CES + CCS + Renewable Tech + 2045 Nuclear",
    "cesccstechret":        "CES + CCS + Renewable Tech + Retirement",
    "cesincccstechinstate": "CES + Incremental In-State CCS + Renewable Tech",
    "cesincccstech":        "CES + Incremental CCS + Tech",
    "cesinstate50":         "CES w/ 50% In-state",
}

def make_case_labels(cases):
    """Build display labels by stripping the scenario prefix."""
    out = {}
    for c in cases:
        parts = c.split("_", 1)
        suffix = parts[1] if len(parts) > 1 else c
        out[c] = POLICY_LABELS.get(suffix, c)
    return out

# ********************************
# PLOT 1: CAPACITY STACKED BAR
# ********************************
def plot_capacity(cap_path, fig_path, scenario):
    cap = pd.read_csv(cap_path)
    cap = cap[cap["Zone"] == "NJ1"]

    periods = [1, 2, 3]
    cases = list(dict.fromkeys(cap["CaseName"].tolist()))
    case_labels = make_case_labels(cases)

    techs = sorted(set(
        c.split("_p")[0] for c in cap.columns
        if "_p" in c and not c.endswith("_p0")
    ))

    def tech_has_capacity(tech):
        return any(
            f"{tech}_p{p}" in cap.columns and cap[f"{tech}_p{p}"].sum() > 0
            for p in periods
        )
    techs = [t for t in techs if tech_has_capacity(t)]

    bars, labels, x_positions = [], [], []
    gap, bar_width, current_x = 2, 0.8, 0

    for p in periods:
        for case in cases:
            case_df = cap[cap["CaseName"] == case]
            row = {}
            for tech in techs:
                col = f"{tech}_p{p}"
                row[tech] = case_df[col].values[0] / 1000 if col in case_df.columns else 0
            bars.append(row)
            labels.append(case)
            x_positions.append(current_x)
            current_x += 1
        current_x += gap

    stack_df = pd.DataFrame(bars, index=x_positions)

    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    bottom = np.zeros(len(stack_df))
    for tech in techs:
        color = TECH_COLORS.get(tech, "#AAAAAA")
        ax.bar(stack_df.index, stack_df[tech].values, bottom=bottom,
               width=bar_width, label=tech, color=color)
        bottom += stack_df[tech].values

    ax.set_xticks(x_positions)
    ax.set_xticklabels([case_labels.get(l, l) for l in labels], rotation=45, ha="right")

    year_labels = {1: "2030", 2: "2035", 3: "2045"}
    group_centers, start = [], 0
    for p in periods:
        group_centers.append(np.mean(x_positions[start:start + len(cases)]))
        start += len(cases) + gap

    fig.canvas.draw()
    ymax = ax.get_ylim()[1]
    for i, center in enumerate(group_centers):
        ax.text(center, ymax * 0.97, year_labels[periods[i]],
                ha="center", fontsize=12, fontweight="bold", va="top")

    ax.set_ylabel("Installed Capacity (GW)")
    ax.set_title(f"NJ Installed Capacity — {scenario}", pad=25, fontsize=13, fontweight="bold")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_path, "NJ_Capacity_Grouped_by_Period.png"), dpi=300,
                facecolor="#FFFFFF", bbox_inches="tight")
    plt.close()

# ********************************
# PLOT 2: EMISSIONS VS COST
# ********************************
def plot_emissions_vs_cost(emissions_path, prices_path, fig_path, scenario):
    merged = pd.merge(
        pd.read_csv(emissions_path),
        pd.read_csv(prices_path),
        on="CaseName"
    ).reset_index(drop=True)

    case_labels = make_case_labels(merged["CaseName"].tolist())

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    for i, row in merged.iterrows():
        display_name = case_labels.get(row["CaseName"], row["CaseName"])
        ax.scatter(row["Total_System_Emissions_p3"], row["Total_Price_p3"],
                   s=100, color=DOT_COLORS[i % len(DOT_COLORS)], zorder=3,
                   label=display_name)

    x = merged["Total_System_Emissions_p3"].values
    y = merged["Total_Price_p3"].values
    m, b = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = m * x_line + b
    ax.plot(x_line, y_line, color="gray", linewidth=1.5, linestyle="--", zorder=1)
    ax.annotate("", xy=(x_line[-1], y_line[-1]), xytext=(x_line[-2], y_line[-2]),
                arrowprops=dict(arrowstyle="-|>", color="gray", lw=1.5))

    ax.set_xlabel("Total System Emissions (metric tons CO2)", fontsize=12)
    ax.set_ylabel("Total Price ($/MWh)", fontsize=12)
    ax.set_title(f"System Emissions vs. Total Energy Price (2045) — {scenario}",
                 fontsize=13, fontweight="bold")
    ax.grid(linestyle="--", alpha=0.4)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0, fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_path, "Emissions_vs_Costs.png"), dpi=300, bbox_inches="tight")
    plt.close()

# ********************************
# PLOT 3: PRICE COMPARISONS
# ********************************
def plot_price_comparisons(prices_path, fig_path, scenario):
    df = pd.read_csv(prices_path)

    # Infer the prefix from whatever cases exist
    all_cases = df["CaseName"].tolist()
    prefix = all_cases[0].split("_")[0] + "_" if all_cases else ""

    compare_cases = {prefix + s: lbl for s, lbl in zip(COMPARE_CASES_SUFFIX, COMPARE_LABELS)
                     if (df["CaseName"] == prefix + s).any()}

    if len(compare_cases) < 2:
        print(f"  [!] Not enough matching cases for price comparison in {scenario}, skipping.")
        return

    n = len(compare_cases)
    ncols = 2
    nrows = (n + 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(10, 4 * nrows), sharey=True)
    axes = np.array(axes).flatten()
    fig.patch.set_facecolor("#FFFFFF")

    for ax, (case_name, case_title) in zip(axes, compare_cases.items()):
        row = df[df["CaseName"] == case_name].iloc[0]
        ax.set_facecolor("#FFFFFF")
        for label, (c1, c2, c3) in PRICE_COMPONENTS.items():
            ax.plot(YEARS, [row[c1], row[c2], row[c3]],
                    label=label, color=PRICE_COLORS[label],
                    linestyle=PRICE_LINE_STYLES[label],
                    marker="o", linewidth=2, markersize=7)
        ax.set_title(case_title, fontsize=9, fontweight="bold")
        ax.set_xticks(YEARS)
        ax.set_xlabel("Year", fontsize=11)
        ax.set_ylabel("Price ($/MWh)", fontsize=11)
        ax.grid(linestyle="--", alpha=0.4)
        ax.legend(fontsize=9)

    # Hide any unused subplots
    for ax in axes[len(compare_cases):]:
        ax.set_visible(False)

    fig.suptitle(f"State and Regional Capacity Prices — {scenario}",
                 fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.savefig(os.path.join(fig_path, "NJ_Price_Compare.png"), dpi=150, bbox_inches="tight")
    plt.close()

# ********************************
# MAIN LOOP
# ********************************
for scenario in SCENARIOS:
    scenario_path = os.path.join(FUTURES_BASE, scenario)
    fig_path      = os.path.join(scenario_path, "FIGURES")
    cap_path      = os.path.join(scenario_path, "Capacities.csv")
    emissions_path = os.path.join(scenario_path, "Emissions.csv")
    prices_path   = os.path.join(scenario_path, "Prices.csv")

    os.makedirs(fig_path, exist_ok=True)

    print(f"Processing {scenario}...")

    if os.path.exists(cap_path):
        plot_capacity(cap_path, fig_path, scenario)
        print(f"  ✓ Capacity plot saved")
    else:
        print(f"  [!] Capacities.csv not found, skipping capacity plot")

    if os.path.exists(emissions_path) and os.path.exists(prices_path):
        plot_emissions_vs_cost(emissions_path, prices_path, fig_path, scenario)
        print(f"  ✓ Emissions vs cost plot saved")
    else:
        print(f"  [!] Emissions.csv or Prices.csv not found, skipping emissions plot")

    if os.path.exists(prices_path):
        plot_price_comparisons(prices_path, fig_path, scenario)
        print(f"  ✓ Price comparison plot saved")
    else:
        print(f"  [!] Prices.csv not found, skipping price comparison plot")

print("\nDone! All figures saved.")

# ********************************
# COMPARISON GROUPS
# ********************************

COMPARISON_GROUPS = [
    {
        "name":     "Demand",
        "scenarios": ["HIGH_DEMAND", "LOW_DEMAND"],
        "labels":   ["High Demand", "Low Demand"],
    },
    {
        "name":     "Natural_Gas",
        "scenarios": ["HIGH_NG", "LOW_NG"],
        "labels":   ["High NG Price", "Low NG Price"],
    },
    {
        "name":     "Nuclear",
        "scenarios": ["HIGH_NUCLEAR", "LOW_NUCLEAR"],
        "labels":   ["High Nuclear", "Low Nuclear"],
    },
    {
        "name":     "Solar",
        "scenarios": ["HIGH_SOLAR", "LOW_SOLAR"],
        "labels":   ["High Solar", "Low Solar"],
    },
    {
        "name":     "Ambition",
        "scenarios": ["HIGHEST_AMBITION", "HIGH_AMBITION", "LOW_AMBITION"],
        "labels":   ["Highest Ambition", "High Ambition", "Low Ambition"],
    },
]

COMPARISON_OUT = "/Users/clarabloom/Thesis/Final_Model_Results/Future_Scenarios/COMPARISON_FIGURES"
os.makedirs(COMPARISON_OUT, exist_ok=True)

# ********************************
# COMPARISON PLOT: EMISSIONS VS COST
# ********************************
def plot_emissions_comparison(group):
    scenarios = group["scenarios"]
    labels    = group["labels"]
    n         = len(scenarios)

    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5), sharey=True, sharex=True)
    if n == 1:
        axes = [axes]
    fig.patch.set_facecolor("#FFFFFF")

    for ax, scenario, label in zip(axes, scenarios, labels):
        emissions_path = os.path.join(FUTURES_BASE, scenario, "Emissions.csv")
        prices_path    = os.path.join(FUTURES_BASE, scenario, "Prices.csv")

        if not os.path.exists(emissions_path) or not os.path.exists(prices_path):
            print(f"  [!] Missing files for {scenario}, skipping panel")
            ax.set_title(label + "\n(data missing)", fontsize=11)
            continue

        merged = pd.merge(
            pd.read_csv(emissions_path),
            pd.read_csv(prices_path),
            on="CaseName"
        ).reset_index(drop=True)

        case_labels = make_case_labels(merged["CaseName"].tolist())
        ax.set_facecolor("#FFFFFF")

        for i, row in merged.iterrows():
            display_name = case_labels.get(row["CaseName"], row["CaseName"])
            ax.scatter(row["Total_System_Emissions_p3"], row["Total_Price_p3"],
                       s=100, color=DOT_COLORS[i % len(DOT_COLORS)],
                       zorder=3, label=display_name)

        x = merged["Total_System_Emissions_p3"].values
        y = merged["Total_Price_p3"].values
        if len(set(x)) > 1:
            m, b   = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = m * x_line + b
            ax.plot(x_line, y_line, color="gray", linewidth=1.5, linestyle="--", zorder=1)
            ax.annotate("", xy=(x_line[-1], y_line[-1]), xytext=(x_line[-2], y_line[-2]),
                        arrowprops=dict(arrowstyle="-|>", color="gray", lw=1.5))

        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_xlabel("Total System Emissions (MT CO2)", fontsize=10)
        ax.set_ylabel("Total Price ($/MWh)", fontsize=10)
        ax.grid(linestyle="--", alpha=0.4)

    # Single shared legend using handles from the last valid axis
    handles, labels_ = ax.get_legend_handles_labels()
    fig.legend(handles, labels_, loc="lower center", fontsize=8,
               ncol=5, bbox_to_anchor=(0.5, -0.08), borderaxespad=0)

    fig.suptitle(...)

    fig.suptitle(f"Emissions vs. Energy Price (2045) — {group['name']} Comparison",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(COMPARISON_OUT, f"Comparison_{group['name']}_Emissions.png"),
                dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Emissions comparison saved for {group['name']}")

# ********************************
# COMPARISON PLOT: CAPACITY
# ********************************
def plot_capacity_comparison(group):
    scenarios = group["scenarios"]
    labels    = group["labels"]
    n         = len(scenarios)

    # Collect all cases across scenarios to build a shared y scale
    fig, axes = plt.subplots(1, n, figsize=(14 * n // 2, 7), sharey=True)
    if n == 1:
        axes = [axes]
    fig.patch.set_facecolor("#FFFFFF")

    for ax, scenario, label in zip(axes, scenarios, labels):
        cap_path = os.path.join(FUTURES_BASE, scenario, "Capacities.csv")

        if not os.path.exists(cap_path):
            print(f"  [!] Missing Capacities.csv for {scenario}, skipping panel")
            ax.set_title(label + "\n(data missing)", fontsize=11)
            continue

        cap   = pd.read_csv(cap_path)
        cap   = cap[cap["Zone"] == "NJ1"]
        cases = list(dict.fromkeys(cap["CaseName"].tolist()))
        case_labels = make_case_labels(cases)
        periods = [1, 2, 3]

        techs = sorted(set(
            c.split("_p")[0] for c in cap.columns
            if "_p" in c and not c.endswith("_p0")
        ))
        techs = [t for t in techs if any(
            cap[f"{t}_p{p}"].sum() > 0 for p in periods if f"{t}_p{p}" in cap.columns
        )]

        bars, bar_labels, x_positions = [], [], []
        gap, bar_width, current_x = 2, 0.8, 0

        for p in periods:
            for case in cases:
                case_df = cap[cap["CaseName"] == case]
                row = {tech: (case_df[f"{tech}_p{p}"].values[0] / 1000
                              if f"{tech}_p{p}" in case_df.columns else 0)
                       for tech in techs}
                bars.append(row)
                bar_labels.append(case)
                x_positions.append(current_x)
                current_x += 1
            current_x += gap

        stack_df = pd.DataFrame(bars, index=x_positions)
        ax.set_facecolor("#FFFFFF")

        bottom = np.zeros(len(stack_df))
        for tech in techs:
            color = TECH_COLORS.get(tech, "#AAAAAA")
            ax.bar(stack_df.index, stack_df[tech].values, bottom=bottom,
                   width=bar_width, label=tech, color=color)
            bottom += stack_df[tech].values

        ax.set_xticks(x_positions)
        ax.set_xticklabels([case_labels.get(l, l) for l in bar_labels],
                           rotation=45, ha="right", fontsize=7)

        year_label_map = {1: "2030", 2: "2035", 3: "2045"}
        group_centers, start = [], 0
        for p in periods:
            group_centers.append(np.mean(x_positions[start:start + len(cases)]))
            start += len(cases) + gap

        fig.canvas.draw()
        ymax = ax.get_ylim()[1]
        for i, center in enumerate(group_centers):
            ax.text(center, ymax * 0.97, year_label_map[periods[i]],
                    ha="center", fontsize=10, fontweight="bold", va="top")

        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_ylabel("Installed Capacity (GW)", fontsize=10)
        ax.grid(linestyle="--", alpha=0.4)

    # Single shared legend using handles from the last valid axis
    handles, labels_ = ax.get_legend_handles_labels()

    fig.legend(handles, labels_, loc="lower center", fontsize=8,
               ncol=5, bbox_to_anchor=(0.5, -0.12), borderaxespad=0)

    fig.suptitle(...)
    fig.suptitle(f"NJ Installed Capacity — {group['name']} Comparison",
                 fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(COMPARISON_OUT, f"Comparison_{group['name']}_Capacity.png"),
                dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Capacity comparison saved for {group['name']}")

# ********************************
# RUN COMPARISONS
# ********************************
print("\nGenerating comparison plots...")
for group in COMPARISON_GROUPS:
    print(f"\n--- {group['name']} ---")
    plot_emissions_comparison(group)
    plot_capacity_comparison(group)

print("\nAll comparison plots saved to:", COMPARISON_OUT)