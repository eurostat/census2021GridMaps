import svgwrite
import csv
import fiona
from trivariate import trivariate_classifier



def make_svg_map(
        out_svg_path,
        in_CSV,
        res = 1000,
        scale = 1/4500000,
        width_mm = 841, height_mm = 1189,
        cx = 4300000, cy = 3300000,
        colors = {"0": "#4daf4a", "1": "#377eb8", "2": "#e41a1c", "m0": "#ab606a", "m1": "#ae7f30", "m2": "#4f9685", "center": "#999"}
        ):

    # transform for europe view
    # A0 dimensions in millimeters
    width_m = width_mm / scale / 1000
    height_m = height_mm / scale / 1000
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"

    # Create an SVG drawing object with A0 dimensions in landscape orientation
    dwg = svgwrite.Drawing(out_svg_path, size=(f'{width_mm}mm', f'{height_mm}mm'))
    # Set the viewBox attribute to map the custom coordinates to the SVG canvas
    #dwg.viewbox(x_min, y_min, width_m, height_m)
    #dwg.viewbox(0, 0, width_mm/1000*96/25.4, height_mm/1000*96/25.4)



    #print("Load cell data", res)
    cells = []
    with open(in_CSV, mode='r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for cell in csv_reader:
            if cell['T'] == '0' or cell['T'] == '': continue
            del cell['M']
            del cell['F']
            del cell['EMP']
            del cell['NAT']
            del cell['EU_OTH']
            del cell['OTH']
            del cell['SAME']
            del cell['CHG_IN']
            del cell['CHG_OUT']
            del cell['CONFIDENTIALSTATUS']
            del cell['POPULATED']
            del cell['LAND_SURFACE']
            #del cell['NB']
            del cell['fid']

            #cell['x'] = int(cell['x'])
            #cell['y'] = int(cell['y'])

            sp = cell['GRD_ID'].split('N')[1].split('E')
            cell['x'] = int(sp[1])
            cell['y'] = int(sp[0])
            del cell['GRD_ID']

            cell['T'] = int(cell['T'])

            cell['Y_LT15'] = 0 if cell['Y_LT15']=="" else int(cell['Y_LT15'])
            cell['Y_1564'] = 0 if cell['Y_1564']=="" else int(cell['Y_1564'])
            cell['Y_GE65'] = 0 if cell['Y_GE65']=="" else int(cell['Y_GE65'])
            cell["T_"] = cell['Y_LT15'] + cell['Y_1564'] + cell['Y_GE65']

            #print(cell)
            cells.append(cell)

    #print(len(cells), "cells loaded")
    #print(cells[0])

    #print("Sort cells")
    cells.sort(key=lambda d: (-d['y'], d['x']))


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


    #define the trivariate classifier
    classifier = trivariate_classifier(
        ['Y_LT15', 'Y_1564', 'Y_GE65'],
        lambda cell:cell["T_"],
        {'center': [0.15, 0.6, 0.25], 'centerCoefficient': 0.25}
        )


    #print("Draw cells")
    gCircles = dwg.g(id='circles', transform=transform_str)
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
        gCircles.add(dwg.circle(center=(round(cell['x']+res/2), round(y_min + y_max - cell['y']-res/2)), r=round(diameter/2), fill=color))


    # draw boundaries
    gBN = dwg.g(id='boundaries', transform=transform_str, fill="none", stroke_width=1500, stroke_linecap="round", stroke_linejoin="round")
    lines = fiona.open('assets/BN_3M.gpkg') 
    for feature in lines:

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

