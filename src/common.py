import csv
from ternary import ternary_classifier


font_name='Myriad Pro'
mm_to_px = 96 / 25.4  #in px/mm


#colors = {"0": "#4daf4a", "1": "#377eb8", "2": "#e41a1c", "m0": "#ab606a", "m1": "#ae7f30", "m2": "#4f9685", "center": "#777"}
#colors = {"0": "#51cc3d", "1": "#3d81cd", "2": "#cd3e3f", "m0": "#9036b2", "m1": "#b29536", "m2": "#35b29c", "center": "#777777"}
#colors = {"0": "#18b200", "1": "#005cbf", "2": "#bf0001", "m0": "#ac00bf", "m1": "#bf9300", "m2": "#00a7b2", "center": "#808080"}

#yellow blue red
#purple orange green
#colors = {"0": "#b3b300", "1": "#377eb8", "2": "#e41a1c",
#          "m0": "#984ea3", "m1": "#ff7f00", "m2": "#4daf4a",
#          "center": "#808080"}

colors = {"0": "#18b200", "1": "#005cbf", "2": "#bf0001", "m0": "#9d4a9e", "m1": "#ba9b00", "m2": "#0d9467", "center": "#808080"}



# try yellow - blue - red
#         green   purple   orange




center_coefficient = 0.25

#age
tri_variable = ['Y_LT15', 'Y_1564', 'Y_GE65']
tri_center = [0.15, 0.64, 0.21]

#birth
#tri_variable = ['OTH', 'NAT', 'EU_OTH']
#tri_center = [0.09, 0.87, 0.04]

#moving
#tri_variable = ['CHG_OUT', 'SAME', 'CHG_IN']
#tri_center = [0.01, 0.897, 0.093]

#define the ternary classifier
classifier = ternary_classifier(
    tri_variable,
    lambda cell:cell["T_"],
    {'center': tri_center, 'centerCoefficient': center_coefficient}
    )


def get_cells(bbox, res, geoToPixX, geoToPixY):
    with open("/home/juju/geodata/census/2021/aggregated/"+res+".csv", mode='r') as file:
        csv_reader = csv.DictReader(file)

        cells = []
        (x_min, y_min, x_max, y_max) = bbox
        for cell in csv_reader:
            if cell['T'] == "0" or cell['T'] == 0 or cell['T'] == None: continue

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

            cells.append(cell)

        return cells


'''''
def get_cells2(bbox, res, geoToPixX, geoToPixY):
    cells_file = fiona.open("/home/juju/geodata/census/2021/ESTAT_Census_2021_V2.gpkg", 'r')
    cells = list(cells_file.items(bbox=bbox))

    cells___ = []
    (x_min, y_min, x_max, y_max) = bbox
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
    return cells___
'''''
