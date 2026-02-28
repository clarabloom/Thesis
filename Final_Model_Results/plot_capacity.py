import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

BASE_PATH = "Final_Model_Results/BASE"
FIG_PATH = os.path.join(BASE_PATH, "FIGURES")

# ***********************
# CUSTOMIZE COLORS HERE
# ***********************

CASE_LABELS = {
    "lownuclear_base":                    "Base",
    "lownuclear_ces":                     "CES",
    "lownuclear_cesccs":                  "CES + CCS",
    "lownuclear_cesccstech":              "CES + CCS + Renewable Tech",
    "lownuclear_cesccstechnuc35":         "CES + CCS + RenewableTech + 2035 Nuclear",
    "lownuclear_cesccstechnuc45":         "CES + CCS + Renewable Tech + 2045 Nuclear",
    "lownuclear_cesccstechret":           "CES + CCS + Renewable Tech + Retirement",
    "lownuclear_cesincccstechinstate":    "CES + Incremental In-State CCS + Renewable Tech",
    "lownuclear_cesincccstech":           "CES + Incremental CCS + Tech",
    "lownuclear_cesinstate50":            "CES w/ 50% In-state",

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

    "highambition_base":                    "Base",
    "highambition_ces":                     "CES",
    "highambition_cesccs":                  "CES + CCS",
    "highambition_cesccstech":              "CES + CCS + Renewable Tech",
    "highambition_cesccstechnuc35":         "CES + CCS + Renewable Tech + 2035 Nuclear",
    "highambition_cesccstechnuc45":         "CES + CCS + Renewable Tech + 2045 Nuclear",
    "highambition_cesccstechret":           "CES + CCS + Renewable Tech + Retirement",
    "highambition_cesincccstechinstate":    "CES + Incremental In-State CCS + Renewable Tech",
    "highambition_cesincccstech":           "CES + Incremental CCS + Tech",
    "highambition_cesinstate50":            "CES w/ 50% In-state",

    "lowambition_base":                    "Base",
    "lowambition_ces":                     "CES",
    "lowambition_cesccs":                  "CES + CCS",
    "lowambition_cesccstech":              "CES + CCS + Renewable Tech",
    "lowambition_cesccstechnuc35":         "CES + CCS + Renewable Tech + 2035 Nuclear",
    "lowambition_cesccstechnuc45":         "CES + CCS + Renewable Tech + 2045 Nuclear",
    "lowambition_cesccstechret":           "CES + CCS + Renewable Tech + Retirement",
    "lowambition_cesincccstechinstate":    "CES + Incremental In-State CCS + Renewable Tech",
    "lowambition_cesincccstech":           "CES + Incremental CCS + Tech",
    "lowambition_cesinstate50":            "CES w/ 50% In-state",

}

TECH_COLORS = {
    "Battery_Energy":    "#8172B2",  # purple
    "Battery_Power":     "#DE8647",  # dark orange
    "Existing_Nuclear":  "#F598B8",  # light pink
    "Hydropower":        "#369CE0",  # blue
    "Minor_Techs":       "#61C272",  # green
    "Natural_Gas":       "#A8A8A8",  # gray
    "New_Nuclear":       "#EB5E78",  # bright pink
    "Solar":             "#EBBB52",  # yellow
    "Wind":              "#87D4D4",  # teal
}

# ***********************
# PLOT NJ CAPACITY
# ***********************
cap = pd.read_csv("Final_Model_Results/BASE/Capacities_by_Zone_by_Tech_by_Year_ALL_CASES.csv")

# Only NJ
cap = cap[cap["Zone"] == "NJ1"]

periods = [1, 2, 3]
cases = list(dict.fromkeys(cap["CaseName"].tolist()))

# Identify technologies
techs = sorted(list(set(
    c.split("_p")[0] for c in cap.columns if "_p" in c and not c.endswith("_p0")
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
    current_x += gap

# Convert to dataframe
stack_df = pd.DataFrame(bars)
stack_df.index = x_positions

# -----------------------------
# PLOT
# -----------------------------
fig, ax = plt.subplots(figsize=(16, 8))

# White background
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")

bottom = np.zeros(len(stack_df))
for tech in techs:
    values = stack_df[tech].values
    color = TECH_COLORS.get(tech, "#AAAAAA")  # falls back to gray if tech not in dict
    ax.bar(
        stack_df.index,
        values,
        bottom=bottom,
        width=bar_width,
        label=tech,
        color=color
    )
    bottom += values

# X ticks
ax.set_xticks(x_positions)
display_labels = [CASE_LABELS.get(l, l) for l in labels]
ax.set_xticklabels(display_labels, rotation=45, ha="right")

# Year labels centered above each group
year_labels = {1: "2030", 2: "2035", 3: "2045"}
group_centers = []
start = 0
for p in periods:
    center = np.mean(x_positions[start:start + len(cases)])
    group_centers.append(center)
    start += len(cases) + gap

fig.canvas.draw()
ymax = ax.get_ylim()[1]
for i, center in enumerate(group_centers):
    ax.text(center, ymax * 0.97,
            year_labels[periods[i]],
            ha="center", fontsize=12, fontweight="bold",
            va="top")

ax.set_ylabel("Installed Capacity (GW)")
ax.set_title("NJ Installed Capacity by Technology and Policy Case", pad=25, fontsize=13, fontweight="bold")
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig(os.path.join(FIG_PATH,
    "NJ_Capacity_Grouped_by_Period.png"), dpi=300, facecolor="#FFFFFF")
plt.show()