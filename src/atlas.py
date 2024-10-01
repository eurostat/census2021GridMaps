from atlas_utils import make_svg_map, combine_pdfs, make_index_page
import cairosvg
import concurrent.futures


print("Start")

#TODO
#decompose make svg and to_pdf
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
    CODE = 1
    def __init__(self, x: float, y: float, i: int = None, j: int = None, title: str = None):
        self.code = Page.CODE
        Page.CODE += 1
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.title = title



pages = []

xmi = 2500000; ymi = 1334600
xma = 6107000; yma = 5450000

def make_sub_row(j, ri, ox, oy, dx):
    for i in ri:
        ox_ =0; oy_ = 0
        if i==6 and j==6: oy_ = -300000
        if i==7 and j==6: oy_ = -100000
        pages.append(Page(xmi + i*dx + ox + ox_, ymi + j*dy + oy + oy_, i, j, str(i)+"_"+str(j)))

for j in range(6, 5, -1):
    if   j==12: make_sub_row(j, range(9, 12, 1), 90000, 0, dx)
    elif j==11: make_sub_row(j, range(9, 13, 1), 5000, 0, dx)
    elif j==10: make_sub_row(j, range(8, 14, 1), -50000, 0, dx)
    elif  j==9: make_sub_row(j, range(7, 13, 1), 85000, 0, dx)
    elif  j==8: make_sub_row(j, range(7, 14, 1), 0, 0, dx)
    elif  j==7:
        make_sub_row(j, range(2, 4, 1), 80000, -40000, dx)
        make_sub_row(j, range(8, 14, 1), 0, 0, dx)
    elif  j==6:
        #make_sub_row(j, range(2, 4, 1), 50000, 150000, dx)
        make_sub_row(j, range(6, 14, 1), -100000, 0, dx)
    else: make_sub_row(j, range(0, 17, 1), 0, 0, dx)



''''
#cyprus
pages.append(Page(code, 6421000, 1639000, title="Cyprus")); code+=1

#acores
pages.append(Page(code, 952995, 2764729, title="Açores")); code+=1
pages.append(Page(code, 1149886, 2516476, title="Açores")); code+=1
pages.append(Page(code, 1296216, 2313164, title="Açores")); code+=1

#madeira
pages.append(Page(code, 1847000, 1521000, title="Madeira")); code+=1

#canaries
pages.append(Page(code, 1660000, 1010000, title="Canarias")); code+=1
pages.append(Page(code, 1830000, 1010000, title="Canarias")); code+=1
pages.append(Page(code, 1955151, 1010000, title="Canarias")); code+=1
'''

print(len(pages), "pages")


pdfs = []
#indp = make_index_page(pages)
#pdfs.append(indp)


#print("load cells")
#cells = load_cells('/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.csv')
#print(len(cells), "cells loaded")


# function to make a page
def make_page(page):
    print("page", page.code, page.title)

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

    if not ok:
        print("WARNING: useless page", page.title)
        return

    #print("make pdf")
    cairosvg.svg2pdf(url=file_name+'.svg', write_to=file_name+'.pdf')

    #print("page", page.code, "done")

    #pdfs.append(file_name+'.pdf')
    return file_name+'.pdf'


#for page in pages: make_page(page)



#launch parallel computation   
with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_to_use) as executor:
    tasks_to_do = {executor.submit(make_page, page): page for page in pages}

    # merge task outputs
    for task_output in concurrent.futures.as_completed(tasks_to_do):
        out = task_output.result()
        if(out==None): continue
        pdfs.append(out)

    #sort pages
    pdfs.sort(key = lambda pdf: int(pdf.replace(out_folder + "pages/","").replace(".pdf","")))

    print("combine", len(pdfs), "pages")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")

