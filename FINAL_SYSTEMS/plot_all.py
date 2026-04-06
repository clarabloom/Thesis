import textwrap

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import numpy as np
from matplotlib.legend_handler import HandlerBase
from matplotlib.lines import Line2D

# ********************************
# CONFIGURATION
# ********************************

import matplotlib as mpl

mpl.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 12,
    "legend.title_fontsize": 13,
})

FUTURES_BASE   = "FINAL_SYSTEMS"
DATA_DIR       = FUTURES_BASE
COMPARISON_OUT = os.path.join(FUTURES_BASE, "COMPARISON_FIGURES")
os.makedirs(COMPARISON_OUT, exist_ok=True)

SCENARIO_PREFIXES = [
    "base",
    "highestamb",
    "highambition",
    "lowambition",
    "highdemand",
    "lowdemand",
    "highng",
    "lowng",
    "highnuclear",
    "lownuclear",
    "highsolar",
    "lowsolar",
    "batterieslow",
    "batterieshigh",
    "lds",
    "hightx",
]

SCENARIO_LABELS = {
    "base":          "Base",
    "highestamb":    "Highest Ambition",
    "highambition":  "High Ambition",
    "lowambition":   "Low Ambition",
    "highdemand":    "High Demand",
    "lowdemand":     "Low Demand",
    "highng":        "High Natural Gas Price",
    "lowng":         "Low Natural Gas Price",
    "highnuclear":   "High Nuclear Cost",
    "lownuclear":    "Low Nuclear Cost",
    "highsolar":     "High Solar Cost",
    "lowsolar":      "Low Solar Cost",
    "batterieslow":  "Low Battery Cost",
    "batterieshigh": "High Battery Cost",
    "lds":           "Long Duration Storage",
    "hightx":        "High Transmission",
}

TECH_COLORS = {
    "Battery_Energy":        "#8172B2",
    "Battery_Power":         "#DE8647",
    "Existing_Nuclear":      "#F598B8",
    "New_Nuclear":           "#EB5E78",
    "Hydropower":            "#369CE0",
    "Minor_Techs":           "#61C272",
    "Coal":                  "#5C4033",
    "Natural_Gas":           "#A8A8A8",
    "Solar":                 "#EBBB52",
    "Wind":                  "#87D4D4",
    "Long_Duration_Storage": "#418DCC",
}

def _lighten(hex_color, factor=0.45):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02X}{g:02X}{b:02X}"

TECH_COLORS_LIGHT = {tech: _lighten(color) for tech, color in TECH_COLORS.items()}

DOT_COLORS = [
    '#48ABE8', '#F29D13', '#77B053', '#F5867F', '#9368B3',
    '#9E5139', '#F291C7', '#393E41', '#B7C480', '#7CC5CC',
    '#D62728', '#c2c0c0', '#ebdc38'
]

# Price decomposition: five components, each gets its own color.
# EAC and MinCap are combined into a single "Credits" component.
PRICE_DECOMP_COMPONENTS = [
    ("Energy",               "Energy_Price_p{p}",            "#EBBB52"),
    ("PJM Capacity",         "PJM_Capacity_Price_p{p}",      "#F29D13"),
    ("NJ Clean Capacity",    "NJ_Clean_Capacity_Price_p{p}", "#77B053"),
    ("Credits (EAC+MinCap)", None,                            "#9368B3"),
    ("Export Credits",       "Export_Credit_p{p}",           "#369CE0"),
]

# Hatch patterns for each future scenario (applied on top of component color)
DECOMP_HATCHES = ["", "////", "....", "xxxx", "||||", "----", "\\\\\\\\", "++++"]

PRICE_COMPONENTS = {
    "PJM Capacity Price":      ("PJM_Capacity_Price_p1", "PJM_Capacity_Price_p2", "PJM_Capacity_Price_p3"),
    "NJ Clean Capacity Price": ("NJ_Clean_Capacity_Price_p1", "NJ_Clean_Capacity_Price_p2", "NJ_Clean_Capacity_Price_p3"),
}
PRICE_COLORS      = {"PJM Capacity Price": "#F29D13", "NJ Clean Capacity Price": "#77B053"}
PRICE_LINE_STYLES = {"PJM Capacity Price": "--",       "NJ Clean Capacity Price": "-"}

COMPARE_CASES_SUFFIX = ["base", "cesccs", "cesccsret", "cesincccs"]
COMPARE_LABELS       = ["Base", "CES + CCS", "CES + CCS + Retirement", "CES + Incremental CCS"]

YEARS    = [2030, 2035, 2045]
YEAR_MAP = {1: 2030, 2: 2035, 3: 2045}

POLICY_LABELS = {
    "base":                 "Base",
    "ces":                  "Clean Energy Standard (CES)",
    "cesinstate50":         "CES w/ 50% In-State Fulfillment",
    "cesccs":               "CES + Clean Capacity Standard (CCS)",
    "cesccstech":           "CES + CCS + Renewable Tech",
    "cesccstechnuc35":      "CES + CCS + Renew. Tech + 2035 Nuclear",
    "cesccstechnuc45":      "CES + CCS + Renew. Tech + 2045 Nuclear",
    "cesccstechret":        "CES + CCS + Renew. Tech + Retirement",
    "cesincccstechinstate": "CES + Inc. In-State CCS + Renew. Tech",
    "cesincccstech":        "CES + Inc. CCS + Renew. Tech",
    "cesinccsret":          "CES + Inc. CCS + Retirement",
    "cesccsret":            "CES + CCS + Retirement",
    "cesincccs":            "CES + Incremental CCS",
}

POLICY_ORDER = [
    "base", "ces", "cesinstate50", "cesccs", "cesincccs",
    "cesinccsret", "cesccsret", "cesccstech", "cesccstechnuc35",
    "cesccstechnuc45", "cesccstechret", "cesincccstechinstate", "cesincccstech",
]

