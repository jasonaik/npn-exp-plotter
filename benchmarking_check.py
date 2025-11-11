import datetime
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

def generate_benchmarking_linreg(input_file, output_file, npn_cols):
    df = pd.read_csv(input_file)

    df = df[:-2]

    # Define column names
    dronpa_col = 'cells/Single Cells/488nm525-40-A subset | Geometric Mean (FL9-A :: 488nm525-40-A)'
    
    # sns.set_theme(style="whitegrid", context="talk")

    for npn_col in npn_cols:

        # Create condition labels based on row number
        conditions = (["Light-0mM"] * 15 +
                    ["Light-10mM"] * 15 +
                    ["Dark-0mM"] * 15 +
                    ["Dark-10mM"] * 15)

        df["Condition"] = conditions
        df["Light/Dark"] = df["Condition"].str.split("-").str[0]
        df["NPN_mM"] = df["Condition"].str.split("-").str[1]

        # Set up 2×2 grid
        fig, axes = plt.subplots(2, 2, figsize=(12, 10), sharex=True, sharey=True)

        # Flatten axes for easy iteration
        axes = axes.flatten()

        # Define order
        condition_order = ["Light-0mM", "Light-10mM", "Dark-0mM", "Dark-10mM"]

        # Loop through each condition
        for ax, cond in zip(axes, condition_order):
            subset = df[df["Condition"] == cond]

            # Scatter + regression line
            sns.regplot(
                x=dronpa_col, y=npn_col, data=subset,
                scatter_kws={"s": 40, "alpha": 0.7, "edgecolor": "k", "linewidths": 0.3},
                line_kws={"color": "#0072B2", "lw": 2},
                ax=ax
            )

            # Linear regression stats
            slope, intercept, r_value, p_value, std_err = linregress(subset[dronpa_col], subset[npn_col])

            # Annotate
            ax.text(
                0.05, 0.95,
                f"Slope = {slope:.3f}\nIntercept = {intercept:.1f}\n$R^2$ = {r_value**2:.3f}\n$p$ = {p_value:.3f}",
                transform=ax.transAxes, fontsize=9, verticalalignment="top",
                bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
            )

            ax.set_title(cond.replace("-", ", "))
            ax.set_xlabel("Dronpa fluorescence (a.u.)")
            ax.set_ylabel("NPN fluorescence (a.u.)")
            ax.spines[['top','right']].set_visible(False)

        plt.tight_layout()
        plt.show()
        
        date = datetime.date.today()
        
        
        os.makedirs(f"plots/pdf/{date}", exist_ok=True)
        os.makedirs(f"plots/svg/{date}", exist_ok=True)
        
        channel = npn_col.split("::")[1].strip().split(" ")[0].split(")")[0]
        
        fig.savefig(
            f"plots/pdf/{date}/{output_file}-light-dark-{channel}.pdf",
            bbox_inches="tight",   # trims white space
            dpi=300,               # for raster elements (still vector overall)
            transparent=True       # if you want transparent background
        )
        
        fig.savefig(
            f"plots/svg/{date}/{output_file}-light-dark-{channel}.svg",
            bbox_inches="tight",   # trims white space
            dpi=300,               # for raster elements (still vector overall)
            transparent=True       # if you want transparent background
        )
    
if __name__ == "__main__":
    
    npn_cols = ['cells/Single Cells/488nm525-40-A subset | Geometric Mean (FL2-A :: 355nm450-45-A)', 'cells/Single Cells/488nm525-40-A subset | Geometric Mean (FL1-A :: 355nm405-30-A)']

    generate_benchmarking_linreg("data/06-Nov-2025 FlowJo table.csv", "06-11-25", npn_cols)