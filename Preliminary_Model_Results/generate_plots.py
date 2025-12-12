import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')

# Define time periods
periods = ['2030', '2035', '2045']
period_labels = ['p1', 'p2', 'p3']

# Define case name mapping
case_name_mapping = {
    'Basecase_RGGI': 'Baseline',
    'Updated_RGGI_noOOS_noninc': 'CES + CCS',
    'Updated_RGGI_procurement_noOOS_noninc': 'CES + CCS + Tech. Procurement',
    'Updated_RGGI_procurement_noOOS_inc': 'CES + Incremental CCS + Tech. Procurement'
}

def rename_case(case_name):
    """Rename case according to mapping"""
    return case_name_mapping.get(case_name, case_name)

# ===================================================================
# ************************ 1. LINE CHART: COSTS ************************
# ===================================================================

print("Generating costs line chart...")

# Load costs data
df_costs = pd.read_csv("Preliminary_Model_Results/Costs_by_Zone_by_Year_ALL_CASES.csv")

# Extract total price columns
cost_cols = ['Total_Price_p1', 'Total_Price_p2', 'Total_Price_p3']

# Create line chart
fig, ax = plt.subplots(figsize=(10, 6))
for idx, row in df_costs.iterrows():
    case_name = rename_case(row['CaseName'])
    costs = [row[col] for col in cost_cols]
    ax.plot(periods, costs, marker='o', linewidth=2, markersize=8, label=case_name)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Total System Costs ($)', fontsize=12)
ax.set_title('Total System Costs Over Time', fontsize=14, fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('costs_line_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: costs_line_chart.png")

# ===================================================================
# **************** 2. LINE CHARTS: EMISSIONS ****************
# ===================================================================

print("Generating emissions line charts...")

# Load emissions data
df_emissions = pd.read_csv("Preliminary_Model_Results/Load_and_Emissions.csv")

# Total System Emissions
total_emission_cols = [
    "Total_System_Emissions_p1",
    "Total_System_Emissions_p2",
    "Total_System_Emissions_p3"
]

fig, ax = plt.subplots(figsize=(10, 6))
for idx, row in df_emissions.iterrows():
    case_name = rename_case(row['CaseName'])
    emissions = [row[col] for col in total_emission_cols]
    ax.plot(periods, emissions, marker='o', linewidth=2, markersize=8, label=case_name)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Total System Emissions (tons CO2)', fontsize=12)
ax.set_title('Total System Emissions Over Time', fontsize=14, fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('total_emissions_line_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: total_emissions_line_chart.png")

# NJ Emissions
nj_emission_cols = [
    "Total_NJ_Emissions_p1",
    "Total_NJ_Emissions_p2",
    "Total_NJ_Emissions_p3"
]

fig, ax = plt.subplots(figsize=(10, 6))
for idx, row in df_emissions.iterrows():
    case_name = rename_case(row['CaseName'])
    emissions = [row[col] for col in nj_emission_cols]
    ax.plot(periods, emissions, marker='o', linewidth=2, markersize=8, label=case_name)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('NJ Emissions (tons CO2)', fontsize=12)
ax.set_title('NJ Emissions Over Time', fontsize=14, fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('nj_emissions_line_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: nj_emissions_line_chart.png")

# ===================================================================
# ********** 3. GROUPED BAR CHART: CAPACITY BY RESOURCE (2045) **********
# ===================================================================

print("Generating capacity grouped bar chart for 2045...")

# Load capacity data
df_capacity = pd.read_csv("Preliminary_Model_Results/Capacities_by_Zone_by_Tech_by_Year_ALL_CASES.csv")

# Sum across zones for each case
df_capacity_summed = df_capacity.groupby("CaseName").sum(numeric_only=True).reset_index()

# Extract only p3 (2045) columns
p3_cols = [col for col in df_capacity_summed.columns if col.endswith('_p3')]

# Extract technology names
tech_names = [col.replace('_p3', '') for col in p3_cols]

# Prepare data for grouped bar chart
cases = df_capacity_summed['CaseName'].tolist()
renamed_cases = [rename_case(case) for case in cases]
n_cases = len(cases)
n_techs = len(tech_names)

# Create grouped bar chart
fig, ax = plt.subplots(figsize=(14, 7))

x = np.arange(n_techs)
width = 0.8 / n_cases

for i, (case, renamed_case) in enumerate(zip(cases, renamed_cases)):
    case_row = df_capacity_summed[df_capacity_summed['CaseName'] == case].iloc[0]
    values = [case_row[col] for col in p3_cols]
    ax.bar(x + i * width, values, width, label=renamed_case)

ax.set_xlabel('Resource Type', fontsize=12)
ax.set_ylabel('Capacity (MW)', fontsize=12)
ax.set_title('Capacity by Resource Type in 2045', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * (n_cases - 1) / 2)
ax.set_xticklabels(tech_names, rotation=45, ha='right')
ax.legend(loc='best')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('capacity_grouped_bar_chart_2045.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: capacity_bar_chart_2045.png")


# ===================================================================
# ********* 4. LINE CHART: NJ CLEAN CONSUMPTION FRACTION *********
# ===================================================================

print("Generating NJ clean consumption fraction line chart...")

# Load generation data
df_generation = pd.read_csv("Preliminary_Model_Results/In_State_Generation_and_Consumption.csv")

# Extract clean consumption fraction columns
clean_consumption_cols = [
    'NJ_In-State_Clean_Consumption_fraction_p1',
    'NJ_In-State_Clean_Consumption_fraction_p2',
    'NJ_In-State_Clean_Consumption_fraction_p3'
]

# Create line chart
fig, ax = plt.subplots(figsize=(10, 6))
for idx, row in df_generation.iterrows():
    case_name = rename_case(row['CaseName'])
    fractions = [row[col] for col in clean_consumption_cols]
    ax.plot(periods, fractions, marker='o', linewidth=2, markersize=8, label=case_name)

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('NJ In-State Clean Consumption Fraction', fontsize=12)
ax.set_title('NJ In-State Clean Consumption Fraction Over Time', fontsize=14, fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('nj_clean_consumption_fraction_line_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: nj_clean_consumption_fraction_line_chart.png")

print("\n" + "="*70)
print("All visualizations generated successfully!")
print("="*70)
print("\nGenerated files:")
print("  1. costs_line_chart.png")
print("  2. total_emissions_line_chart.png")
print("  3. nj_emissions_line_chart.png")
print("  4. capacity_grouped_bar_chart_2045.png")
print("  5. nj_clean_consumption_fraction_line_chart.png")