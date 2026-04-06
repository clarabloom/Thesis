import pandas as pd
from pathlib import Path

# ==================================================
# PATH
# ==================================================

HIGHESTAMB_DIR = Path(
"/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios/highestambition"
)

# Target PJM zones outside NJ
TARGET_ZONES = ["z1", "z2", "z6", "z7", "z17", "z18", "z19", "z20", "z22", "z23", "z24"]


# ==================================================
# PROCESS EACH CASE
# ==================================================

for case_dir in HIGHESTAMB_DIR.iterdir():

    if not case_dir.is_dir():
        continue

    print(f"\nProcessing {case_dir.name}")

    # ==================================================
    # 1. Capacity_reserve_margin.csv
    # ==================================================

    crm_path = case_dir / "inputs/inputs_p3/policies/Capacity_reserve_margin.csv"
    crm = pd.read_csv(crm_path)

    crm["CapRes_9"] = crm["Network_zones"].apply(
        lambda x: 0.0001 if x in TARGET_ZONES else 0
    )

    crm.to_csv(crm_path, index=False)
    print("✓ Added CapRes_9")

    # ==================================================
    # 2. Resource_capacity_reserve_margin.csv
    # ==================================================

    res_path = case_dir / "inputs/inputs_p3/resources/policy_assignments/Resource_capacity_reserve_margin.csv"
    res = pd.read_csv(res_path)

    # safest: copy previous clean eligibility column
    if "Derating_factor_8" in res.columns:
        res["Derating_factor_9"] = res["Derating_factor_8"]
    else:
        res["Derating_factor_9"] = 1

    res.to_csv(res_path, index=False)
    print("✓ Added Derating_factor_9")

    # ==================================================
    # 3. Network.csv
    # ==================================================

    net_path = case_dir / "inputs/inputs_p3/system/Network.csv"
    net = pd.read_csv(net_path)

    net["DerateCapRes_9"] = 0.95
    net["CapRes_Excl_9"] = 0

    net.to_csv(net_path, index=False)
    print("✓ Updated Network.csv")

print("\nAll highest ambition cases updated.")