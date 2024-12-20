from Map import Map
import cairosvg


out = "/home/juju/gisco/census_2021_posters/a0_1km_centre"
map = Map(4070000, 2953000, width_mm = 841, height_mm = 1189)
map.to_svg(out+".svg")
cairosvg.svg2pdf(url=out+".svg", write_to = out+".pdf")

