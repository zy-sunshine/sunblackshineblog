# -*- coding: utf-8 -*-
import os,logging
import re
from base import vcache
from utils import dict4ini
from settings import ROOT_PATH
#from google.appengine.api import users
from google.appengine.ext import db
import pickle
from django.utils.translation import gettext_lazy as _
import urls
from django.conf.urls.defaults import *
from blog.model import Entry
#BLOG = dict4ini.DictIni(os.path.join(ROOT_PATH, 'blog.conf'))
__all__ = ['get_g_blog']
#class LangIterator:
#    def __init__(self,path='locale'):
#        self.iterating = False
#        self.path = path
#        self.list = []
#        for value in  os.listdir(self.path):
#                if os.path.isdir(os.path.join(self.path,value)):
#                    if os.path.exists(os.path.join(self.path,value,'LC_MESSAGES')):
#                        try:
#                            lang=open(os.path.join(self.path,value,'language')).readline()
#                            self.list.append({'code':value,'lang':lang})
#                        except:
#                            self.list.append( {'code':value,'lang':value})
#
#    def __iter__(self):
#        return self
#
#    def next(self):
#        if not self.iterating:
#            self.iterating = True
#            self.cursor = 0
#
#        if self.cursor >= len(self.list):
#            self.iterating = False
#            raise StopIteration
#        else:
#            value = self.list[self.cursor]
#            self.cursor += 1
#            return value
#
#    def getlang(self,language):
#        from django.utils.translation import  to_locale
#        for item in self.list:
#            if item['code']==language or item['code']==to_locale(language):
#                return item
#        return {'code':'en_US','lang':'English'}

class Theme:
    def __init__(self, name='default'):
        self.name = name
        self.mapping_cache = {}
        self.dir = '/themes/%s' % name
        self.viewdir=os.path.join(ROOT_PATH, 'view')
        self.server_dir = os.path.join(ROOT_PATH, 'themes',self.name)
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
##                path = os.path.join(ROOT_PATH, 'themes', 'default', 'templates', name + '.html')
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

class OptionSet(db.Model):
    name=db.StringProperty()
    value=db.TextProperty()
    #blobValue=db.BlobProperty()
    #isBlob=db.BooleanProperty()

    @classmethod
    def getValue(cls,name,default=None):
        try:
            opt=OptionSet.get_by_key_name(name)
            return pickle.loads(str(opt.value))
        except:
            return default

    @classmethod
    def setValue(cls,name,value):
        opt=OptionSet.get_or_insert(name)
        opt.name=name
        opt.value=pickle.dumps(value)
        opt.put()

    @classmethod
    def remove(cls,name):
        opt= OptionSet.get_by_key_name(name)
        if opt:
            opt.delete()

### 配置类继承于 db.Model ,类成员有的为动态初始化, 有的为 db 字段, db 字段为需要保持的配置信息
### 全局配置
class Config(db.Model):
    owner = db.UserProperty()
    author=db.StringProperty(default='admin')
    rpcuser=db.StringProperty(default='admin')
    rpcpassword=db.StringProperty(default='')
    
    timedelta=db.FloatProperty(default=8.0)# hours
    language=db.StringProperty(default="en-us")

    sitemap_entries=db.IntegerProperty(default=30)
    sitemap_include_category=db.BooleanProperty(default=False)
    sitemap_include_tag=db.BooleanProperty(default=False)
    sitemap_ping=db.BooleanProperty(default=False)

    default_theme=Theme("default")

### 整体网站配置
class SiteConfig(Config):
    pass


