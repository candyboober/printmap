from pyproj import Proj
from math import pi


EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0

MAP_SRS = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 '
MAP_SRS += '+lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 '
MAP_SRS += '+units=m +nadgrids=@null +wktext +no_defs'

EPSG4326 = 'epsg:4326'
EPSG3857 = 'epsg:3857'
IN_PROJ = Proj(init=EPSG4326)
OUT_PROJ = Proj(init=EPSG3857)

TMP_DIR = 'tmp'
TMP_GEOJSON = 'tmp.geojson'
