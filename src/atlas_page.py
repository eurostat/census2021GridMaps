import fiona
import svgwrite
from shapely.geometry import shape, box
from atlas_params import scale, width_mm, height_mm, width_m, height_m, res, out_folder, water_color
from common import get_cells_1000_gpkg, classifier, font_name, colors, mm_to_px


show_debug_code = False

width_px = width_mm * mm_to_px
height_px = height_mm * mm_to_px


#the maximum population threshold - depends on the resolution
max_pop = res * 60

#style parameters

#minimum circle size: 0.25 mm
min_diameter = 0.25 * mm_to_px
#maximum diameter: 1.6*res
max_diameter = 1.6 * res * scale * 1000 * mm_to_px

power = 0.25



#pre-open the files
land_file = fiona.open("assets/LAND_1M.gpkg", 'r')
water_file = fiona.open("/home/juju/gisco/census_2021_atlas/data/waters_clc___.gpkg", 'r')
cnt_bn_file = fiona.open("assets/BN_1M.gpkg", 'r')
nuts_bn_file = fiona.open("assets/NUTS_BN_1M.gpkg", 'r')
labels_file = fiona.open("assets/labels.gpkg", "r")


def make_svg_page(page):
    print("page", page.code, page.title)

    cx = page.x; cy = page.y
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    bbox = (x_min, y_min, x_max, y_max)
    bbox_ = box(x_min, y_min, x_max, y_max)

    # coordinates conversion functions
    decimals = 1
    def geoToPixX(xg): return round((xg-x_min)/width_m * width_px, decimals)
    def geoToPixY(yg): return round((1-(yg-y_min)/height_m) * height_px, decimals)
    def transform_coords(coords): return [(geoToPixX(x), geoToPixY(y)) for x, y in coords]


    # create SVG
    out_svg_path = out_folder + 'pages_svg/'+str(page.code)+".svg"
    dwg = svgwrite.Drawing(out_svg_path, size=(f'{width_mm}mm', f'{height_mm}mm'))

    # load cells
    cells = get_cells_1000_gpkg(bbox, res, geoToPixX, geoToPixY)

    # case where there is no cell to draw
    if len(cells) == 0:
        print("WARNING: empty page", page.code, "i=", page.i, "j=", page.j)
        return

    # background color
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=water_color))

    # make groups
    # land + waters
    g_land_waters = dwg.g(id='land')
    dwg.add(g_land_waters)
    # boundaries
    g_boundaries = dwg.g(id='boundaries')
    dwg.add(g_boundaries)
    # circles
    g_circles = dwg.g(id='circles')
    dwg.add(g_circles)
    # labels
    g_labels = dwg.g(id='labels', font_family=font_name, fill='black')
    g_labels_halo = dwg.g(id='labels_halo', font_family=font_name, fill='none', stroke="white", stroke_width="2")
    dwg.add(g_labels_halo)
    dwg.add(g_labels)
    # layout
    g_layout = dwg.g(id='layout')
    dwg.add(g_layout)

    # draw cells
    for cell in cells:

        # compute diameter from total population
        t = cell['T']
        t = t / max_pop
        if t>1: t=1
        t = pow(t, power)
        diameter = min_diameter + t * (max_diameter - min_diameter)

        # get color
        cl = classifier(cell)
        if cell['T_'] == 0 and cl is None: cl = "center"
        color = colors[cl]

        # draw circle
        g_circles.add(dwg.circle(center=(cell['x'], cell['y']), r=round(diameter/2, decimals), fill=color))

    # draw land
    lands = list(land_file.items(bbox=bbox))

    def draw_land_polygon(polygon):
        exterior_coords = transform_coords(list(polygon.exterior.coords))
        g_land_waters.add(dwg.polygon(exterior_coords, fill='white', stroke='none', stroke_width=0))
        interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
        for hole_coords in interior_coords_list:
            g_land_waters.add(dwg.polygon(transform_coords(hole_coords), fill=water_color, stroke='none', stroke_width=0))

    for obj in lands:
        obj = obj[1]

        geom = shape(obj['geometry'])
        geom = geom.intersection(bbox_)
        if geom.is_empty: continue

        if geom.geom_type == 'Polygon': draw_land_polygon(geom)
        elif geom.geom_type == 'MultiPolygon':
            for polygon in geom.geoms: draw_land_polygon(polygon)
        else: print(geom.geom_type)


    # draw inland waters
    waters = list(water_file.items(bbox=bbox))

    def draw_water_polygon(polygon):
        exterior_coords = transform_coords(list(polygon.exterior.coords))
        g_land_waters.add(dwg.polygon(exterior_coords, fill=water_color, stroke='none', stroke_width=0))
        interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
        for hole_coords in interior_coords_list:
            g_land_waters.add(dwg.polygon(transform_coords(hole_coords), fill='white', stroke='none', stroke_width=0))

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
    for obj in list(cnt_bn_file.items(bbox=bbox)):
        obj = obj[1]
        colstr = "#999" if obj['properties'].get("COAS_FLAG") == 'F' else "#ccc"
        #width, in mm
        sw = 1.2 if obj['properties'].get("COAS_FLAG") == 'F' else 0.2
        for line in obj.geometry['coordinates']:
            points = transform_coords(list(line))
            g_boundaries.add(dwg.polyline(points, stroke=colstr, fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))

    # draw nuts boundaries
    # width, in mm
    sw = 0.5
    for obj in list(nuts_bn_file.items(bbox=bbox)):
        obj = obj[1]
        geom = obj.geometry
        for line in geom['coordinates']:
            points = transform_coords(list(line))
            g_boundaries.add(dwg.polyline(points, stroke="#888", fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))

    # draw labels
    for obj in list(labels_file.items(bbox=bbox)):
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
        g_labels.add(obj)
        g_labels_halo.add(obj)

    #page code
    #case wether to show it on the left or on the right
    case = page.code % 2 == 0
    wr = 75; hr = 75; rnd = 23
    xcr = -rnd if case else width_px - wr + rnd
    g_layout.add(dwg.rect(insert=(xcr, -rnd), size=(wr, hr), fill='#004494', fill_opacity=0.8, stroke='none', stroke_width=0, rx=rnd, ry=rnd))
    g_layout.add(dwg.text(page.code, insert=(xcr+(wr+(1 if case else -1)*rnd)/2, (hr-rnd)/2), font_size="20px", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill='	#ffd617', font_family=font_name))

    #debug code
    if show_debug_code:
        dc = "i=" + str(page.i) + "  j=" + str(page.j)
        g_layout.add(dwg.text(dc, insert=(width_px/2, 20), font_size="12px", text_anchor="middle", dominant_baseline="middle", fill='black'))

    #print("Save SVG", res)
    dwg.save()