### 子项目 Blog 配置
class BlogConfig(Config):
    description = db.TextProperty()
    baseurl = db.StringProperty(multiline=False,default=None)
    urlpath = db.StringProperty(multiline=False)
    title = db.StringProperty(multiline=False,default='Micolog')
    subtitle = db.StringProperty(multiline=False,default='This is a micro blog.')
    entrycount = db.IntegerProperty(default=0)
    posts_per_page= db.IntegerProperty(default=10)
    feedurl = db.StringProperty(multiline=False,default='/blog/feed')
    blogversion = db.StringProperty(multiline=False,default='0.30')
    theme_name = db.StringProperty(multiline=False,default='default')
    enable_memcache = db.BooleanProperty(default = False)
    default_link_format=db.StringProperty(multiline=False,default='?p=%(post_id)s')
    link_format=db.StringProperty(multiline=False,default='/blog/%(year)s/%(month)s/%(day)s/%(postname)s.html')
    comment_notify_mail=db.BooleanProperty(default=True)
    #评论顺序
    comments_order=db.IntegerProperty(default=0)
    #每页评论数
    comments_per_page=db.IntegerProperty(default=20)
    #comment check type 0-No 1-算术 2-验证码 3-客户端计算
    comment_check_type=db.IntegerProperty(default=1)
    #0 default 1 identicon
    avatar_style=db.IntegerProperty(default=0)

    blognotice=db.TextProperty(default='')

    domain=db.StringProperty()
    show_excerpt=db.BooleanProperty(default=True)
    version=0.741

    allow_pingback=db.BooleanProperty(default=False)
    allow_trackback=db.BooleanProperty(default=False)

    theme=None
    langs=None
    application=None
    
    def __init__(self,
               parent=None,
               key_name=None,
               _app=None,
               _from_entity=False,
               **kwds):
        from micolog_plugin import Plugins
        self.plugins = Plugins(self)
        db.Model.__init__(self,parent,key_name,_app,_from_entity,**kwds)
        self.iterating = False

    def tigger_filter(self,name,content,*arg1,**arg2):
        return self.plugins.tigger_filter(name,content,blog=self,*arg1,**arg2)

    def tigger_action(self,name,*arg1,**arg2):
         return self.plugins.tigger_action(name,blog=self,*arg1,**arg2)

    def tigger_urlmap(self,url,*arg1,**arg2):
        return self.plugins.tigger_urlmap(url,blog=self,*arg1,**arg2)

    def get_ziplist(self):
        return self.plugins.get_ziplist();

    def save(self):
        self.put()

    def initialsetup(self):
        self.title = 'Your Blog Title'
        self.subtitle = 'Your Blog Subtitle'

    def get_theme(self):
        self.theme= Theme(self.theme_name);
        return self.theme

    def get_langs(self):
        self.langs=LangIterator()
        return self.langs

    def cur_language(self):
        return self.get_langs().getlang(self.language)

    def rootpath(self):
        return ROOT_PATH

    @vcache("blog.hotposts")
    def hotposts(self):
        return Entry.all().filter('entrytype =','post').filter("published =", True).order('-readtimes').fetch(8)

    @vcache("blog.recentposts")
    def recentposts(self):
        return Entry.all().filter('entrytype =','post').filter("published =", True).order('-date').fetch(8)

    @vcache("blog.postscount")
    def postscount(self):
        return Entry.all().filter('entrytype =','post').filter("published =", True).order('-date').count()
        
    def __iter__(self):
        return self

    def next(self):
        if not self.iterating:
            self.iterating = True
            self.methods = filter(lambda m: (m not in ['next', 'list'] and not m.startswith('__')), dir(self))
            self.list = [ getattr(self, m) for m in self.methods ]
            self.cursor = 0

        if self.cursor >= len(self.list):
            self.iterating = False
            raise StopIteration
        else:
            name = self.methods[self.cursor]
            member = self.list[self.cursor]
            self.cursor += 1

            if not hasattr(member, '__call__'):
                return '%s: %s' % (name, member)
            else:
                return self.next()
                
    def addUrlHandler(self, regexp, handler):
        regex = re.compile(regexp, re.UNICODE)
        regex_all = [ pattern.regex for pattern in urls.urlpatterns ]
        if regex not in regex_all:
            urls.urlpatterns += patterns('',
                (regexp, handler),
                )
            
    def removeUrlHandler(self, regexp, handler):
        regex = re.compile(regexp, re.UNICODE)
        findit = None
        for pattern in urls.urlpatterns:
            if pattern.regex == regex:
                findit = pattern
                break
        if findit:
            logging.debug('=========: findit %s', findit)
            urls.urlpatterns.remove(findit)
        else:
            logging.debug('=========: not findit %s', findit)
        
def InitBlogData():
    global g_blog
    OptionSet.setValue('PluginActive',[u'googleAnalytics', u'wordpress', u'sys_plugin'])

    g_blog = BlogConfig(key_name = 'default')
    g_blog.domain=os.environ['HTTP_HOST']
    g_blog.baseurl='http://' + g_blog.domain + '/blog'
    g_blog.feedurl=g_blog.baseurl+"/feed"
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    lang="zh-cn"
    if os.environ.has_key('HTTP_ACCEPT_LANGUAGE'):
        lang=os.environ['HTTP_ACCEPT_LANGUAGE'].split(',')[0]
    from django.utils.translation import  activate,to_locale
    g_blog.language=to_locale(lang)
    from django.conf import settings
    settings._target = None
    activate(g_blog.language)
    g_blog.save()

    entry=Entry(title=_("Hello world!").decode('utf8'))
    entry.content=_('<p>Welcome to micolog. This is your first post. Edit or delete it, then start blogging!</p>').decode('utf8')
    entry.save(True)
    link=Link(href='http://xuming.net',linktext=_("Xuming's blog").decode('utf8'))
    link.put()
    return g_blog

def get_g_blog():
    global g_blog
    try:
       if g_blog :
           return g_blog
    except:
        pass
    g_blog = BlogConfig.get_by_key_name('default')
    if not g_blog:
        g_blog=InitBlogData()


    g_blog.get_theme()
    g_blog.rootdir=os.path.dirname(__file__)
    return g_blog

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

