# -*- coding: utf-8 -*-
import os,logging
import re
from django.conf import settings
#from base import vcache
#from utils import dict4ini
#from google.appengine.api import users
#from google.appengine.ext import db
from gae_adapter import models

import pickle
from django.utils.translation import gettext_lazy as _
import urls
from django.conf.urls.defaults import *
#from blog.models import Entry

#BLOG = dict4ini.DictIni(os.path.join(settings.ROOT_PATH, 'blog.conf'))
__all__ = ['get_g_blog', 'Theme', 'ThemeIterator', 'LangIterator']

class Theme:
    def __init__(self, name='default'):
        self.name = name
        self.mapping_cache = {}
        self.dir = '/themes/%s' % name
        self.viewdir=os.path.join(settings.ROOT_PATH, 'view')
        self.server_dir = os.path.join(settings.ROOT_PATH, 'themes',self.name)
        if os.path.exists(self.server_dir):
            self.isZip=False
        else:
            self.isZip=True
            self.server_dir =self.server_dir+".zip"
        #self.server_dir=os.path.join(self.server_dir,"templates")
        logging.debug('server_dir:%s'%self.server_dir)

    def __getattr__(self, name):
        if self.mapping_cache.has_key(name):
            return self.mapping_cache[name]
        else:

            path ="/".join((self.name,'templates', name + '.html'))
            logging.debug('path:%s'%path)
##            if not os.path.exists(path):
##                path = os.path.join(settings.ROOT_PATH, 'themes', 'default', 'templates', name + '.html')
##                if not os.path.exists(path):
##                    path = None
            self.mapping_cache[name]=path
            return path


class ThemeIterator:
    def __init__(self, theme_path='themes'):
        self.iterating = False
        self.theme_path = theme_path
        self.list = []

    def __iter__(self):
        return self

    def next(self):
        if not self.iterating:
            self.iterating = True
            self.list = os.listdir(self.theme_path)
            self.cursor = 0

        if self.cursor >= len(self.list):
            self.iterating = False
            raise StopIteration
        else:
            value = self.list[self.cursor]
            self.cursor += 1
            if value.endswith('.zip'):
                value=value[:-4]
            return value
            #return (str(value), unicode(value))

class LangIterator:
    def __init__(self,path='locale'):
        self.iterating = False
        self.path = path
        self.list = []
        for value in  os.listdir(self.path):
                if os.path.isdir(os.path.join(self.path,value)):
                    if os.path.exists(os.path.join(self.path,value,'LC_MESSAGES')):
                        try:
                            lang=open(os.path.join(self.path,value,'language')).readline()
                            self.list.append({'code':value,'lang':lang})
                        except:
                            self.list.append( {'code':value,'lang':value})

    def __iter__(self):
        return self

    def next(self):
        if not self.iterating:
            self.iterating = True
            self.cursor = 0

        if self.cursor >= len(self.list):
            self.iterating = False
            raise StopIteration
        else:
            value = self.list[self.cursor]
            self.cursor += 1
            return value

    def getlang(self,language):
        from django.utils.translation import  to_locale
        for item in self.list:
            if item['code']==language or item['code']==to_locale(language):
                return item
        return {'code':'en_US','lang':'English'}

class OptionSet(models.Model):
    name=models.StringProperty()
    value=models.TextProperty()
    #blobValue=models.BlobProperty()
    #isBlob=models.BooleanProperty()

    @classmethod
    def getValue(cls,name,default=None):
        try:
            opt=OptionSet.get_by_key_name(name)
            return pickle.loads(str(opt.value))
        except:
            return default

    @classmethod
    def setValue(cls,name,value):
        opt, created = OptionSet.get_or_create(name = name)
        opt.name=name
        opt.value=pickle.dumps(value)
        opt.save()

    @classmethod
    def remove(cls,name):
        opt= OptionSet.get_by_key_name(name)
        if opt:
            opt.delete()

