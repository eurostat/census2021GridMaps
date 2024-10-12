import svgwrite
import fiona


out_folder = '/home/juju/gisco/census_2021_map/'


out_path_svg = out_folder + 'map_age_labels.svg'
gpkg_path = 'assets/labels_filtered.gpkg'
font_name='Myriad Pro'

# transform for europe view
# A0 dimensions in millimeters (landscape)
scale = 1/4500000
# A0 dimensions in millimeters
width_mm = 841
height_mm = 1189
width_px = width_mm * 96 / 25.4
height_px = height_mm * 96 / 25.4

cx = 4300000
cy = 3300000
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000
x_min, x_max = cx - width_m/2, cx + width_m/2
y_min, y_max = cy - height_m/2, cy + height_m/2
#transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"



dwg = svgwrite.Drawing(out_path_svg, size=(f'{width_px}px', f'{height_px}px'))
#dwg.viewbox(x_min, y_min, width_m, height_m)


# Create group elements
g = dwg.g(id='labels', font_family=font_name, fill='black')
gh = dwg.g(id='labels_halo', font_family=font_name, fill='none', stroke="white", stroke_width="2.5")
dwg.add(gh)
dwg.add(g)

def geoToPixX(xg):
    return (xg-x_min)/width_m * width_px
def geoToPixY(yg):
    return (1-(yg-y_min)/height_m) * height_px


print("Make map")
layer = fiona.open(gpkg_path)
for feature in layer:
    cc = feature['properties']['cc']
    if cc=="UK": continue
    if cc=="UA": continue
    if cc=="RS": continue
    if cc=="BA": continue
    if cc=="AL": continue
    if cc=="ME": continue
    if cc=="IS": continue
    if cc=="MK": continue
    if cc=="FO": continue
    if cc=="SJ": continue
    x, y = feature['geometry']['coordinates']
    name = feature['properties']['name']
    r1 = feature['properties']['r1']
    font_size="13pt" if r1<800 else "16pt" #check that - maybe should be in pixel unit ?
    label = dwg.text(name, insert=(5+round(geoToPixX(x)), -5+round(geoToPixY(y))), font_size=font_size)
    g.add(label)
    gh.add(label)
    #g.add(dwg.text(name, insert=(width_px/2, height_px/2)))

print("Save")
dwg.save()

