import svgwrite
import fiona
#from shapely.geometry import shape, box
from ternary import ternary_classifier


out_folder = '/home/juju/gisco/census_2021_map/'

cells_file = fiona.open("/home/juju/geodata/census/2021/ESTAT_Census_2021_V2.gpkg", 'r')
lines_file = fiona.open('assets/BN_3M.gpkg') 

#the grid resolution in meters
res = 5000

#the maximum population threshold - depends on the resolution
max_pop = res * 60

#the visualisation scale
scale = 1/4500000

#style parameters

mm_to_px = 96 / 25.4  #in px/mm
#minimum circle size: 0.25 mm
min_diameter = 0.25 * mm_to_px
#maximum diameter
max_diameter = 1.2 * mm_to_px

#min_diameter = 0.25 / 1000 / scale
#maximum diameter: 1.6*resolution
#max_diameter = res * 1.6
#print(min_diameter, max_diameter)
power = 0.25


#define the colors, for each ternary class
#colors = {"0": "#4daf4a", "1": "#377eb8", "2": "#e41a1c", "m0": "#ab606a", "m1": "#ae7f30", "m2": "#4f9685", "center": "#999"}
from atlas_params import colors, tri_center, center_coefficient, tri_variable


#define the ternary classifier
classifier = ternary_classifier(
    tri_variable,
    lambda cell:cell["T_"],
    {'center': tri_center, 'centerCoefficient': center_coefficient}
    )


def make_map(path_svg,
             width_mm = 841, height_mm = 1189,
             cx = 4300000, cy = 3300000
             ):

    # transform for europe view
    # A0 dimensions in millimeters
    width_m = width_mm / scale / 1000
    height_m = height_mm / scale / 1000
    width_px = width_mm * mm_to_px
    height_px = height_mm * mm_to_px
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    bbox = (x_min, y_min, x_max, y_max)
    #bbox_ = box(x_min, y_min, x_max, y_max)

    #coordinates conversion functions
    decimals = 1
    def geoToPixX(xg): return round((xg-x_min)/width_m * width_px, decimals)
    def geoToPixY(yg): return round((1-(yg-y_min)/height_m) * height_px, decimals)
    #def transform_coords(coords): return [(geoToPixX(x), geoToPixY(y)) for x, y in coords]

    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"

    # Create an SVG drawing object with A0 dimensions in landscape orientation
    dwg = svgwrite.Drawing(path_svg, size=(f'{width_mm}mm', f'{height_mm}mm'))
    # Set the viewBox attribute to map the custom coordinates to the SVG canvas
    #dwg.viewbox(x_min, y_min, width_m, height_m)
    #dwg.viewbox(0, 0, width_mm/1000*96/25.4, height_mm/1000*96/25.4)



    #load cell data
    cells_ = list(cells_file.items(bbox=bbox))
    cells = []
    for cell in cells_:
        cell = cell[1]
        cell = cell['properties']
        if cell['T'] == 0 or cell['T'] == None: continue

        c = {}
        sp = cell["GRD_ID"].split('N')[1].split('E')
        x = int(sp[1])
        y = int(sp[0])
        c['x'] = geoToPixX(x + res/2)
        c['y'] = geoToPixY(y + res/2)

        c['T'] = int(cell['T'])

        c["T_"] = 0
        for var in tri_variable:
            c[var] = 0 if cell[var]==None else int(cell[var])
            c["T_"] += c[var]

        cells.append(c)
    cells_ = None


    #print(len(cells), "cells loaded")
    #print(cells[0])

    #print("Sort cells")
    cells.sort(key=lambda d: (-d['y'], d['x']))


    #print("Draw cells")
    gCircles = dwg.g(id='circles') #, transform=transform_str)
    for cell in cells:
        if cell['x']<x_min: continue
        if cell['x']>x_max: continue
        if cell['y']<y_min: continue
        if cell['y']>y_max: continue

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

    # draw boundaries
    gBN = dwg.g(id='boundaries', transform=transform_str, fill="none", stroke_width=1500, stroke_linecap="round", stroke_linejoin="round")
    lines_ = list(lines_file.items(bbox=bbox))
    for feature in lines_:
        feature = feature[1]

        #if (feature['properties'].get("EU_FLAG") == 'T' or feature['properties'].get("CNTR_CODE") == 'NO') and feature['properties'].get("COAS_FLAG") == 'T': continue
        colstr = "#888" if feature['properties'].get("COAS_FLAG") == 'F' else "#cacaca"

        geom = feature.geometry
        for line in geom['coordinates']:
            points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
            gBN.add(dwg.polyline(points, stroke=colstr))


    dwg.add(gBN)
    dwg.add(gCircles)

    print("Save SVG", res)
    dwg.save()



#print("Make europe map")
#make_map(out_folder + 'map_age_EUR.svg')

print("Make CY map")
make_map(path_svg = out_folder + 'map_age_CY.svg', width_mm = 50, height_mm = 40, cx = 6438000, cy = 1678693)

exit()
print("Make Canaries map")
make_map(path_svg = out_folder + 'map_age_cana.svg', width_mm = 120, height_mm = 60, cx = 1805783, cy = 1020991)
print("Make Madeira map")
make_map(path_svg = out_folder + 'map_age_madeira.svg', width_mm = 30, height_mm = 15, cx = 1841039, cy = 1522346)
print("Make Azores map")
make_map(path_svg = out_folder + 'map_age_azor.svg', width_mm = 110, height_mm = 140, cx = 1140466, cy = 2505249)
