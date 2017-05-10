from django.http import HttpResponse

import mimetypes
import os
import urllib
import uuid


def respond_as_attachment(request, file_stream):
    """
    mixin that return file like stream
    """
    original_filename = str(uuid.uuid4()) + '.png'
    response = HttpResponse(file_stream.read())
    file_stream.seek(0, os.SEEK_END)
    response['Content-Length'] = file_stream.tell()
    file_stream.close()
    type, encoding = mimetypes.guess_type(original_filename)
    if type is None:
        type = 'application/octet-stream'
    response['Content-Type'] = type
    if encoding is not None:
        response['Content-Encoding'] = encoding

    if 'WebKit' in request.META['HTTP_USER_AGENT']:
        filename_header = 'filename=%s' % original_filename.encode('utf-8')
    elif 'MSIE' in request.META['HTTP_USER_AGENT']:
        filename_header = ''
    else:
        encoded_name = original_filename.encode('utf-8')
        filename_header = \
            'filename*=UTF-8\'\'%s' % urllib.quote(encoded_name)
    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response
