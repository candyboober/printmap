from cStringIO import StringIO
from math import ceil
import urllib

from PIL import Image

from . import utils


class BaseMapImager(object):
    zoom = None
    upperleft = None
    lowerright = None
    maxsize = 450
    scale = 1
    bottom = 0
    encoded_delimeter = '%2C'

    def __init__(self, *args, **kwargs):
        self.unpack_kwargs(**kwargs)
        self.valid_params()
        self.set_coords_angles_of_image()

    def valid_params(self):
        if not hasattr(self, 'upperleft') or not hasattr(self, 'lowerright'):
            raise Exception('Not enough params, need lowerright and upperleft')

    def unpack_kwargs(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def init_image(self):
        self.create_parent_image()
        self.fill_image()
        return self.parent_image

    def create_parent_image(self):
        size = (int(self.dx), int(self.dy))
        self.parent_image = Image.new("RGBA", size)

    def load_image(self, url):
        f = urllib.urlopen(url)
        return Image.open(StringIO(f.read()))

    def fill_image(self):
        for x in range(self.cols):
            for y in range(self.rows):
                self.fill_in_position(x, y)

    def set_coords_angles_of_image(self):
        ullat, ullon = map(float, self.upperleft.split(','))
        lrlat, lrlon = map(float, self.lowerright.split(','))
        self.coords = {'upperleft_lat': ullat,
                       'upperleft_lon': ullon,
                       'lowerright_lat': lrlat,
                       'lowerright_lon': lrlon}


class MapImager(BaseMapImager):
    def __init__(self, *args, **kwargs):
        super(MapImager, self).__init__(*args, **kwargs)
        self.set_size_of_image()
        self.get_cols_rows()
        self.set_sizes_of_chunk(self.bottom)

    def set_size_of_image(self):
        coords = self.coords
        upperleft_x_y = utils.latlontopixels(coords['upperleft_lat'],
                                             coords['upperleft_lon'],
                                             self.zoom)
        self.upperleft_x, self.upperleft_y = upperleft_x_y
        lowerright_x_y = utils.latlontopixels(coords['lowerright_lat'],
                                              coords['lowerright_lon'],
                                              self.zoom)
        self.lowerright_x, self.lowerright_y = lowerright_x_y
        self.dx = self.lowerright_x - self.upperleft_x
        self.dy = self.upperleft_y - self.lowerright_y

    def get_cols_rows(self):
        self.cols = int(ceil(self.dx / self.maxsize))
        self.rows = int(ceil(self.dy / self.maxsize))

    def set_sizes_of_chunk(self, bottom):
        self.largura = int(ceil(self.dx / self.cols))
        self.altura = int(ceil(self.dy / self.rows))
        self.alturaplus = self.altura + bottom

    def set_position(self, x, y):
        dxn = self.largura * (0.5 + x)
        dyn = self.altura * (0.5 + y)
        px = self.upperleft_x + dxn
        py = self.upperleft_y - dyn - self.bottom / 2
        latn, lonn = utils.pixelstolatlon(px, py, self.zoom)
        return self.latn_lonn_to_string(latn, lonn)

    def latn_lonn_to_string(self, latn, lonn):
        return ','.join((str(latn), str(lonn)))

    def fill_in_position(self, x, y):
        position = self.set_position(x, y)
        urlparams = self.get_url_params(position)
        url = self.url + urlparams
        image_inst = self.load_image(url)
        self.parent_image.paste(image_inst,
                                (int(x * self.largura),
                                 int(y * self.altura)))


class GoogleImager(MapImager):
    """
    interprate for google
    """

    url = 'http://maps.google.com/maps/api/staticmap?'
    maxsize = 640

    def get_url_params(self, position):
        url = urllib.urlencode({'center': position,
                                'zoom': str(self.zoom),
                                'size': '%dx%d' % (self.largura,
                                                   self.alturaplus),
                                'maptype': self.map_type,
                                'scale': self.scale})
        return url.replace(self.encoded_delimeter, ',')


class YandexImager(MapImager):
    url = 'https://static-maps.yandex.ru/1.x/?'
    maxsize = 450

    # def load_image(url):
    #     return urllib.urlopen(url)

    def latn_lonn_to_string(self, latn, lonn):
        return ','.join((str(lonn), str(latn)))

    def get_url_params(self, position):
        url = urllib.urlencode({'ll': position,
                                'z': str(self.zoom),
                                'size': '%d,%d' % (self.largura,
                                                   self.alturaplus),
                                'l': self.map_type,
                                'scale': self.scale})
        return url.replace(self.encoded_delimeter, ',')


class GoogleMapImager(GoogleImager):
    map_type = 'roadmap'


class GoogleSatImager(GoogleImager):
    map_type = 'satellite'


class YandexMapImager(YandexImager):
    map_type = 'map'


class YandexSatImager(YandexMapImager):
    map_type = 'sat'


class TwoGisMapImager(MapImager):
    url = 'http://static.maps.2gis.com/1.0?'
    maxsize = 1200

    def latn_lonn_to_string(self, latn, lonn):
        return ','.join((str(lonn), str(latn)))

    def get_url_params(self, position):
        url = urllib.urlencode({'center': position,
                                'zoom': str(self.zoom),
                                'size': '%d,%d' % (self.largura,
                                                   self.alturaplus)})
        return url.replace(self.encoded_delimeter, ',')


class OSMMapImager(MapImager):
    access_token = 'pk.eyJ1IjoiZGVubnk1MzEiLCJhIjoiY2l3NHhlbjkwMDAwcTJ0bzRzc3p0bmNxaCJ9.QG39g1_q4GANnTPVIizKEg'
    url = 'https://api.mapbox.com/v4/mapbox.emerald/'
    maxsize = 1280

    def latn_lonn_to_string(self, latn, lonn):
        return ','.join((str(lonn), str(latn)))

    def get_url_params(self, position):
        url = '%s,%s/%sx%s.png?' % (position,
                                    self.zoom,
                                    self.largura,
                                    self.altura)
        url += urllib.urlencode({'access_token': self.access_token})
        return url.replace(self.encoded_delimeter, ',')


class RosreestrImager(MapImager):
    maxsize = 2048
    url = 'http://pkk5.rosreestr.ru/arcgis/rest/services/Cadastre/Cadastre/MapServer/export?'
    layers = 'show:0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24'
    bboxSR = 4326
    imageSR = 3857
    size = '2048,2048'
    format = 'png24'
    transparent = True
    f = 'image'
    dpi = 15
    bbox = None

    def __init__(self, *args, **kwargs):
        super(RosreestrImager, self).__init__(*args, **kwargs)
        self.calculate_numbers_of_chunks()
        self.calculate_delta_coords_image()

    def calculate_delta_coords_image(self):
        self.calculate_delta_lon()
        self.calculate_delta_lat()

    def calculate_delta_lon(self):
        lowerright = self.coords['lowerright_lon']
        upperleft = self.coords['upperleft_lon']
        self.delta_lon = abs(upperleft - lowerright) / \
            self.number_of_chunks

    def calculate_delta_lat(self):
        lowerright = self.coords['lowerright_lat']
        upperleft = self.coords['upperleft_lat']
        self.delta_lat = abs(upperleft - lowerright) / \
            self.number_of_chunks

    def latn_lonn_to_string(self, latn, lonn):
        return ','.join((str(lonn), str(latn)))

    def get_image_size(self):
        return '%s,%s' % (self.maxsize, self.maxsize)

    def calculate_numbers_of_chunks(self):
        self.number_of_chunks = self.detail_level + 1

    def set_position(self, x, y):
        ullon = self.coords['upperleft_lon'] + self.delta_lon * x
        lrlon = ullon + self.delta_lon * (x + 1)
        ullat = self.coords['upperleft_lat'] + self.delta_lon * y
        lrlat = ullat + self.delta_lat * (y + 1)
        return '%s,%s,%s,%s' % (ullon, ullat, lrlon, lrlat)

    def get_url_params(self, position):
        url = urllib.urlencode({'layers': self.layers,
                                'bboxSR': self.bboxSR,
                                'imageSR': self.imageSR,
                                'size': self.get_image_size(),
                                'format': self.format,
                                'transparent': self.transparent,
                                'f': self.f,
                                'dpi': self.dpi,
                                'bbox': position})
        return url.replace(self.encoded_delimeter, ',')


def select_map_image(name):
    map_hash = {'google_map': GoogleMapImager,
                'google_sat': GoogleSatImager,
                'yandex_map': YandexMapImager,
                'yandex_sat': YandexSatImager,
                '2gis': TwoGisMapImager,
                'osm': OSMMapImager}
    return map_hash[name]

def create_map_image(map_lay):
    map_lay.render_map()
    return PIL.Image.open(map_lay.map_tmp_file.name)
