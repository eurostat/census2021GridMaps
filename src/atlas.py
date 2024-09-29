from utils import make_svg_map, load_cells, combine_pdfs
import cairosvg
import fiona


print("Start")



out_folder = '/home/juju/gisco/census_2021_atlas/'

scale = 1/1200000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000

overlap_m = 20000
dx = width_m - overlap_m
dy = height_m - overlap_m

print("load cells")
cells = load_cells('/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv')
print(len(cells), "cells loaded")

print("load boundaries")
lines = fiona.open("assets/BN_1M.gpkg")
print(len(lines), "boundaries loaded")


cx0 = 990000
cy0 = 500000

pdfs = []
code = 1
for j in range(15, 0, -1):
    for i in range(30):

        print("make svg", i, j)
        file_name = out_folder + '/pages/page_'+str(code)+'_'+str(i)+'_'+str(j)
        ok = make_svg_map(
            cells,
            file_name+'.svg',
            1000,
            scale = scale,
            width_mm = width_mm, height_mm = height_mm,
            cx = cx0 + i*dx, cy = cy0 + j*dy,
            lines = lines
            )

        if not ok: continue

        print("make pdf", i, j)
        cairosvg.svg2pdf(url=file_name+'.svg', write_to=file_name+'.pdf')
        pdfs.append(file_name+'.pdf')

        code += 1


print("combine", len(pdfs), "pages")
combine_pdfs(pdfs, out_folder + "atlas.pdf")