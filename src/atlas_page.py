import fiona
import svgwrite
from ternary import ternary_classifier
from shapely.geometry import shape, box
from atlas_params import width_mm, height_mm, width_m, height_m, res, out_folder, font_name, tri_variable, tri_center, center_coefficient, colors, water_color


show_debug_code = False

mm_to_px = 96 / 25.4  #in px/mm
width_px = width_mm * mm_to_px
height_px = height_mm * mm_to_px


#the maximum population threshold - depends on the resolution
max_pop = res * 60

#style parameters

#minimum circle diameter
min_diameter = 0.25 * mm_to_px
#maximum diameter
max_diameter = 1.2 * mm_to_px
#print(min_diameter, max_diameter)
power = 0.25



#define the ternary classifier
classifier = ternary_classifier(
    tri_variable,
    lambda cell:cell["T_"],
    {'center': tri_center, 'centerCoefficient': center_coefficient}
    )


#pre-open the files
cells_ = fiona.open("/home/juju/geodata/census/2021/ESTAT_Census_2021_V2.gpkg", 'r')
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
    bbox = (x_min, y_min, x_max, y_max)
    bbox_ = box(x_min, y_min, x_max, y_max)

    #coordinates conversion functions
    decimals = 1
    def geoToPixX(xg): return round((xg-x_min)/width_m * width_px, decimals)
    def geoToPixY(yg): return round((1-(yg-y_min)/height_m) * height_px, decimals)
    def transform_coords(coords): return [(geoToPixX(x), geoToPixY(y)) for x, y in coords]


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

        #get cell x/y
        sp = cell["GRD_ID"].split('N')[1].split('E')
        x = int(sp[1])
        y = int(sp[0])

        if x+res < x_min: continue
        if x > x_max: continue
        if y+res < y_min: continue
        if y > y_max: continue

        cell['x'] = geoToPixX(x + res/2)
        cell['y'] = geoToPixY(y + res/2)


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
    dwg.add(dwg.rect(insert=(0, 0), size=(width_px, height_px), fill=water_color))

    #make groups

    #land + waters
    gLandWaters = dwg.g(id='land')
    dwg.add(gLandWaters)

    #boundaries
    gBN = dwg.g(id='boundaries')
    dwg.add(gBN)

    #circles
    gCircles = dwg.g(id='circles')
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
        gCircles.add(dwg.circle(center=(cell['x'], cell['y']), r=round(diameter/2, decimals), fill=color))

    #case where there is no cell to draw
    if no_cells:
        print("WARNING: empty page", page.code, "i=", page.i, "j=", page.j)
        return

    #land
    lands = list(land.items(bbox=bbox))

    def draw_land_polygon(polygon):
        exterior_coords = transform_coords(list(polygon.exterior.coords))
        gLandWaters.add(dwg.polygon(exterior_coords, fill='white', stroke='none', stroke_width=0))
        interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
        for hole_coords in interior_coords_list:
            gLandWaters.add(dwg.polygon(transform_coords(hole_coords), fill=water_color, stroke='none', stroke_width=0))

    for obj in lands:
        obj = obj[1]

        geom = shape(obj['geometry'])
        geom = geom.intersection(bbox_)
        if geom.is_empty: continue

        if geom.geom_type == 'Polygon': draw_land_polygon(geom)
        elif geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms: draw_land_polygon(polygon)
        else: print(geom.geom_type)



    #inland waters
    waters = list(water.items(bbox=bbox))

    def draw_water_polygon(polygon):
        exterior_coords = transform_coords(list(polygon.exterior.coords))
        gLandWaters.add(dwg.polygon(exterior_coords, fill=water_color, stroke='none', stroke_width=0))
        interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
        for hole_coords in interior_coords_list:
            gLandWaters.add(dwg.polygon(transform_coords(hole_coords), fill='white', stroke='none', stroke_width=0))

    for obj in waters:
        obj = obj[1]
        geom = shape(obj['geometry'])

        geom = shape(obj['geometry'])
        geom = geom.intersection(bbox_)
        if geom.is_empty: continue

        if geom.geom_type == 'Polygon': draw_water_polygon(geom)
        elif geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms: draw_water_polygon(polygon)
        else: print(geom.geom_type)



    # draw country boundaries
    for obj in list(cnt_bn.items(bbox=bbox)):
        obj = obj[1]
        #if obj['properties'].get("COAS_FLAG") == 'T': continue
        colstr = "#999" if obj['properties'].get("COAS_FLAG") == 'F' else "#ccc"
        #width, in mm
        sw = 1.0 if obj['properties'].get("COAS_FLAG") == 'F' else 0.2
        for line in obj.geometry['coordinates']:
            points = transform_coords(list(line))
            gBN.add(dwg.polyline(points, stroke=colstr, fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))

    # draw nuts boundaries
    #width, in mm
    sw = 0.5
    for obj in list(nuts_bn.items(bbox=bbox)):
        obj = obj[1]
        geom = obj.geometry
        for line in geom['coordinates']:
            points = transform_coords(list(line))
            gBN.add(dwg.polyline(points, stroke="#888", fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))

    # draw labels
    for obj in list(labels.items(bbox=bbox)):
        obj = obj[1]

        #skip too high density
        rs = obj['properties']['rs']
        if(rs<210): continue

        #skip countries
        cc = obj['properties']['cc']
        skip_countries = ["UK", "UA", "MD", "RS", "XK", "BA", "AL", "ME", "IS", "MK", "FO", "SJ", "AD"]
        if cc in skip_countries: continue

        #draw label
        x, y = obj['geometry']['coordinates']
        name = obj['properties']['name']
        r1 = obj['properties']['r1']
        font_size="9px" if r1<800 else "11px"
        obj = dwg.text(name, insert=(5.0+geoToPixX(x), -5.0+geoToPixY(y)), font_size=font_size)
        g.add(obj)
        gh.add(obj)

    #page code
    #case wether to show it on the left or on the right
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


