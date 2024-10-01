from atlas_utils import make_svg_map, combine_pdfs
import cairosvg
import concurrent.futures


print("Start")

#TODO
#show assemply table
#better define assembly table: function to generate it
#euronym for non greek characters
#road network in background ? no...


num_processors_to_use = 1

out_folder = '/home/juju/gisco/census_2021_atlas/'

scale = 1/1200000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000

overlap_m = 30000
dx = width_m - overlap_m
dy = height_m - overlap_m


print("Make pages index")
#print(dx, dy)

class Page:
    def __init__(self, code: int, x: float, y: float, i: int = None, j: int = None, title: str = None):
        self.code = code
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.title = title


pages = []
code = 1

''''
cx0 = 990000
cy0 = 500000
for j in range(15, 0, -1):
    for i in range(30):
        cx = cx0 + i*dx
        cy = cy0 + j*dy
        p = Page(code, cx, cy, i, j)
        pages.append(p)
        code += 1
'''


xmi = 2500000
ymi = 1334600
xma = 6107000
yma = 5450000
for j in range(10, 8, -1):
    for i in range(0, 5, 1):
        pages.append(Page(code, xmi+i*dx, ymi+j*dy, str(i)+"_"+str(j))); code+=1


#acores
pages.append(Page(code, 952995, 2764729, "Açores")); code+=1
pages.append(Page(code, 1149886, 2516476, "Açores")); code+=1
pages.append(Page(code, 1296216, 2313164, "Açores")); code+=1

#madeira
pages.append(Page(code, 1847000, 1521000, "Madeira")); code+=1

#canaries
pages.append(Page(code, 1660000, 1010000, "Canarias")); code+=1
pages.append(Page(code, 1830000, 1010000, "Canarias")); code+=1
pages.append(Page(code, 1955151, 1010000, "Canarias")); code+=1

#cyprus
pages.append(Page(code, 6421000, 1639000, "Cyprus")); code+=1

print(len(pages), "pages")



#print("load cells")
#cells = load_cells('/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv')
#print(len(cells), "cells loaded")


# function to make a page
def make_page(page):
    print("page", page.code)

    file_name = out_folder + 'pages/'+str(page.code)
    ok = make_svg_map(
        "/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.gpkg",
        file_name+'.svg',
        1000,
        scale = scale,
        width_mm = width_mm, height_mm = height_mm,
        cx = page.x, cy=page.y,
        boundaries_file = "assets/BN_1M.gpkg",
        labels_file = "assets/labels.gpkg",
        title = "page=" + str(page.code) + "  i=" + str(page.i) + "  j=" + str(page.j)
        )

    if not ok: return

    #print("make pdf")
    cairosvg.svg2pdf(url=file_name+'.svg', write_to=file_name+'.pdf')

    print("page", page.code, "done")

    #pdfs.append(file_name+'.pdf')
    return file_name+'.pdf'


#for page in pages: make_page(page)



#launch parallel computation   
with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_to_use) as executor:
    tasks_to_do = {executor.submit(make_page, page): page for page in pages}

    # merge task outputs
    pdfs = []
    for task_output in concurrent.futures.as_completed(tasks_to_do):
        out = task_output.result()
        if(out==None): continue
        pdfs.append(out)

    #sort pages
    pdfs.sort(key = lambda pdf: int(pdf.replace(out_folder + "pages/","").replace(".pdf","")))

    print("combine", len(pdfs), "pages")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")

