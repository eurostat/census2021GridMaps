from utils import make_svg_map, load_cells, combine_pdfs
import cairosvg


print("Start")



out_folder = '/home/juju/gisco/census_2021_atlas/'

scale = 1/1000000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000

overlap = 0.1

cx0 = 4300000
cy0 = 3300000
dx = width_mm * (1-2*overlap)
dy = height_m * (1-2*overlap)

print("load cells")
cells = load_cells('/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv')
print(len(cells), "cells loaded")

pdfs = []
i=0
for j in range(10):

    print("make svg", i, j)
    file_name = out_folder + 'map_age_EUR_'+str(i)+'_'+str(j)
    ok = make_svg_map(
        cells,
        file_name+'.svg',
        1000,
        scale = scale,
        width_mm = width_mm, height_mm = height_mm,
        cx = cx0 + i*dx, cy = cy0 + j*dy,
        bn_scale = "3M"
        )

    if not ok: continue

    print("make pdf", i, j)
    cairosvg.svg2pdf(url=file_name+'.svg', write_to=file_name+'.pdf')
    pdfs.append(file_name+'.pdf')


combine_pdfs(pdfs, out_folder + "atlas.pdf")