# ── Capacity plot configuration ──────────────────────────────────────────────
# Edit to restrict which periods / policies appear in the NJ vs System plots.
CAPACITY_PERIODS       = [3]   # 1=2030  2=2035  3=2045

CAPACITY_POLICY_FILTER = [
    "base", "ces", "cesccs", "cesincccs", "cesinstate50",
    "cesccstechret", "cesccstechnuc35", "cesccstechnuc45"
]

# CAPACITY_POLICY_FILTER = ["base", "ces", "cesinstate50", "cesccs", "cesincccs",
#     "cesinccsret", "cesccsret", "cesccstech", "cesccstechnuc35",
#     "cesccstechnuc45", "cesccstechret", "cesincccstechinstate", "cesincccstech",]


def policy_sort_key(case_name):
    scenario = infer_scenario(case_name) or ""
    suffix   = case_name[len(scenario)+1:].lower() if scenario else case_name.lower()
    try:
        return POLICY_ORDER.index(suffix)
    except ValueError:
        return len(POLICY_ORDER)


# ── Comparison groups ────────────────────────────────────────────────────────
# Add "solo": True to groups that have only one future and should be plotted
# against the base scenario for reference.  The plotting functions treat these
# identically to paired groups; the single-scenario logic already works.
COMPARISON_GROUPS = [
    {"name": "Demand",
     "scenarios": ["highdemand", "lowdemand"],
     "labels":    ["High Demand", "Low Demand"]},
    {"name": "Natural_Gas",
     "scenarios": ["highng", "lowng"],
     "labels":    ["High NG Price", "Low NG Price"]},
    {"name": "Nuclear",
     "scenarios": ["highnuclear", "lownuclear"],
     "labels":    ["High Nuclear", "Low Nuclear"]},
    {"name": "Solar",
     "scenarios": ["highsolar", "lowsolar"],
     "labels":    ["High Solar", "Low Solar"]},
    {"name": "Ambition",
     "scenarios": ["highestamb", "highambition", "lowambition"],
     "labels":    ["Highest Ambition", "High Ambition", "Low Ambition"]},
    {"name": "Battery",
     "scenarios": ["batterieshigh", "batterieslow"],
     "labels":    ["High Battery Cost", "Low Battery Cost"]},
    # Solo groups — single future compared against base
    {"name": "Long_Duration_Storage",
     "scenarios": ["lds"],
     "labels":    ["Long Duration Storage"],
     "solo": True},
    {"name": "High_Transmission",
     "scenarios": ["hightx"],
     "labels":    ["High Transmission"],
     "solo": True},
]

# ********************************
# LOAD ALL DATA ONCE
# ********************************
cap_all       = pd.read_csv(os.path.join(DATA_DIR, "ALL_CASE_capacity_summary.csv"))
emissions_all = pd.read_csv(os.path.join(DATA_DIR, "ALL_CASE_load_emissions.csv"))
prices_all    = pd.read_csv(os.path.join(DATA_DIR, "ALL_CASE_prices.csv"))

SCENARIO_PREFIXES_SORTED = sorted(SCENARIO_PREFIXES, key=len, reverse=True)

def infer_scenario(case_name):
    cn = case_name.lower()
    for s in SCENARIO_PREFIXES_SORTED:
        if cn.startswith(s + "_") or cn == s:
            return s
    return None

def slice_scenario(df, scenario):
    mask = df["CaseName"].apply(lambda c: infer_scenario(c) == scenario)
    return df[mask].copy()

def make_case_labels(cases):
    out = {}
    for c in cases:
        scenario = infer_scenario(c) or ""
        suffix   = c[len(scenario)+1:] if scenario else c
        out[c]   = POLICY_LABELS.get(suffix.lower(), suffix)
    return out


# ********************************
# LEGEND HELPERS FOR EMISSIONS PLOTS
# ********************************

class _BlankHandler(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent,
                       width, height, fontsize, trans):
        from matplotlib.patches import Rectangle
        r = Rectangle((0, 0), 0, 0, visible=False)
        return [r]


def _build_emissions_legend(ax, handles, labels, wrap_width=28, fontsize=8,
                             bbox_to_anchor=(1.02, 1)):
    spaced_handles, spaced_labels = [], []
    blank = mpatches.Patch(visible=False)
    for handle, label in zip(handles, labels):
        lines = textwrap.wrap(label, width=wrap_width) or [""]
        spaced_handles.append(handle);  spaced_labels.append(lines[0])
        for cont in lines[1:]:
            spaced_handles.append(blank); spaced_labels.append("  " + cont)
        spaced_handles.append(blank);    spaced_labels.append("")
    ax.legend(spaced_handles, spaced_labels,
              bbox_to_anchor=bbox_to_anchor, loc="upper left",
              borderaxespad=0, fontsize=fontsize,
              handlelength=1.5, handletextpad=0.5, labelspacing=0.1,
              handler_map={mpatches.Patch: _BlankHandler()})


# ********************************
# POLICY KEY HELPERS
# ********************************

def wrap_labels(labels, width=32):
    return ["\n".join(textwrap.wrap(l, width)) for l in labels]

def wrap_policy_key(case_nums, case_labels, width=32):
    lines = []
    for c in case_nums:
        label   = f"{case_nums[c]}  {case_labels[c]}"
        wrapped = textwrap.wrap(label, width=width)
        lines.append(wrapped[0])
        for w in wrapped[1:]:
            lines.append("   " + w)
        lines.append(" ")
    return "\n".join(lines)


