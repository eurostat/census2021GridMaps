

out_folder = '/home/juju/gisco/census_2021_atlas/'

res = 1000
scale = 1/1200000
width_mm = 210
height_mm = 297 #A4
width_m = width_mm / scale / 1000
height_m = height_mm / scale / 1000
font_name='Myriad Pro'


tri_variable = ['Y_LT15', 'Y_1564', 'Y_GE65']
tri_center = [0.15, 0.64, 0.21]
center_coefficient = 0.25
