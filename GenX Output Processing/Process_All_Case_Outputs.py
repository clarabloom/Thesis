#!/usr/bin/env python3

import os
import pandas as pd
from pathlib import Path
import numpy as np

# =====================================================
# ROOT DIRECTORIES
# =====================================================

BASE_DIR    = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/base")
FUTURES_DIR = Path("/scratch/gpfs/JENKINS/cb2158/GenX.jl-main/example_systems/FINAL_SYSTEMS/futures_scenarios")

# =====================================================
# FIND ALL CASE DIRECTORIES
# =====================================================

def find_all_cases():
    cases = []
    for case in BASE_DIR.iterdir():
        if case.is_dir():
            cases.append(case)
    for scenario in FUTURES_DIR.iterdir():
        if scenario.is_dir():
            for case in scenario.iterdir():
                if case.is_dir():
                    cases.append(case)
    return cases

# =====================================================
# HELPERS
# =====================================================

# (zone-specific and system helpers are defined in the CAPACITY section below)

# =====================================================
# CAPACITY
# =====================================================

# =====================================================
# CAPACITY HELPERS — zone-specific and system-wide,
# supporting both EndCap (periods 1-3) and StartCap (period 0)
# =====================================================

def _cap_col(start):
    return "StartCap" if start else "EndCap"

def _ecap_col(start):
    return "StartEnergyCap" if start else "EndEnergyCap"

def _get_zone_cap(df, zone, tech, start=False):
    mask = df.Resource.str.startswith(zone + "_") & df.Resource.str.contains(tech, case=False)
    return df.loc[mask, _cap_col(start)].sum()

def _get_zone_ecap(df, zone, tech, start=False):
    mask = df.Resource.str.startswith(zone + "_") & df.Resource.str.contains(tech, case=False)
    return df.loc[mask, _ecap_col(start)].sum()

def _get_sys_cap(df, tech, start=False):
    return df.loc[df.Resource.str.contains(tech, case=False), _cap_col(start)].sum()

def _get_sys_ecap(df, tech, start=False):
    return df.loc[df.Resource.str.contains(tech, case=False), _ecap_col(start)].sum()

def _tech_row(cap_in, zone, p, start=False):
    """Return a dict of all tech capacities for a given zone and period label p."""
    g  = lambda tech: _get_zone_cap(cap_in, zone, tech, start)
    ge = lambda tech: _get_zone_ecap(cap_in, zone, tech, start)
    return {
        f"Minor_Techs_p{p}":      g("geothermal") + g("biomass") + g("petroleum"),
        f"Hydropower_p{p}":       g("conventional_hydro"),
        f"Existing_Nuclear_p{p}": g("nuclear_1"),
        f"New_Nuclear_p{p}":      g("nuclear_nuclear"),
        f"Coal_p{p}":             g("coal"),
        f"Solar_p{p}":            g("solar") + g("pv") + g("distributed"),
        f"Wind_p{p}":             g("wind"),
        f"Natural_Gas_p{p}":      g("gas"),
        f"Battery_Power_p{p}":    g("batt"),
        f"Battery_Energy_p{p}":   ge("batt"),
        f"Long_Duration_Storage_p{p}":   ge("LDS"),
    }

def _tech_row_system(cap_in, p, start=False):
    """Return a dict of all tech capacities summed across all zones."""
    g  = lambda tech: _get_sys_cap(cap_in, tech, start)
    ge = lambda tech: _get_sys_ecap(cap_in, tech, start)
    return {
        f"Minor_Techs_p{p}":      g("geothermal") + g("biomass") + g("petroleum"),
        f"Hydropower_p{p}":       g("conventional_hydro"),
        f"Existing_Nuclear_p{p}": g("nuclear_1"),
        f"New_Nuclear_p{p}":      g("nuclear_nuclear"),
        f"Coal_p{p}":             g("coal"),
        f"Solar_p{p}":            g("solar") + g("pv") + g("distributed"),
        f"Wind_p{p}":             g("wind"),
        f"Natural_Gas_p{p}":      g("gas"),
        f"Battery_Power_p{p}":    g("batt"),
        f"Battery_Energy_p{p}":   ge("batt"),
        f"Long_Duration_Storage_p{p}":   ge("lds"),
    }

