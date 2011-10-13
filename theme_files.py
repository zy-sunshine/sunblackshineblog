# -*- coding: utf-8 -*-

#cwd = os.getcwd()
#theme_path = os.path.join(cwd, 'themes')
#file_modifieds={}

#max_age = 600  #expires in 10 minutes


#def format_date(dt):
#    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

# [[zy
import logging
import mimetypes
import os
import posixpath
import re
import stat
import urllib
from email.Utils import parsedate_tz, mktime_tz

from django.template import loader
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.template import Template, Context, TemplateDoesNotExist
from django.utils.http import http_date

from django.views.static import directory_index, was_modified_since

from datetime import datetime, timedelta

def serve(request, path, document_root=None, show_indexes=False):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """
    
    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
        logging.debug('++++++++++++++++++')
        logging.debug(path)
        logging.debug(newpath)
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    logging.debug('+=====%s'%fullpath)
    logging.debug('***++++++++++++++++++1')
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(newpath, fullpath)
        raise Http404("Directory indexes are not allowed here.")
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    logging.debug('***++++++++++++++++++2')
    mimetype, encoding = mimetypes.guess_type(fullpath)
    logging.debug('***++++++++++++++++++3')
    mimetype = mimetype or 'application/octet-stream'
    logging.debug('***++++++++++++++++++4')
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        logging.debug('***++++++++++++++++++5')
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    logging.debug('***++++++++++++++++++6')
    response = HttpResponse(contents, mimetype=mimetype)
    logging.debug('***++++++++++++++++++7')
    #response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    max_age = 600  #expires in 10 minutes
    logging.debug('***++++++++++++++++++8')
    cache_expires(response, max_age)
    response["Content-Length"] = len(contents)
    if encoding:
        response["Content-Encoding"] = encoding
    return response
# zy]]


def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def cache_expires(response, seconds=0, **kw):
    """
    Set expiration on this request.  This sets the response to
    expire in the given seconds, and any other attributes are used
    for cache_control (e.g., private=True, etc).

    this function is modified from webob.Response
    it will be good if google.appengine.ext.webapp.Response inherits from this class...
    """
    logging.debug('++++++++--------++++++++++++++')
    if not seconds:
        # To really expire something, you have to force a
        # bunch of these cache control attributes, and IE may
        # not pay attention to those still so we also set
        # Expires.
        response['Cache-Control'] = 'max-age=0, must-revalidate, no-cache, no-store'
        response['Expires'] = format_date(datetime.utcnow())
        #if 'last-modified' not in self.headers:
        #    self.last_modified = format_date(datetime.utcnow())
        response['Pragma'] = 'no-cache'
    else:
        response['Cache-Control'] = 'max-age=%d' % seconds
        response['Expires'] = format_date(datetime.utcnow() + timedelta(seconds=seconds))


#def main():
#    application = webapp.WSGIApplication(
#            [
#                ('/themes/[\\w\\-]+/templates/.*', NotFound),
#                ('/themes/(?P<prefix>[\\w\\-]+)/(?P<name>.+)', GetFile),
#                ('.*', NotFound),
#                ],
#            debug=True)
#    wsgiref.handlers.CGIHandler().run(application)
#
#if __name__ == '__main__':
#    main()

