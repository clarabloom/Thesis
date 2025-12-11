import pandas as pd
import re
import os
import numpy as np

# ==============================
# Hard-coded configuration
# ==============================


# === NEW: Hard-code the input cases here (name, path) ===
# Each tuple is (case_name, power_csv_path)
CASE_DIRS = [
    "Basecase_RGGI",
    "Updated_RGGI_noprocurement",
    "Updated_RGGI_noprocurement_noOOS",
    "Updated_RGGI_procurement_noOOS",
    "Basecase_RGGI_solarderate",
    "Updated_RGGI_noprocurement_solarderate",
    "Updated_RGGI_noprocurement_noOOS_solarderate",
    "Updated_RGGI_procurement_noOOS_solarderate",  
]


def get_totalgen(df: pd.DataFrame, zone: str):
    mask = (
        ~df.columns.str.contains(re.escape('batter'), case=False, regex=True)
        & ~df.columns.str.contains(re.escape('stor'), case=False, regex=True)
        & df.columns.str.contains(re.escape(zone), case=False, regex=True)
    )
    return df.loc[['AnnualSum'], mask].sum(axis=1).iat[0]

def get_techs_pwr(df: pd.DataFrame, zones: str, techs: list):
    # Create a boolean mask for zone
    zone_mask = df.columns.str.contains('|'.join(zones), regex=True)
    
    # Create a boolean mask for any tech in the list
    tech_mask = df.columns.str.contains('|'.join(techs), regex=True)
    
    return df.loc[:, zone_mask & tech_mask].sum(axis=1).values[2::]
# ==============================
# Core logic (generation)
# ==============================

# === Existing function, modified only to read from a given base_dir ===
def calculate_revenue(df, period, base_dir):
    power_path = os.path.join(base_dir, "results", f"results_p{period}", "power.csv")
    charge_path = os.path.join(base_dir, "results", f"results_p{period}", "charge.csv")
    dem_path       = os.path.join(base_dir, "inputs", f"inputs_p{period}", "TDR_results", "Demand_data.csv")

    power = pd.read_csv(power_path, header='infer',index_col=0)
    

    instategen = []
    instategen.append(round(get_totalgen(power,'NJ1')))
    df[f"In_State_Generation_p{period}"] = instategen

    charge = pd.read_csv(charge_path, header='infer',index_col=0)
    dem_in = pd.read_csv(dem_path, header='infer')
    hourly_demand = dem_in["Demand_MW_z10"].values
    weights = dem_in["Sub_Weights"].dropna().values
    print(f"[{os.path.basename(os.path.normpath(base_dir))}] p{period}: {len(weights)} sub-weights")
    hourly_weights = [w/168 for w in weights for _ in range(168)]
    loadtot = (hourly_demand * hourly_weights).sum()

    techsnj = ['solar','pv','distributed','wind','nuclear','hydro','bio','batt']
    techsrest = ['pv','landbased','nuclear_nuclear','battery']
    zones = ['DE1','PA3','PA4'] # zones = ['DE1','IL1','KY3','KY4','MD1','MD2','OH1','OH2','OH3','OH4','PA1','PA2','PA3','PA4','VA1','VA2','VA3','VA4','WV1','WV2']

    instateclean = get_techs_pwr(power, ['NJ1'],techsnj) - get_techs_pwr(charge, ['NJ1'],techsnj)
    instatecleantot = (instateclean * hourly_weights).sum()
    instateshortfall = np.clip(hourly_demand - instateclean, 0, None)
    instateshortfalltot = (instateshortfall * hourly_weights).sum()
    instatecleancons = loadtot - instateshortfalltot
    df[f"Total_NJ_Load_p{period}"] = [loadtot]
    df[f"NJ_In-State_Clean_Consumption_p{period}"] = [instatecleancons]
    df[f"NJ_In-State_Clean_Consumption_fraction_p{period}"] = [instatecleancons/loadtot]

    oosclean = get_techs_pwr(power, zones, techsrest) - get_techs_pwr(charge, zones, techsrest)
    ooscleantot = (oosclean * hourly_weights).sum()
    if period == 1:
        cesfrac = 0.85
    else:
        cesfrac = 1
    oosfrac = min((loadtot*cesfrac - instatecleantot)/ooscleantot,1)
    print(oosfrac)
    totalclean = instateclean + oosclean*oosfrac
    totalshortfall = np.clip(hourly_demand - totalclean, 0, None)
    totalshortfalltot = (totalshortfall * hourly_weights).sum()
    totalcleancons = loadtot - totalshortfalltot
    df[f"NJ_Total_Clean_Consumption_p{period}"] = [totalcleancons]
    df[f"NJ_Total_Clean_Consumption_fraction_p{period}"] = [totalcleancons/loadtot]

    return df

def build_single_case_df(base_dir):
    # Base Zone frame (same as your original script)
    df = pd.DataFrame({"Zone": [
        "NJ"
    ]})
    # Run for periods 1–3 (same as original)
    df = calculate_revenue(df, 1, base_dir)
    df = calculate_revenue(df, 2, base_dir)
    df = calculate_revenue(df, 3, base_dir)
    df = df.round(2)
    return df

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    case_paths = [
        p if os.path.isabs(p) else os.path.join(script_dir, p)
        for p in CASE_DIRS
    ]

    all_case_dfs = []
    for case_path in case_paths:
        case_name = os.path.basename(os.path.normpath(case_path))
        if not os.path.isdir(case_path):
            print(f"WARNING: Skipping '{case_name}' because the folder was not found at: {case_path}")
            continue

        df_case = build_single_case_df(case_path)
        # Insert CaseName as the FIRST column
        df_case.insert(0, "CaseName", case_name)
        all_case_dfs.append(df_case)

    if not all_case_dfs:
        print("No valid case directories were provided. Please edit CASE_DIRS and try again.")
        return

    combined = pd.concat(all_case_dfs, axis=0, ignore_index=True, sort=False)
    out_path = os.path.join(script_dir, "In_State_Generation_and_Consumption.csv")
    combined.to_csv(out_path, index=False)
    print(f"\nWrote {len(all_case_dfs)} cases to: {out_path}")

if __name__ == "__main__":
    main()