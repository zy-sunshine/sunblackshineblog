from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('')
urlpatterns += patterns('sinaweibo.views',
    (r'^/$', 'mainPage'),
    (r'^/login_weibo/$', 'login'),
)
