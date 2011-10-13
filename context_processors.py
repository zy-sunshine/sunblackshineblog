#!/usr/bin/env python
#coding=utf-8

from django.conf import settings
from configs import g_blog
def common(request):
    """
    Adds site config context variables to the context.

    """
    return {'SITE': settings.SITE_CONFIG, 
            'THEME_MEDIA_URL': settings.THEME_MEDIA_URL,
            'MEDIA_URL': settings.MEDIA_URL,
            'blog': g_blog}
