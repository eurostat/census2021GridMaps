from atlas_utils import make_svg_page, combine_pdfs
from atlas_index import get_index, make_index_page
import cairosvg
import concurrent.futures
from atlas_params import out_folder
import subprocess

print("Start")

#TODO

# try yellow - blue - red
#         green   purple   orange

#improve title and legend pages. Add metadata.
#euronym for non greek characters
# https://ec.europa.eu/component-library/v1.15.0/eu/components/detail/eu-style-color/

#check greek names on poster
#show other categories
#minimap
#arrow direction




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
def make_pdf_pages(do_all_pages = True):

    #make pdfs
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', out_folder + "doc_start.docx", '--outdir', out_folder])
    #cairosvg.svg2pdf(url=out_folder + 'title.svg', write_to=out_folder + 'title.pdf')
    #cairosvg.svg2pdf(url=out_folder + 'legend.svg', write_to=out_folder + 'legend.pdf')
    cairosvg.svg2pdf(url=out_folder + 'index.svg', write_to=out_folder + 'index.pdf')

    #make pages pdf, in parellel
    if do_all_pages:
        def make(p):
            print("pdf", p.code)
            cairosvg.svg2pdf(url=out_folder + 'pages_svg/'+str(p.code)+".svg", write_to = out_folder + 'pages_pdf/'+str(p.code)+".pdf")
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_pdf) as executor:
            tasks_to_do = {executor.submit(make, p): p for p in pages}
            concurrent.futures.as_completed(tasks_to_do)


#combine all pdf pages into a single pdf document
def combine_pdf_pages():

    #combine PDF pages
    pdfs = [
        out_folder + "doc_start.pdf",
        out_folder + 'index.pdf',
            ]
    for p in pages:
        pdfs.append(out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    print("combine", len(pdfs), "pages")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")


make_svg_pages()
make_pdf_pages()
combine_pdf_pages()
