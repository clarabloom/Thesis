import pandas as pd

# ===============================
# INPUT FILE
# ===============================

base_path = "Futures_Files/SOLAR_COSTS/Vre_p1.csv"

# ===============================
# SETTINGS
# ===============================

RESOURCE_FILTER = "utilitypv"     # match solar utility-scale rows
CAPEX_COLUMN = "Inv_Cost_per_MWyr"

solar_scalars = {
    "low": 0.75,   # cheaper solar
    "high": 1.25   # more expensive solar
}

output_prefix = "Futures_Files/SOLAR_COSTS/"

# ===============================
# LOAD BASE FILE
# ===============================

df_base = pd.read_csv(base_path)

# Safety checks
if CAPEX_COLUMN not in df_base.columns:
    raise ValueError(f"{CAPEX_COLUMN} not found in Vre.csv")

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

for scenario, scalar in solar_scalars.items():

    df_future = df_base.copy()

    # Adjust only solar rows
    df_future.loc[solar_mask, CAPEX_COLUMN] = (
        df_future.loc[solar_mask, CAPEX_COLUMN] * scalar
    )

    output_path = f"{output_prefix}Vre_{scenario}_solar_p1.csv"

    df_future.to_csv(output_path, index=False)

    print(f"Saved {scenario} solar cost scenario to {output_path}")

print("All solar cost scenarios generated successfully.")