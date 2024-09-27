from utils import make_svg_map, load_cells


print("Start")



out_folder = '/home/juju/gisco/census_2021_atlas/'

scale = 1/1000000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000

overlap = 0.15

cx = 4300000
cy = 3300000

print("load cells")
cells = load_cells('/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv')
print(len(cells), "cells loaded")

print("make svg", cx, cy)
make_svg_map(
    cells,
    out_folder + 'map_age_EUR.svg',
    1000,
    scale = scale,
    width_mm = width_mm, height_mm = height_mm,
    cx = cx, cy = cy,
    bn_scale = "3M"
    )


print(len(cells), "cells left")