def calculate_capacity(base_dir):
    """
    Returns a DataFrame with two rows per period (NJ1 and System).
    Period 0 = StartCap from results_p1 (initial installed capacity).
    Periods 1-3 = EndCap from each results_p{period}.
    """
    df = pd.DataFrame({"Zone": ["NJ1", "System"]})

    # Period 0: start capacity (read from results_p1, use StartCap columns)
    cap_path_p1 = base_dir / "results/results_p1/capacity.csv"
    if cap_path_p1.exists():
        cap_in = pd.read_csv(cap_path_p1)
        nj_row  = _tech_row(cap_in, "NJ1", p=0, start=True)
        sys_row = _tech_row_system(cap_in, p=0, start=True)
        for col in nj_row:
            df[col] = [nj_row[col], sys_row[col]]
    else:
        print(f"  Missing results_p1 for start capacity: {cap_path_p1}")

    # Periods 1-3: end capacity
    for period in [1, 2, 3]:
        cap_path = base_dir / f"results/results_p{period}/capacity.csv"
        if not cap_path.exists():
            print(f"  Missing capacity file: {cap_path}")
            continue
        cap_in  = pd.read_csv(cap_path)
        nj_row  = _tech_row(cap_in, "NJ1", p=period, start=False)
        sys_row = _tech_row_system(cap_in, p=period, start=False)
        for col in nj_row:
            df[col] = [nj_row[col], sys_row[col]]

    return df.round(2)

# =====================================================
# LOAD + EMISSIONS
# =====================================================

def calculate_load_emissions(base_dir):
    df = pd.DataFrame({"Zone": ["NJ"]})

    for period in [1, 2, 3]:
        dem_path       = base_dir / f"inputs/inputs_p{period}/TDR_results/Demand_data.csv"
        emissions_path = base_dir / f"results/results_p{period}/emissions.csv"

        if not dem_path.exists() or not emissions_path.exists():
            continue

        dem_in    = pd.read_csv(dem_path)
        emissions = pd.read_csv(emissions_path)

        hourly_demand  = dem_in["Demand_MW_z10"].values
        weights        = dem_in["Sub_Weights"].dropna().values
        hourly_weights = [w / 168 for w in weights for _ in range(168)]
        loadtot        = (hourly_demand * hourly_weights).sum()

        df[f"Total_NJ_Load_p{period}"]        = [loadtot]
        df[f"Total_NJ_Emissions_p{period}"]   = [emissions["10"].iloc[1]]
        df[f"Total_System_Emissions_p{period}"] = [emissions["Total"].iloc[1]]

    return df.round(2)

# =====================================================
# PRICES  (full calculation from calculate_cost)
# =====================================================

