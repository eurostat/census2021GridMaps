import fiona
import svgwrite
from trivariate import trivariate_classifier
from shapely.geometry import shape
from atlas_params import scale, width_mm, height_mm, width_m, height_m, res, out_folder, font_name, tri_variable, tri_center, center_coefficient, colors, water_color


show_debug_code = False


#the maximum population threshold - depends on the resolution
max_pop = res * 60

#style parameters

#minimum circle size: 0.25 mm
min_diameter = 0.25 / 1000 / scale
#maximum diameter: 1.6*resolution
max_diameter = res * 1.6
#print(min_diameter, max_diameter)
power = 0.25

#define the trivariate classifier
classifier = trivariate_classifier(
    tri_variable,
    lambda cell:cell["T_"],
    {'center': tri_center, 'centerCoefficient': center_coefficient}
    )


#pre-open the files
cells_ = fiona.open("/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.gpkg", 'r')
land = fiona.open("assets/LAND_1M.gpkg", 'r')
water = fiona.open("/home/juju/gisco/census_2021_atlas/data/waters_clc___.gpkg", 'r')
cnt_bn = fiona.open("assets/BN_1M.gpkg", 'r')
nuts_bn = fiona.open("assets/NUTS_BN_1M.gpkg", 'r')
labels = fiona.open("assets/labels.gpkg", "r")



def make_svg_page(page):
    print("page", page.code, page.title)

    # transform for europe view
    cx = page.x; cy = page.y
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"
    bbox = (x_min, y_min, x_max, y_max)

    # Create an SVG drawing object
    out_svg_path = out_folder + 'pages_svg/'+str(page.code)+".svg"
    dwg = svgwrite.Drawing(out_svg_path, size=(f'{width_mm}mm', f'{height_mm}mm'))
    # Set the viewBox attribute to map the custom coordinates to the SVG canvas
    #dwg.viewbox(x_min, y_min, width_m, height_m)
    #dwg.viewbox(0, 0, width_mm/1000*96/25.4, height_mm/1000*96/25.4)

    #load cells
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

        cell["T_"] = 0
        for var in tri_variable:
            cell[var] = 0 if cell[var]==None else int(cell[var])
            cell["T_"] += cell[var]

        cells___.append(cell)
    cells = cells___

    # Set the background color to white
    #dwg.add(dwg.rect(insert=(x_min, y_min), size=(width_m, height_m), fill='#dfdfdf'))

    # Set the background color
    dwg.add(dwg.rect(transform=transform_str, insert=(x_min, y_min), size=(width_m, height_m), fill=water_color))

    #make groups

    #land + waters
    gLandWaters = dwg.g(id='land', transform=transform_str)
    dwg.add(gLandWaters)

    #boundaries
    gBN = dwg.g(id='boundaries', transform=transform_str)
    dwg.add(gBN)

    #circles
    gCircles = dwg.g(id='circles', transform=transform_str)
    dwg.add(gCircles)

    #labels
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
        print("WARNING: empty page", page.code, "i=", page.i, "j=", page.j)
        return

    #land
    def transform_coords(coords): return [(x, y_min + y_max - y) for x, y in coords]
    lands = list(land.items(bbox=bbox))
    for obj in lands:
        obj = obj[1]
        geom = shape(obj['geometry'])
        if geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms:
                exterior_coords = transform_coords(list(polygon.exterior.coords))
                gLandWaters.add(dwg.polygon(exterior_coords, fill='white', stroke='none', stroke_width=0))
                interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
                for hole_coords in interior_coords_list:
                    gLandWaters.add(dwg.polygon(transform_coords(hole_coords), fill=water_color, stroke='none', stroke_width=0))
        else: print(geom.geom_type)

    #waters
    waters = list(water.items(bbox=bbox))
    for obj in waters:
        obj = obj[1]
        geom = shape(obj['geometry'])
        if geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms:
                exterior_coords = transform_coords(list(polygon.exterior.coords))
                gLandWaters.add(dwg.polygon(exterior_coords, fill=water_color, stroke='none', stroke_width=0))
                interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
                for hole_coords in interior_coords_list:
                    gLandWaters.add(dwg.polygon(transform_coords(hole_coords), fill='white', stroke='none', stroke_width=0))
        else: print(geom.geom_type)

    # draw country boundaries
    for obj in list(cnt_bn.items(bbox=bbox)):
        obj = obj[1]
        #if obj['properties'].get("COAS_FLAG") == 'T': continue
        colstr = "#999" if obj['properties'].get("COAS_FLAG") == 'F' else "#ccc"
        sw = 350 if obj['properties'].get("COAS_FLAG") == 'F' else 60
        for line in obj.geometry['coordinates']:
            points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
            gBN.add(dwg.polyline(points, stroke=colstr, fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))

    # draw nuts boundaries
    for obj in list(nuts_bn.items(bbox=bbox)):
        obj = obj[1]
        geom = obj.geometry
        for line in geom['coordinates']:
            points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
            gBN.add(dwg.polyline(points, stroke="#888", fill="none", stroke_width=170, stroke_linecap="round", stroke_linejoin="round"))


    # draw labels
    #coordinates conversion functions
    width_px = width_mm * 96 / 25.4
    height_px = height_mm * 96 / 25.4
    def geoToPixX(xg): return (xg-x_min)/width_m * width_px
    def geoToPixY(yg): return (1-(yg-y_min)/height_m) * height_px
    for obj in list(labels.items(bbox=bbox)):
        obj = obj[1]

        rs = obj['properties']['rs']
        if(rs<210): continue

        cc = obj['properties']['cc']
        #TODO simplify
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

    #code
    case = page.code % 2 == 0
    wr = 75; hr = 75; rnd = 23
    xcr = -rnd if case else width_px - wr + rnd
    gLayout.add(dwg.rect(insert=(xcr, -rnd), size=(wr, hr), fill='#004494', fill_opacity=0.8, stroke='none', stroke_width=0, rx=rnd, ry=rnd))
    gLayout.add(dwg.text(page.code, insert=(xcr+(wr+(1 if case else -1)*rnd)/2, (hr-rnd)/2), font_size="20px", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill='	#ffd617', font_family=font_name))

    #debug code
    if show_debug_code:
        dc = "i=" + str(page.i) + "  j=" + str(page.j)
        gLayout.add(dwg.text(dc, insert=(width_px/2, 20), font_size="12px", text_anchor="middle", dominant_baseline="middle", fill='black'))

    #print("Save SVG", res)
    dwg.save()


