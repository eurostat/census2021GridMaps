import fiona
import svgwrite
from trivariate import trivariate_classifier
import pypdf
from shapely.geometry import shape

def make_svg_map(
        cells_file,
        out_svg_path,
        res = 1000,
        scale = 1/4500000,
        width_mm = 841, height_mm = 1189,
        cx = 4300000, cy = 3300000,
        colors = {"0": "#4daf4a", "1": "#377eb8", "2": "#e41a1c", "m0": "#ab606a", "m1": "#ae7f30", "m2": "#4f9685", "center": "#999"},
        land_file = None,
        boundaries_file = None,
        nuts_file = None,
        labels_file = None,
        font_name='Myriad Pro',
        title = None,
        page = None
        ):

    # transform for europe view
    width_m = width_mm / scale / 1000
    height_m = height_mm / scale / 1000
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"
    bbox = (x_min, y_min, x_max, y_max)

    # Create an SVG drawing object
    dwg = svgwrite.Drawing(out_svg_path, size=(f'{width_mm}mm', f'{height_mm}mm'))
    # Set the viewBox attribute to map the custom coordinates to the SVG canvas
    #dwg.viewbox(x_min, y_min, width_m, height_m)
    #dwg.viewbox(0, 0, width_mm/1000*96/25.4, height_mm/1000*96/25.4)


    #load cells
    cells_ = fiona.open(cells_file, 'r')
    cells = list(cells_.items(bbox=bbox))

    cells___ = []
    for cell in cells:
        cell = cell[1]
        cell = cell['properties']

        if cell['T'] == 0 or cell['T'] == None: continue

        sp = cell["GRD_ID"].split('N')[1].split('E')
        cell['x'] = int(sp[1])
        cell['y'] = int(sp[0])

        cell['T'] = int(cell['T'])

        cell['Y_LT15'] = 0 if cell['Y_LT15']==None else int(cell['Y_LT15'])
        cell['Y_1564'] = 0 if cell['Y_1564']==None else int(cell['Y_1564'])
        cell['Y_GE65'] = 0 if cell['Y_GE65']==None else int(cell['Y_GE65'])
        cell["T_"] = cell['Y_LT15'] + cell['Y_1564'] + cell['Y_GE65']

        cells___.append(cell)
    cells = cells___

    # Set the background color to white
    #dwg.add(dwg.rect(insert=(x_min, y_min), size=(width_m, height_m), fill='#dfdfdf'))


    #the maximum population threshold - depends on the resolution
    max_pop = res * 60

    #style parameters

    #minimum circle size: 0.25 mm
    min_diameter = 0.25 / 1000 / scale
    #maximum diameter: 1.6*resolution
    max_diameter = res * 1.6
    #print(min_diameter, max_diameter)
    power = 0.25


    water_color = '#e1ecf5'

    # Set the background color
    dwg.add(dwg.rect(transform=transform_str, insert=(x_min, y_min), size=(width_m, height_m), fill=water_color))

    #define the trivariate classifier
    classifier = trivariate_classifier(
        ['Y_LT15', 'Y_1564', 'Y_GE65'],
        lambda cell:cell["T_"],
        {'center': [0.15, 0.64, 0.21], 'centerCoefficient': 0.25}
        )

    #make groups

    #land
    gLand = dwg.g(id='land', transform=transform_str)
    dwg.add(gLand)

    #boundaries
    gBN = dwg.g(id='boundaries', transform=transform_str)
    dwg.add(gBN)

    #circles
    gCircles = dwg.g(id='circles', transform=transform_str)
    dwg.add(gCircles)

    #labels
    if labels_file: 
        g = dwg.g(id='labels', font_family=font_name, fill='black')
        gh = dwg.g(id='labels_halo', font_family=font_name, fill='none', stroke="white", stroke_width="2")
        dwg.add(gh)
        dwg.add(g)

    #layout
    gLayout = dwg.g(id='layout')
    dwg.add(gLayout)






    #print("Draw cells")
    no_cells = True
    for cell in cells:
        if cell['x']+res < x_min: continue
        if cell['x'] > x_max: continue
        if cell['y']+res < y_min: continue
        if cell['y'] > y_max: continue
        no_cells = False

        #compute diameter from total population
        t = cell['T']
        t = t / max_pop
        if t>1: t=1
        t = pow(t, power)
        diameter = min_diameter + t * (max_diameter - min_diameter)

        #get color
        cl = classifier(cell)
        if cell['T_'] == 0 and cl is None: cl = "center"
        color = colors[cl]

        #draw circle
        gCircles.add(dwg.circle(center=(round(cell['x']+res/2), round(y_min + y_max - cell['y']-res/2)), r=round(diameter/2), fill=color))

    #case where there is no cell to draw
    if no_cells:
        print("WARNING: empty page", title)
        return

    #land
    if land_file:
        objs = fiona.open(land_file, 'r')
        objs = list(objs.items(bbox=bbox))
        def transform_coords(coords): return [(x, y_min + y_max - y) for x, y in coords]
        for obj in objs:
            obj = obj[1]
            geom = shape(obj['geometry'])
            if geom.geom_type == 'MultiPolygon':
                for polygon in geom.geoms:
                    exterior_coords = transform_coords(list(polygon.exterior.coords))
                    interior_coords_list = transform_coords([list(interior.coords) for interior in polygon.interiors])
                    gLand.add(dwg.polygon(exterior_coords, fill='white', stroke='none', stroke_width=0))
                    for hole_coords in interior_coords_list:
                        gLand.add(dwg.polygon(hole_coords, fill=water_color, stroke='none', stroke_width=0))
            else:
                print(geom.geom_type)



    # draw country boundaries
    if boundaries_file:
        objs = fiona.open(boundaries_file, 'r')
        objs = list(objs.items(bbox=bbox))
        for obj in objs:
            obj = obj[1]
            colstr = "#888" if obj['properties'].get("COAS_FLAG") == 'F' else "#cacaca"
            sw = 300 if obj['properties'].get("COAS_FLAG") == 'F' else 120
            geom = obj.geometry
            for line in geom['coordinates']:
                points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
                gBN.add(dwg.polyline(points, stroke=colstr, fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))

    # draw nuts boundaries
    if nuts_file:
        objs = fiona.open(nuts_file, 'r')
        objs = list(objs.items(bbox=bbox))
        for obj in objs:
            obj = obj[1]
            geom = obj.geometry
            for line in geom['coordinates']:
                points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
                gBN.add(dwg.polyline(points, stroke="#888", fill="none", stroke_width=180, stroke_linecap="round", stroke_linejoin="round"))



    if labels_file:

        #coordinates conversion functions
        width_px = width_mm * 96 / 25.4
        height_px = height_mm * 96 / 25.4
        def geoToPixX(xg): return (xg-x_min)/width_m * width_px
        def geoToPixY(yg): return (1-(yg-y_min)/height_m) * height_px

        #load labels
        labels_ = fiona.open(labels_file, "r")
        labels = list(labels_.items(bbox=bbox))

        for obj in labels:
            obj = obj[1]

            rs = obj['properties']['rs']
            if(rs<210): continue

            cc = obj['properties']['cc']
            if cc=="UK": continue
            if cc=="UA": continue
            if cc=="MD": continue
            if cc=="RS": continue
            if cc=="XK": continue
            if cc=="BA": continue
            if cc=="AL": continue
            if cc=="ME": continue
            if cc=="IS": continue
            if cc=="MK": continue
            if cc=="FO": continue
            if cc=="SJ": continue
            if cc=="AD": continue
            x, y = obj['geometry']['coordinates']
            name = obj['properties']['name']
            r1 = obj['properties']['r1']
            font_size="9px" if r1<800 else "11px"
            obj = dwg.text(name, insert=(5+round(geoToPixX(x)), -5+round(geoToPixY(y))), font_size=font_size)
            g.add(obj)
            gh.add(obj)


    if page:
        gLayout.add(dwg.rect(insert=(width_px-70, -30), size=(100, 90), fill='black', stroke='none', stroke_width=0, fill_opacity=0.4, rx=20, ry=20))
        gLayout.add(dwg.text(page, insert=(width_px-35, 30), font_size="18px", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill='white'))

    if title:
        gLayout.add(dwg.text(title, insert=(width_px/2, 20), font_size="12px", text_anchor="middle", dominant_baseline="middle", fill='black'))


    #print("Save SVG", res)
    dwg.save()