# ********************************
# CORE PLOT: DELTA CAPACITY vs BASE POLICY
# ********************************
def _draw_nj_vs_system_capacity(cap_df, ax, title, base_cap_df=None,
                                 include_base_policy=False,
                                 periods=None, policy_filter=None):
    if periods is None:
        periods = CAPACITY_PERIODS
    if policy_filter is None:
        policy_filter = CAPACITY_POLICY_FILTER

    nj_df  = cap_df[cap_df["Zone"] == "NJ1"].copy()
    sys_df = cap_df[cap_df["Zone"] == "System"].copy()
    has_system = not sys_df.empty

    if nj_df.empty:
        ax.set_title(title + "\n(no data)", fontsize=13); return

    if base_cap_df is not None:
        ref_nj  = base_cap_df[base_cap_df["Zone"] == "NJ1"].copy()
        ref_sys = base_cap_df[base_cap_df["Zone"] == "System"].copy()
    else:
        ref_nj = nj_df; ref_sys = sys_df

    def get_suffix(cn):
        s = infer_scenario(cn)
        if s: return cn[len(s):].lstrip("_").lower()
        parts = cn.split("_", 1)
        return parts[1].lower() if len(parts) > 1 else cn.lower()

    all_cases = sorted(dict.fromkeys(nj_df["CaseName"].tolist()), key=policy_sort_key)
    cases = all_cases if include_base_policy else [
        c for c in all_cases if get_suffix(c) != "base"
    ]
    if policy_filter is not None:
        pf = [p.lower() for p in policy_filter]
        cases = [c for c in cases if get_suffix(c) in pf]
    if not cases:
        ax.set_title(title + "\n(no data)", fontsize=13); return

    case_labels = make_case_labels(cases)

    def get_val(df, cn, tech, p):
        if cn is None: return 0.0
        row = df[df["CaseName"] == cn]
        col = f"{tech}_p{p}"
        return row[col].values[0] / 1000 if col in row.columns and len(row) > 0 else 0.0

    def ref_cn(case):
        if base_cap_df is None:
            for rc in ref_nj["CaseName"].tolist():
                if get_suffix(rc) == "base": return rc
            return None
        suffix = get_suffix(case)
        for rc in ref_nj["CaseName"].tolist():
            if get_suffix(rc) == suffix: return rc
        return None

    techs = sorted(set(
        c.rsplit("_p", 1)[0] for c in nj_df.columns
        if "_p" in c and c.rsplit("_p", 1)[-1] in ["1", "2", "3"]
    ))

    def has_delta(tech):
        for p in periods:
            for case in cases:
                nj_delta = abs(get_val(nj_df, case, tech, p) - get_val(ref_nj, ref_cn(case), tech, p))
                if nj_delta > 1e-6:
                    return True
                if has_system:
                    sys_delta = abs(get_val(sys_df, case, tech, p) - get_val(ref_sys, ref_cn(case), tech, p))
                    if sys_delta > 1e-6:
                        return True
        return False

    techs = [t for t in techs if has_delta(t)]

    nj_pos_bars, nj_neg_bars, sys_pos_bars, sys_neg_bars = [], [], [], []
    bar_labels, x_positions = [], []
    gap, bar_width, bar_spacing, current_x = 1, 0.3, 0.35, 0

    for p in periods:
        for case in cases:
            ref = ref_cn(case)
            nj_pos, nj_neg, sys_pos, sys_neg = {}, {}, {}, {}
            for tech in techs:
                nd = get_val(nj_df, case, tech, p) - get_val(ref_nj, ref, tech, p)
                nj_pos[tech] = max(nd, 0); nj_neg[tech] = min(nd, 0)
                if has_system:
                    sd = get_val(sys_df, case, tech, p) - get_val(ref_sys, ref, tech, p)
                    sys_pos[tech] = max(sd, 0); sys_neg[tech] = min(sd, 0)
                else:
                    sys_pos[tech] = sys_neg[tech] = 0.0
            nj_pos_bars.append(nj_pos);  nj_neg_bars.append(nj_neg)
            sys_pos_bars.append(sys_pos); sys_neg_bars.append(sys_neg)
            bar_labels.append(case); x_positions.append(current_x)
            current_x += bar_spacing
        current_x += gap

    nj_pos_df  = pd.DataFrame(nj_pos_bars,  index=x_positions)
    nj_neg_df  = pd.DataFrame(nj_neg_bars,  index=x_positions)
    sys_pos_df = pd.DataFrame(sys_pos_bars, index=x_positions)
    sys_neg_df = pd.DataFrame(sys_neg_bars, index=x_positions)

    def draw_stack(stack_df, start_bottoms, color_fn, hatch=None):
        bottoms = start_bottoms.copy()
        for tech in techs:
            ax.bar(stack_df.index, stack_df[tech].values, bottom=bottoms,
                   width=bar_width, color=color_fn(tech),
                   hatch=hatch, edgecolor="white" if hatch else None,
                   linewidth=0.3 if hatch else None,
                   label="_nolegend_", zorder=2)
            bottoms += stack_df[tech].values
        return bottoms

    zero = np.zeros(len(x_positions))
    nj_pos_tops = draw_stack(nj_pos_df, zero, lambda t: TECH_COLORS.get(t, "#AAAAAA"))
    if has_system:
        draw_stack(sys_pos_df, nj_pos_tops, lambda t: TECH_COLORS_LIGHT.get(t, "#DDDDDD"), hatch="////")
    nj_neg_tops = draw_stack(nj_neg_df, zero, lambda t: TECH_COLORS.get(t, "#AAAAAA"))
    if has_system:
        draw_stack(sys_neg_df, nj_neg_tops, lambda t: TECH_COLORS_LIGHT.get(t, "#DDDDDD"), hatch="////")

    ax.axhline(0, color="black", linewidth=0.8, zorder=3)
    if x_positions:
        ax.set_xlim(x_positions[0] - bar_width, x_positions[-1] + bar_width)

    case_nums = {case: str(i + 1) for i, case in enumerate(cases)}
    ax.set_xticks(x_positions)
    ax.set_xticklabels([case_nums[c] for c in bar_labels], fontsize=11)
    ax._policy_key_text = wrap_policy_key(case_nums, case_labels, width=32)
    ax._policy_key_nums = case_nums
    ax._case_labels     = case_labels

    # Store x_positions and bar_labels on ax for secondary axis use
    ax._bar_x_positions = x_positions
    ax._bar_labels      = bar_labels

    year_label_map = {1: "2030", 2: "2035", 3: "2045"}
    start = 0
    for p in periods:
        group_x = x_positions[start:start + len(cases)]
        if group_x:
            center = np.mean(group_x)
            ax.text(center, 0.98, year_label_map[p],
                    transform=ax.get_xaxis_transform(),
                    ha="center", va="top", fontsize=13, fontweight="bold")
        start += len(cases) + gap

    legend_handles = []
    for tech in techs:
        legend_handles.append(mpatches.Patch(
            facecolor=TECH_COLORS.get(tech, "#AAAAAA"), label=f"{tech} (NJ)"))
        if has_system:
            legend_handles.append(mpatches.Patch(
                facecolor=TECH_COLORS_LIGHT.get(tech, "#DDDDDD"), hatch="////",
                edgecolor="white", label=f"{tech} (System)"))
    ax._nj_sys_legend_handles = legend_handles

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel("Capacity Change vs. Base Policy Scenario (GW)", fontsize=13)
    ax.set_xlabel("Policy  (see key)", fontsize=12, style="italic")
    ax.grid(linestyle="--", alpha=0.4)
    ax.set_facecolor("#FFFFFF")


