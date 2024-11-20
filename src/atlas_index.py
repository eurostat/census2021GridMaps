import svgwrite
import fiona
import math
from shapely.geometry import box, LineString
from atlas_params import width_m, height_m, width_mm, height_mm, out_folder
from common import blue_eu


overlap_m = 30000
dx = width_m - overlap_m
dy = height_m - overlap_m


class Page:
    CODE = 1
    def __init__(self, x: float, y: float, i: int = None, j: int = None, title: str = None):
        self.code = Page.CODE
        Page.CODE += 1
        self.x = x
        self.y = y
        self.i = i
        self.j = j
        self.box = box(x-width_m/2, y-height_m/2, x+width_m/2, y+height_m/2)
        self.title = title
        self.arrows = []

    def make_arrows(self, pages):
        for p in pages:
            if(p.code == self.code): continue

            #compute intersection of pages
            inter = self.box.intersection(p.box)

            # intersection too small: no arrow necessary
            if inter.is_empty or inter.area < 3000000000: continue

            # compute page frame
            frame = self.box.buffer(-20000)
            frame = self.box.difference(frame)

            # compute arrow orientation
            orientation = math.atan2(p.y-self.y, p.x-self.x)

            # make ray line from page center to far away in the direction
            far = 10e6
            ray_line = LineString([(self.x, self.y), (self.x + far*math.cos(orientation), self.y + far*math.sin(orientation))])
            #ray_line = LineString([(self.x, self.y), (p.x,p.y)])

            # compute arrow position from intersection of ray line and frame
            position = ray_line.intersection(frame)
            if position.is_empty: continue
            position = position.centroid

            # add arrow
            self.arrows.append(Arrow(p.code, position.x, position.y, orientation))


class Arrow:
    def __init__(self, code:int, x: float, y: float, orientation: float):
        self.code = code
        self.x = x
        self.y = y
        self.orientation = orientation




def get_index():

    pages = []



    # ireland
    pages.append(Page(3034000, 3483400, title="ireland 1"))
    pages.append(Page(3206000, 3483400, title="ireland 2"))
    pages.append(Page(3166000, 3564800, title="ireland 3"))

    #south west position for europe
    xmi = 2500000; ymi = 1350000

    def make_sub_row(j, ri, ox, oy, dx):
        for i in ri:

            # make special page for Venezia
            if Page.CODE == 74:
                pages.append(Page(4496383, 2473699, title="venezia"))

            ox_ =0; oy_ = 0
            if i==9 and j==12: oy_ = -150000; ox_ = 0
            if i==10 and j==12: oy_ = -30000
            if i==8 and j==10: ox_ = 70000
            if i==7 and j==8: ox_ = 80000; oy_ = 60000 #NO SW
            if i==13 and j==8: ox_ = -50000
            if i==13 and j==7: ox_ = -50000
            #if i==3 and j==6: ox_ = -50000 #dublin
            if i==7 and j==6: oy_ = -70000
            if i==13 and j==6: ox_ = -80000
            if i==3 and j==5: oy_ = -150000 #britanny
            if i==4 and j==5: oy_ = -110000 #normandy
            if i==13 and j==5: oy_ = -180000
            if i==4 and j==4: ox_ = 80000
            if i==15 and j==4: ox_ = -60000

            if i==2 and j==3: oy_ = -40000
            if i==3 and j==3: oy_ = -90000
            if i==6 and j==3: oy_ = 50000 #marseille
            if i==7 and j==3: oy_ = 50000 #genoa
            if i==8 and j==3: oy_ = 50000 #firenze
            if i==11 and j==3: ox_ = -100000
            if i==12 and j==3: ox_ = 50000

            if i==1 and j==2: ox_ = 80000
            if i==12 and j==2: oy_ = -100000
            if i==15 and j==2: ox_ = -70000
            if i==6 and j==2: oy_ = 150000; ox_ = -70000
            if i==8 and j==2: oy_ = 100000; ox_ = 70000 #corsica
            if i==9 and j==2: oy_ = 100000; ox_ = 80000 #roma

            if i==1 and j==1: oy_ = 170000
            if i==3 and j==1: oy_ = 50000
            if i==4 and j==1: oy_ = 80000
            if i==5 and j==1: oy_ = 200000
            if i==6 and j==1: oy_ = 200000; ox_ = -70000
            if i==8 and j==1: oy_ = 180000; ox_ = -50000 #sardinia
            if i==10 and j==1: oy_ = -90000; ox_ = -10000 #sicilia east
            if i==9 and j==0: ox_ = 150000 #lampedusa malta
            pages.append(Page(xmi + i*dx + ox + ox_, ymi + j*dy + oy + oy_, i, j, str(i)+"_"+str(j)))

    for j in range(12, -1, -1):
        if   j==12: make_sub_row(j, range(9, 12, 1), 90000, 0, dx)
        elif j==11: make_sub_row(j, range(9, 13, 1), 5000, 0, dx)
        elif j==10: make_sub_row(j, range(8, 14, 1), -50000, 0, dx)
        elif  j==9: make_sub_row(j, range(7, 13, 1), 85000, 0, dx)
        elif  j==8: make_sub_row(j, range(7, 14, 1), 0, 0, dx)
        elif  j==7: make_sub_row(j, range(8, 14, 1), 0, 0, dx)
        elif  j==6: make_sub_row(j, range(7, 14, 1), -100000, 0, dx)
        elif  j==5: make_sub_row(j, range(3, 14, 1), 160000, 0, dx)
        elif  j==4: make_sub_row(j, range(4, 16, 1), 0, 0, dx)
        elif  j==3: make_sub_row(j, range(1, 15, 1), 100000, 0, dx)
        elif  j==2:
            make_sub_row(j, range(1, 7, 1), -70000, 15000, dx)
            make_sub_row(j, range(8, 16, 1), -70000, 15000, dx)
        elif  j==1:
            make_sub_row(j, range(1, 7, 1), 0, 30000, dx)
            make_sub_row(j, range(8, 9, 1), 0, 30000, dx)
            make_sub_row(j, range(10, 12, 1), -100000, 30000, dx)
            make_sub_row(j, range(13, 17, 1), -80000, 30000, dx)
        elif  j==0:
            make_sub_row(j, range(3, 4, 1), 0, 240000, dx)
            make_sub_row(j, range(9, 10, 1), 0, 120000, dx)
            make_sub_row(j, range(14, 16, 1), 0, 220000, dx)

    #cyprus
    pages.append(Page(6421000, 1639000, title="Cyprus"))

    #acores
    pages.append(Page(952995, 2764729, title="Açores"))
    pages.append(Page(1149886, 2516476, title="Açores"))
    pages.append(Page(1296216, 2313164, title="Açores"))

    #madeira
    pages.append(Page(1847000, 1521000, title="Madeira"))

    #canaries
    pages.append(Page(1640000, 1080000, title="Canarias"))
    pages.append(Page(1830000, 1080000, title="Canarias"))
    pages.append(Page(1955151, 1080000, title="Canarias"))

    # show info on selected pages
    #for p in pages: if(p.code == 27 or p.code == 34 or p.code == 35): print(p.code, p.x, p.y)

    # make arrows and count them
    cnt = 0
    for p in pages: p.make_arrows(pages); cnt += len(p.arrows)
    print(cnt, "arrows")

    return pages


