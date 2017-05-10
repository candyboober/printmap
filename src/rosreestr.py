import urllib

from PIL import Image

from .map_imager import BaseMapImager


class RosreestrImager(BaseMapImager):
    # longitude binded to x coordinates
    # latitude to y
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

    def __init__(self, **kwargs):
        super(RosreestrImager, self).__init__(**kwargs)
        self.normalize_angles()
        self.calculate_bbox()
        self.calculate_numbers_of_chunks()
        self.calculate_delta_coords_image()
        self.create_parent_image()

    def normalize_angles(self):
        self.normalize_angle('lowerright')
        self.normalize_angle('upperleft')

    def normalize_angle(self, name):
        angle_attr = getattr(self, name)
        tmp = angle_attr.split(',')
        tmp.reverse()
        setattr(self, name, ','.join(tmp))

    def calculate_bbox(self):
        self.bbox = self.upperleft + ',' + self.lowerright

    def calculate_numbers_of_chunks(self):
        self.number_of_chunks = self.detail_level + 1

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

    def create_parent_image(self):
        self.parent_image = Image.new("RGBA")

    def create_image(self):
        for x in xrange(1, self.number_of_chunks + 1):
            for y in xrange(1, self.number_of_chunks + 1):
                self.create_chunk_image(x, y)

    def create_chunk_image(self, x, y):
        bbox = self.calculate_bbox_chunk(x, y)
        urlparams = self.get_url_params(bbox)
        url = self.url + urlparams
        img = self.load_image(url)

    def calculate_bbox_chunk(self, x, y):
        ullon = self.coords['upperleft_lon']
        lrlon = ullon + self.delta_lon * x
        ullat = self.coords['upperleft_lat']
        lrlat = ullat + self.delta_lat * y
        return '%s,%s,%s,%s' % (ullon, ullat, lrlon, lrlat)

    def init_image(self):
        urlparams = self.get_url_params()
        url = self.url + urlparams
        return self.load_image(url)

    def get_url_params(self, bbox=None):
        url = urllib.urlencode({'layers': self.layers,
                                'bboxSR': self.bboxSR,
                                'imageSR': self.imageSR,
                                'size': self.get_image_size(),
                                'format': self.format,
                                'transparent': self.transparent,
                                'f': self.f,
                                'dpi': self.dpi,
                                'bbox': bbox or self.bbox})
        return url.replace(self.encoded_delimeter, ',')

    def get_image_size(self):
        return '%s,%s' % (self.maxsize, self.maxsize)
