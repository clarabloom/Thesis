import shutil
import pandas as pd
from pathlib import Path

# ==================================================
# PATHS
# ==================================================

BASE_DIR    = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

FUTURE_NAME = "lds"

# ==================================================
# CONFIG
# ==================================================

LDS_NAME = "LDS"

CAPEX_KW = 2500       # can test 2000 later
FOM_PERCENT = 0.025

EFFICIENCY = 0.65
DURATION   = 100

DERATING_VALUE = 0.95

# Map zone prefix → MinCap constraint column index
ZONE_TO_MINCAP = {
    "NY":   6,
    "MD":   7,
    "VA":   8,
    "ISONE":9,
    "NJ":   10,
}

# ==================================================
# STEP 1: COPY CASES
# ==================================================

def create_future_cases():
    future_dir = FUTURES_DIR / FUTURE_NAME
    future_dir.mkdir(exist_ok=True)

    for base_case in BASE_DIR.iterdir():
        if not base_case.is_dir():
            continue

        old_name = base_case.name

        if old_name.startswith("base_"):
            new_name = FUTURE_NAME + "_" + old_name[len("base_"):]
        else:
            new_name = old_name

        new_case_path = future_dir / new_name

        if not new_case_path.exists():
            shutil.copytree(base_case, new_case_path)
            print(f"Copied {old_name} → {new_name}")

# ==================================================
# STEP 2: ADD LDS TO STORAGE
# ==================================================

def add_lds(storage_path):
    df = pd.read_csv(storage_path)

    # --- find battery rows ---
    batt_rows = df[df["Resource"].str.contains("batt", case=False)]

    template_rows = batt_rows[batt_rows["Inv_Cost_per_MWyr"] > 0]
    if template_rows.empty:
        print(f"⚠ No valid battery template in {storage_path}")
        return

    template = template_rows.iloc[0]

    # ratio of annualized cost to capex
    ratio = template["Inv_Cost_per_MWyr"] / template["capex_mw"]

    capex_mw = CAPEX_KW * 1000
    inv_cost_mwyr = capex_mw * ratio

    # add fixed O&M
    fom = capex_mw * FOM_PERCENT
    inv_cost_total = inv_cost_mwyr + fom

    # --- zones ---
    zones = df["Resource"].str.extract(r"^(.*?)_")[0].dropna().unique()

    new_rows = []

    for z in zones:
        resource_name = f"{z}_{LDS_NAME}"

        if resource_name in df["Resource"].values:
            continue

        row = template.copy()

        row["Resource"] = resource_name
        row["Zone"] = df.loc[df["Resource"].str.startswith(z + "_"), "Zone"].values[0]

        row["Existing_Cap_MW"] = 0
        row["Existing_Cap_MWh"] = 0
        row["Existing_Charge_Cap_MW"] = 0

        row["New_Build"] = 1
        row["Can_Retire"] = 0

        row["Min_Duration"] = DURATION
        row["Max_Duration"] = DURATION

        row["Eff_Up"] = EFFICIENCY
        row["Eff_Down"] = EFFICIENCY

        row["Inv_Cost_per_MWyr"] = round(inv_cost_total, 2)
        row["Inv_Cost_per_MWhyr"] = 0

        row["capex_mw"] = capex_mw
        row["capex_mwh"] = 0

        row["Max_Cap_MW"] = -1
        row["Max_Cap_MWh"] = -1

        new_rows.append(row)

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        df.to_csv(storage_path, index=False)
        print(f"  ✓ Added LDS to {storage_path.name}")

# ==================================================
# STEP 3: MULTISTAGE FILE
# ==================================================

def update_multistage(path):
    df = pd.read_csv(path)

    zones = df["Resource"].str.extract(r"^(.*?)_")[0].dropna().unique()

    for z in zones:
        name = f"{z}_{LDS_NAME}"

        if name not in df["Resource"].values:
            new_row = {col: 0 for col in df.columns}
            new_row["Resource"] = name
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(path, index=False)

