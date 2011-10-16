#coding=utf-8
import os, logging
from django.http import HttpResponse, HttpRequest, HttpResponseNotAllowed
from django.template import RequestContext, loader
from settings import SITE_CONFIG
from utils import AppContext, get_extra_context, get_template_uri
from django import shortcuts
from django.utils.encoding import iri_to_uri
#from google.appengine.api import users
from django.contrib import auth
from django.contrib.auth.views import login, logout
from google.appengine.api import memcache
from django.core import urlresolvers

import configs
from utils import get_absolute_path

from admin.models import User
from functools import wraps

from django.template import TemplateDoesNotExist
import traceback
import urllib

from django.core.urlresolvers import reverse

def vcache(key="",time=3600):
    def _decorate(method):
        def _wrapper(*args, **kwargs):
            if not configs.get_g_blog().enable_memcache:
                return method(*args, **kwargs)

            result=method(*args, **kwargs)
            memcache.set(key,result,time)
            return result

        return _wrapper
    return _decorate


#From http://djangosnippets.org/snippets/2041/
class CallableViewClass(type):
    def __new__(cls, name, bases, dct):
        if 'HEAD' not in dct and 'GET' in dct:
            # XXX: this function could possibly be moved out
            # to the global namespace to save memory.
            def HEAD(self, request, *args, **kwargs):
                response = self.get(request, *args, **kwargs)
                response.content = u''
                return response
            dct['HEAD'] = HEAD

        dct['permitted_methods'] = []
        for method in ('GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE'):
            if hasattr(dct.get(method, None), '__call__'):
                dct['permitted_methods'].append(method)

        return type.__new__(cls, name, bases, dct)

    def __call__(cls, *args, **kwargs):
        if args and isinstance(args[0], HttpRequest):
            instance = super(CallableViewClass, cls).__call__()
            return instance.__call__(*args, **kwargs)
        else:
            instance = super(CallableViewClass, cls).__call__(*args, **kwargs)
            return instance

class TemplateView(object):
    __metaclass__ = CallableViewClass

    def __call__(self, request, *args, **kwargs):
        if request.method in self.permitted_methods:
            handler = getattr(self, request.method)
            # XXX: Could possibly check if 'before' returns a response
            # and return that instead.
            self.before(request, args, kwargs)
            if hasattr(self, 'initialize'):
                self.initialize(request)
            handler(*args, **kwargs)
            return self.response

        return HttpResponseNotAllowed(self.permitted_methods)

    def before(self, request, args, kwargs):
        """Override this method to add common functionality to all HTTP method handlers.

        args and kwargs are passed as regular arguments so you can add/remove arguments:
            def before(self, request, args, kwargs):
                kwargs['article'] = get_object_or_404(Article, id=kwargs.pop('article_id')
            def GET(self, request, article): # <== 'article' instead of 'article_id'
                ...
            def post(delf, request, article): # <== 'article' instead of 'article_id'
                ...
        """
        self.request = request
        self.response = HttpResponse()
        self.response.headers = Setter(self.response)
        self.response.out = Writer(self.response)
        self.request.uri = get_absolute_path(request)
        self.request.str_cookies = request.COOKIES
        self.request.remote_addr = request.META['REMOTE_ADDR']
        self.request.get_all = lambda x: request.REQUEST.getlist(x)
    def initialize(self, request):
        pass
        
class Setter(object):
    def __init__(self, response):
        self.response = response
    def __getitem__(self, header):
        self.response[header]
    def __delitem__(self, header):
        del self.response[header]
    def __setitem__(self, header, value):
        self.response[header] = value
    def add_header(self, header, value):
        self.response[header] = value

class Writer(object):
    def __init__(self, response):
        self.response = response
    def write(self, data):
        self.response.write(data)

