#coding=utf-8
import os
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from gaesessions import get_current_session
import django
from django import http
from django import shortcuts

from django.core.urlresolvers import reverse

from utils import get_template_uri, get_extra_context, AppContext

appContext = AppContext(current_app = 'home')

def index(request):
    params = get_extra_context(appContext)
    template = get_template_uri(appContext, 'home.html')
    return shortcuts.render_to_response(template, params)
