from ternary import ternary_classifier


out_folder = '/home/juju/gisco/census_2021_atlas/'

res = 1000
scale = 1/1200000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000
font_name='Myriad Pro'



#colors = {"0": "#4daf4a", "1": "#377eb8", "2": "#e41a1c", "m0": "#ab606a", "m1": "#ae7f30", "m2": "#4f9685", "center": "#777"}
#colors = {"0": "#51cc3d", "1": "#3d81cd", "2": "#cd3e3f", "m0": "#9036b2", "m1": "#b29536", "m2": "#35b29c", "center": "#777777"}
#colors = {"0": "#18b200", "1": "#005cbf", "2": "#bf0001", "m0": "#ac00bf", "m1": "#bf9300", "m2": "#00a7b2", "center": "#808080"}

#yellow blue red
#purple orange green
#colors = {"0": "#b3b300", "1": "#377eb8", "2": "#e41a1c",
#          "m0": "#984ea3", "m1": "#ff7f00", "m2": "#4daf4a",
#          "center": "#808080"}

colors = {"0": "#18b200", "1": "#005cbf", "2": "#bf0001", "m0": "#9d4a9e", "m1": "#ba9b00", "m2": "#0d9467", "center": "#808080"}

water_color = '#ebeff2' #'#ebf2f7'


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