class SiteRequestHandler(TemplateView):
    def __init__(self):
        self.template_vals = {}
        ## Don not define self.app_context there, it will override in sub class when use in render* method
    def initialize(self, request):
        TemplateView.initialize(self, request)
        ## some for authorize
        #self.login_user = users.get_current_user()
        self.login_user = auth.authenticate(username='john', password='secret')
        self.is_login = (self.login_user is not None)
        self.loginurl=reverse(login)#users.create_login_url(self.request.path)
        self.logouturl=reverse(logout)#users.create_logout_url(self.request.path)
        #self.is_admin = users.is_current_user_admin()
        self.is_admin = False # TODO: make it valid
        # three status: admin author login
        if self.is_admin:
            self.auth = 'admin'
            self.author=User.all().filter('email =',self.login_user.email()).get()
            if not self.author:
                # init author database
                self.author=User(dispname=self.login_user.nickname(),email=self.login_user.email())
                self.author.isadmin=True
                self.author.user=self.login_user
                self.author.put()
        elif self.is_login:
            self.author=User.all().filter('email =',self.login_user.email()).get()
            if self.author:
                self.auth='author'
            else:
                self.auth = 'login'
        else:
            self.auth = 'guest'

        try:
            #self.referer = self.request.headers['referer']
            self.referer = self.request.META['HTTP_REFERER']
        except:
            self.referer = None

    ### TODO: check code position

    def error(self,errorcode,message='an error occured'):
        if errorcode == 404:
            message = 'Sorry, we were not able to find the requested page.  We have logged this error and will look into it.'
        elif errorcode == 403:
            message = 'Sorry, that page is reserved for administrators.  '
        elif errorcode == 500:
            message = "Sorry, the server encountered an error.  We have logged this error and will look into it."

        message+="<p><pre>"+traceback.format_exc()+"</pre><br></p>"
        #self.template_vals.update( {'errorcode':errorcode,'message':message})

        # TODO:zy
        #if errorcode>0:
            #self.response.set_status(errorcode)


        #errorfile=getattr(self.blog.theme,'error'+str(errorcode))
        #logging.debug(errorfile)
##        if not errorfile:
##            errorfile=self.blog.theme.error
        errorfile='error'+str(errorcode)+".html"
        #try:
        #    content=micolog_template.render(self.blog.theme,errorfile, self.template_vals)
        #except TemplateDoesNotExist:
        #    try:
        #        content=micolog_template.render(self.blog.theme,"error.html", self.template_vals)
        #    except TemplateDoesNotExist:
        #        content=micolog_template.render(self.blog.default_theme,"error.html", self.template_vals)
        #    except:
        #        content=message
        #except:
        #    content=message
        #self.response.out.write(content)
        return self.render(errorfile, {'errorcode':errorcode,'message':message})

    def message(self,msg,returl=None,title='Infomation'):
        return self.render('msg',{'message':msg,'title':title,'returl':returl})

    def render(self, template_file, params={}, mimetype=None, status=None,
            content_type=None):
        """
        Helper method to render the appropriate template
        """
        params.update(self.template_vals)
        template = get_template_uri(self.app_context, template_file)
        t = loader.get_template(template)
        c = RequestContext(self.request, params)
        self.response.write(t.render(c))
        if mimetype:
            content_type = mimetype
        if content_type:
            self.response['Content-Type'] = content_type
        #response = HttpResponse(t.render(c), **kargs)
        
    def render2(self, template_file, params={}, **kargs):
        self.render(template_file, params, **kargs)
    
    def render2_bak(self, template_file, params={}):
        """
        Helper method to render the appropriate template
        """

        params.update(self.template_vals)
        template = get_template_uri(self.app_context, template_file)
        return shortcuts.render_to_response(template_name = template, dictionary = params,
                                            context_instance = RequestContext(self.request))

    def param(self, name, **kw):
        method = getattr(self.request, self.request.method)
        method2 = getattr(self.request, self.request.method == 'GET' and 'POST' or 'GET')
        ret = method.get(name)
        if not ret:
            ret = method2.get(name, **kw)
        return ret and ret or ''

    def paramstr(self, name, **kw):
        return self.param(name, **kw)
    
    def paramint(self, name, default=0):
        value = self.param(name)
        try:
           return int(value)
        except:
           return default

    def parambool(self, name, default=False):
        value = self.param(name)
        try:
           return value=='on'
        except:
           return default
           
    def paramfloat(self, name, default=0.00):
        value = self.param(name)
        try:
           return float(value)
        except:
           return default
           
    def paramlist(self, name, **kw):
        lst = self.param(name)
        return lst and lst.split(',') or []
        
    def write(self, s):
        self.response.out.write(s)

    def chk_login(self, redirect_url='/'):
        if self.is_login:
            return True
        else:
            self.redirect(redirect_url)
            return False

    def chk_admin(self, redirect_url='/'):
        if self.is_admin:
            return True
        else:
            self.redirect(redirect_url)
            return False
            
    def redirect(self, to, *args, **kwargs):
        if kwargs.pop('permanent', False):
            self.response.status_code = 301
        else:
            self.response.status_code = 302
        # If it's a model, use get_absolute_url()
        iri = to
        if hasattr(to, 'get_absolute_url'):
            iri = to.get_absolute_url()
        else:
            # Next try a reverse URL resolution.
            try:
                iri = urlresolvers.reverse(to, args=args, kwargs=kwargs)
            except urlresolvers.NoReverseMatch:
                # If this is a callable, re-raise.
                if callable(to):
                    raise
                # If this doesn't "feel" like a URL, re-raise.
                if '/' not in to and '.' not in to:
                    raise
        self.response['Location'] = iri_to_uri(iri)
        #return shortcuts.redirect(uri)
        

