from django.test import TestCase

from PIL import Image

from .map_layer_imager.google_map_image import GoogleMapImager


class GoogleImagerTestCase(TestCase):
    def test_imager_created(self):
        data = {'upperleft': '47.57837853860192,37.832794189453125',
                'lowerright': '46.9465122958623,39.05914306640625',
                'scale': 1,
                'maxsize': 640,
                'zoom': 10}
        imager = GoogleMapImager(**data)
        img = imager.init_image()
        self.assertTrue(isinstance(img, Image))