scale = 1/30000000
def make_index_page(pages):

    cx = 3700000
    cy = 3300000

    # transform for europe view
    width_m2 = width_mm / scale / 1000
    height_m2 = height_mm / scale / 1000
    x_min, x_max = cx - width_m2/2, cx + width_m2/2
    y_min, y_max = cy - height_m2/2, cy + height_m2/2
    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"

    # Create an SVG drawing object
    dwg = svgwrite.Drawing(out_folder + "index.svg", size=(f'{width_mm}mm', f'{height_mm}mm'))

    #title
    dwg.add(dwg.text("Index", insert=("25mm", "30mm"), font_size="18pt", fill="black", font_weight='bold'))

    #make groups

    #boundaries
    gBN = dwg.g(id='boundaries', transform=transform_str)
    dwg.add(gBN)
    #pages
    gP = dwg.g(id='pages', transform=transform_str)
    dwg.add(gP)
    #page nb
    gPNB = dwg.g(id='page_numbers', transform=transform_str)
    dwg.add(gPNB)

    #draw pages and number
    wp2 = width_m/2
    hp2 = height_m/2
    fsi = 90000
    for p in pages:

        url = "https://ec.europa.eu/assets/estat/E/E4/gisco/website/census_2021_grid_map/index.html?z=150&lay=trivariate&trivariate_selection=age&x="+str(p.x)+"&y="+str(p.y)

        #make page rectangle
        points = [(p.x-wp2, y_min + y_max-p.y+hp2), (p.x+wp2, y_min + y_max-p.y+hp2), (p.x+wp2, y_min + y_max-p.y-hp2), (p.x-wp2, y_min + y_max-p.y-hp2)]
        link = gP.add(dwg.a(href=url, target="_blank"))
        link.add(dwg.polygon(points, fill=blue_eu, fill_opacity=0.1, stroke=blue_eu, stroke_width=5000))

        #make page number label
        link = gPNB.add(dwg.a(href=url, target="_blank"))
        link.add(dwg.text(p.code, insert=(p.x, y_min + y_max-p.y), text_anchor="middle", dominant_baseline="middle", font_size=fsi, stroke="white", font_weight='bold', stroke_width=20000))
        link.add(dwg.text(p.code, insert=(p.x, y_min + y_max-p.y), text_anchor="middle", dominant_baseline="middle", font_size=fsi, fill=blue_eu, font_weight='bold'))


    #draw boundaries
    boundaries = fiona.open("assets/BN_60M.gpkg", 'r')
    boundaries = list(boundaries.items())
    for boundary in boundaries:
        geom = boundary[1].geometry
        for line in geom['coordinates']:
            points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
            gBN.add(dwg.polyline(points, stroke="#404040", fill="none", stroke_width=6000, stroke_linecap="round", stroke_linejoin="round"))


    #print("Save SVG", res)
    dwg.save()
