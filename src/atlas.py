from atlas_page import make_svg_page
from atlas_index import get_index, make_index_page
import cairosvg
import pypdf
import concurrent.futures
from atlas_params import out_folder
import subprocess

print("Start")

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



# convert to pdf
def make_pdf_pages(do_all_pages = True):
    print("Make PDF pages")

    # make pages pdf, in parallel
    if do_all_pages:
        def make(p):
            print("pdf", p.code)
            cairosvg.svg2pdf(url=out_folder + 'pages_svg/'+str(p.code)+".svg", write_to = out_folder + 'pages_pdf/'+str(p.code)+".pdf")
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_processors_pdf) as executor:
            tasks_to_do = {executor.submit(make, p): p for p in pages}
            concurrent.futures.as_completed(tasks_to_do)

    # other pages
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', "docs/atlas_first_pages.docx", '--outdir', out_folder])
    cairosvg.svg2pdf(url=out_folder + 'index.svg', write_to=out_folder + 'index.pdf')

# combine all pdf pages into a single pdf document
def combine_pdf_pages():
    print("combine PDF pages")

    # combine PDF pages
    pdfs = [
        out_folder + "atlas_first_pages.pdf",
        out_folder + 'index.pdf',
            ]
    for p in pages:
        pdfs.append(out_folder + 'pages_pdf/'+str(p.code)+".pdf")

    pdfs.append("docs/blank.pdf")

    print("   ", len(pdfs), "pages to combine")
    combine_pdfs(pdfs, out_folder + "atlas.pdf")


#combine multiple PDF files into one
def combine_pdfs(pdf_list, output_pdf_path):
    pdf_writer = pypdf.PdfWriter()
    for pdf_file in pdf_list:
        pdf_reader = pypdf.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
    with open(output_pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)





make_svg_pages()
make_pdf_pages()
combine_pdf_pages()
