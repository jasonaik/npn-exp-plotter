import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import sys

NUM_REPS = 3

def generate_wash_bar_plot(file_path, col_name, y_label, row_names):
    # Column name for fluorescence values
    value_col = f"{col_name}"

    df = pd.read_csv(file_path)

    df = df.rename(columns={df.columns[0]: 'Well'})
    
    df = df[~df['Well'].isin(['Mean', 'SD'])]
    
    df["index"] = range(len(df))
    df["group"] = df["index"] // 3
    df["Well"] = [row_names[g] for g in df["group"]]
    
    result = df.groupby("group", as_index=False)[col_name].agg(['mean', 'std'])
    
    result["Well"] = [row_names[g] for g in result['group']]
    
    pd.set_option('display.max_columns', None)
    
    print(result)    

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial"],  
        "font.size": 10,                   
        "axes.labelsize": 12,
        "axes.titlesize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })

    # Positions and bar width
    x = np.arange(len(result["Well"]))
    width = 0.35

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(
        x - width/2, result["mean"],
        yerr=[result["std"]],
        width=width,
        color="#d86ecc", edgecolor="black",
        alpha=0.6, capsize=5, linewidth=0.5, 
        error_kw=dict(elinewidth=0.8, capthick=0.8)
    )

    # Overlay individual data points
    jitter = 0.07   # horizontal spread for visibility
    dot_size = 25   # point size
    dot_alpha = 1 # transparency

    for i, well in enumerate(result["Well"]):

        vals = df.loc[df["Well"] == well, value_col].values

        ax.scatter(
            np.repeat(i - width/2, len(vals)) +
            np.random.uniform(-jitter, jitter, len(vals)),
            vals,
            color="#d86ecc", s=dot_size, alpha=dot_alpha, zorder=1
        )

    ax.set_xticks(x)
    ax.set_xticklabels(result["Well"], fontsize=12)
    ax.set_xlabel("Construct", fontsize=13, labelpad=10)
    ax.set_ylabel(f"{y_label} Fluorescence Intensity (a.u.)", fontsize=13, labelpad=10)
    # ax.set_title(f"Difference in {col_name} Fluorescence Intensity by Wash", fontsize=15, pad=15)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", which="major", labelsize=11)

    # Add subtle horizontal gridlines
    ax.yaxis.grid(True, linestyle="-", linewidth=0.8, alpha=0.4)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.show()
    
    date = datetime.date.today()

    os.makedirs(f"plots/pdf/{date}", exist_ok=True)
    os.makedirs(f"plots/svg/{date}", exist_ok=True)
    
    fig.savefig(
        f"plots/pdf/{date}/16-10-wash-results-{y_label}-{filter}.pdf",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )
    
    fig.savefig(
        f"plots/svg/{date}/16-10-wash-results-{y_label}-{filter}.svg",
        bbox_inches="tight",   # trims white space
        dpi=300,               # for raster elements (still vector overall)
        transparent=True       # if you want transparent background
    )



if __name__ == "__main__":
    row_names = ["ICR58 + 110", "ICR66 + 110", "ICR185 + 190", "ICR186 + 190", "ICR187 + 190", "ICR188 + 190"]

    column_names = ["cells/Single Cells/355nm450-45-H subset | Geometric Mean (FL2-A :: 355nm450-45-A)"]
    
    y_label = "Geometric Mean"
    
    file = "data/test.csv"

    for col_name in column_names:
        generate_wash_bar_plot(file, col_name, y_label, row_names)
