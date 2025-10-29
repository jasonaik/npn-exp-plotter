import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

NUM_REPS = 3

def generate_wash_bar_plot(col_name):
    # Column name for fluorescence values
    value_col = f"cells/Single Cells | {col_name} (FL2-H :: 355nm450-45-H)"

    df = pd.read_csv("data/14-10-flowjo-data.csv")

    df = df.rename(columns={df.columns[0]: 'Well'})
    df = df[:-2]

    first_col = df.columns[0]
    df = df.rename(columns={first_col: 'WellRaw'})
    df['Well'] = df['WellRaw'].astype(str).str.replace(r'\.fcs$', '', regex=True).str.strip()

    # icr_66 is empty vector, icr_58 is OMP
    icr_66_0  = df.loc[df['Well'].str[0].eq('A')].copy()
    icr_66_10 = df.loc[df['Well'].str[0].eq('C')].copy()
    icr_58_0  = df.loc[df['Well'].str[0].eq('B')].copy()
    icr_58_10 = df.loc[df['Well'].str[0].eq('D')].copy()

    for d in [icr_66_0, icr_66_10, icr_58_0, icr_58_10]:
        d['Col'] = d['Well'].str.extract(r'(\d+)$').astype(int)
        d['Washes'] = ((d['Col'] - 1) // NUM_REPS) 


    def summarize_groups(df, value_col=f"cells/Single Cells | {col_name} (FL2-H :: 355nm450-45-H)"):
        summary = df.groupby('Washes')[value_col].agg(['mean', 'std']).reset_index()
        return summary

    sum_66_0  = summarize_groups(icr_66_0)
    sum_66_10 = summarize_groups(icr_66_10)
    sum_58_0  = summarize_groups(icr_58_0)
    sum_58_10 = summarize_groups(icr_58_10)

    df_58_diff = sum_58_10[["Washes"]].copy()
    df_58_diff['mean_diff'] = sum_58_10["mean"] - sum_58_0["mean"]
    df_58_diff['std_combined'] = (sum_58_10['std']**2 + sum_58_0['std']**2)**0.5

    df_66_diff = sum_66_10[["Washes"]].copy()
    df_66_diff['mean_diff'] = sum_66_10["mean"] - sum_66_0["mean"]
    df_66_diff['std_combined'] = (sum_66_10['std']**2 + sum_66_0['std']**2)**0.5
        

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial"],  
        "font.size": 10,                   
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 9,
    })

    # Positions and bar width
    x = np.arange(len(df_66_diff["Washes"]))
    width = 0.35

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(
        x - width/2, df_66_diff["mean_diff"],
        yerr=[df_66_diff["std_combined"]],
        width=width, label="Empty Vector",
        color="#BFBFBF", edgecolor="black",
        alpha=0.6, capsize=5, linewidth=0.5, 
        error_kw=dict(elinewidth=0.8, capthick=0.8)
    )
    bars2 = ax.bar(
        x + width/2, df_58_diff["mean_diff"],
        yerr=df_58_diff["std_combined"],
        width=width, label="OMP",
        color="#d86ecc", edgecolor="black",
        alpha=0.6, capsize=5, linewidth=0.5, 
        error_kw=dict(elinewidth=0.8, capthick=0.8)
    )


    # Overlay individual data points
    jitter = 0.07   # horizontal spread for visibility
    dot_size = 25   # point size
    dot_alpha = 1 # transparency

    for i, wash in enumerate(df_66_diff["Washes"]):

        # === Empty Vector (icr_66): difference (10 mM - 0 mM) ===
        vals_0mM = icr_66_0.loc[icr_66_0["Washes"] == wash, value_col].values
        vals_10mM = icr_66_10.loc[icr_66_10["Washes"] == wash, value_col].values
        diffs_66 = vals_10mM - vals_0mM

        # Scatter (Empty Vector, gray)
        ax.scatter(
            np.repeat(i - width/2, len(diffs_66)) +
            np.random.uniform(-jitter, jitter, len(diffs_66)),
            diffs_66,
            color="#BFBFBF", s=dot_size, alpha=dot_alpha, zorder=1
        )

        # === OMP (icr_58): difference (10 mM - 0 mM) ===
        vals_0mM = icr_58_0.loc[icr_58_0["Washes"] == wash, value_col].values
        vals_10mM = icr_58_10.loc[icr_58_10["Washes"] == wash, value_col].values
        diffs_58 = vals_10mM - vals_0mM

        # Scatter (OMP, pink)
        ax.scatter(
            np.repeat(i + width/2, len(diffs_58)) +
            np.random.uniform(-jitter, jitter, len(diffs_58)),
            diffs_58,
            color="#d86ecc", s=dot_size, alpha=dot_alpha, zorder=1
        )

    ax.set_xticks(x)
    ax.set_xticklabels(df_66_diff["Washes"], fontsize=12)
    ax.set_xlabel("Washes", fontsize=13, labelpad=10)
    ax.set_ylabel(f"Δ {col_name} Fluorescence Intensity (a.u.)", fontsize=13, labelpad=10)
    # ax.set_title(f"Difference in {col_name} Fluorescence Intensity by Wash", fontsize=15, pad=15)

    ax.legend(frameon=False, fontsize=12, loc="center left", bbox_to_anchor=(1, 0.5))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", which="major", labelsize=11)

    # Add subtle horizontal gridlines
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.show()

    fig.savefig(
        f"plots/pdf/16-10-wash-results-{col_name}.pdf",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )
    
    fig.savefig(
        f"plots/svg/16-10-wash-results-{col_name}.svg",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )



if __name__ == "__main__":
    pass
