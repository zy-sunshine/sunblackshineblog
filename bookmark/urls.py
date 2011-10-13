from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('')
urlpatterns += patterns('bookmark.views',
    (r'^$', 'index'),
    (r'^new$', 'new'),
    (r'^edit/(\d+)$', 'edit'),
)
