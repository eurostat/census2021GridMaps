from atlas_utils import make_svg_page, combine_pdfs
from atlas_index import get_index, make_index_page
import cairosvg
import concurrent.futures
from atlas_params import out_folder

print("Start")

#TODO
#move britanny raw back west
#improve index page - 91,109, 68,69

#improve title and legend pages. Add metadata.
#euronym for non greek characters
#check greek names on poster
#show other categories
#minimap
#arrow direction
# try yellow - blue - red
#         green   purple   orange
# rebalance red - green different




num_processors_svg = 1
num_processors_pdf = 1


print("Make pages index")
pages = get_index()
print(len(pages), "pages")

#make index SVG page
make_index_page(pages)
#exit()

#make all pages
def make_svg_pages():
    #launch parallel computation   
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_svg) as executor:
        tasks_to_do = {executor.submit(make_svg_page, page): page for page in pages}
        concurrent.futures.as_completed(tasks_to_do)



#convert to pdf
def make_pdf_pages():

    #make pdfs
    cairosvg.svg2pdf(url=out_folder + 'title.svg', write_to=out_folder + 'title.pdf')
    cairosvg.svg2pdf(url=out_folder + 'legend.svg', write_to=out_folder + 'legend.pdf')
    cairosvg.svg2pdf(url=out_folder + 'index.svg', write_to=out_folder + 'index.pdf')

    #make pages pdf, in parellel
    def make(p):
        print("pdf", p.code)
        cairosvg.svg2pdf(url=out_folder + 'pages_svg/'+str(p.code)+".svg", write_to = out_folder + 'pages_pdf/'+str(p.code)+".pdf")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_pdf) as executor:
        tasks_to_do = {executor.submit(make, p): p for p in pages}
        concurrent.futures.as_completed(tasks_to_do)

    #combine PDF pages
    pdfs = [
        out_folder + 'title.pdf',
        out_folder + 'blank.pdf',
        out_folder + 'legend.pdf',
        #out_folder + 'blank.pdf',
        out_folder + 'index.pdf',
        #out_folder + 'blank.pdf'
            ]
    for p in pages:
        pdfs.append(out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    print("combine", len(pdfs), "pages")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")


make_svg_pages()
make_pdf_pages()