class Sitemap:
    def __init__(self):
        self.NOTIFICATION_SITES = [
          ('http', 'www.google.com', 'webmasters/sitemaps/ping', {}, '', 'sitemap'),
          ]
    def notifySearch(self):
        """ Send notification of the new Sitemap(s) to the search engines. """

        url=g_blog.baseurl+"/sitemap"
    
        # Cycle through notifications
        # To understand this, see the comment near the NOTIFICATION_SITES comment
        for ping in self.NOTIFICATION_SITES:
            query_map             = ping[3]
            query_attr            = ping[5]
            query_map[query_attr] = url
            query = urllib.urlencode(query_map)
            notify = urlparse.urlunsplit((ping[0], ping[1], ping[2], query, ping[4]))
            # Send the notification
            logging.info('Notifying search engines. %s'%ping[1])
            logging.info('url: %s'%notify)
            try:
                result = urlfetch.fetch(notify)
                if result.status_code == 200:
                    logging.info('Notify Result: %s' % result.content)
                if result.status_code == 404:
                    logging.info('HTTP error 404: Not Found')
                    logging.warning('Cannot contact: %s' % ping[1])
      
            except :
                logging.error('Cannot contact: %s' % ping[1])

class BlogOld:
    def __getattr__(self, name):
        val = self.__dict__['BLOG'].get(name, None)
        if val in ('False', 'True'):
           val = val == 'False' and False or True
        val = val == 'None' and None or val
        return val
        
    def __setattr__(self, name, value):
        val = value
        if val in (False, True):
            val = val and 'True' or 'False'
        val = val == None and 'None' or val
        self.__dict__['BLOG'][name] = val
        
    def __init__(self,
               parent=None,
               key_name=None,
               _app=None,
               _from_entity=False,
               **kwds):
        self.__dict__['blog_conf'] = os.path.join(ROOT_PATH, 'blog.conf')
        self.__dict__['BLOG'] = dict4ini.DictIni(self.__dict__['blog_conf'])
        self.__dict__['theme'] = None
        self.__dict__['langs'] = None
        self.__dict__['application'] = None
        
        from micolog_plugin import Plugins
        self.__dict__['plugins'] = Plugins(self)
        #db.Model.__init__(self,parent,key_name,_app,_from_entity,**kwds)

    def tigger_filter(self,name,content,*arg1,**arg2):
        return self.__dict__['plugins'].tigger_filter(name,content,blog=self,*arg1,**arg2)

    def tigger_action(self,name,*arg1,**arg2):
        return self.__dict__['plugins'].tigger_action(name,blog=self,*arg1,**arg2)

    def tigger_urlmap(self,url,*arg1,**arg2):
        return self.__dict__['plugins'].tigger_urlmap(url,blog=self,*arg1,**arg2)

    def get_ziplist(self):
        return self.__dict__['plugins'].get_ziplist();

    def save(self):
        self.__dict__['BLOG'].save()

    def initialsetup(self):
        self.title = 'Your Blog Title'
        self.subtitle = 'Your Blog Subtitle'

    def get_theme(self):
        self.__dict__['theme'] = Theme(self.theme_name);
        return self.__dict__['theme']

    def get_langs(self):
        self.__dict__['langs'] = LangIterator()
        return self.__dict__['theme']

    def cur_language(self):
        return self.get_langs().getlang(self.language)

    def rootpath(self):
        return ROOT_PATH

    @vcache("blog.hotposts")
    def hotposts(self):
        return Entry.all().filter('entrytype =','post').filter("published =", True).order('-readtimes').fetch(8)

    @vcache("blog.recentposts")
    def recentposts(self):
        return Entry.all().filter('entrytype =','post').filter("published =", True).order('-date').fetch(8)

    @vcache("blog.postscount")
    def postscount(self):
        return Entry.all().filter('entrytype =','post').filter("published =", True).order('-date').count()

#g_blog = Blog()



    #owner = db.UserProperty()
    #author=db.StringProperty(default='admin')
    #rpcuser=db.StringProperty(default='admin')
    #rpcpassword=db.StringProperty(default='')
    #description = db.TextProperty()
    #urlpath = db.StringProperty(multiline=False)

    #enable_memcache = db.BooleanProperty(default = False)
    #link_format=db.StringProperty(multiline=False,default='%(year)s/%(month)s/%(day)s/%(postname)s.html')
    #comment_notify_mail=db.BooleanProperty(default=True)


    #blognotice=db.TextProperty(default='')

    #domain=db.StringProperty()
    #show_excerpt=db.BooleanProperty(default=True)
    #version=0.741
    
    #language=db.StringProperty(default="en-us")

