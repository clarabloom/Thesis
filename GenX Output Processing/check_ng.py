import os
import pandas as pd
import numpy as np

# ============================
# PATHS
# ============================

BASE_PATH = "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS"

SCENARIOS = {
    "base":   "base/base_base",
    "highng": "futures_scenarios/highng/highng_cesccs",
    "lowng":  "futures_scenarios/lowng/lowng_cesccs",
}

PERIODS = ["inputs_p1", "inputs_p2", "inputs_p3"]

# ============================
# LOAD FUNCTION
# ============================

def load_fuels_data(scenario_path, period):
    path = os.path.join(
        BASE_PATH,
        scenario_path,
        "inputs",
        period,
        "TDR_results",
        "Fuels_data.csv"
    )
    
    if not os.path.exists(path):
        print(f"❌ Missing: {path}")
        return None
    
    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]
    return df

# ============================
# MAIN CHECK
# ============================

for period in PERIODS:
    print(f"\n==================== {period} ====================")
    
    dfs = {}
    
    # Load data
    for name, path in SCENARIOS.items():
        df = load_fuels_data(path, period)
        if df is not None:
            dfs[name] = df
    
    if not all(k in dfs for k in ["base", "highng", "lowng"]):
        print("Missing data, skipping period")
        continue

    # Identify natural gas columns
    cols = [c for c in dfs["base"].columns if "naturalgas" in c]
    
    if not cols:
        print("❌ No natural gas columns found")
        continue

    print(f"Natural gas columns: {cols}\n")

    # ============================
    # COMPARISON
    # ============================

    for col in cols:
        print(f"--- {col} ---")
        
        base_vals = dfs["base"][col].to_numpy()
        high_vals = dfs["highng"][col].to_numpy()
        low_vals  = dfs["lowng"][col].to_numpy()

        # Summary stats
        def summary(x):
            return f"mean={np.mean(x):.3f}, min={np.min(x):.3f}, max={np.max(x):.3f}, n={len(x)}"
        
        print(f"base:   {summary(base_vals)}")
        print(f"highng: {summary(high_vals)}")
        print(f"lowng:  {summary(low_vals)}")

        # Compare using means (robust to different lengths)
        base_mean = np.mean(base_vals)
        high_mean = np.mean(high_vals)
        low_mean  = np.mean(low_vals)

        if high_mean > base_mean:
            print("  ✅ highng > base (mean)")
        else:
            print("  ❌ ERROR: highng NOT higher than base")

        if low_mean < base_mean:
            print("  ✅ lowng < base (mean)")
        else:
            print("  ❌ ERROR: lowng NOT lower than base")

        if high_mean > low_mean:
            print("  ✅ highng > lowng")
        else:
            print("  ❌ ERROR: highng NOT higher than lowng")

        print()