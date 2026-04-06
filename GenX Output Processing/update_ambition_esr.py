import pandas as pd
from pathlib import Path

ROOT = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

SCENARIOS = {
    "highambition": "high",
    "lowambition": "low"
}

PERIODS = ["p1","p2","p3"]


def adjust_esr(df, mode):
    # Find the network zones column regardless of case
    zone_col = next((c for c in df.columns if c.lower() == "network_zones"), None)
    if zone_col is None:
        raise ValueError(f"No 'Network_zones' column found. Columns are: {list(df.columns)}")

    esr_cols = [c for c in df.columns if c.lower() != "network_zones"]

    for col in esr_cols:
        # Coerce the column to numeric upfront — non-numeric becomes NaN
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
        bad = df[col][pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()]
        if not bad.empty:
            print(f"    Non-numeric values in '{col}': {bad.tolist()}")

        def transform(row, col=col):
            if str(row[zone_col]).lower() in ["z10", "nj", "nj1"]:
                return row[col]
            val = row[col]
            if pd.isna(val):
                return val
            if mode == "high":
                return min(float(val) * 1.5, 1)
            elif mode == "low":
                return float(val) / 2
            return val

        df[col] = df.apply(transform, axis=1)
    return df

for scenario, mode in SCENARIOS.items():

    scenario_dir = ROOT / scenario

    print(f"\nProcessing {scenario} ({mode})")

    for case_dir in scenario_dir.iterdir():

        if not case_dir.is_dir():
            continue

        print(f"  Case: {case_dir.name}")

        for p in PERIODS:

            file_path = case_dir / "inputs" / f"inputs_{p}" / "policies" / "Energy_share_requirement.csv"

            if not file_path.exists():
                print(f"    Missing: {file_path}")
                continue

            df = pd.read_csv(file_path)

            df = adjust_esr(df, mode)

            df.to_csv(file_path, index=False)

            print(f"    ✓ Updated {p}")

print("\nAll ESR files updated.")