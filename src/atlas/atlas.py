import

#the grid resolution in meters
res = 1000
in_CSV = '/home/juju/geodata/census/out/ESTAT_Census_2021_V2_'+str(res)+'.csv'


#the visualisation scale
scale = 1/4500000




out_folder = '/home/juju/gisco/census_2021_atlas/'

print("Make europe map")
make_map(out_folder + 'map_age_EUR.svg')

