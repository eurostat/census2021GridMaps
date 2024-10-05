from atlas_utils import make_svg_map, combine_pdfs
from atlas_index import get_index, make_index_page
import cairosvg
import concurrent.futures


print("Start")

#TODO
# simplify signature
# check MD,BELA boundaries are out
# inland waters

#improve index page - 54-55,92,110, 69,70, 51
#page odd/even
#improve title and legend pages. Add metadata.
#euronym for non greek characters
#check greek names on poster
#show other categories
#minimap
#arrow direction
#background
#test borders 1:100k
# try yellow - blue - red
#         green   purple   orange
# rebalance red - green different




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
pages = get_index()
print(len(pages), "pages")



#make index page
make_index_page(
    pages,
    "assets/BN_60M.gpkg",
    out_folder + 'index.svg',
    width_m,
    height_m
)
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
            colors = {"0": "#4daf4a", "1": "#377eb8", "2": "#e41a1c", "m0": "#ab606a", "m1": "#ae7f30", "m2": "#4f9685", "center": "#666"},
            cx = page.x, cy=page.y,
            land_file = "assets/LAND_1M.gpkg",
            boundaries_file = "assets/BN_1M.gpkg",
            nuts_file = "assets/NUTS_BN_1M.gpkg",
            labels_file = "assets/labels.gpkg",
            title = "i=" + str(page.i) + "  j=" + str(page.j),
            page = page.code
            )

    #launch parallel computation   
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_to_use) as executor:
        tasks_to_do = {executor.submit(make_page, page): page for page in pages}
        for task_output in concurrent.futures.as_completed(tasks_to_do): pass




def make_pdf():

    cairosvg.svg2pdf(url=out_folder + 'title.svg', write_to=out_folder + 'title.pdf')
    cairosvg.svg2pdf(url=out_folder + 'legend.svg', write_to=out_folder + 'legend.pdf')
    cairosvg.svg2pdf(url=out_folder + 'index.svg', write_to=out_folder + 'index.pdf')

    #pages TODO: parallel ?
    for p in pages:
        print("pdf", p.code)
        cairosvg.svg2pdf(url=out_folder + 'pages_svg/'+str(p.code)+".svg", write_to = out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    #combine
    pdfs = [
        out_folder + 'title.pdf',
        out_folder + 'blank.pdf',
        out_folder + 'legend.pdf',
        out_folder + 'blank.pdf',
        out_folder + 'index.pdf',
        out_folder + 'blank.pdf'
            ]
    for p in pages:
        pdfs.append(out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    print("combine", len(pdfs), "pages")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")


make_svg()
make_pdf()
