import fiona


cells_file = "/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.gpkg"
cells_ = fiona.open(cells_file, 'r')
cells = list(cells_.items())


tt = 0
t15 = 0
t1564 = 0
t65 = 0
for cell in cells:
    cell = cell[1]
    cell = cell['properties']

    tt += int(cell['T'])
    t15 += 0 if cell['Y_LT15']==None else int(cell['Y_LT15'])
    t1564 += 0 if cell['Y_1564']==None else int(cell['Y_1564'])
    t65 += 0 if cell['Y_GE65']==None else int(cell['Y_GE65'])

tt_ = t15 + t1564 + t65
print(tt, tt_, t15, t1564, t65)
print(t15/tt_)
print(t1564/tt_)
print(t65/tt_)

#0.15003568623944244
#0.6408736511371474
#0.2090906626234101