class AdminBaseRequestHandler(SiteRequestHandler):
    def __init__(self):
        SiteRequestHandler.__init__(self)
        self.app = AppContext(current_app = 'admin')
        self.app_context = self.app
        self.template_vals = get_extra_context(self.app_context)
        # TODO: remove
        self.current='home'
    def initialize(self, request):
        SiteRequestHandler.initialize(self, request)
        self.blog = configs.get_g_blog()
        #self.admin = g_admin
        #self.site = g_site
        # TODO: remove
        self.template_vals.update({'self':self,'blog':self.blog,'current':self.current})

class BlogRequestHandler(SiteRequestHandler):
    def __init__(self):
        SiteRequestHandler.__init__(self)
        self.current='home'
        self.app = AppContext(current_app = 'blog')
        self.app_context = self.app
        self.template_vals = get_extra_context(self.app_context)
    def initialize(self, request):
        SiteRequestHandler.initialize(self, request)
        self.blog = configs.get_g_blog()

        self.template_vals.update({'self':self,'blog':self.blog,'current':self.current})

### Adapt to micolog
class BaseRequestHandler(BlogRequestHandler):
    def __init__(self):
        BlogRequestHandler.__init__(self)
    def initialize(self, request):
        BlogRequestHandler.initialize(self, request)




#class MyView(View):
#    def __init__(self, arg=None):
#        self.arg = arg
#    def get(request):
#        return HttpResponse(self.arg or 'No args passed')
#
#@login_required
#class MyOtherView(View):
#    def post(request):
#        return HttpResponse()
#
## in urls.py
## And all the following work as expected.
#urlpatterns = patterns(''
#    url(r'^myview1$', 'myapp.views.MyView', name='myview1'),
#    url(r'^myview2$', myapp.views.MyView, name='myview2'),
#    url(r'^myview3$', myapp.views.MyView('foobar'), name='myview3'),
#    url(r'^myotherview$', 'myapp.views.MyOtherView', name='otherview'),
#)

class Pager(object):

    def __init__(self, model=None,query=None, items_per_page=10):
        if model:
            self.query = model.all()
        else:
            self.query=query

        self.items_per_page = items_per_page

    def fetch(self, p):
        if hasattr(self.query,'__len__'):
            max_offset=len(self.query)
        else:
            max_offset = self.query.count()
        n = max_offset / self.items_per_page
        if max_offset % self.items_per_page != 0:
            n += 1

        if p < 0 or p > n:
            p = 1
        offset = (p - 1) * self.items_per_page
        if hasattr(self.query,'fetch'):
            results = self.query.fetch(self.items_per_page, offset)
        else:
            results = self.query[offset:offset+self.items_per_page]



        links = {'count':max_offset,'page_index':p,'prev': p - 1, 'next': p + 1, 'last': n}
        if links['next'] > n:
            links['next'] = 0

        return (results, links)

##############################################################

logging.info('module base reloaded')
def urldecode(value):
    return  urllib.unquote(urllib.unquote(value)).decode('utf8')
    #return  urllib.unquote(value).decode('utf8')

