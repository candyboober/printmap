from math import pi, log, tan, atan, exp
import urllib2
import json

from . import consts
from .exceptions import GeometryTypeError


def latlontopixels(lat, lon, zoom):
    mx = (lon * consts.ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi / 360.0)) / (pi / 180.0)
    my = (my * consts.ORIGIN_SHIFT) / 180.0
    res = consts.INITIAL_RESOLUTION / (2**zoom)
    px = (mx + consts.ORIGIN_SHIFT) / res
    py = (my + consts.ORIGIN_SHIFT) / res
    return px, py


def pixelstolatlon(px, py, zoom):
    """
    convert resolution of image to coordinates
    """
    res = consts.INITIAL_RESOLUTION / (2**zoom)
    mx = px * res - consts.ORIGIN_SHIFT
    my = py * res - consts.ORIGIN_SHIFT
    lat = (my / consts.ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2 * atan(exp(lat * pi / 180.0)) - pi / 2.0)
    lon = (mx / consts.ORIGIN_SHIFT) * 180.0
    return lat, lon


def get_coords(upperleft, lowerright, concat=True):
    """
    convert bounds coordinates strings to array of coordinates
    """
    upperleft = coords_string_to_float(upperleft, reverse=True)
    # upperleft = coords_string_to_float(upperleft)
    lowerright = coords_string_to_float(lowerright, reverse=True)
    if concat:
        return upperleft + lowerright
    else:
        return upperleft, lowerright


def coords_string_to_float(coord, reverse=False):
    """
    string coordiantes to float
    """
    values = coord.split(',')
    result = [float(v) for v in values]
    if reverse:
        result.reverse()
    return result


def map_geom_data(obj):
    """
    from url and styles hash
    create object that include
    geomatry of object and styles
    """
    response = urllib2.urlopen(obj['url']).read()
    response = json.loads(response)
    layer = {}
    if 'features' in response:
        layer['geom'] = [geom['geometry'] for geom in response['features']]
    else:
        msg = 'Invalid geojson'
        raise GeometryTypeError(msg)
    if 'style' in obj:
        layer['style'] = obj['style']
    else:
        layer['style'] = {}
    return layer
