from cStringIO import StringIO

import PIL


def concat_images(image, layer, rosreestr=None):
    """
    function that concat png images like sandwich
    used for concat google map static image and
        mapnik layers image
    image - png image google map
    layer - png mapnik image
    """
    buf = StringIO()
    if rosreestr:
        rosreestr = rosreestr.resize(image.size)
        image = PIL.Image.alpha_composite(image, rosreestr)
    PIL.Image.alpha_composite(image, layer).save(buf, 'PNG')
    buf.seek(0)
    return buf
