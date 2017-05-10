from pyproj import Proj
from math import pi


EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

map_srs = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 '
map_srs += '+lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 '
map_srs += '+units=m +nadgrids=@null +wktext +no_defs'

print_folder = 'print_images'

epsg4326 = 'epsg:4326'
epsg3857 = 'epsg:3857'
in_proj = Proj(init=epsg4326)
out_proj = Proj(init=epsg3857)

DOC_TEMPLATE_MARGIN = 200
