import basic_plotter

row_names = ["ICR58 + 110", "ICR66 + 110", "ICR185 + 190", "ICR186 + 190", "ICR187 + 190", "ICR188 + 190"]

column_names = ["cells/Single Cells/355nm450-45-H subset | Geometric Mean (FL2-A :: 355nm450-45-A)"]

file = "data/28-Oct-2025-dronpa-185-188-190.csv"

for col_name in column_names:
    basic_plotter.generate_wash_bar_plot(col_name, file)
