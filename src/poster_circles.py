import svgwrite
import fiona
from common import get_cells, classifier, colors, mm_to_px


out_folder = '/home/juju/gisco/census_2021_map/'

lines_file = fiona.open('assets/BN_3M.gpkg', 'r')



#the grid resolution in meters
res = 5000

#the maximum population threshold - depends on the resolution
max_pop = res * 60

#the visualisation scale
scale = 1/4500000

#minimum circle size: 0.25 mm
min_diameter = 0.25 * mm_to_px
#maximum diameter: 1.6*res
max_diameter = 1.6 * res * scale * 1000 * mm_to_px

power = 0.25



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
    def transform_coords(coords): return [(geoToPixX(x), geoToPixY(y)) for x, y in coords]

    # Create an SVG drawing object with A0 dimensions in landscape orientation
    dwg = svgwrite.Drawing(path_svg, size=(f'{width_mm}mm', f'{height_mm}mm'))

    #load cells
    cells = get_cells(bbox, res, geoToPixX, geoToPixY)

    #sort cells
    cells.sort(key=lambda d: (-d['y'], d['x']))

    #create svg groups
    gCircles = dwg.g(id='circles')
    gBN = dwg.g(id='boundaries', fill="none", stroke_width=0.5, stroke_linecap="round", stroke_linejoin="round")
    dwg.add(gBN)
    dwg.add(gCircles)

    #draw cells
    for cell in cells:

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
    lines_ = list(lines_file.items(bbox=bbox))
    for feature in lines_:
        feature = feature[1]
        colstr = "#888" if feature['properties'].get("COAS_FLAG") == 'F' else "#cacaca"
        geom = feature.geometry
        for line in geom['coordinates']:
            points = transform_coords(line)
            gBN.add(dwg.polyline(points, stroke=colstr))

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
