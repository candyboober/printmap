from cStringIO import StringIO

import PIL


def concat_images(image, layer, rosreestr):
    """
    function that concat png images like sandwich
    used for concat google map static image and
        mapnik layers image
    image - png image google map
    layer - png mapnik image
    """
    buf = StringIO()
    img = None
    if rosreestr:
        rosreestr = rosreestr.resize(image.size)
        img = PIL.Image.alpha_composite(image, rosreestr)
    PIL.Image.alpha_composite(img or image, layer).save(buf, 'PNG')
    buf.seek(0)
    return buf
