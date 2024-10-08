import fiona


cells_file = "/home/juju/geodata/census/Eurostat_Census-GRID_2021_V2-0/ESTAT_Census_2021_V2.gpkg"
cells_ = fiona.open(cells_file, 'r')
cells = list(cells_.items())


tt = 0
t15 = 0;t1564 = 0;t65 = 0
NAT=0; EU_OTH=0; OTH=0
SAME=0; CHG_IN=0; CHG_OUT=0
for cell in cells:
    cell = cell[1]
    cell = cell['properties']

    tt += int(cell['T'])

    t15 += 0 if cell['Y_LT15']==None else int(cell['Y_LT15'])
    t1564 += 0 if cell['Y_1564']==None else int(cell['Y_1564'])
    t65 += 0 if cell['Y_GE65']==None else int(cell['Y_GE65'])

    NAT += 0 if cell['NAT']==None else int(cell['NAT'])
    EU_OTH += 0 if cell['EU_OTH']==None else int(cell['EU_OTH'])
    OTH += 0 if cell['OTH']==None else int(cell['OTH'])

    SAME += 0 if cell['SAME']==None else int(cell['SAME'])
    CHG_IN += 0 if cell['CHG_IN']==None else int(cell['CHG_IN'])
    CHG_OUT += 0 if cell['CHG_OUT']==None else int(cell['CHG_OUT'])


# M=0, F=0
# Y_LT15=0, Y_1564=0, Y_GE65=0
# EMP=0
# NAT=0, EU_OTH=0, OTH=0
# SAME=0, CHG_IN=0, CHG_OUT=0,

tt_ = t15 + t1564 + t65
print(tt, tt_, t15, t1564, t65)
print(t15/tt_)
print(t1564/tt_)
print(t65/tt_)

#0.15003568623944244
#0.6408736511371474
#0.2090906626234101

tt_ = NAT + EU_OTH + OTH
print(NAT/tt_)
print(EU_OTH/tt_)
print(OTH/tt_)

tt_ = SAME + CHG_IN + CHG_OUT
print(SAME/tt_)
print(CHG_IN/tt_)
print(CHG_OUT/tt_)

