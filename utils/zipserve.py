#!/usr/bin/env python

import email.Utils
import logging
import mimetypes
import time
import zipfile

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from base import TemplateView

def make_zip_handler(zipfilename, max_age=None, public=None):
  """Factory function to construct a custom ZipHandler instance.

  Args:
    zipfilename: The filename of a zipfile.
    max_age: Optional expiration time; defaults to ZipHandler.MAX_AGE.
    public: Optional public flag; defaults to ZipHandler.PUBLIC.

  Returns:
    A ZipHandler subclass.
  """


  class CustomZipHandler(ZipHandler):
    def GET(self, name):
      self.ServeFromZipFile(self.ZIPFILENAME, name)
    ZIPFILENAME = zipfilename
    if max_age is not None:
      MAX_AGE = max_age
    if public is not None:
      PUBLIC = public

  return CustomZipHandler


class ZipHandler(TemplateView):
  """Request handler serving static files from zipfiles."""


  zipfile_cache = {}

  def GET(self, prefix, name):
    """GET request handler.

    Typically the arguments are passed from the matching groups in the
    URL pattern passed to WSGIApplication().

    Args:
      prefix: The zipfilename without the .zip suffix.
      name: The name within the zipfile.
    """
    self.ServeFromZipFile(prefix + '.zip', name)

  def ServeFromZipFile(self, zipfilename, name):
    """Helper for the GET request handler.

    This serves the contents of file 'name' from zipfile
    'zipfilename', logging a message and returning a 404 response if
    either the zipfile cannot be opened or the named file cannot be
    read from it.

    Args:
      zipfilename: The name of the zipfile.
      name: The name within the zipfile.
    """

    zipfile_object = self.zipfile_cache.get(zipfilename)
    if zipfile_object is None:
      try:
        zipfile_object = zipfile.ZipFile(zipfilename)
      except (IOError, RuntimeError, zipfile.BadZipfile), err:


        logging.error('Can\'t open zipfile %s: %s', zipfilename, err)
        zipfile_object = ''
      self.zipfile_cache[zipfilename] = zipfile_object
    if zipfile_object == '':
      self.error(404)
      self.response.out.write('Not found')
      return
    try:
      data = zipfile_object.read(name)
    except (KeyError, RuntimeError), err:
      self.error(404)
      self.response.out.write('Not found')
      return
    content_type, encoding = mimetypes.guess_type(name)
    if content_type:
      self.response.headers['Content-Type'] = content_type
    self.SetCachingHeaders()
    self.response.out.write(data)


  MAX_AGE = 600


  PUBLIC = True

  def SetCachingHeaders(self):
    """Helper to set the caching headers.

    Override this to customize the headers beyond setting MAX_AGE.
    """
    max_age = self.MAX_AGE
    self.response.headers['Expires'] = email.Utils.formatdate(
        time.time() + max_age, usegmt=True)
    cache_control = []
    if self.PUBLIC:
      cache_control.append('public')
    cache_control.append('max-age=%d' % max_age)
    self.response.headers['Cache-Control'] = ', '.join(cache_control)


def main():
  """Main program.

  This is invoked when this package is referenced from app.yaml.
  """
  application = webapp.WSGIApplication([('/([^/]+)/(.*)', ZipHandler)])
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