def calculate_prices(base_dir):
    import pandas as pd

    df = pd.DataFrame({"Zone": ["NJ"]})
    base_dir_str = str(base_dir).lower()

    for period in [1, 2, 3]:

        # ================================
        # PATHS
        # ================================
        dem_path    = base_dir / f"inputs/inputs_p{period}/TDR_results/Demand_data.csv"
        capres_path = base_dir / f"inputs/inputs_p{period}/policies/Capacity_reserve_margin.csv"
        esr_input   = base_dir / f"inputs/inputs_p{period}/policies/Energy_share_requirement.csv"
        mincap_input = base_dir / f"inputs/inputs_p{period}/policies/Minimum_capacity_requirement.csv"

        prices_path = base_dir / f"results/results_p{period}/prices.csv"
        resmar_path = base_dir / f"results/results_p{period}/ReserveMargin_w.csv"
        esr_path    = base_dir / f"results/results_p{period}/ESR_prices_and_penalties.csv"
        mincap_path = base_dir / f"results/results_p{period}/MinCapReq_prices_and_penalties.csv"
        flow_path   = base_dir / f"results/results_p{period}/flow.csv"

        # ================================
        # CHECK FILES
        # ================================
        required = [dem_path, capres_path, prices_path, resmar_path, esr_path, mincap_path]
        if any(not p.exists() for p in required):
            print(f"Skipping p{period} (missing files)")
            continue

        # ================================
        # LOAD DATA
        # ================================
        dem_in = pd.read_csv(dem_path)
        prices = pd.read_csv(prices_path)
        resmar = pd.read_csv(resmar_path)
        esr    = pd.read_csv(esr_path)
        mincap = pd.read_csv(mincap_path)

        hourly_demand  = dem_in["Demand_MW_z10"].values
        weights        = dem_in["Sub_Weights"].dropna().values
        hourly_weights = [w / 168 for w in weights for _ in range(168)]

        denom = (pd.Series(hourly_weights) * hourly_demand).sum()

        # ================================
        # (1) ENERGY PRICE
        # ================================
        energy_price = (
            (prices["10"].values * hourly_weights * hourly_demand).sum() / denom
        )

        # ================================
        # (2) PJM CAPACITY PRICE
        # ================================
        pjm_cap_price = (
            (resmar["CapRes_5"].values * 1.0 * hourly_weights * hourly_demand).sum()
            / denom
        )

        # ================================
        # (3) NJ CLEAN CAPACITY PRICE
        # ================================
        capres = pd.read_csv(capres_path)

        try:
            captarget = capres.loc[
                capres["Network_zones"] == "z10", "CapRes_8"
            ].values[0]
        except:
            captarget = 0

        if captarget != 0:
            captarget += 1

        if "CapRes_8" in resmar.columns and captarget != 0:
            nj_cap_price = (
                (resmar["CapRes_8"].fillna(0).values
                 * captarget * hourly_weights * hourly_demand).sum()
                / denom
            )
        else:
            nj_cap_price = 0

        # ================================
        # (4) ESR (CLEAN ENERGY CREDIT)
        # ================================
        eac_price = 0.0
        try:
            # ESR_8 → index 7
            eac_price = float(esr["ESR_Price"].iloc[7])
        except Exception as e:
            print(f"  Warning: ESR price failed for p{period}: {e}")
            eac_price = 0.0
        # ================================
        # (5) MINCAP (PROCUREMENT)
        # ================================
        try:
            mincap_inputs = pd.read_csv(mincap_input)

            constraints = ["NJ_storage", "NJ_solar"]

            total_required_cap = mincap_inputs.loc[
                mincap_inputs["MinCapReqConstraint"].isin(constraints),
                "MinCapReq"
            ].sum()
        except:
            total_required_cap = 0
            
        try:
            mincap_inputs = pd.read_csv(mincap_input)

            nuc_constraint = ["NJ_nuclear"]

            total_required_cap = total_required_cap + mincap_inputs.loc[
                mincap_inputs["MinCapReqConstraint"].isin(nuc_constraint),
                "MinCapReq"
            ].sum()
        except:
            total_required_cap = total_required_cap

        if "Price" in mincap.columns and total_required_cap != 0:
            shadow = mincap["Price"].fillna(0).values

            mincap_price = (
                (shadow * total_required_cap * hourly_weights * hourly_demand).sum()
                / denom
            )
        else:
            mincap_price = 0

        # ================================
        # (6) EXPORT CREDIT — DEBUG MODE
        # ================================
        export_credit = 0
        
        network_path = base_dir / f"inputs/inputs_p{period}/system/Network.csv"
        
        print(f"\n--- DEBUG EXPORT p{period} ---")
        
        if not flow_path.exists():
            print("❌ flow file missing:", flow_path)
        
        if not network_path.exists():
            print("❌ network file missing:", network_path)
        
        if flow_path.exists() and network_path.exists():
            try:
                flows = pd.read_csv(flow_path)
                network = pd.read_csv(network_path)
        
                print("Flow shape:", flows.shape)
                print("Network shape:", network.shape)
                print("Flow columns:", flows.columns[:10])
                print("Network columns:", network.columns.tolist())
        
                # Drop time column
                if "Line" in flows.columns:
                    flow_values = flows.drop(columns=["Line"])
                else:
                    print("❌ 'Line' column not found")
                    flow_values = flows.copy()
        
                print("Flow values shape:", flow_values.shape)
        
                # Check alignment
                if len(flow_values.columns) != len(network):
                    print("❌ Mismatch: flow columns vs network rows")
                    print(len(flow_values.columns), "vs", len(network))
        
                export_series = []
                matched_lines = 0
        
                for i, col in enumerate(flow_values.columns):
                    from_zone = network.loc[i, "from_zone"]
                    to_zone   = network.loc[i, "to_zone"]
        
                    flow = flow_values[col].values
        
                    if i < 5:  # print first few lines
                        print(f"Line {i}: {from_zone} → {to_zone}")
                        print("  sample flows:", flow[:5])
        
                    # CASE 1: export from NJ
                    if from_zone == "NJ1":
                        exports = np.clip(flow, 0, None)
                        if exports.sum() > 0:
                            print(f"✅ Export line (from NJ1): line {i}")
                            matched_lines += 1
                            export_series.append(exports)
        
                    # CASE 2: export into NJ (negative flow)
                    elif to_zone == "NJ1":
                        exports = np.clip(-flow, 0, None)
                        if exports.sum() > 0:
                            print(f"✅ Export line (to NJ1): line {i}")
                            matched_lines += 1
                            export_series.append(exports)
        
                print("Matched export lines:", matched_lines)
        
                if export_series:
                    total_exports = sum(export_series)
                    print("Total exports sample:", total_exports[:10])
        
                    prices_vec = prices["10"].values[:len(total_exports)]
                    print("Price sample:", prices_vec[:10])
        
                    export_revenue = (
                        total_exports
                        * prices_vec
                        * hourly_weights[:len(total_exports)]
                    ).sum()
        
                    export_credit = export_revenue / denom
        
                    print("✅ Export credit computed:", export_credit)
        
                else:
                    print("⚠️ No export flows detected → export_credit = 0")
        
            except Exception as e:
                print("❌ HARD ERROR:", e)
                raise e  # IMPORTANT: don't silently fail anymore

        # ================================
        # TOTAL PRICE
        # ================================
        total_price = (
            energy_price
            + pjm_cap_price
            + nj_cap_price
            + eac_price
            + mincap_price
            - export_credit
        )

        # ================================
        # STORE
        # ================================
        df[f"Energy_Price_p{period}"] = [round(energy_price, 2)]
        df[f"PJM_Capacity_Price_p{period}"] = [round(pjm_cap_price, 2)]
        df[f"NJ_Clean_Capacity_Price_p{period}"] = [round(nj_cap_price, 2)]
        df[f"EAC_Price_p{period}"] = [round(eac_price, 2)]
        df[f"MinCap_Price_p{period}"] = [round(mincap_price, 2)]
        df[f"Export_Credit_p{period}"] = [round(export_credit, 2)]
        df[f"Total_Price_p{period}"] = [round(total_price, 2)]

    return df

