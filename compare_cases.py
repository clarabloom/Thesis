import pandas as pd
import numpy as np

# ===================================================================
# ************************ COMPARE EMISSIONS ************************
# ===================================================================

print("*" * 70)
print("EMISSIONS COMPARISON:")
print("*" * 70)
print()

# Load the CSV
df = pd.read_csv("Load_and_Emissions.csv")

# Columns to compare
cols = [
    "Total_System_Emissions_p1",
    "Total_System_Emissions_p2",
    "Total_System_Emissions_p3"
]

# First row (baseline)
first = df.iloc[0]

# Loop over all rows except the first
for i in range(1, len(df)):
    case = df.loc[i, "CaseName"]
    print(f"Compared to baseline ({df.loc[0, 'CaseName']}) → {case}")
    
    for col in cols:
        pct_diff = (df.loc[i, col] - first[col]) / first[col] * 100
        print(f"  {col}: {pct_diff:.3f}%")
    print()

# ===================================================================
# ************************ COMPARE CAPACITY ************************
# ===================================================================
print()
print()
print("*" * 70)
print("CAPACITY COMPARISON:")
print("*" * 70)
print()

df = pd.read_csv("Capacities_by_Zone_by_Tech_by_Year_ALL_CASES.csv")

# Sum across zones for each case
# Group by CaseName and sum all technology_year columns
df_summed = df.groupby("CaseName").sum(numeric_only=True).reset_index()

# Columns to compare (all except CaseName)
tech_year_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# First row (baseline)
baseline_row = df_summed.iloc[0]

# Calculate percentage differences and store results
results = []
max_pct_diff = 0
max_pct_info = {}

# Loop through all cases except baseline
for i in range(1, len(df_summed)):
    case = df_summed.loc[i, "CaseName"]
    
    for col in tech_year_cols:
        baseline_val = baseline_row[col]
        case_val = df_summed.loc[i, col]
        
        # Calculate percentage difference
        if baseline_val != 0:
            pct_diff = (case_val - baseline_val) / baseline_val * 100
        else:
            # Handle division by zero
            pct_diff = np.nan if case_val == 0 else float('inf')
        
        results.append({
            "CaseName": case,
            "Technology_Year": col,
            "Baseline_Capacity": baseline_val,
            "Case_Capacity": case_val,
            "Percent_Difference": pct_diff
        })
        
        # Track maximum absolute percentage difference
        if not np.isnan(pct_diff) and not np.isinf(pct_diff):
            abs_pct_diff = abs(pct_diff)
            if abs_pct_diff > max_pct_diff:
                max_pct_diff = abs_pct_diff
                max_pct_info = {
                    "CaseName": case,
                    "Technology_Year": col,
                    "Percent_Difference": pct_diff,
                    "Baseline_Capacity": baseline_val,
                    "Case_Capacity": case_val
                }

# Create output dataframe
output_df = pd.DataFrame(results)

# Save to CSV
output_df.to_csv("capacity_percentage_differences.csv", index=False)

print(f"Total comparisons: {len(output_df)}")
print()

# Calculate summary statistics
valid_pct_diffs = output_df[
    (output_df["Percent_Difference"].notna()) & 
    (output_df["Percent_Difference"] != np.inf) &
    (output_df["Percent_Difference"] != -np.inf)
]["Percent_Difference"]


if len(valid_pct_diffs) > 0:
    mean_pct_diff = valid_pct_diffs.mean()
    median_pct_diff = valid_pct_diffs.median()
    
    print("=" * 70)
    print("SUMMARY STATISTICS:")
    print("=" * 70)
    print(f"Mean Percent Difference: {mean_pct_diff:.3f}%")
    print(f"Median Percent Difference: {median_pct_diff:.3f}%")
    print("=" * 70)
    print()

# Print largest percentage difference
if max_pct_info:
    print("=" * 70)
    print("LARGEST PERCENTAGE DIFFERENCE:")
    print("=" * 70)
    print(f"Case: {max_pct_info['CaseName']}")
    print(f"Technology_Year: {max_pct_info['Technology_Year']}")
    print(f"Baseline Capacity: {max_pct_info['Baseline_Capacity']:.2f}")
    print(f"Case Capacity: {max_pct_info['Case_Capacity']:.2f}")
    print(f"Percent Difference: {max_pct_info['Percent_Difference']:.3f}%")
    print("=" * 70)
else:
    print("No valid percentage differences found.")

# ===================================================================
# ************************ COMPARE GENERATION ************************
# ===================================================================
print()
print()
print("*" * 70)
print("GENERATION COMPARISON:")
print("*" * 70)
print()


# Load the generation and consumption CSV
df = pd.read_csv("In_State_Generation_and_Consumption.csv")

# Get baseline (first row)
baseline_case = df.loc[0, "CaseName"]
baseline_row = df.iloc[0]

# Get all numeric data columns only
data_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Calculate percentage differences and store results
results = []
max_pct_diff = 0
max_pct_info = {}

