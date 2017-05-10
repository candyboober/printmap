# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic import View

import json

from .map_imager import select_map_image, RosreestrImager
from .map_filler import MapFiller
from . import utils
from .concat import concat_images
from .mixins import respond_as_attachment


class PrintLayView(View):
    def get(self, request, *args, **kwargs):
        self.init_data(request)
        if self.include_rosreestr:
            self.create_rosreestr_image()
        try:
            self.create_map_image()
        except IOError:
            return HttpResponse('Произошла ошибка. Попробуй задать меньше "Максимальный размер плитки (тайла)"')
        self.create_lay_image()
        image_stream = concat_images(self.img, self.lay, self.img_rosreestr)
        return respond_as_attachment(request, image_stream)

    def init_data(self, request):
        self.img_rosreestr = None
        self.data = json.loads(request.GET['data'])
        self.valid_data()
        self.unpack_data()

    def valid_data(self):
        if 'layersProps' not in self.data:
            return HttpResponse('Data is not a valid')
        if 'mapName' not in self.data:
            return HttpResponse('Data is not a valid')

    def unpack_data(self):
        self.layers_props = json.loads(self.data['layersProps'])
        self.upperleft = self.data['upperleft']
        self.lowerright = self.data['lowerright']
        self.detail_level = int(self.data['detailLevel'])
        self.zoom = int(self.data['zoom'])
        self.zoom += self.detail_level
        self.map_name = self.data['mapName']
        self.include_rosreestr = self.data['includeRosreestr']

    def create_rosreestr_image(self):
        rosreestr_imager = RosreestrImager(upperleft=self.upperleft,
                                           lowerright=self.lowerright,
                                           detail_level=self.detail_level,
                                           zoom=self.zoom)
        self.img_rosreestr = rosreestr_imager.init_image()

    def create_map_image(self):
        map_imager = select_map_image(self.map_name)
        self.imager = map_imager(upperleft=self.upperleft,
                                 lowerright=self.lowerright,
                                 zoom=self.zoom)
        self.img = self.imager.init_image()

    def create_lay_image(self):
        layers = map(utils.map_geom_data,
                     self.layers_props)

        Map = MapFiller(self.imager)
        Map.filling_map(layers)
        Map.zoom_to_layers_box()
        self.lay = Map.create_map_image()
