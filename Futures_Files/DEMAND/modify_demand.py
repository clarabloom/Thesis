import pandas as pd

base_path = "Futures_Files/DEMAND/Demand_data_p2_base.csv"

DEMAND_PREFIX = "Demand_MW_"

demand_scalars = {
    "low": 0.90,
    "high": 1.10
}

output_prefix = "Futures_Files/DEMAND/"

df_base = pd.read_csv(base_path)

demand_cols = [c for c in df_base.columns if c.startswith(DEMAND_PREFIX)]


for scenario, scalar in demand_scalars.items():
    df_future = df_base.copy()
    
    df_future[demand_cols] = df_future[demand_cols] * scalar
    
    output_path = f"{output_prefix}demand_p2_{scenario}.csv"
    df_future.to_csv(output_path, index=False)
    
    print(f"Saved {scenario} demand scenario to {output_path}")

print("All demand scenarios generated successfully.")