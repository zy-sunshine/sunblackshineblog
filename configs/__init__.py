import os
from models import Theme, ThemeIterator, LangIterator
from models import OptionSet, Config, SiteConfig, BlogConfig
#from models import InitDefaultUser, getDefaultUser, InitBlogData, get_g_blog, Sitemap
#from models import *
#from micolog_plugin import Plugins
from django.contrib.auth.models import User
#from blog.models import Link

class BlogConfigObject:
    def __init__(self, *args, **kwds):
        self.__dict__['blog_config'] = BlogConfig(*args, **kwds)
        self.__dict__['version'] = 0.741
        self.__dict__['theme'] = None
        self.__dict__['langs'] = None
        self.__dict__['application'] = None
        
        self.__dict__['iterating'] = False

    def get_theme(self):
        self.theme = Theme(self.theme_name);
        return self.theme

    def get_langs(self):
        self.langs=LangIterator()
        return self.langs

    def cur_language(self):
        return self.get_langs().getlang(self.language)

    def __iter__(self):
        return self

    def next(self):
        if not self.iterating:
            self.iterating = True
            self.methods = filter(lambda m: (m not in ['next', 'list'] and not m.startswith('__')), dir(self)+dir(self.blog_config))
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
        
    def __getattr__(self, key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        elif self.__dict__['blog_config'].__dict__.has_key(key):
            return self.__dict__['blog_config'].__dict__[key]
        else:
            return None
            
    def __setattr__(self, key, value):
        if hasattr(self.blog_config, key):
            self.__dict__['blog_config'].__dict__[key] = value
            #setattr(self.blog_config, key, value)
        else:
            #setattr(self, key, value)
            self.__dict__[key] = value
            
    def save(self):
        self.blog_config.save()
        
def InitDefaultUser():
    user = User()
    user.username = 'test'
    user.email = 'test@example.com'
    user.password = 'test'
    user.save()
    return user
    
def getDefaultUser():
    default_user = User.objects.all()
    default_user = default_user and default_user[0] or InitDefaultUser()
    #if(not default_user):
    #    default_user = InitDefualtUser()
    return default_user
    
def InitBlogData():
    global g_blog
    OptionSet.setValue('PluginActive',[u'googleAnalytics', u'wordpress', u'sys_plugin'])

    g_blog = BlogConfigObject(key_name = 'default')#BlogConfig(key_name = 'default')
    g_blog.owner = getDefaultUser()
    g_blog.domain='127.0.0.1'#os.environ['HTTP_HOST']
    g_blog.baseurl='http://' + g_blog.domain + '/blog'
    g_blog.feedurl=g_blog.baseurl+"/feed"
    #os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    lang="zh-cn"
    #if os.environ.has_key('HTTP_ACCEPT_LANGUAGE'):
    #    lang=os.environ['HTTP_ACCEPT_LANGUAGE'].split(',')[0]
    from django.utils.translation import  activate,to_locale
    g_blog.language=to_locale(lang)
    from django.conf import settings
    settings._target = None
    activate(g_blog.language)
    g_blog.save()

    #entry=Entry(title=_("Hello world!").decode('utf8'))
    #entry.content=_('<p>Welcome to micolog. This is your first post. Edit or delete it, then start blogging!</p>').decode('utf8')
    #entry.save(True)
    #link=Link(href='http://xuming.net',linktext=_("Xuming's blog").decode('utf8'))
    #link.put()
    return g_blog

def get_g_blog():
    global g_blog
    try:
       if g_blog :
           return g_blog
    except:
        pass
    try:
        g_blog = BlogConfig.get_by_key_name('default')
    except:
        g_blog = None
    if not g_blog:
        g_blog=InitBlogData()


    g_blog.get_theme()
    g_blog.rootdir=os.path.dirname(__file__)
    return g_blog



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
