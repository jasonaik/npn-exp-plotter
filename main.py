import light_dark_plotter

row_names = ["ICR58_0", "ICR186_0", "ICR187_0", "ICR186+190_0", "ICR187+190_0", 
             "ICR58_10", "ICR186_10", "ICR187_10", "ICR186+190_10", "ICR187+190_10"]

column_names = ["cells/Single Cells/488nm525-40-A subset | Geometric Mean (FL1-A :: 355nm405-30-A)"]

y_label = "Geometric Mean"

file = "data/06-Nov-2025 FlowJo table.csv"

savefile = "06-11-25"
    
# light_dark = {
#     "01": {"condition": "Dark", "color": "#00f7ff"},
#     "02": {"condition": "Light", "color": "#8200c8"},
# }

light_dark = {
    "01": {"condition": "Light", "color": "#d86ecc"},
    "02": {"condition": "Dark", "color": "#bfbfbf"},
}


for col_name in column_names:
    light_dark_plotter.generate_light_dark_plot(file, savefile, col_name, y_label, row_names, light_dark)
