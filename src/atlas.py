from utils import make_svg_map


print("Start")



out_folder = '/home/juju/gisco/census_2021_atlas/'

make_svg_map(
    out_folder + 'map_age_EUR.svg',
    '/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv',
    1000,
    scale = 1/4500000,
    #width_mm = 841, height_mm = 1189, #A0
    width_mm = 210, height_mm = 297, #A4
    cx = 4300000, cy = 3300000,
    )