# =====================================================
# MAIN
# =====================================================

def main():
    cases = find_all_cases()

    capacity_rows  = []
    emissions_rows = []
    prices_rows    = []

    for case_path in cases:
        case_name = case_path.name
        print(f"Processing {case_name}")

        cap_df   = calculate_capacity(case_path)
        em_df    = calculate_load_emissions(case_path)
        price_df = calculate_prices(case_path)

        for df_, name in [(cap_df, "CaseName"), (em_df, "CaseName"), (price_df, "CaseName")]:
            df_.insert(0, name, case_name)

        # Per-case saves
        cap_df.to_csv(  case_path / f"{case_name}_capacity_summary.csv",       index=False)
        em_df.to_csv(   case_path / f"{case_name}_load_emissions_summary.csv",  index=False)
        price_df.to_csv(case_path / f"{case_name}_price_summary.csv",           index=False)

        capacity_rows.append(cap_df)
        emissions_rows.append(em_df)
        prices_rows.append(price_df)

    pd.concat(capacity_rows,  ignore_index=True).to_csv("ALL_CASE_capacity_summary.csv",  index=False)
    pd.concat(emissions_rows, ignore_index=True).to_csv("ALL_CASE_load_emissions.csv",     index=False)
    pd.concat(prices_rows,    ignore_index=True).to_csv("ALL_CASE_prices.csv",             index=False)

    print(f"\nDone. Processed {len(cases)} cases.")

if __name__ == "__main__":
    main()