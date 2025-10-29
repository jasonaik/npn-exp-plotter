import washes_comparison

column_names = ["Mean", "Median", "Geometric Mean", "Mode"]

for col_name in column_names:
    washes_comparison.generate_wash_bar_plot(col_name)
