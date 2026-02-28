import pandas as pd

# ===============================
# INPUT FILE
# ===============================

base_path = "Futures_Files/NUCLEAR_COST/Thermal_p1.csv"

# ===============================
# SETTINGS
# ===============================

RESOURCE_FILTER = "nuclear"     # match nuclear rows
CAPEX_COLUMN = "Inv_Cost_per_MWyr"

nuclear_scalars = {
    "low": 0.9,   # cheaper nuclear
    "high": 1.1   # more expensive nuclear
}

output_prefix = "Futures_Files/NUCLEAR_COST/"

# ===============================
# LOAD BASE FILE
# ===============================

df_base = pd.read_csv(base_path)

# Safety checks
if CAPEX_COLUMN not in df_base.columns:
    raise ValueError(f"{CAPEX_COLUMN} not found in Theraml.csv")

if "Resource" not in df_base.columns:
    raise ValueError("Column 'Resource' not found — cannot filter utilitypv rows.")

# Identify solar rows
solar_mask = df_base["Resource"].str.contains(
    RESOURCE_FILTER,
    case=False,
    na=False
)

print(f"Found {solar_mask.sum()} utilitypv resources.")

# ===============================
# GENERATE FUTURES
# ===============================

for scenario, scalar in nuclear_scalars.items():

    df_future = df_base.copy()

    # Adjust only nuclear rows
    df_future.loc[solar_mask, CAPEX_COLUMN] = (
        df_future.loc[solar_mask, CAPEX_COLUMN] * scalar
    )

    output_path = f"{output_prefix}Thermal_{scenario}_nuclear_p1.csv"

    df_future.to_csv(output_path, index=False)

    print(f"Saved {scenario} nuclear cost scenario to {output_path}")

print("All nuclear cost scenarios generated successfully.")