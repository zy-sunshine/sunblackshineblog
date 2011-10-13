import logging, os

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
webapp_django_version = '1.2'
from google.appengine.dist import use_library
use_library ('django', '1.2')

# Google App Engine imports.
from google.appengine.ext.webapp import util

# Force Django to reload its settings.
from django.conf import settings
settings._target = None

import django.core.handlers.wsgi
import django.core.signals
import django.db
#import django.dispatch.dispatcher
import django.dispatch

def log_exception(*args, **kwds):
  logging.exception('Exception in request:')

# Log errors.
post_save = django.dispatch.Signal()
#django.dispatch.dispatcher.connect(
post_save.connect(
   log_exception, django.core.signals.got_request_exception)

# Unregister the rollback event handler.
#django.dispatch.dispatcher.disconnect(
post_save.disconnect(
    django.db._rollback_on_exception,
    django.core.signals.got_request_exception)

def main():
  # Create a Django application for WSGI.
  application = django.core.handlers.wsgi.WSGIHandler()

  # Run the WSGI CGI handler with that application.
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()