import math
from shapely.geometry import shape, box, LineString
from common import mm_to_px, get_cells_1000_gpkg, classifier, font_name, colors, mm_to_px, blue_eu, yellow_eu, get_svg_arc_path
import fiona
from math import cos,sin,pi
import svgwrite

show_debug_code = False

#pre-open the files
land_file = fiona.open("assets/LAND_1M.gpkg", 'r')
no_data_geo_file = fiona.open("assets/NO_DATA_GEO.gpkg", 'r')
water_file = fiona.open("/home/juju/gisco/census_2021_atlas/data/waters_clc___.gpkg", 'r')
cnt_bn_file = fiona.open("assets/BN_1M.gpkg", 'r')
nuts_bn_file = fiona.open("assets/NUTS_BN_1M.gpkg", 'r')
labels_file = fiona.open("assets/labels.gpkg", "r")
minimap_file = fiona.open("assets/minimap.gpkg", "r")





class Map:
    CODE = 1
    def __init__(self, x: float, y: float, title:str=None, width_mm:int=210, height_mm:int=297, scale:float = 1/1200000):
        self.code = Map.CODE
        Map.CODE += 1
        self.x = x
        self.y = y

        self.width_mm = width_mm
        self.height_mm = height_mm
        self.scale = scale

        self.width_px = width_mm * mm_to_px
        self.height_px = height_mm * mm_to_px
        self.width_m = width_mm / scale / 1000
        self.height_m = height_mm / scale / 1000


        self.box = box(x-self.width_m/2, y-self.height_m/2, x+self.width_m/2, y+self.height_m/2)
        self.title = title
        self.arrows = []


    def to_svg(self, out_svg_path, res = 1000, power = 0.25, water_color = '#ebeff2', for_atlas=False):

        print("map", self.code, self.title)

        #the maximum population threshold - depends on the resolution
        max_pop = res * 60

        #minimum circle size: 0.25 mm
        min_diameter = 0.25 * mm_to_px
        #maximum diameter: 1.6*res
        max_diameter = 1.6 * res * self.scale * 1000 * mm_to_px


        cx = self.x; cy = self.y
        x_min, x_max = cx - self.width_m/2, cx + self.width_m/2
        y_min, y_max = cy - self.height_m/2, cy + self.height_m/2
        bbox = (x_min, y_min, x_max, y_max)
        bbox_ = box(x_min, y_min, x_max, y_max)

        # coordinates conversion functions
        decimals = 1
        def geoToPixX(xg): return round((xg-x_min)/self.width_m * self.width_px, decimals)
        def geoToPixY(yg): return round((1-(yg-y_min)/self.height_m) * self.height_px, decimals)
        def transform_coords(coords): return [(geoToPixX(x), geoToPixY(y)) for x, y in coords]

        # create SVG
        dwg = svgwrite.Drawing(out_svg_path, size=(f'{self.width_mm}mm', f'{self.height_mm}mm'))

        # load cells
        cells = get_cells_1000_gpkg(bbox, res, geoToPixX, geoToPixY)

        # case where there is no cell to draw
        if len(cells) == 0:
            print("WARNING: empty page", self.code)
            return

        # background color
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=water_color))

        # make groups
        # land + waters
        g_land_waters = dwg.g(id='land')
        dwg.add(g_land_waters)
        # boundaries
        g_boundaries = dwg.g(id='boundaries')
        dwg.add(g_boundaries)
        # circles
        g_circles = dwg.g(id='circles')
        dwg.add(g_circles)
        # labels
        g_labels = dwg.g(id='labels', font_family=font_name, fill='black')
        g_labels_halo = dwg.g(id='labels_halo', font_family=font_name, fill='none', stroke="white", stroke_width="2")
        dwg.add(g_labels_halo)
        dwg.add(g_labels)
        # layout
        g_layout = dwg.g(id='layout')
        dwg.add(g_layout)

        # draw cells
        for cell in cells:

            # compute diameter from total population
            t = cell['T']
            t = t / max_pop
            if t>1: t=1
            t = pow(t, power)
            diameter = min_diameter + t * (max_diameter - min_diameter)

            # get color
            cl = classifier(cell)
            if cell['T_'] == 0 and cl is None: cl = "center"
            color = colors[cl]

            # draw circle
            g_circles.add(dwg.circle(center=(cell['x'], cell['y']), r=round(diameter/2, decimals), fill=color))


        def draw_polygon(polygon, transform_coords, group, fill_color, hole_fill_color, fill_opacity=1):
            exterior_coords = transform_coords(list(polygon.exterior.coords))
            group.add(dwg.polygon(exterior_coords, fill=fill_color, stroke='none', stroke_width=0, fill_opacity=fill_opacity))
            interior_coords_list = [list(interior.coords) for interior in polygon.interiors]
            for hole_coords in interior_coords_list:
                group.add(dwg.polygon(transform_coords(hole_coords), fill=hole_fill_color, stroke='none', stroke_width=0, fill_opacity=fill_opacity))

        def draw_polygon_layer(objs, bbox_, transform_coords, group, fill_color, hole_fill_color, fill_opacity=1):
            for obj in objs:
                obj = obj[1]

                geom = shape(obj['geometry'])
                if(bbox_): geom = geom.intersection(bbox_)
                if geom.is_empty: continue

                if geom.geom_type == 'Polygon': draw_polygon(geom, transform_coords, group, fill_color, hole_fill_color, fill_opacity)
                elif geom.geom_type == 'MultiPolygon':
                    for geom_ in geom.geoms: draw_polygon(geom_, transform_coords, group, fill_color, hole_fill_color, fill_opacity)
                else: print(geom.geom_type)

        # draw land
        objs = list(land_file.items(bbox=bbox))
        draw_polygon_layer(objs, bbox_, transform_coords, g_land_waters, 'white', water_color)

        # draw inland waters
        objs = list(water_file.items(bbox=bbox))
        draw_polygon_layer(objs, bbox_, transform_coords, g_land_waters, water_color, 'white')

        # no_data_geo
        objs = list(no_data_geo_file.items(bbox=bbox))
        draw_polygon_layer(objs, bbox_, transform_coords, g_land_waters, '#e3dfda', water_color)



        # draw country boundaries and coast line
        def draw_line(line, transform_coords, group, stroke_color, stroke_width):
            points = transform_coords(list(line.coords))
            group.add(dwg.polyline(points, stroke=stroke_color, fill="none", stroke_width=stroke_width, stroke_linecap="round", stroke_linejoin="round"))

        lines = cnt_bn_file.items(bbox=bbox)
        for obj in list(lines):
            obj = obj[1]

            geom = shape(obj['geometry'])
            geom = geom.intersection(bbox_)
            if geom.is_empty: continue

            colstr = "#888" if obj['properties'].get("COAS_FLAG") == 'F' else "#ccc"
            #width, in mm
            sw = 1.2 if obj['properties'].get("COAS_FLAG") == 'F' else 0.2

            if geom.geom_type == 'LineString': draw_line(geom, transform_coords, g_boundaries, colstr, sw)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms: draw_line(line, transform_coords, g_boundaries, colstr, sw)
            else: print(geom.geom_type)

        # draw nuts boundaries
        # width, in mm
        sw = 0.5
        colstr = "#888"
        lines = nuts_bn_file.items(bbox=bbox)
        for obj in list(lines):
            obj = obj[1]
            geom = shape(obj['geometry'])
            geom = geom.intersection(bbox_)
            if geom.is_empty: continue

            if geom.geom_type == 'LineString': draw_line(geom, transform_coords, g_boundaries, colstr, sw)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms: draw_line(line, transform_coords, g_boundaries, colstr, sw)
            else: print(geom.geom_type)


        # draw labels
        for obj in list(labels_file.items(bbox=bbox)):
            obj = obj[1]

            #skip too high density
            rs = obj['properties']['rs']
            if(rs<210): continue

            #skip countries
            cc = obj['properties']['cc']
            skip_countries = ["UK", "UA", "MD", "RS", "XK", "BA", "AL", "ME", "IS", "MK", "FO", "SJ", "AD"]
            if cc in skip_countries: continue

            #draw label
            x, y = obj['geometry']['coordinates']
            name = obj['properties']['name']
            r1 = obj['properties']['r1']
            font_size="9px" if r1<800 else "11px"
            obj = dwg.text(name, insert=(5.0+geoToPixX(x), -5.0+geoToPixY(y)), font_size=font_size)
            g_labels.add(obj)
            g_labels_halo.add(obj)


        if for_atlas:
            #page code
            #case whether to show it on the left or on the right
            f_opacity = 0.65
            case = self.code % 2 == 1
            wr = 56; hr = 56; rnd = 17
            xcr = -rnd if case else self.width_px - wr + rnd
            g_layout.add(dwg.rect(insert=(xcr, -rnd), size=(wr, hr), fill=blue_eu, fill_opacity=f_opacity, stroke='none', stroke_width=0, rx=rnd, ry=rnd))
            g_layout.add(dwg.text(self.code, insert=(xcr+(wr+(1 if case else -1)*rnd)/2, (hr-rnd)/2), font_size="15px", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill=yellow_eu, font_family=font_name))

            # arrows
            r = 11
            ea = pi/3
            for arr in self.arrows:

                #skip the ones for the page next to it
                #the page next is:
                if case and arr.code==self.code+1: continue
                if not case and arr.code==self.code-1: continue

                x = geoToPixX(arr.x)
                y = geoToPixY(arr.y)
                ori = arr.orientation
                g_layout.add(dwg.polyline([(x+r*cos(ori+ea),y-r*sin(ori+ea)), (x+r*cos(ori-ea),y-r*sin(ori-ea)), (x+2*r*cos(ori), y-2*r*sin(ori))], fill_opacity=f_opacity, fill=blue_eu))
                #g_layout.add(dwg.circle(center=(x, y), r=r, fill_opacity=f_opacity, fill=blue_eu))
                arc_path = get_svg_arc_path(x, y, r, ori+ea, ori-ea)
                g_layout.add(dwg.path(d=arc_path, fill_opacity=f_opacity, fill=blue_eu))
                g_layout.add(dwg.text(arr.code, insert=(x, y), font_size="6pt", font_weight="bold", text_anchor="middle", dominant_baseline="middle", fill=yellow_eu, font_family=font_name))


            #minimap
            f_opacity = 0.75
            rnd_ = 4
            ww_px = 34
            hh_px = 38
            y_ = 48
            x_ = 4 if case else self.width_px - ww_px - 4
            g_minimap = dwg.g(id='minimap', transform="translate("+str(x_)+", "+str(y_)+")")
            dwg.add(g_minimap)
            g_minimap.add(dwg.rect(insert=(0,0), size=(ww_px, hh_px), fill="white", fill_opacity=f_opacity, stroke='#888', stroke_width=1, rx=rnd_, ry=rnd_))

            sc = 1/440000000
            ww_m = ww_px/mm_to_px / sc / 1000
            hh_m = hh_px/mm_to_px / sc / 1000

            def geoToPixX_(xg): return round((xg-2300000)/ww_m * ww_px, decimals)
            def geoToPixY_(yg): return round((1-(yg-1200000)/hh_m) * hh_px, decimals)
            def transform_coords_(coords): return [(geoToPixX_(x), geoToPixY_(y)) for x, y in coords]

            #minimap polygons
            minimap_poly = minimap_file.items()
            draw_polygon_layer(minimap_poly, False, transform_coords_, g_minimap, blue_eu, "white", f_opacity)

            #minimap circle
            c_radius = 1.5
            xxx = geoToPixX_(self.x)
            if(xxx<c_radius): xxx = c_radius
            elif(xxx>ww_px-c_radius): xxx = ww_px-c_radius
            yyy = geoToPixY_(self.y)
            if(yyy<c_radius): yyy = c_radius
            elif(yyy>hh_px-c_radius): yyy = hh_px-c_radius
            g_minimap.add(dwg.circle(center=(xxx, yyy), r=c_radius, fill="red")) #, stroke='#888', stroke_width=1



        #debug code
        if show_debug_code:
            dc = "title=" + str(self.title)
            g_layout.add(dwg.text(dc, insert=(self.width_px/2, 20), font_size="12px", text_anchor="middle", dominant_baseline="middle", fill='black'))

        #print("Save SVG", res)
        dwg.save()











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