# ==================================================
# STEP 4: RESERVE MARGIN
# ==================================================

def update_derating(path):
    df = pd.read_csv(path)

    zones = df["Resource"].str.extract(r"^(.*?)_")[0].dropna().unique()
    new_rows = []

    for z in zones:
        name = f"{z}_{LDS_NAME}"

        if name in df["Resource"].values:
            idx = df[df["Resource"] == name].index[0]
            df.at[idx, "CapRes_8"] = 1
            df.at[idx, "Derating_factor_8"] = DERATING_VALUE
        else:
            row = {col: 0 for col in df.columns}
            row["Resource"] = name
            if "CapRes_8" in df.columns:
                row["CapRes_8"] = 1
            if "Derating_factor_8" in df.columns:
                row["Derating_factor_8"] = DERATING_VALUE
            new_rows.append(row)

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    df.fillna(0, inplace=True)
    df.to_csv(path, index=False)

# ==================================================
# STEP 5: MINCAP
# ==================================================

def update_mincap(path):
    df = pd.read_csv(path)

    if "Resource" not in df.columns:
        print(f"  ⚠ No Resource column in {path}")
        return

    zones = df["Resource"].str.extract(r"^(.*?)_")[0].dropna().unique()

    for z in zones:
        name = f"{z}_{LDS_NAME}"

        if name not in df["Resource"].values:
            new_row = {col: 0 for col in df.columns}
            new_row["Resource"] = name
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        idx = df[df["Resource"] == name].index[0]

        # assign correct MinCap column
        if z.startswith("NJ"):
            zone_key = "NJ"
        elif z.startswith("NY"):
            zone_key = "NY"
        elif z.startswith("MD"):
            zone_key = "MD"
        elif z.startswith("VA"):
            zone_key = "VA"
        elif z.startswith("ISONE"):
            zone_key = "ISONE"
        else:
            continue

        if zone_key not in ZONE_TO_MINCAP:
            continue

        mincap_col = f"Min_Cap_{ZONE_TO_MINCAP[zone_key]}"

        if mincap_col not in df.columns:
            continue

        # zero out then set correct column
        for col in df.columns:
            if col.startswith("Min_Cap_"):
                df.at[idx, col] = 0

        df.at[idx, mincap_col] = 1

    df.fillna(0, inplace=True)
    df.to_csv(path, index=False)

# ==================================================
# STEP 6: APPLY TO ALL CASES
# ==================================================

def apply_updates():
    future_dir = FUTURES_DIR / FUTURE_NAME

    if not future_dir.exists():
        print(f"⚠ Missing future dir: {future_dir}")
        return

    for case in sorted(future_dir.iterdir()):
        if not case.is_dir():
            continue

        print(f"\nUpdating {case.name}")

        for period in ["p1", "p2", "p3"]:
            storage   = case / f"inputs/inputs_{period}/resources/Storage.csv"
            multistage = case / f"inputs/inputs_{period}/resources/Resource_multistage_data.csv"
            derating  = case / f"inputs/inputs_{period}/resources/policy_assignments/Resource_capacity_reserve_margin.csv"
            mincap    = case / f"inputs/inputs_{period}/resources/policy_assignments/Resource_minimum_capacity_requirement.csv"

            if storage.exists():
                add_lds(storage)
            else:
                print(f"  ⚠ Missing: {storage}")

            if multistage.exists():
                update_multistage(multistage)
            else:
                print(f"  ⚠ Missing: {multistage}")

            if derating.exists():
                update_derating(derating)
            else:
                print(f"  ⚠ Missing: {derating}")

            if mincap.exists():
                update_mincap(mincap)
            else:
                print(f"  ⚠ Missing: {mincap}")

# ==================================================
# MAIN
# ==================================================

def main():
    print("=== Creating future cases ===")
    create_future_cases()

    print("\n=== Adding long-duration storage ===")
    apply_updates()

    print("\nDone!")

if __name__ == "__main__":
    main()