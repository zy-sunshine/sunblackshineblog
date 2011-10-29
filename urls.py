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


from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from settings import MEDIA_URL, THEME_MEDIA_URL, MEDIA_ROOT, THEME_ROOT, THEME_MEDIA_URL
#from blog.views import CheckCode

#from utils import zipserve

from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
    (r'^$', include('home.urls')),
    # [[ZY
    (r'^%s/(?P<path>.*)$' % MEDIA_URL.strip('/\\'), 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    (r'^%s/(?P<path>.*)$' % THEME_MEDIA_URL.strip('/\\'), 'theme_files.serve', {'document_root': THEME_ROOT}),
    (r'^about$', direct_to_template, {
        'template': 'about.html',  # TODO: About page show error style.
    }),
    (r'^weibo', include('sinaweibo.urls')),
    (r'^blog', include('blog.urls')),
    (r'^admin', include('admin.urls')),
    (r'^tests', include('tests.urls')),
	#(r'^checkcode/', CheckCode),
	#(r'^tinymce/(.*)', zipserve.make_zip_handler('tinymce.zip') ),
	#(r'^i18n/', include('django.conf.urls.i18n'))
	
	(r'^accounts/login/$',  login),
    (r'^accounts/logout/$', logout),
    # ZY]]
    )
