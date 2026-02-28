import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

BASE_PATH = "/Users/clarabloom/Thesis/Final_Model_Results/BASE"
FIG_PATH = os.path.join(BASE_PATH, "figures")

# ***********************
# PLOT NJ COSTS
# ***********************

df = pd.read_csv(os.path.join(BASE_PATH, "Costs_by_Case_and_Period_ALL_CASES.csv"))

df_long = df.melt(
    id_vars="CaseName",
    value_vars=["NJ_Cost_p1", "NJ_Cost_p2", "NJ_Cost_p3"],
    var_name="Period",
    value_name="Cost"
)

df_long["Period"] = df_long["Period"].str.extract(r"p(\d)").astype(int)
df_long["Cost_Billions"] = df_long["Cost"] / 1e9

plt.figure(figsize=(8,5))

for case in df_long["CaseName"].unique():
    subset = df_long[df_long["CaseName"] == case]
    plt.plot(subset["Period"], subset["Cost_Billions"], marker="o", label=case)

plt.xlabel("Planning Period")
plt.ylabel("NJ Cost (Billion $)")
plt.title("NJ Cost by Case and Planning Period")
plt.xticks([1,2,3])
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(os.path.join(FIG_PATH, "NJ_Cost_by_Case_and_Period.png"), dpi=300)
plt.show()

# ***********************
# PLOT NJ CAPACITY
# ***********************

cap = pd.read_csv(os.path.join(BASE_PATH,
        "Capacities_by_Zone_by_Tech_by_Year_ALL_CASES (4).csv"))

# Only NJ
cap = cap[cap["Zone"] == "NJ1"]

periods = [1, 2, 3]
cases = sorted(cap["CaseName"].unique())

# Identify technologies
techs = sorted(list(set(
    c.split("_p")[0] for c in cap.columns if "_p" in c
)))

# Remove techs that are zero everywhere
def tech_has_capacity(tech):
    for p in periods:
        col = f"{tech}_p{p}"
        if col in cap.columns and cap[col].sum() > 0:
            return True
    return False

techs = [t for t in techs if tech_has_capacity(t)]

# -----------------------------
# BUILD DATA STRUCTURE
# -----------------------------

bars = []
labels = []
x_positions = []

gap = 2
bar_width = 0.8
current_x = 0

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
    
    current_x += gap  # add space between periods

# Convert to dataframe
stack_df = pd.DataFrame(bars)
stack_df.index = x_positions

# -----------------------------
# PLOT
# -----------------------------

fig, ax = plt.subplots(figsize=(16,8))

# Background color
fig.patch.set_facecolor("#F7F7F7")
ax.set_facecolor("#FFFFFF")

bottom = np.zeros(len(stack_df))

for tech in techs:
    values = stack_df[tech].values
    ax.bar(
        stack_df.index,
        values,
        bottom=bottom,
        width=bar_width,
        label=tech
    )
    bottom += values

# X ticks
ax.set_xticks(x_positions)
ax.set_xticklabels(labels, rotation=45, ha="right")

# Period labels centered above groups
group_centers = []
start = 0
for p in periods:
    center = np.mean(x_positions[start:start+len(cases)])
    group_centers.append(center)
    start += len(cases) + gap

for i, center in enumerate(group_centers):
    ax.text(center, ax.get_ylim()[1]*1.02,
            f"Period {periods[i]}",
            ha="center", fontsize=12, fontweight="bold")

ax.set_ylabel("Installed Capacity (GW)")
ax.set_title("NJ Installed Capacity by Technology and Policy Case")

ax.legend(bbox_to_anchor=(1.02,1), loc="upper left")

plt.tight_layout()
plt.savefig(os.path.join(FIG_PATH,
            "NJ_Capacity_Grouped_by_Period.png"), dpi=300)
plt.show()

# ***********************
# PLOT NJ GENERATION
# ***********************

gen = pd.read_csv(os.path.join(
    BASE_PATH,
    "In_State_Generation_and_Consumption (3).csv"
))

cases = sorted(gen["CaseName"].unique())
periods = [1, 2, 3]

# Optional: highlight baseline
BASELINE_CASE = "base_base"

# Manual case colors (edit as desired)
case_colors = {
    "base_base": "#000000",
    "base_cesccs": "#1F77B4",
    "base_cesccstech": "#2CA02C",
    "base_cesccstechret": "#FF7F0E",
    "base_cesincccstech": "#9467BD",
    "base_cesincccstechinstate": "#D62728"
}

plt.figure(figsize=(9,6))

for case in cases:
    subset = gen[gen["CaseName"] == case]
    
    values = [
        subset[f"NJ_Total_Clean_Consumption_fraction_p{p}"].values[0] * 100
        for p in periods
    ]
    
    linewidth = 3 if case == BASELINE_CASE else 1.8
    linestyle = "-" if case == BASELINE_CASE else "--"
    
    plt.plot(
        periods,
        values,
        marker="o",
        linewidth=linewidth,
        linestyle=linestyle,
        label=case,
        color=case_colors.get(case, "#555555")
    )

plt.xlabel("Planning Period")
plt.ylabel("NJ Clean Consumption (%)")
plt.title("NJ Clean Consumption Fraction by Case")
plt.xticks([1,2,3])
plt.ylim(0,100)
plt.grid(True, linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()

plt.savefig(os.path.join(
    FIG_PATH,
    "NJ_Clean_Consumption_Fraction_by_Case.png"
), dpi=300)

plt.show()

# ***********************
# PLOT System EMISSIONS
# ***********************

emis = pd.read_csv("/Users/clarabloom/Thesis/Final_Model_Results/BASE/Load_and_Emissions (5).csv")

plt.figure()

for case in emis["CaseName"].unique():
    subset = emis[emis["CaseName"] == case]
    
    plt.plot([1,2,3],
             [subset["Total_System_Emissions_p1"].values[0],
              subset["Total_System_Emissions_p2"].values[0],
              subset["Total_System_Emissions_p3"].values[0]],
             marker="o",
             label=case)

plt.xlabel("Planning Period")
plt.ylabel("Total System Emissions (tons)")
plt.title("System Emissions by Case")
plt.xticks([1,2,3])
plt.legend()
plt.grid(True)

# save figure to base > figures folder
plt.savefig("/Users/clarabloom/Thesis/Final_Model_Results/BASE/figures/System_Emis_by_Case_and_Period.png", dpi=300)
plt.show()

# ***********************
# PLOT NJ EMISSIONS
# ***********************
plt.figure()

for case in emis["CaseName"].unique():
    subset = emis[emis["CaseName"] == case]
    
    plt.plot([1,2,3],
             [subset["Total_NJ_Emissions_p1"].values[0],
              subset["Total_NJ_Emissions_p2"].values[0],
              subset["Total_NJ_Emissions_p3"].values[0]],
             marker="o",
             label=case)

plt.xlabel("Planning Period")
plt.ylabel("NJ Emissions (tons)")
plt.title("NJ Emissions by Case")
plt.xticks([1,2,3])
plt.legend()
plt.grid(True)

# save figure to base > figures folder
plt.savefig("/Users/clarabloom/Thesis/Final_Model_Results/BASE/figures/NJ_Emis_by_Case_and_Period.png", dpi=300)
plt.show()

