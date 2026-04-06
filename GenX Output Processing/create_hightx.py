import os
import shutil
import pandas as pd

# ============================
# USER SETTINGS
# ============================

BASE_DIR = "/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS"

SOURCE_DIR = os.path.join(BASE_DIR, "base")
TARGET_DIR = os.path.join(BASE_DIR, "futures_scenarios/hightx")

PERIODS = ["inputs_p1", "inputs_p2", "inputs_p3"]

TX_SCALE = 2.0  # try 2x first

# ============================
# STEP 1: COPY CASES
# ============================

print("\nCopying base cases...\n")

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

for case in os.listdir(SOURCE_DIR):
    src = os.path.join(SOURCE_DIR, case)
    if not os.path.isdir(src):
        continue

    # rename: base_x → hightx_x
    new_name = f"hightx_{case.split('_', 1)[1]}"
    dst = os.path.join(TARGET_DIR, new_name)

    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    print(f"{case} → {new_name}")

# ============================
# STEP 2: MODIFY NETWORK
# ============================

print("\nScaling transmission...\n")

for case in os.listdir(TARGET_DIR):
    case_path = os.path.join(TARGET_DIR, case)

    for p in PERIODS:
        net_path = os.path.join(case_path, "inputs", p, "system", "Network.csv")

        if not os.path.exists(net_path):
            print(f"Missing: {net_path}")
            continue

        df = pd.read_csv(net_path)

        # --- scale main capacity ---
        if "Line_Max_Flow_MW" in df.columns:
            df["Line_Max_Flow_MW"] *= TX_SCALE
        else:
            raise ValueError("Missing Line_Max_Flow_MW")

        # --- scale reinforcement capacity ---
        if "Line_Max_Reinforcement_MW" in df.columns:
            df["Line_Max_Reinforcement_MW"] *= TX_SCALE

        # --- optional: cap by physical max if needed ---
        if "Line_Max_Flow_Possible_MW" in df.columns:
            df["Line_Max_Flow_MW"] = df[
                ["Line_Max_Flow_MW", "Line_Max_Flow_Possible_MW"]
            ].min(axis=1)

        df.to_csv(net_path, index=False)

        print(f"{case} | {p} updated")

print("\n✅ High transmission futures ready.")