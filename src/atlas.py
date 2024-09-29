from atlas_utils import make_svg_map, load_cells, combine_pdfs
import cairosvg
import fiona


print("Start")

#TODO
#show code on page
#parallel
#load labels and bn using spatial index
#show assemply table
#better define assembly table: function to generate it
#euronym for non greek characters
#road network in background ? no...



out_folder = '/home/juju/gisco/census_2021_atlas/'

scale = 1/1200000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000

overlap_m = 25000
dx = width_m - overlap_m
dy = height_m - overlap_m


print("Make pages index")
#print(dx, dy)

class Page:
    def __init__(self, code: int, x: float, y: float, i: int = None, j: int = None):
        self.code = code
        self.x = x
        self.y = y
        self.i = i
        self.j = j

cx0 = 990000
cy0 = 500000
code = 1
pages = []
for j in range(14, 0, -1):
    for i in range(30):
        cx = cx0 + i*dx
        cy = cy0 + j*dy
        p = Page(code, cx, cy, i, j)
        pages.append(p)
        code += 1

print(len(pages), "pages")




print("load cells")
cells = load_cells('/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv')
print(len(cells), "cells loaded")

print("load boundaries")
lines = fiona.open("assets/BN_1M.gpkg")
print(len(lines), "boundaries loaded")

print("load labels")
labels = fiona.open("assets/labels.gpkg")
print(len(labels), "labels loaded")



pdfs = []
for page in pages:
    print("page", page.code)

    file_name = out_folder + '/pages/page_'+str(page.code)
    ok = make_svg_map(
        cells,
        file_name+'.svg',
        1000,
        scale = scale,
        width_mm = width_mm, height_mm = height_mm,
        cx = page.x, cy=page.y,
        lines = lines,
        labels=labels,
        title = "page " + str(page.code) + " - i=" + str(page.i) + ", j=" + str(page.j)
        )

    if not ok: continue

    #print("make pdf")
    cairosvg.svg2pdf(url=file_name+'.svg', write_to=file_name+'.pdf')
    pdfs.append(file_name+'.pdf')

    print("done")


print("combine", len(pdfs), "pages")
combine_pdfs(pdfs, out_folder + "atlas.pdf")