# Function to combine multiple PDF files into one
def combine_pdfs(pdf_list, output_pdf_path):
    pdf_writer = pypdf.PdfWriter()  # Use 'pypdf.PdfWriter()' for pypdf library

    # Loop through all PDFs in the list
    for pdf_file in pdf_list:
        pdf_reader = pypdf.PdfReader(pdf_file)  # Use 'pypdf.PdfReader()' for pypdf
        # Add each page to the writer object
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)
    
    # Write the combined PDF to the output file
    with open(output_pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)




def make_index_page(
        pages,
        boundaries_file,
        out_svg_path,
        width_p_m,
        height_p_m,
        scale = 1/35000000,
        width_mm = 210,
        height_mm = 297
        ):

    cx = 3900000
    cy = 3300000

    # transform for europe view
    width_m = width_mm / scale / 1000
    height_m = height_mm / scale / 1000
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"

    # Create an SVG drawing object
    dwg = svgwrite.Drawing(out_svg_path, size=(f'{width_mm}mm', f'{height_mm}mm'))

    #make groups

    #boundaries
    gBN = dwg.g(id='boundaries', transform=transform_str)
    dwg.add(gBN)
    #pages
    gP = dwg.g(id='pages', transform=transform_str)
    dwg.add(gP)
    #page nb
    gPNB = dwg.g(id='page_numbers', transform=transform_str)
    dwg.add(gPNB)

    #draw pages and number
    width_p_m = width_p_m/2
    height_p_m = height_p_m/2
    for p in pages:
        points = [(p.x-width_p_m, y_min + y_max-p.y+height_p_m), (p.x+width_p_m, y_min + y_max-p.y+height_p_m), (p.x+width_p_m, y_min + y_max-p.y-height_p_m), (p.x-width_p_m, y_min + y_max-p.y-height_p_m)]
        gP.add(dwg.polygon(points, fill='#9162ff', fill_opacity=0.1, stroke='#9162ff', stroke_width=5000))
        gPNB.add(dwg.text(p.code, insert=(p.x, y_min + y_max-p.y), text_anchor="middle", dominant_baseline="middle", font_size=90000, stroke="white", font_weight='bold', stroke_width=20000))
        gPNB.add(dwg.text(p.code, insert=(p.x, y_min + y_max-p.y), text_anchor="middle", dominant_baseline="middle", font_size=90000, fill="black", font_weight='bold'))


    #draw boundaries
    boundaries_ = fiona.open(boundaries_file, 'r')
    boundaries = list(boundaries_.items())
    for boundary in boundaries:
        boundary = boundary[1]
        geom = boundary.geometry
        for line in geom['coordinates']:
            points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
            gBN.add(dwg.polyline(points, stroke="black", fill="none", stroke_width=6000, stroke_linecap="round", stroke_linejoin="round"))


    #print("Save SVG", res)
    dwg.save()
