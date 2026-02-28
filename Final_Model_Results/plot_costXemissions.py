import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
emissions_df = pd.read_csv("/Users/clarabloom/Thesis/Final_Model_Results/BASE/Load_and_Emissions.csv")
prices_df = pd.read_csv("/Users/clarabloom/Thesis/Final_Model_Results/BASE/Prices_by_Zone_by_Year_ALL_CASES (1).csv")

# Merge on CaseName
merged = pd.merge(emissions_df, prices_df, on="CaseName").reset_index(drop=True)

CASE_LABELS = {
    "base_base":                    "Base",
    "base_ces":                     "CES",
    "base_cesccs":                  "CES + CCS",
    "base_cesccstech":              "CES + CCS + Renewable Tech",
    "base_cesccstechnuc35":         "CES + CCS + Renewable Tech + 2035 Nuclear",
    "base_cesccstechnuc45":         "CES + CCS + Renewable Tech + 2045 Nuclear",
    "base_cesccstechret":           "CES + CCS + Renewable Tech + Retirement",
    "base_cesincccstechinstate":    "CES + Incremental In-State CCS + Renewable Tech",
    "base_cesincccstech":           "CES + Incremental CCS + Tech",
    "base_cesinstate50":            "CES w/ 50% In-state",
}

colors = [
    '#48ABE8', '#F29D13', '#77B053', '#F5867F', '#9368B3',
    '#9E5139', '#F291C7', '#393E41', '#B7C480', '#7CC5CC'
]

# Plot
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")

for i, row in merged.iterrows():
    color = colors[i % len(colors)]
    display_name = CASE_LABELS.get(row['CaseName'], row['CaseName'])
    ax.scatter(row["Total_System_Emissions_p3"], row["Total_Price_p3"],
               s=100, color=color, zorder=3,
               label=f"{display_name}")
    
# Trendline
x = merged["Total_System_Emissions_p3"].values
y = merged["Total_Price_p3"].values
m, b = np.polyfit(x, y, 1)
x_line = np.linspace(x.min(), x.max(), 100)
y_line = m * x_line + b

ax.plot(x_line, y_line, color="gray", linewidth=1.5, linestyle="--", zorder=1)
                                        
# Arrow at the end of the trendline
ax.annotate("",
            xy=(x_line[-1], y_line[-1]),           # arrowhead
            xytext=(x_line[-2], y_line[-2]),      # arrow tail
            arrowprops=dict(arrowstyle="-|>", color="gray", lw=1.5))

ax.set_xlabel("Total System Emissions (metric tons CO2)", fontsize=12)
ax.set_ylabel("Total Price ($/MWh)", fontsize=12)
ax.set_title("System Emissions vs. Total Energy Price (2045)", fontsize=13, fontweight="bold")
ax.grid(linestyle="--", alpha=0.4)

ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0)

plt.tight_layout()
plt.savefig("/Users/clarabloom/Thesis/Final_Model_Results/BASE/figures/Emissions_vs_Costs.png",
            dpi=300, bbox_inches="tight")
plt.show()