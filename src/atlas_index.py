

def get_index():

    class Page:
        CODE = 1
        def __init__(self, x: float, y: float, i: int = None, j: int = None, title: str = None):
            self.code = Page.CODE
            Page.CODE += 1
            self.x = x
            self.y = y
            self.i = i
            self.j = j
            self.title = title

    pages = []

    #south west position for europe
    xmi = 2500000; ymi = 1350000

    def make_sub_row(j, ri, ox, oy, dx):
        for i in ri:
            ox_ =0; oy_ = 0
            if i==8 and j==10: ox_ = 70000
            if i==7 and j==8: ox_ = 60000
            if i==13 and j==8: ox_ = -50000
            if i==13 and j==7: ox_ = -50000
            if i==7 and j==6: oy_ = -70000
            if i==13 and j==6: ox_ = -80000
            if i==3 and j==5: oy_ = -150000 #britanny
            if i==13 and j==5: oy_ = -150000
            if i==14 and j==5: oy_ = -150000
            if i==4 and j==4: ox_ = 80000
            if i==15 and j==4: ox_ = -60000; oy_ = -100000
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
            if i==6 and j==1: oy_ = 200000; ox_ = -50000
            if i==8 and j==1: oy_ = 180000; ox_ = -50000 #sardinia
            if i==10 and j==0: oy_ = 80000 #malta
            pages.append(Page(xmi + i*dx + ox + ox_, ymi + j*dy + oy + oy_, i, j, str(i)+"_"+str(j)))

    for j in range(12, -1, -1):
        if   j==12: make_sub_row(j, range(9, 12, 1), 90000, 0, dx)
        elif j==11: make_sub_row(j, range(9, 13, 1), 5000, 0, dx)
        elif j==10: make_sub_row(j, range(8, 14, 1), -50000, 0, dx)
        elif  j==9: make_sub_row(j, range(7, 13, 1), 85000, 0, dx)
        elif  j==8: make_sub_row(j, range(7, 14, 1), 0, 0, dx)
        elif  j==7:
            make_sub_row(j, range(2, 4, 1), 80000, -40000, dx)
            make_sub_row(j, range(8, 14, 1), 0, 0, dx)
        elif  j==6:
            make_sub_row(j, range(2, 4, 1), 50000, 150000, dx)
            make_sub_row(j, range(7, 14, 1), -100000, 0, dx)
        elif  j==5: make_sub_row(j, range(3, 15, 1), 120000, 0, dx)
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
            make_sub_row(j, range(3, 4, 1), 0, 200000, dx)
            make_sub_row(j, range(9, 11, 1), 0, 120000, dx)
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

    return pages



def make_index_page(
        pages,
        boundaries_file,
        out_svg_path,
        width_p_m,
        height_p_m,
        scale = 1/35000000,
        width_mm = 210,
        height_mm = 297
        ):

    cx = 3900000
    cy = 3300000

    # transform for europe view
    width_m = width_mm / scale / 1000
    height_m = height_mm / scale / 1000
    x_min, x_max = cx - width_m/2, cx + width_m/2
    y_min, y_max = cy - height_m/2, cy + height_m/2
    transform_str = f"scale({scale*1000*96/25.4} {scale*1000*96/25.4}) translate({-x_min} {-y_min})"

    # Create an SVG drawing object
    dwg = svgwrite.Drawing(out_svg_path, size=(f'{width_mm}mm', f'{height_mm}mm'))

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
    width_p_m = width_p_m/2
    height_p_m = height_p_m/2
    for p in pages:
        points = [(p.x-width_p_m, y_min + y_max-p.y+height_p_m), (p.x+width_p_m, y_min + y_max-p.y+height_p_m), (p.x+width_p_m, y_min + y_max-p.y-height_p_m), (p.x-width_p_m, y_min + y_max-p.y-height_p_m)]
        gP.add(dwg.polygon(points, fill='#9162ff', fill_opacity=0.1, stroke='#9162ff', stroke_width=5000))
        gPNB.add(dwg.text(p.code, insert=(p.x, y_min + y_max-p.y), text_anchor="middle", dominant_baseline="middle", font_size=90000, stroke="white", font_weight='bold', stroke_width=20000))
        gPNB.add(dwg.text(p.code, insert=(p.x, y_min + y_max-p.y), text_anchor="middle", dominant_baseline="middle", font_size=90000, fill="black", font_weight='bold'))


    #draw boundaries
    boundaries_ = fiona.open(boundaries_file, 'r')
    boundaries = list(boundaries_.items())
    for boundary in boundaries:
        boundary = boundary[1]
        geom = boundary.geometry
        for line in geom['coordinates']:
            points = [ (round(x), round(y_min + y_max - y)) for x, y in line]
            gBN.add(dwg.polyline(points, stroke="black", fill="none", stroke_width=6000, stroke_linecap="round", stroke_linejoin="round"))


    #print("Save SVG", res)
    dwg.save()