# ********************************
# CORE PLOT: EMISSIONS VS COST (per-scenario)
# ********************************
def _draw_emissions_vs_cost(em_df, pr_df, ax, title, period=3):
    merged = pd.merge(em_df, pr_df, on="CaseName").reset_index(drop=True)
    if merged.empty:
        ax.set_title(title + "\n(no data)", fontsize=11); return
    merged = merged.dropna(subset=[f"Total_System_Emissions_p{period}", f"Total_Price_p{period}"])
    if merged.empty:
        ax.set_title(title + "\n(no data yet)", fontsize=11); return
    merged = merged.iloc[
        sorted(range(len(merged)), key=lambda i: policy_sort_key(merged.iloc[i]["CaseName"]))
    ].reset_index(drop=True)

    base_row = None
    for _, row in merged.iterrows():
        if row["CaseName"][len(infer_scenario(row["CaseName"]) or ""):].lstrip("_").lower() == "base":
            base_row = row; break
    base_em     = base_row[f"Total_System_Emissions_p{period}"] if base_row is not None else 0.0
    case_labels = make_case_labels(merged["CaseName"].tolist())

    for i, row in merged.iterrows():
        ax.scatter(base_em - row[f"Total_System_Emissions_p{period}"],
                   row[f"Total_Price_p{period}"],
                   s=100, color=DOT_COLORS[i % len(DOT_COLORS)], zorder=3,
                   label=case_labels.get(row["CaseName"], row["CaseName"]))

    x = np.array([base_em - e for e in merged[f"Total_System_Emissions_p{period}"].values])
    y = merged[f"Total_Price_p{period}"].values
    if len(set(x)) > 1 and len(x) >= 2:
        try:
            m, b = np.polyfit(x, y, 1)
            xl = np.linspace(x.min(), x.max(), 100)
            ax.plot(xl, m * xl + b, color="gray", linewidth=1.5, linestyle="--", zorder=1)
            ax.annotate("", xy=(xl[-1], m*xl[-1]+b), xytext=(xl[-2], m*xl[-2]+b),
                        arrowprops=dict(arrowstyle="-|>", color="gray", lw=1.5))
        except np.linalg.LinAlgError:
            pass

    ax.axvline(0, color="black", linewidth=0.8, linestyle=":", zorder=1, alpha=0.6)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel("Emission Reduction vs. Base Policy (MT CO₂)", fontsize=10)
    ax.set_ylabel("Total Price ($/MWh)", fontsize=10)
    ax.grid(linestyle="--", alpha=0.4)
    ax.set_facecolor("#FFFFFF")


# ********************************
# CORE PLOT: PRICE COMPARISONS (line chart)
# ********************************
def _draw_price_comparisons(pr_df, axes, scenario_prefix, fig_title):
    compare_cases = {
        f"{scenario_prefix}_{s}": lbl
        for s, lbl in zip(COMPARE_CASES_SUFFIX, COMPARE_LABELS)
        if (pr_df["CaseName"] == f"{scenario_prefix}_{s}").any()
    }
    if len(compare_cases) < 2:
        print(f"  [!] Not enough cases for price comparison in {scenario_prefix}, skipping.")
        return False
    for ax, (case_name, case_title) in zip(axes, compare_cases.items()):
        row = pr_df[pr_df["CaseName"] == case_name].iloc[0]
        ax.set_facecolor("#FFFFFF")
        for label, (c1, c2, c3) in PRICE_COMPONENTS.items():
            if all(col in pr_df.columns for col in [c1, c2, c3]):
                ax.plot(YEARS, [row[c1], row[c2], row[c3]],
                        label=label, color=PRICE_COLORS[label],
                        linestyle=PRICE_LINE_STYLES[label],
                        marker="o", linewidth=2, markersize=7)
        ax.set_title(case_title, fontsize=9, fontweight="bold")
        ax.set_xticks(YEARS)
        ax.set_xlabel("Year", fontsize=11)
        ax.set_ylabel("Price ($/MWh)", fontsize=11)
        ax.grid(linestyle="--", alpha=0.4)
        ax.legend(fontsize=9)
    for ax in axes[len(compare_cases):]:
        ax.set_visible(False)
    return True