### 配置类继承于 models.Model ,类成员有的为动态初始化, 有的为 db 字段, db 字段为需要保持的配置信息
### 全局配置
   
class Config(models.Model):
    owner = models.UserProperty()
    author=models.StringProperty(default='admin')
    rpcuser=models.StringProperty(default='admin')
    rpcpassword=models.StringProperty(default='')
    
    timedelta=models.FloatProperty(default=8.0)# hours
    language=models.StringProperty(default="en-us")

    sitemap_entries=models.IntegerProperty(default=30)
    sitemap_include_category=models.BooleanProperty(default=False)
    sitemap_include_tag=models.BooleanProperty(default=False)
    sitemap_ping=models.BooleanProperty(default=False)
    #def __init__(self, *args, **kwds):
    #    models.Model.__init__(self, *args, **kwds)
    #    self.default_theme=Theme("default")

### 整体网站配置
class SiteConfig(Config):
    def __init__(self, *args, **kwds):
        Config.__init__(self, *args, **kwds)

### 子项目 Blog 配置
class BlogConfig(Config):
    def __init__(self, *args, **kwds):
        Config.__init__(self, *args, **kwds)
    description = models.TextProperty()
    baseurl = models.StringProperty(multiline=False,default=None)
    urlpath = models.StringProperty(multiline=False)
    title = models.StringProperty(multiline=False,default='Micolog')
    subtitle = models.StringProperty(multiline=False,default='This is a micro blog.')
    entrycount = models.IntegerProperty(default=0)
    posts_per_page= models.IntegerProperty(default=10)
    feedurl = models.StringProperty(multiline=False,default='/blog/feed')
    blogversion = models.StringProperty(multiline=False,default='0.30')
    theme_name = models.StringProperty(multiline=False,default='default')
    enable_memcache = models.BooleanProperty(default = False)
    default_link_format=models.StringProperty(multiline=False,default='?p=%(post_id)s')
    link_format=models.StringProperty(multiline=False,default='/blog/%(year)s/%(month)s/%(day)s/%(postname)s.html')
    comment_notify_mail=models.BooleanProperty(default=True)
    #评论顺序
    comments_order=models.IntegerProperty(default=0)
    #每页评论数
    comments_per_page=models.IntegerProperty(default=20)
    #comment check type 0-No 1-算术 2-验证码 3-客户端计算
    comment_check_type=models.IntegerProperty(default=1)
    #0 default 1 identicon
    avatar_style=models.IntegerProperty(default=0)

    blognotice=models.TextProperty(default='')

    domain=models.StringProperty()
    show_excerpt=models.BooleanProperty(default=True)
    
    allow_pingback=models.BooleanProperty(default=False)
    allow_trackback=models.BooleanProperty(default=False)

#blog_config = gblog_init()


#from django.conf import settings
#settings._target = None

#try:
#    global g_blog
#    g_blog=gblog_init()
#
#    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#    from django.utils.translation import  activate
#    from django.conf import settings
#    settings._target = None
#    activate(g_blog.language)
#except:
#    pass


#global g_blog
#g_blog = gblog_init()

#g_blog = Blog()



    #owner = models.UserProperty()
    #author=models.StringProperty(default='admin')
    #rpcuser=models.StringProperty(default='admin')
    #rpcpassword=models.StringProperty(default='')
    #description = models.TextProperty()
    #urlpath = models.StringProperty(multiline=False)

    #enable_memcache = models.BooleanProperty(default = False)
    #link_format=models.StringProperty(multiline=False,default='%(year)s/%(month)s/%(day)s/%(postname)s.html')
    #comment_notify_mail=models.BooleanProperty(default=True)


    #blognotice=models.TextProperty(default='')

    #domain=models.StringProperty()
    #show_excerpt=models.BooleanProperty(default=True)
    #version=0.741
    
    #language=models.StringProperty(default="en-us")

