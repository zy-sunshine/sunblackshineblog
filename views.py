# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from django.conf import settings
from settings import SITECONFIG

from google.appengine.api import users

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

import django
from django import http
from django import shortcuts

from utils import get_template_uri, AppContext

appContext = AppContext('bookmark')

class Bookmark(db.Model):
  giver = db.UserProperty()
  
  title = db.StringProperty(required=True)
  url = db.URLProperty(required=True)
  #recipient = db.StringProperty(required=True)

  description = db.TextProperty()
  
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now=True)

class BookmarkForm(djangoforms.ModelForm):
  class Meta:
    model = Bookmark
    exclude = ['giver', 'created', 'modified']

def respond(request, user, template, params=None):
  """Helper to render a response, passing standard stuff to the response.

  Args:
    request: The request object.
    user: The User object representing the current user; or None if nobody
      is logged in.
    template: The template name; '.html' is appended automatically.
    params: A dict giving the template parameters; modified in-place.

  Returns:
    Whatever render_to_response(template, params) returns.

  Raises:
    Whatever render_to_response(template, params) raises.
  """
  if params is None:
    params = {}
  if user:
    params['user'] = user
    params['sign_out'] = users.create_logout_url('/')
    params['is_admin'] = (users.is_current_user_admin() and
                          'Dev' in os.getenv('SERVER_SOFTWARE'))
  else:
    params['sign_in'] = users.create_login_url(request.path)
  params['SITECONFIG'] = SITECONFIG
  return shortcuts.render_to_response(get_template_uri(appContext, template), params)


def index(request):
  """Request / -- show all bookmarks."""
  user = users.get_current_user()
  bookmarks = db.GqlQuery('SELECT * FROM Bookmark ORDER BY created DESC')
  return respond(request, user, 'list.html', {'bookmarks': bookmarks})

def edit(request, bookmark_id):
  """Create or edit a bookmark.  GET shows a blank form, POST processes it."""
  user = users.get_current_user()
  if user is None:
    return http.HttpResponseForbidden('You must be signed in to add or edit a bookmark')

  bookmark = None
  if bookmark_id:
    bookmark = Bookmark.get(db.Key.from_path(Bookmark.kind(), int(bookmark_id)))    # TODO: syntax
    if bookmark is None:
      return http.HttpResponseNotFound('No bookmark exists with that key (%r)' %
                                       bookmark_id)

  form = BookmarkForm(data=request.POST or None, instance=bookmark)                 # TODO: syntax

  if not request.POST:
    # Have None Post Value, we need create one form.
    return respond(request, user, 'bookmark', {'form': form, 'bookmark': bookmark})
    
  # Have Post Value, we need check the post valiable.
  errors = form.errors
  if not errors:
    try:
      bookmark = form.save(commit=False) # Don't save now.
    except ValueError, err:
      errors['__all__'] = unicode(err)
  if errors:
    return respond(request, user, 'bookmark', {'form': form, 'bookmark': bookmark})

  if not bookmark.giver:
    bookmark.giver = user
  bookmark.put() # Save it OR save() in django?

  return http.HttpResponseRedirect('/')

def new(request):
  """Create a bookmark.  GET shows a blank form, POST processes it."""
  return edit(request, None)
