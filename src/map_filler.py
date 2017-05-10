import mapnik
from mapnik._mapnik import DataGeometryType
from pyproj import transform
import PIL

import os
import json
from tempfile import NamedTemporaryFile

from . import utils
from . import consts
from . exceptions import GeometryTypeError


class MapFiller(mapnik.Map):
    tmp_dir = 'tmp'
    style_hash = {'stroke': 'color',
                  'fill': 'color',
                  'fill_opacity': 'opacity',
                  'stroke_opacity': 'opacity',
                  'opacity': 'opacity',
                  'stroke_width': 'weight',
                  'width': 'weight'}
    """
    mapnik.Map object that create map with included styles,
        datasource, coordinates
    """
    def __init__(self, imager, **kwargs):
        self.upperleft = imager.upperleft
        self.lowerright = imager.lowerright
        box_xy = self.create_valid_box(imager)
        super(MapFiller, self).__init__(*box_xy, **kwargs)
        self.srs = consts.map_srs

        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def create_valid_box(self, imager):
        self.dx = int(imager.dx)
        self.dy = int(imager.dy)
        return self.dx, self.dy

    def filling_map(self, layers):
        for i in range(len(layers)):
            self.append_layer(layers[i], i)

    def correct_layer_geom(self, layer):
        for j in range(len(layer['geom'])):
            if layer['geom'][j]:
                layer['geom'][j]['coordinates'] = \
                    self.epsg4326_to_3857(layer['geom'][j])
        return layer

    def append_layer(self, layer, i):
        layer = self.correct_layer_geom(layer)
        if layer['geom']:
            layer_geojson = self.create_geojson(layer['geom'])
        else:
            return

        filename = os.path.join(self.tmp_dir, 'tmp.geojson')
        datasource = self.write_datasource(filename, layer_geojson)
        symbolizer = self.create_symbolizer(datasource)
        self.set_style(symbolizer, layer['style'])

        name = 'style%s' % str(i)
        self.push_style(name, symbolizer)
        self.push_layer(name, datasource)

    def push_layer(self, name, datasource):
        new_layer = mapnik.Layer(name)
        new_layer.datasource = datasource
        new_layer.srs = consts.map_srs
        new_layer.styles.append(name)
        self.layers.append(new_layer)

    def push_style(self, name, symbolizer):
        style = mapnik.Style()
        rule = mapnik.Rule()
        rule.symbols.append(symbolizer)
        style.rules.append(rule)
        self.append_style(name, style)

    def create_symbolizer(self, datasource):
        geom_type = datasource.geometry_type()
        if geom_type == DataGeometryType.Point:
            symbolizer = mapnik.PointSymbolizer()
        elif geom_type == DataGeometryType.Polygon:
            symbolizer = mapnik.PolygonSymbolizer()
        elif geom_type == DataGeometryType.LineString:
            symbolizer = mapnik.LineSymbolizer()
        elif geom_type == DataGeometryType.Collection:
            symbolizer = mapnik.LineSymbolizer()
        else:
            msg = 'Invalid geomerty type of object %s' % datasource
            raise GeometryTypeError(msg)
        return symbolizer

    def write_datasource(self, filename, geojson):
        with open(filename, 'w') as f:
            f.write(json.dumps(geojson))
        datasource = mapnik.Datasource(type='geojson', file=filename)
        os.remove(filename)
        return datasource

    def epsg4326_to_3857(self, coordinates):
        if coordinates['type'] == 'Point':
            return self.transform_point(coordinates['coordinates'])
        elif coordinates['type'] == 'MultiLineString' or \
                coordinates['type'] == 'Polygon':
                return self.list_comp_map(coordinates['coordinates'])
        elif coordinates['type'] == 'LineString' or \
                coordinates['type'] == 'MultiPoint':
                coords = coordinates['coordinates']
                return [self.transform_point(p) for p in coords]
        elif coordinates['type'] == 'MultiPolygon':
            return map(lambda cc: self.list_comp_map(cc),
                       coordinates['coordinates'])
        else:
            msg = 'Invalid geomerty type of json object by database'
            raise GeometryTypeError(msg)

    def create_geojson(self, geom):
        geojson = {"type": "FeatureCollection"}
        geojson['features'] = [{"type": "Feature",
                                        "geometry": coord,
                                        "properties": {}} for coord in geom]
        return geojson

    def set_style(self, sym, params):
        for k, v in self.style_hash.iteritems():
            if hasattr(sym, k) and v in params:
                if v == 'color':
                    setattr(sym, k, mapnik.Color(str(params[v])))
                else:
                    setattr(sym, k, float(params[v]))
        return sym

    def render_map(self):
        self.map_tmp_file = NamedTemporaryFile()
        mapnik.render_to_file(self,
                              self.map_tmp_file.name,
                              'png')

    def create_map_image(self):
        self.render_map()
        return PIL.Image.open(self.map_tmp_file.name)

    def zoom_to_layers_box(self):
        box = self.create_box(self.upperleft, self.lowerright)
        self.zoom_to_box(box)

    def create_box(self, upperleft, lowerright):
        upperleft, lowerright = utils.get_coords(upperleft, lowerright, False)
        upperleft = MapFiller.transform_point(upperleft)
        lowerright = MapFiller.transform_point(lowerright)
        coords = upperleft + lowerright
        return mapnik.Box2d(*coords)

    @staticmethod
    def transform_point(coords):
        return list(transform(consts.in_proj,
                              consts.out_proj,
                              *coords))

    def list_comp_map(self, list_of_points):
        return map(lambda c: [self.transform_point(p) for p in c],
                   list_of_points)
