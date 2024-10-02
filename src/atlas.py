from atlas_utils import make_svg_map, combine_pdfs, make_index_page
import cairosvg
import concurrent.futures


print("Start")

#TODO
#decompose make svg and to_pdf
#code on pages
#20km to the north ?
#improve index page
#page title and legend
#euronym for non greek characters
#check greek names


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
        if i==3 and j==5: oy_ = -130000
        if i==13 and j==5: oy_ = -100000
        if i==14 and j==5: oy_ = -100000
        pages.append(Page(xmi + i*dx + ox + ox_, ymi + j*dy + oy + oy_, i, j, str(i)+"_"+str(j)))

for j in range(12, -1, -1):
    if   j==12: make_sub_row(j, range(9, 12, 1), 90000, 0, dx)
    elif j==11: make_sub_row(j, range(9, 13, 1), 5000, 0, dx)
    elif j==10: make_sub_row(j, range(8, 14, 1), -50000, 0, dx)
    elif  j==9: make_sub_row(j, range(7, 13, 1), 85000, 0, dx)
    elif  j==8: make_sub_row(j, range(7, 14, 1), 0, 0, dx)
    elif  j==7:
        make_sub_row(j, range(2, 4, 1), 80000, -40000, dx)
        make_sub_row(j, range(8, 14, 1), 0, 0, dx)
    elif  j==6:
        make_sub_row(j, range(2, 4, 1), 50000, 150000, dx)
        make_sub_row(j, range(6, 14, 1), -100000, 0, dx)
    elif  j==5: make_sub_row(j, range(3, 15, 1), 120000, 0, dx)
    elif  j==4: make_sub_row(j, range(4, 16, 1), 0, 0, dx)
    elif  j==3: make_sub_row(j, range(1, 15, 1), 0, 0, dx)
    elif  j==2: make_sub_row(j, range(1, 16, 1), 0, 0, dx)
    elif  j==1: make_sub_row(j, range(1, 17, 1), 0, 0, dx)
    elif  j==0:
        make_sub_row(j, range(3, 4, 1), 0, 0, dx)
        make_sub_row(j, range(9, 11, 1), 0, 0, dx)
        make_sub_row(j, range(14, 16, 1), 0, 0, dx)

#cyprus
pages.append(Page(6421000, 1639000, title="Cyprus"))

#acores
pages.append(Page(952995, 2764729, title="Açores"))
pages.append(Page(1149886, 2516476, title="Açores"))
pages.append(Page(1296216, 2313164, title="Açores"))

#madeira
pages.append(Page(1847000, 1521000, title="Madeira"))

#canaries
pages.append(Page(1640000, 1080000, title="Canarias"))
pages.append(Page(1830000, 1080000, title="Canarias"))
pages.append(Page(1955151, 1080000, title="Canarias"))

print(len(pages), "pages")

index_file = out_folder + 'index'
make_index_page(
    pages,
    "assets/BN_60M.gpkg",
    index_file + '.svg',
    width_m,
    height_m
)

#cairosvg.svg2pdf(url=index_file+'.svg', write_to=index_file+'.pdf')

#exit()


def make_svg():

    # function to make a page
    def make_page(page):
        print("page", page.code, page.title)

        make_svg_map(
            "/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.gpkg",
            out_folder + 'pages_svg/'+str(page.code)+".svg",
            1000,
            scale = scale,
            width_mm = width_mm, height_mm = height_mm,
            cx = page.x, cy=page.y,
            boundaries_file = "assets/BN_1M.gpkg",
            labels_file = "assets/labels.gpkg",
            title = "code=" + str(page.code) + "  i=" + str(page.i) + "  j=" + str(page.j)
            )

    #launch parallel computation   
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_to_use) as executor:
        tasks_to_do = {executor.submit(make_page, page): page for page in pages}
        for task_output in concurrent.futures.as_completed(tasks_to_do): pass




def make_pdf():

    #index file
    cairosvg.svg2pdf(url=index_file+'.svg', write_to=index_file+'.pdf')
    #pages
    for p in pages:
        print("pdf", p.code)
        cairosvg.svg2pdf(url=out_folder + 'pages_svg/'+str(p.code)+".svg", write_to = out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    #combine
    pdfs = [index_file+".pdf"]
    for p in pages:
        pdfs.append(out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    print("combine", len(pdfs), "pages")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")


#make_svg()
make_pdf()
