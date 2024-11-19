import fiona
from math import cos,sin,pi
import svgwrite
from shapely.geometry import shape, box
from atlas_params import scale, width_mm, height_mm, width_m, height_m, res, out_folder, water_color
from common import get_cells_1000_gpkg, classifier, font_name, colors, mm_to_px, blue_eu, yellow_eu, get_svg_arc_path


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
no_data_geo_file = fiona.open("assets/NO_DATA_GEO.gpkg", 'r')
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


    def draw_polygon(polygon, group, fill_color, hole_fill_color):
        exterior_coords = transform_coords(list(polygon.exterior.coords))
        group.add(dwg.polygon(exterior_coords, fill=fill_color, stroke='none', stroke_width=0))
        interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
        for hole_coords in interior_coords_list:
            group.add(dwg.polygon(transform_coords(hole_coords), fill=hole_fill_color, stroke='none', stroke_width=0))

    def draw_polygon_layer(objs, group, fill_color, hole_fill_color):
        for obj in objs:
            obj = obj[1]

            geom = shape(obj['geometry'])
            geom = geom.intersection(bbox_)
            if geom.is_empty: continue

            if geom.geom_type == 'Polygon': draw_polygon(geom, group, fill_color, hole_fill_color)
            elif geom.geom_type == 'MultiPolygon':
                for geom_ in geom.geoms: draw_polygon(geom_, group, fill_color, hole_fill_color)
            else: print(geom.geom_type)

    # draw land
    objs = list(land_file.items(bbox=bbox))
    draw_polygon_layer(objs, g_land_waters, 'white', water_color)

    # draw inland waters
    objs = list(water_file.items(bbox=bbox))
    draw_polygon_layer(objs, g_land_waters, water_color, 'white')

    # no_data_geo
    objs = list(no_data_geo_file.items(bbox=bbox))
    draw_polygon_layer(objs, g_land_waters, '#dedede', water_color)



    # draw country boundaries and coast line
    def draw_boundary_line(line, colstr, sw):
        points = transform_coords(list(line.coords))
        g_boundaries.add(dwg.polyline(points, stroke=colstr, fill="none", stroke_width=sw, stroke_linecap="round", stroke_linejoin="round"))


    for obj in list(cnt_bn_file.items(bbox=bbox)):
        obj = obj[1]

        geom = shape(obj['geometry'])
        geom = geom.intersection(bbox_)
        if geom.is_empty: continue

        colstr = "#888" if obj['properties'].get("COAS_FLAG") == 'F' else "#ccc"
        #width, in mm
        sw = 1.2 if obj['properties'].get("COAS_FLAG") == 'F' else 0.2

        if geom.geom_type == 'LineString': draw_boundary_line(geom, colstr, sw)
        elif geom.geom_type == 'MultiLineString':
            for line in geom.geoms: draw_boundary_line(line, colstr, sw)
        else: print(geom.geom_type)

    # draw nuts boundaries
    # width, in mm
    sw = 0.5
    colstr = "#888"
    for obj in list(nuts_bn_file.items(bbox=bbox)):
        obj = obj[1]
        geom = shape(obj['geometry'])
        geom = geom.intersection(bbox_)
        if geom.is_empty: continue

        if geom.geom_type == 'LineString': draw_boundary_line(geom, colstr, sw)
        elif geom.geom_type == 'MultiLineString':
            for line in geom.geoms: draw_boundary_line(line, colstr, sw)
        else: print(geom.geom_type)


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
    f_opacity = 0.65
    case = page.code % 2 == 1
    wr = 75; hr = 75; rnd = 23
    xcr = -rnd if case else width_px - wr + rnd
    g_layout.add(dwg.rect(insert=(xcr, -rnd), size=(wr, hr), fill=blue_eu, fill_opacity=f_opacity, stroke='none', stroke_width=0, rx=rnd, ry=rnd))
    g_layout.add(dwg.text(page.code, insert=(xcr+(wr+(1 if case else -1)*rnd)/2, (hr-rnd)/2), font_size="20px", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill=yellow_eu, font_family=font_name))

    # arrows
    r = 11
    ea = pi/3
    for arr in page.arrows:
        x = geoToPixX(arr.x)
        y = geoToPixY(arr.y)
        ori = arr.orientation
        g_layout.add(dwg.polyline([(x+r*cos(ori+ea),y-r*sin(ori+ea)), (x+r*cos(ori-ea),y-r*sin(ori-ea)), (x+2*r*cos(ori), y-2*r*sin(ori))], fill_opacity=f_opacity, fill=blue_eu))
        #g_layout.add(dwg.circle(center=(x, y), r=r, fill_opacity=f_opacity, fill=blue_eu))
        arc_path = get_svg_arc_path(x, y, r, ori+ea, ori-ea)
        g_layout.add(dwg.path(d=arc_path, fill_opacity=f_opacity, fill=blue_eu))
        g_layout.add(dwg.text(arr.code, insert=(x, y), font_size="6pt", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill=yellow_eu, font_family=font_name))


    #debug code
    if show_debug_code:
        dc = "i=" + str(page.i) + "  j=" + str(page.j)
        g_layout.add(dwg.text(dc, insert=(width_px/2, 20), font_size="12px", text_anchor="middle", dominant_baseline="middle", fill='black'))

    #print("Save SVG", res)
    dwg.save()


