import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import sys
import os

NUM_REPS = 3
pd.set_option('display.max_columns', None)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],  
    "font.size": 10,                   
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

def generate_light_dark_plot(file_path, savefile, col_name, y_label, row_names, light_dark, filter):
    # Create plots folder (safe if exists)
    os.makedirs("plots", exist_ok=True)

    # Load & clean
    df = pd.read_csv(file_path)
    df = df.rename(columns={df.columns[0]: 'Well'})
    df = df[~df['Well'].isin(['Mean', 'SD'])].copy()

    # # e.g. "light A1" -> "light" 
    # df["prefix"] = df["Well"].str.split().str[0].str.lower()

    # numeric/2-char prefixes 
    df["prefix2"] = df["Well"].str[:2]  


    raw_by_prefix = {}
    summaries = []

    for prefix, meta in light_dark.items():
        condition = meta["condition"]
        color = meta["color"]

        # # e.g. "light A1" -> "light" 
        # d = df[df["prefix"] == prefix.lower()].copy()

        # numeric/2-char prefixes 
        d = df[df["prefix2"] == prefix].copy()

        if d.empty:
            continue

        # Group every 3 rows → 1 construct
        d["idx_in_prefix"] = range(len(d))
        d["group"] = d["idx_in_prefix"] // 3
        n_groups = d["group"].max() + 1

        if len(row_names) < n_groups:
            raise ValueError(f"row_names has {len(row_names)} items but prefix {prefix} needs {n_groups}.")
        d["WellLabel"] = d["group"].map(dict(enumerate(row_names)))

        raw_by_prefix[prefix] = d

        # Summary per construct
        summ = (
            d.groupby("group", as_index=False)[col_name]
              .agg(mean="mean", std="std")
              .assign(prefix=prefix, condition=condition, color=color)
        )
        summ["WellLabel"] = summ["group"].map(dict(enumerate(row_names)))
        summaries.append(summ)

    if not summaries:
        print("No data matched the provided prefixes.")
        return

    combined = pd.concat(summaries, ignore_index=True)

    # Prepare for plotting
    conditions_present = [light_dark[p]["condition"] for p in raw_by_prefix.keys()]
    unique_conditions = list(dict.fromkeys(conditions_present))
    wells = combined["WellLabel"].drop_duplicates().tolist()
    x = np.arange(len(wells))
    n_conditions = len(unique_conditions)
    width = 0.8 / n_conditions

    fig, ax = plt.subplots(figsize=(12, 6))

    # Assign one color per condition (take first prefix's color that matches)
    cond_colors = {}
    for prefix, meta in light_dark.items():
        cond = meta["condition"]
        if cond not in cond_colors:
            cond_colors[cond] = meta["color"]

    # Plot grouped bars
    for i, cond in enumerate(unique_conditions):
        sub = combined[combined["condition"] == cond].copy()
        sub = sub.set_index("WellLabel").reindex(wells).reset_index()
        color = cond_colors[cond]
        x_offset = x + (i - (n_conditions - 1) / 2) * width

        ax.bar(
            x_offset, sub["mean"],
            yerr=sub["std"],
            width=width,
            color=color,
            edgecolor="black",
            alpha=0.5, capsize=4, linewidth=0.6,
            label=cond,
            error_kw=dict(elinewidth=0.8, capthick=0.8)
        )

        # Overlay dots (replicates)
        jitter = 0.06
        dot_size = 25
        for prefix, meta in light_dark.items():
            if meta["condition"] != cond:
                continue
            d_raw = raw_by_prefix[prefix]
            grp_to_well = d_raw.drop_duplicates("group")[["group", "WellLabel"]].set_index("group")["WellLabel"]

            for gi, well_label in enumerate(wells):
                groups_for_well = grp_to_well[grp_to_well == well_label].index.tolist()
                if not groups_for_well:
                    continue
                g = groups_for_well[0]
                vals = d_raw.loc[d_raw["group"] == g, col_name].values
                ax.scatter(
                    np.repeat(x_offset[gi], len(vals)) + np.random.uniform(-jitter, jitter, len(vals)),
                    vals,
                    color=color,
                    s=dot_size, alpha=1, zorder=3
                )

    # Format axes and legend
    ax.set_xticks(x)
    ax.set_xticklabels(wells, fontsize=12)
    ax.set_xlabel("Construct", fontsize=13, labelpad=8)
    ax.set_ylabel(f"{y_label} Fluorescence Intensity (a.u.)", fontsize=13, labelpad=8)
    ax.legend(frameon=False, fontsize=12, loc="center left", bbox_to_anchor=(1, 0.5))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.show()
    
    date = datetime.date.today()
    
    
    os.makedirs(f"plots/pdf/{date}", exist_ok=True)
    os.makedirs(f"plots/svg/{date}", exist_ok=True)
    
    fig.savefig(
        f"plots/pdf/{date}/{savefile}-light-dark-{y_label}-{filter}.pdf",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )
    
    fig.savefig(
        f"plots/svg/{date}/{savefile}-light-dark-{y_label}-{filter}.svg",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )



if __name__ == "__main__":
    row_names = ["ICR58 + ICR190", "ICR66 + ICR190", "ICR185 + ICR190", "ICR186 + ICR190", "ICR187 + ICR190", "ICR188 + ICR190"]
    # row_names = ["ICR58", "ICR66", "ICR186", "ICR187", "ICR188"]
    
    column_names = ["cells/Single Cells/355nm405-30-A subset | Geometric Mean (FL1-H :: 355nm405-30-H)"]
    
    y_label = "Geometric Mean"
    
    filter = "355nm405-30-A"
    
    file = "data/28-Oct-2025 FlowJo table.csv"
    
    savefile = "28-10-25"
    
# light_dark = {
#     "01": {"condition": "Dark", "color": "#00f7ff"},
#     "02": {"condition": "Light", "color": "#8200c8"},
# }

light_dark = {
    "02": {"condition": "Light", "color": "#d86ecc"},
    "01": {"condition": "Dark", "color": "#bfbfbf"},
}


for col_name in column_names:
    generate_light_dark_plot(file, savefile, col_name, y_label, row_names, light_dark, filter)