def urlencode(value):
    return urllib.quote(value.encode('utf8'))

def sid():
    now=datetime.datetime.now()
    return now.strftime('%y%m%d%H%M%S')+str(now.microsecond)

def requires_admin(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_login:
            self.redirect(users.create_login_url(self.request.uri))
            return
        elif not (self.is_admin or self.author):
            self.error(403)
            return
        else:
            method(self, *args, **kwargs)
            return
    return wrapper
    
    
def printinfo(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        print self #.__name__
        print dir(self)
        for x in self.__dict__:
            print x
        return method(self, *args, **kwargs)
    return wrapper
#only ajax methed allowed
def ajaxonly(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.request.headers["X-Requested-With"]=="XMLHttpRequest":
             self.error(404)
        else:
            return method(self, *args, **kwargs)
    return wrapper

#only request from same host can passed
def hostonly(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if  self.request.headers['Referer'].startswith(os.environ['HTTP_HOST'],7):
            return method(self, *args, **kwargs)
        else:
            self.error(404)
    return wrapper

def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def cache(key="",time=3600):
    def _decorate(method):
        def _wrapper(*args, **kwargs):
            if not configs.get_g_blog().enable_memcache:
                return method(*args, **kwargs)
            html= memcache.get(skey)
            #arg[0] is BaseRequestHandler object

            if html:
                logging.info('cache:'+skey)
                response.last_modified =html[1]
                ilen=len(html)
                if ilen>=3:
                    response.set_status(html[2])
                if ilen>=4:
                    for skey,value in html[3].items():
                        response.headers[skey]=value
                response.out.write(html[0])
            else:
                if 'last-modified' not in response.headers:
                    response.last_modified = format_date(datetime.utcnow())

                method(*args, **kwargs)
                result=response.out.getvalue()
                status_code = response._Response__status[0]
                logging.debug("Cache:%s"%status_code)
                memcache.set(skey,(result,response.last_modified,status_code,response.headers),time)

        return _wrapper
    return _decorate

#-------------------------------------------------------------------------------
class PingbackError(Exception):
    """Raised if the remote server caused an exception while pingbacking.
    This is not raised if the pingback function is unable to locate a
    remote server.
    """

    _ = lambda x: x
    default_messages = {
        16: _(u'source URL does not exist'),
        17: _(u'The source URL does not contain a link to the target URL'),
        32: _(u'The specified target URL does not exist'),
        33: _(u'The specified target URL cannot be used as a target'),
        48: _(u'The pingback has already been registered'),
        49: _(u'Access Denied')
    }
    del _

    def __init__(self, fault_code, internal_message=None):
        Exception.__init__(self)
        self.fault_code = fault_code
        self._internal_message = internal_message

    def as_fault(self):
        """Return the pingback errors XMLRPC fault."""
        return Fault(self.fault_code, self.internal_message or
                     'unknown server error')

    @property
    def ignore_silently(self):
        """If the error can be ignored silently."""
        return self.fault_code in (17, 33, 48, 49)

    @property
    def means_missing(self):
        """If the error means that the resource is missing or not
        accepting pingbacks.
        """
        return self.fault_code in (32, 33)

    @property
    def internal_message(self):
        if self._internal_message is not None:
            return self._internal_message
        return self.default_messages.get(self.fault_code) or 'server error'

    @property
    def message(self):
        msg = self.default_messages.get(self.fault_code)
        if msg is not None:
            return _(msg)
        return _(u'An unknown server error (%s) occurred') % self.fault_code

class util:
    @classmethod
    def do_trackback(cls, tbUrl=None, title=None, excerpt=None, url=None, blog_name=None):
        taskqueue.add(url='/admin/do/trackback_ping',
            params={'tbUrl': tbUrl,'title':title,'excerpt':excerpt,'url':url,'blog_name':blog_name})

    #pingback ping
    @classmethod
    def do_pingback(cls,source_uri, target_uri):
        taskqueue.add(url='/admin/do/pingback_ping',
            params={'source': source_uri,'target':target_uri})

from utils.BeautifulSoup import BeautifulSoup
def get_excerpt(content):
    soup = BeautifulSoup(content)
    return soup.getText()[:100]
