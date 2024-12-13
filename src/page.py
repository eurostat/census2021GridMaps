import math
from shapely.geometry import box, LineString
#from atlas_params import width_m, height_m, width_mm, height_mm, out_folder
from common import mm_to_px


class Page:
    CODE = 1
    def __init__(self, x: float, y: float, i: int = None, j: int = None, title: str = None, width_mm:int=210, height_mm:int=297, scale:float = 1/1200000):
        self.code = Page.CODE
        Page.CODE += 1
        self.x = x
        self.y = y
        self.i = i
        self.j = j

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