# ********************************
# PER-SCENARIO PLOTS
# ********************************
def plot_scenario(scenario_prefix):
    label    = SCENARIO_LABELS.get(scenario_prefix, scenario_prefix)
    fig_path = os.path.join(FUTURES_BASE, "SCENARIO_FIGURES", scenario_prefix.upper())
    os.makedirs(fig_path, exist_ok=True)

    cap_df = slice_scenario(cap_all,       scenario_prefix)
    em_df  = slice_scenario(emissions_all, scenario_prefix)
    pr_df  = slice_scenario(prices_all,    scenario_prefix)

    # --- Plot 1: NJ + System Capacity delta ---
    if not cap_df.empty:
        ref_df = None
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor("#FFFFFF")
        _draw_nj_vs_system_capacity(
            cap_df, ax,
            f"NJ & System Capacity Change vs. Base Policy Scenario — {label} Future",
            base_cap_df=ref_df)
        handles = getattr(ax, "_nj_sys_legend_handles", ax.get_legend_handles_labels()[0])
        lbls = wrap_labels([h.get_label() for h in handles], width=32)
        ax.legend(handles, lbls, bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=11)
        fig.canvas.draw()
        key_text = getattr(ax, "_policy_key_text", "")
        if key_text:
            legend = ax.get_legend()
            bbox = legend.get_window_extent(fig.canvas.get_renderer())
            ba   = bbox.transformed(ax.transAxes.inverted())
            ax.annotate("Policy Key:", xy=(ba.x0, ba.y0 - 0.02), xycoords="axes fraction",
                        fontsize=11, fontweight="bold", va="top", ha="left")
            ax.annotate(key_text, xy=(ba.x0, ba.y0 - 0.05), xycoords="axes fraction",
                        fontsize=11, va="top", ha="left", linespacing=1.1,
                        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#CCCCCC"),
                        annotation_clip=False)
        plt.tight_layout()
        plt.savefig(os.path.join(fig_path, "NJ_vs_System_Capacity.png"),
                    dpi=300, facecolor="#FFFFFF", bbox_inches="tight")
        plt.close()
        print(f"  ✓ NJ vs System capacity plot saved")
    else:
        print(f"  [!] No capacity data for {scenario_prefix}")

    # --- Plot 2: Emissions vs Cost (2045 and 2035) ---
    if not em_df.empty and not pr_df.empty:
        for period, year_label, filename in [
            (3, "2045", "Cost_vs_Emission_Reduction.png"),
            (2, "2035", "Cost_vs_Emission_Reduction_2035.png"),
        ]:
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor("#FFFFFF")
            _draw_emissions_vs_cost(em_df, pr_df, ax,
                                    f"Cost vs. Emission Reduction ({year_label}) — {label}",
                                    period=period)
            handles, lbls = ax.get_legend_handles_labels()
            _build_emissions_legend(ax, handles, lbls)
            plt.tight_layout()
            plt.savefig(os.path.join(fig_path, filename), dpi=300, bbox_inches="tight")
            plt.close()
            print(f"  ✓ Emissions vs cost plot saved ({year_label})")
    else:
        print(f"  [!] Missing emissions or prices data for {scenario_prefix}")

    # --- Plot 3: Price Comparisons ---
    if not pr_df.empty:
        ncols = 2
        nrows = (len(COMPARE_CASES_SUFFIX) + 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(10, 4 * nrows), sharey=True)
        axes = np.array(axes).flatten()
        fig.patch.set_facecolor("#FFFFFF")
        ok = _draw_price_comparisons(pr_df, axes, scenario_prefix,
                                     f"State and Regional Capacity Prices — {label}")
        if ok:
            fig.suptitle(f"State and Regional Capacity Prices — {label}",
                         fontsize=13, fontweight="bold", y=0.98)
            plt.tight_layout()
            plt.subplots_adjust(top=0.88)
            plt.savefig(os.path.join(fig_path, "NJ_Price_Compare.png"),
                        dpi=150, bbox_inches="tight")
            print(f"  ✓ Price comparison plot saved")
        plt.close()


# ********************************
# COMPARISON PLOT: PRICE vs DIRECT EMISSIONS
# Works for both paired groups and solo groups.
# For solo groups the base future is added as a reference series.
# ********************************

FUTURE_COLORS  = ["#48ABE8","#F29D13","#77B053","#F5867F","#9368B3","#9E5139","#393E41","#7CC5CC"]
FUTURE_MARKERS = ["o","s","^","D","v","P","X","*"]

# Color/marker reserved for the base reference series in solo plots
BASE_REF_COLOR  = "#888888"
BASE_REF_MARKER = "o"

