from utils import make_svg_map


print("Start")



out_folder = '/home/juju/gisco/census_2021_atlas/'
res = 1000
in_CSV = '/home/juju/geodata/census/out/ESTAT_Census_2021_V2_'+str(res)+'.csv'

make_svg_map(
    out_folder + 'map_age_EUR.svg',
    in_CSV,
    res,
    scale = 1/4500000,
    #width_mm = 841, height_mm = 1189,
    width_mm = 210, height_mm = 297,
    cx = 4300000, cy = 3300000,
    )

