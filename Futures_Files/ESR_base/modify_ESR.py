import pandas as pd

base_path = "Futures_Files/ESR_cesinstate75/ESR_ces75_p1.csv"
ESR_PREFIX = "ESR_"
ESR_scalars = {
    "low": 0.50,
    "high": 1.50,
}
output_prefix = "Futures_Files/ESR_cesinstate75/"

df_base = pd.read_csv(base_path)
demand_cols = [c for c in df_base.columns if c.startswith(ESR_PREFIX)]

for scenario, scalar in ESR_scalars.items():
    df_future = df_base.copy()
    mask = df_future["Network_zones"] != "z10"
    df_future.loc[mask, demand_cols] = (df_future.loc[mask, demand_cols] * scalar).clip(upper=1)
    output_path = f"{output_prefix}ESR_{scenario}_p1.csv"
    df_future.to_csv(output_path, index=False)
    print(f"Saved {scenario} demand scenario to {output_path}")

print("All demand scenarios generated successfully.")