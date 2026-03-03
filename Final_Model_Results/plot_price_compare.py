import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("/Users/clarabloom/Thesis/Final_Model_Results/BASE/Prices_by_Zone_by_Year_ALL_CASES (1).csv")

# Cases and display titles
cases = {
    "base_base":     "Base",
    "base_cesccs":   "CES + CCS",
    "base_cesccstechret": "CES + CCS + Renewable Tech + Retirement",
    "base_cesincccstech": "CES + Incremental CCS + Tech",
}

years = [2030, 2035, 2045]

price_components = {
    "PJM Capacity Price":    ("PJM_Capacity_Price_p1",    "PJM_Capacity_Price_p2",    "PJM_Capacity_Price_p3"),
    "NJ Clean Capacity Price": ("NJ_Clean_Capacity_Price_p1", "NJ_Clean_Capacity_Price_p2", "NJ_Clean_Capacity_Price_p3"),
}

colors = {
    "PJM Capacity Price":      "#F29D13",
    "NJ Clean Capacity Price": "#77B053",
}

line_styles = {
    "PJM Capacity Price":      "--",
    "NJ Clean Capacity Price": "-",
}

fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharey=True)
axes = axes.flatten()
fig.patch.set_facecolor("#FFFFFF")

for ax, (case_name, case_title) in zip(axes, cases.items()):
    row = df[df["CaseName"] == case_name].iloc[0]
    ax.set_facecolor("#FFFFFF")

    for label, (c1, c2, c3) in price_components.items():
        values = [row[c1], row[c2], row[c3]]
        ax.plot(years, values,
                label=label,
                color=colors[label],
                linestyle=line_styles[label],
                marker="o",
                linewidth=2,
                markersize=7)

    ax.set_title(case_title, fontsize=9, fontweight="bold")
    ax.set_xticks(years)
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Price ($/MWh)", fontsize=11)
    ax.grid(linestyle="--", alpha=0.4)
    ax.legend(fontsize=9)

fig.suptitle("State and Regional Capacity Prices by Case", fontsize=15, fontweight="bold", y=0.98)
plt.tight_layout()
plt.subplots_adjust(top=0.88)
plt.savefig('/Users/clarabloom/Thesis/Final_Model_Results/BASE/FIGURES/NJ_Price_Compare.png', dpi=150)
plt.show()