def plot_emissions_comparison(group):
    is_solo = group.get("solo", False)

    if is_solo:
        plot_scenarios = ["base"] + group["scenarios"]
        plot_labels    = ["Base (reference)"] + group["labels"]
    else:
        plot_scenarios = group["scenarios"]
        plot_labels    = group["labels"]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # Collect all policy suffixes across every scenario being plotted
    all_policies = []
    for scenario in plot_scenarios:
        em_df  = slice_scenario(emissions_all, scenario)
        pr_df  = slice_scenario(prices_all, scenario)
        merged = pd.merge(em_df, pr_df, on="CaseName").reset_index(drop=True)
        merged = merged.dropna(subset=["Total_System_Emissions_p3", "Total_Price_p3"])
        for c in merged["CaseName"]:
            suffix = c[len(infer_scenario(c) or ""):].lstrip("_").lower()
            if suffix not in all_policies:
                all_policies.append(suffix)

    all_policies = sorted(all_policies, key=lambda s: POLICY_ORDER.index(s)
                          if s in POLICY_ORDER else len(POLICY_ORDER))
    policy_color = {p: DOT_COLORS[i % len(DOT_COLORS)] for i, p in enumerate(all_policies)}

    # ── draw base trendline as a reference on every plot ────────────────────
    # For solo plots this is handled naturally in the main loop (base is in
    # plot_scenarios). For paired plots we draw it here separately so it
    # appears behind the scenario points/lines without adding dots.
    if not is_solo:
        base_em_df  = slice_scenario(emissions_all, "base")
        base_pr_df  = slice_scenario(prices_all, "base")
        base_merged = pd.merge(base_em_df, base_pr_df, on="CaseName").reset_index(drop=True)
        base_merged = base_merged.dropna(subset=["Total_System_Emissions_p3", "Total_Price_p3"])
        if not base_merged.empty:
            bx = base_merged["Total_Price_p3"].values
            by = base_merged["Total_System_Emissions_p3"].values
            if len(set(bx)) > 1 and len(bx) >= 2:
                try:
                    m, b = np.polyfit(bx, by, 1)
                    xl   = np.linspace(bx.min(), bx.max(), 100)
                    ax.plot(xl, m*xl+b, color=BASE_REF_COLOR, linewidth=2,
                            linestyle=":", zorder=1)
                    ax.annotate("", xy=(xl[-1], m*xl[-1]+b), xytext=(xl[-2], m*xl[-2]+b),
                                arrowprops=dict(arrowstyle="-|>", color=BASE_REF_COLOR, lw=2))
                except np.linalg.LinAlgError:
                    pass

    # ── main loop: one pass per scenario ────────────────────────────────────
    for idx, (scenario, label) in enumerate(zip(plot_scenarios, plot_labels)):
        marker = FUTURE_MARKERS[idx % len(FUTURE_MARKERS)]

        if is_solo and scenario == "base":
            dot_alpha  = 0.55
            line_ls    = ":"
            line_color = BASE_REF_COLOR
        else:
            adj_idx    = idx - (1 if is_solo else 0)
            dot_alpha  = 1.0
            line_ls    = "--"
            line_color = FUTURE_COLORS[adj_idx % len(FUTURE_COLORS)]

        em_df  = slice_scenario(emissions_all, scenario)
        pr_df  = slice_scenario(prices_all, scenario)
        merged = pd.merge(em_df, pr_df, on="CaseName").reset_index(drop=True)
        merged = merged.dropna(subset=["Total_System_Emissions_p3", "Total_Price_p3"])
        if merged.empty:
            continue
        merged = merged.iloc[sorted(range(len(merged)),
                                    key=lambda i: policy_sort_key(merged.iloc[i]["CaseName"]))
                             ].reset_index(drop=True)
        case_labels = make_case_labels(merged["CaseName"].tolist())
        x = merged["Total_Price_p3"].values
        y = merged["Total_System_Emissions_p3"].values

        for i, row in merged.iterrows():
            suffix = row["CaseName"][len(infer_scenario(row["CaseName"]) or ""):].lstrip("_").lower()
            ax.scatter(row["Total_Price_p3"], row["Total_System_Emissions_p3"],
                       s=90, color=policy_color.get(suffix, "#AAAAAA"),
                       marker=marker, alpha=dot_alpha, zorder=3,
                       label=case_labels.get(row["CaseName"], row["CaseName"])
                             if idx == (1 if is_solo else 0) else "_nolegend_")

        if len(set(x)) > 1 and len(x) >= 2:
            try:
                m, b = np.polyfit(x, y, 1)
                xl   = np.linspace(x.min(), x.max(), 100)
                ax.plot(xl, m*xl+b, color=line_color, linewidth=2,
                        linestyle=line_ls, zorder=2, label=f"{label} trend")
                ax.annotate("", xy=(xl[-1], m*xl[-1]+b), xytext=(xl[-2], m*xl[-2]+b),
                            arrowprops=dict(arrowstyle="-|>", color=line_color, lw=2))
            except np.linalg.LinAlgError:
                pass

    # ── legend assembly ──────────────────────────────────────────────────────
    all_handles, all_labels_list = ax.get_legend_handles_labels()
    trend_h  = [h for h, l in zip(all_handles, all_labels_list) if l.endswith(" trend")]
    trend_l  = [l for l in all_labels_list if l.endswith(" trend")]
    policy_h = [h for h, l in zip(all_handles, all_labels_list)
                if l not in ("_nolegend_",) and not l.endswith(" trend")]
    policy_l = [l for l in all_labels_list
                if l not in ("_nolegend_",) and not l.endswith(" trend")]

    if is_solo:
        future_handles = [
            Line2D([0], [0], marker=FUTURE_MARKERS[i % len(FUTURE_MARKERS)],
                   color="gray", linestyle="None", markersize=7, label=lbl)
            for i, lbl in enumerate(plot_labels)
        ]
        combined_handles = future_handles + trend_h + policy_h
        combined_labels  = [h.get_label() for h in future_handles] + trend_l + policy_l
    else:
        # Shape entries for the scenario futures, plus the base reference line
        future_handles = [
            Line2D([0], [0], marker=FUTURE_MARKERS[i % len(FUTURE_MARKERS)],
                   color="gray", linestyle="None", markersize=7, label=lbl)
            for i, lbl in enumerate(plot_labels)
        ]
        base_ref_handle = Line2D([0], [0], color=BASE_REF_COLOR, linewidth=2,
                                 linestyle=":", label="Base (reference) trend")
        combined_handles = future_handles + [base_ref_handle] + trend_h + policy_h
        combined_labels  = ([h.get_label() for h in future_handles]
                            + ["Base (reference) trend"] + trend_l + policy_l)

    _build_emissions_legend(ax, combined_handles, combined_labels, fontsize=9)

    ax.set_xlabel("Total Price ($/MWh)", fontsize=12)
    ax.set_ylabel("Total System Emissions (MT CO₂)", fontsize=12)
    ax.set_title(f"Price vs. Emissions (2045) — {group['name']} Comparison",
                 fontsize=15, fontweight="bold")
    ax.grid(linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(COMPARISON_OUT, f"Comparison_{group['name']}_Emissions.png"),
                dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Emissions comparison saved for {group['name']}")

# ********************************
# COMPARISON PLOT: NJ + SYSTEM CAPACITY
# Works for both paired groups and solo groups.
# For the Ambition group, adds a secondary y-axis showing 2045 REC price
# (EAC_Price_p3) with a consistent scale across all subplots.
# ********************************

EAC_COLOR = "#C94040"   # deep red for the REC price overlay

def plot_nj_system_comparison(group):
    n         = len(group["scenarios"])
    is_ambition = (group["name"] == "Ambition")

    fig, axes = plt.subplots(1, n, figsize=(max(14, 14), 7), sharey=True)
    if n == 1: axes = [axes]
    fig.patch.set_facecolor("#FFFFFF")
    base_cap_df = slice_scenario(cap_all, "base")
    last_ax = axes[0]

    # ── draw capacity bars ───────────────────────────────────────────────────
    for ax, scenario, label in zip(axes, group["scenarios"], group["labels"]):
        cap_df = slice_scenario(cap_all, scenario)
        _draw_nj_vs_system_capacity(cap_df, ax, label, base_cap_df=base_cap_df,
                                    include_base_policy=True)
        last_ax = ax

    # ── Ambition: add EAC_Price_p3 secondary axis ───────────────────────────
    if is_ambition:
        # Pre-collect all EAC values across all subplots so the axis scale is uniform
        all_eac_values = []
        for scenario in group["scenarios"]:
            pr_df = slice_scenario(prices_all, scenario)
            if "EAC_Price_p3" in pr_df.columns:
                all_eac_values.extend(pr_df["EAC_Price_p3"].dropna().tolist())

        # Determine a shared y-range for the secondary axis, with a small margin
        if all_eac_values:
            eac_min = min(all_eac_values)
            eac_max = max(all_eac_values)
            margin  = max((eac_max - eac_min) * 0.12, 1.0)   # at least 1 $/MWh margin
            eac_ylim = (eac_min - margin, eac_max + margin)
        else:
            eac_ylim = (0, 1)

        for ax, scenario in zip(axes, group["scenarios"]):
            pr_df = slice_scenario(prices_all, scenario)
            if pr_df.empty or "EAC_Price_p3" not in pr_df.columns:
                # Still create a twinx so layout is consistent; just leave it blank
                ax2 = ax.twinx()
                ax2.set_ylim(eac_ylim)
                ax2.set_ylabel("2045 REC Price — EAC ($/MWh)", fontsize=11,
                               color=EAC_COLOR, labelpad=8)
                ax2.tick_params(axis="y", labelcolor=EAC_COLOR)
                continue

            # Retrieve the bar x-positions that _draw_nj_vs_system_capacity stored
            x_positions = getattr(ax, "_bar_x_positions", [])
            bar_labels  = getattr(ax, "_bar_labels", [])
            if not x_positions:
                continue

            # Match each bar position to a case name, then look up its EAC price
            eac_x, eac_y = [], []
            for xp, case in zip(x_positions, bar_labels):
                row = pr_df[pr_df["CaseName"] == case]
                if not row.empty and "EAC_Price_p3" in row.columns:
                    val = row["EAC_Price_p3"].values[0]
                    if pd.notna(val):
                        eac_x.append(xp)
                        eac_y.append(val)

            ax2 = ax.twinx()
            ax2.set_ylim(eac_ylim)
            ax2.set_ylabel("2045 REC Price — EAC ($/MWh)", fontsize=11,
                           color=EAC_COLOR, labelpad=8)
            ax2.tick_params(axis="y", labelcolor=EAC_COLOR)

            if eac_x:
                ax2.scatter(eac_x, eac_y, color=EAC_COLOR,
                    marker="D", s=40, zorder=5,
                    label="2045 REC Price (EAC)")
                # Only label the rightmost subplot's secondary axis
                # to avoid clutter; others still share the same tick scale.

        # Add a single legend entry for the EAC line (on the last subplot)
        eac_handle = Line2D([0], [0],
                    color=EAC_COLOR,
                    marker="D",
                    linestyle="None",
                    markersize=6,
                    label="2045 REC Price (EAC)")

    # ── shared technology legend ─────────────────────────────────────────────
    tech_handles = getattr(last_ax, "_nj_sys_legend_handles",
                           last_ax.get_legend_handles_labels()[0])

    if is_ambition and all_eac_values:
        # Append the EAC line handle to the tech legend
        combined_tech_handles = list(tech_handles) + [eac_handle]
        combined_tech_labels  = [h.get_label() for h in tech_handles] + ["2045 REC Price (EAC)"]
    else:
        combined_tech_handles = list(tech_handles)
        combined_tech_labels  = [h.get_label() for h in tech_handles]

    fig.legend(combined_tech_handles, combined_tech_labels,
               loc="lower center", fontsize=11, ncol=6,
               bbox_to_anchor=(0.5, -0.08), borderaxespad=0,
               title="Technology", title_fontsize=11, frameon=True)

    # ── policy key legend ────────────────────────────────────────────────────
    case_nums   = getattr(last_ax, "_policy_key_nums", {})
    case_labels = getattr(last_ax, "_case_labels", make_case_labels(list(case_nums.keys())))
    policy_handles = [mpatches.Patch(visible=False) for _ in case_nums]
    policy_lbls    = [f"{case_nums[c]}  {case_labels.get(c, c)}" for c in case_nums]
    fig.legend(policy_handles, policy_lbls,
               loc="lower center", fontsize=10, ncol=min(4, len(policy_lbls)),
               bbox_to_anchor=(0.5, -0.22), borderaxespad=0,
               title="Policy Key", title_fontsize=11, frameon=True,
               handlelength=0, handletextpad=0,
               handler_map={mpatches.Patch: _BlankHandler()}, columnspacing=3.0)

    # Title distinguishes solo from paired groups
    is_solo   = group.get("solo", False)
    group_lbl = group["labels"][0] if is_solo else f"{group['name']} Comparison"
    fig.suptitle(
        f"NJ & System Capacity Change vs. Base Future Scenario (Policy Fixed) — {group_lbl}",
        fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(os.path.join(COMPARISON_OUT,
                             f"Comparison_{group['name']}_NJ_vs_System_Capacity.png"),
                dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ NJ vs System capacity comparison saved for {group['name']}")


# ********************************
# HELPER: extract the five price components for one row
# ********************************
def _get_price_components(row, period):
    def col(name):
        key = f"{name}_p{period}"
        return row.get(key, 0.0) if key in row.index else 0.0

    return {
        "Energy":               col("Energy_Price"),
        "PJM Capacity":         col("PJM_Capacity_Price"),
        "NJ Clean Capacity":    col("NJ_Clean_Capacity_Price"),
        "Credits (EAC+MinCap)": col("EAC_Price") + col("MinCap_Price"),
        "Export Credits":       col("Export_Credit") * -1.0,  # negative — reduces consumer cost
    }


# ********************************
# COMPARISON PLOT: PRICE DECOMPOSITION
# ********************************
def plot_price_decomposition(group, period=3):
    year        = YEAR_MAP.get(period, period)
    scenarios   = group["scenarios"]
    labels      = group["labels"]
    n_scenarios = len(scenarios)

    # Collect all policy suffixes present across all scenarios in this group
    all_suffixes = []
    for scenario in scenarios:
        pr_df = slice_scenario(prices_all, scenario)
        for c in pr_df["CaseName"]:
            s      = infer_scenario(c) or ""
            suffix = c[len(s):].lstrip("_").lower()
            if suffix not in all_suffixes:
                all_suffixes.append(suffix)
    all_suffixes = sorted(all_suffixes,
                          key=lambda s: POLICY_ORDER.index(s) if s in POLICY_ORDER else len(POLICY_ORDER))

    n_policies  = len(all_suffixes)
    bar_width   = min(0.7 / max(n_scenarios, 1), 0.25)
    group_gap   = 0.6
    group_width = bar_width * n_scenarios

    fig, ax = plt.subplots(figsize=(max(10, 2.2 * n_policies), 7))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    group_centers = []

    for g_idx, suffix in enumerate(all_suffixes):
        group_start  = g_idx * (group_width + group_gap)
        group_center = group_start + group_width / 2 - bar_width / 2
        group_centers.append(group_center)

        for s_idx, scenario in enumerate(scenarios):
            pr_df  = slice_scenario(prices_all, scenario)
            case   = f"{scenario}_{suffix}"
            row_df = pr_df[pr_df["CaseName"] == case]
            if row_df.empty: continue

            hatch      = DECOMP_HATCHES[s_idx % len(DECOMP_HATCHES)]
            x_pos      = group_start + s_idx * bar_width
            pos_bottom = 0.0
            neg_bottom = 0.0
            comps      = _get_price_components(row_df.iloc[0], period)

            for comp_name, _, comp_color in PRICE_DECOMP_COMPONENTS:
                val = comps[comp_name]
                if val >= 0:
                    ax.bar(x_pos, val, bottom=pos_bottom,
                           width=bar_width * 0.88, color=comp_color,
                           hatch=hatch, edgecolor="white", linewidth=0.4,
                           label="_nolegend_", zorder=2)
                    pos_bottom += val
                else:
                    ax.bar(x_pos, val, bottom=neg_bottom,
                           width=bar_width * 0.88, color=comp_color,
                           hatch=hatch, edgecolor="white", linewidth=0.4,
                           label="_nolegend_", zorder=2)
                    neg_bottom += val

    ax.set_xticks(group_centers)
    ax.set_xticklabels(
        ["\n".join(textwrap.wrap(POLICY_LABELS.get(s, s), width=16)) for s in all_suffixes],
        fontsize=11)

    # Legend 1: price components (solid color swatches)
    comp_handles = [
        mpatches.Patch(facecolor=color, edgecolor="white", label=name)
        for name, _, color in PRICE_DECOMP_COMPONENTS
    ]
    leg1 = ax.legend(comp_handles, [h.get_label() for h in comp_handles],
                     title="Price Component", title_fontsize=11,
                     fontsize=10, loc="upper left",
                     bbox_to_anchor=(1.01, 1.0), borderaxespad=0, frameon=True)
    ax.add_artist(leg1)

    # Legend 2: future scenarios (hatch patterns on neutral grey)
    future_handles = [
        mpatches.Patch(facecolor="#BBBBBB",
                       hatch=DECOMP_HATCHES[i % len(DECOMP_HATCHES)],
                       edgecolor="white", label=lbl)
        for i, lbl in enumerate(labels)
    ]
    ax.legend(future_handles, [h.get_label() for h in future_handles],
              title="Future Scenario", title_fontsize=11,
              fontsize=10, loc="upper left",
              bbox_to_anchor=(1.01, 0.50), borderaxespad=0, frameon=True)

    ax.set_ylabel("Price ($/MWh)", fontsize=13)
    ax.set_title(f"Price Decomposition ({year}) — {group['name']}",
                 fontsize=14, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_xlim(-group_gap / 2,
                (n_policies - 1) * (group_width + group_gap) + group_width + group_gap / 2)

    plt.tight_layout()
    plt.savefig(os.path.join(COMPARISON_OUT,
                             f"Comparison_{group['name']}_Price_Decomposition.png"),
                dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Price decomposition saved for {group['name']}")


# ********************************
# RUN
# ********************************
print("=== Per-scenario plots ===")
for scenario_prefix in SCENARIO_PREFIXES:
    print(f"\nProcessing {scenario_prefix}...")
    plot_scenario(scenario_prefix)

print("\n=== Comparison group plots ===")

BASE_GROUP = {"name": "Base", "scenarios": ["base"], "labels": ["Base"], "solo": True}

for group in COMPARISON_GROUPS:
    print(f"\n--- {group['name']} ---")
    plot_emissions_comparison(group)
    plot_nj_system_comparison(group)
    plot_price_decomposition(group)

# Base-only price decomposition
print("\n--- Base (standalone price decomposition) ---")
plot_price_decomposition(BASE_GROUP)

print("\nDone! Scenario figures in:", os.path.join(FUTURES_BASE, "SCENARIO_FIGURES"))
print("Comparison figures in:", COMPARISON_OUT)