# Loop through all cases except baseline
for i in range(1, len(df)):
    case = df.loc[i, "CaseName"]
    
    for col in data_cols:
        baseline_val = baseline_row[col]
        case_val = df.loc[i, col]
        
        # Calculate percentage difference
        if baseline_val != 0:
            pct_diff = (case_val - baseline_val) / baseline_val * 100
        else:
            # Handle division by zero
            pct_diff = np.nan if case_val == 0 else float('inf')
        
        results.append({
            "CaseName": case,
            "Metric": col,
            "Baseline_Value": baseline_val,
            "Case_Value": case_val,
            "Percent_Difference": pct_diff
        })
        
        # Track maximum absolute percentage difference
        if not np.isnan(pct_diff) and not np.isinf(pct_diff):
            abs_pct_diff = abs(pct_diff)
            if abs_pct_diff > max_pct_diff:
                max_pct_diff = abs_pct_diff
                max_pct_info = {
                    "CaseName": case,
                    "Metric": col,
                    "Percent_Difference": pct_diff,
                    "Baseline_Value": baseline_val,
                    "Case_Value": case_val
                }

# Create output dataframe
output_df = pd.DataFrame(results)

# Save to CSV
output_df.to_csv("generation_consumption_percentage_differences.csv", index=False)

print(f"Total comparisons: {len(output_df)}")
print()

# Calculate summary statistics
valid_pct_diffs = output_df[
    (output_df["Percent_Difference"].notna()) & 
    (output_df["Percent_Difference"] != np.inf) &
    (output_df["Percent_Difference"] != -np.inf)
]["Percent_Difference"]

if len(valid_pct_diffs) > 0:
    mean_pct_diff = valid_pct_diffs.mean()
    median_pct_diff = valid_pct_diffs.median()
    
    print("=" * 70)
    print("SUMMARY STATISTICS:")
    print("=" * 70)
    print(f"Mean Percent Difference: {mean_pct_diff:.3f}%")
    print(f"Median Percent Difference: {median_pct_diff:.3f}%")
    print("=" * 70)
    print()

# Print largest percentage difference
if max_pct_info:
    print("=" * 70)
    print("LARGEST PERCENTAGE DIFFERENCE:")
    print("=" * 70)
    print(f"Case: {max_pct_info['CaseName']}")
    print(f"Metric: {max_pct_info['Metric']}")
    print(f"Baseline Value: {max_pct_info['Baseline_Value']:.2f}")
    print(f"Case Value: {max_pct_info['Case_Value']:.2f}")
    print(f"Percent Difference: {max_pct_info['Percent_Difference']:.3f}%")
    print("=" * 70)
else:
    print("No valid percentage differences found.")


# ===================================================================
# ************************ COMPARE COSTS ************************
# ===================================================================
print()
print()
print("*" * 70)
print("COST COMPARISON:")
print("*" * 70)
print()

# Load the costs CSV
df = pd.read_csv("Costs_by_Zone_by_Year_ALL_CASES.csv")

# Get baseline (first row)
baseline_case = df.loc[0, "CaseName"]
baseline_row = df.iloc[0]

# Get all numeric data columns only
data_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Calculate percentage differences and store results
results = []
max_pct_diff = 0
max_pct_info = {}

# Loop through all cases except baseline
for i in range(1, len(df)):
    case = df.loc[i, "CaseName"]
    
    for col in data_cols:
        baseline_val = baseline_row[col]
        case_val = df.loc[i, col]
        
        # Calculate percentage difference
        if baseline_val != 0:
            pct_diff = (case_val - baseline_val) / baseline_val * 100
        else:
            # Handle division by zero
            pct_diff = np.nan if case_val == 0 else float('inf')
        
        results.append({
            "CaseName": case,
            "Metric": col,
            "Baseline_Value": baseline_val,
            "Case_Value": case_val,
            "Percent_Difference": pct_diff
        })
        
        # Track maximum absolute percentage difference
        if not np.isnan(pct_diff) and not np.isinf(pct_diff):
            abs_pct_diff = abs(pct_diff)
            if abs_pct_diff > max_pct_diff:
                max_pct_diff = abs_pct_diff
                max_pct_info = {
                    "CaseName": case,
                    "Metric": col,
                    "Percent_Difference": pct_diff,
                    "Baseline_Value": baseline_val,
                    "Case_Value": case_val
                }

# Create output dataframe
output_df = pd.DataFrame(results)

# Save to CSV
output_df.to_csv("generation_consumption_percentage_differences.csv", index=False)

print(f"Total comparisons: {len(output_df)}")
print()

# Calculate summary statistics
valid_pct_diffs = output_df[
    (output_df["Percent_Difference"].notna()) & 
    (output_df["Percent_Difference"] != np.inf) &
    (output_df["Percent_Difference"] != -np.inf)
]["Percent_Difference"]

if len(valid_pct_diffs) > 0:
    mean_pct_diff = valid_pct_diffs.mean()
    median_pct_diff = valid_pct_diffs.median()
    
    print("=" * 70)
    print("SUMMARY STATISTICS:")
    print("=" * 70)
    print(f"Mean Percent Difference: {mean_pct_diff:.3f}%")
    print(f"Median Percent Difference: {median_pct_diff:.3f}%")
    print("=" * 70)
    print()

# Print largest percentage difference
if max_pct_info:
    print("=" * 70)
    print("LARGEST PERCENTAGE DIFFERENCE:")
    print("=" * 70)
    print(f"Case: {max_pct_info['CaseName']}")
    print(f"Metric: {max_pct_info['Metric']}")
    print(f"Baseline Value: {max_pct_info['Baseline_Value']:.2f}")
    print(f"Case Value: {max_pct_info['Case_Value']:.2f}")
    print(f"Percent Difference: {max_pct_info['Percent_Difference']:.3f}%")
    print("=" * 70)
else:
    print("No valid percentage differences found.")

