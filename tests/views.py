#coding=utf-8
import os
import re
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.webapp import template
from weibopy.auth import OAuthHandler
from weibopy.api import API
from gaesessions import get_current_session
import django
from django import http
from django import shortcuts
from django.template import RequestContext
from blog.model import Entry, Link, Archive, Tag, Category, Comment

import configs

from django.core.urlresolvers import reverse
from google.appengine.ext import db

from utils import get_template_uri, get_extra_context, AppContext, register_templatetags

from base import TemplateView, Pager, BlogRequestHandler, BaseRequestHandler
from datetime import datetime ,timedelta
import base64,random
_ = lambda x: x

def InitBlogData():
	entry=Entry(title=_("Hello world!").decode('utf8'))
	entry.content=_('<p>Welcome to micolog. This is your first post. Edit or delete it, then start blogging!</p>').decode('utf8')
	entry.save(True)
	link=Link(href='http://xuming.net',linktext=_("Xuming's blog").decode('utf8'))
	link.put()
	
	
class BlogView(TemplateView):
    def __init__(self):
        self.blog = configs.get_g_blog()
        self.app_context = AppContext(current_app = 'blog')
        self.template_vals = get_extra_context(self.app_context)
    def test(self):
        pass
    def initialize(self, request):
        m_pages=Entry.all().filter('entrytype =','page')\
            .filter('published =',True)\
            .filter('entry_parent =',0)\
            .order('menu_order')
        blogroll=Link.all().filter('linktype =','blogroll')
        archives=Archive.all().order('-year').order('-month').fetch(12)
        alltags=Tag.all()
        self.template_vals.update({
                        'menu_pages':m_pages,
                        'categories':Category.all(),
                        'blogroll':blogroll,
                        'archives':archives,
                        'alltags':alltags,
                        'recent_comments':Comment.all().order('-date').fetch(5)
        })

    def render(self, template, params):
        params.update(self.template_vals)
        template = get_template_uri(self.app_context, 'index.html')
        return shortcuts.render_to_response(template_name = template, dictionary = params,
                                            context_instance = RequestContext(self.request))

class TestBlog(BaseRequestHandler):
    def __init__(self):
        BlogRequestHandler.__init__(self)
        pass
    def initialize(self, request):
        pass
    def GET(self):
        a = configs.get_g_blog()
        #a = self.blog
        #return self.render('test/testblog.html', {})
        return self.render2('/test/testblog.html', {})
        #return self.redirect('/')
        
class TestApplication(BaseRequestHandler):
    def __init__(self):
        BlogRequestHandler.__init__(self)
        pass
    def initialize(self, request):
        pass
    def GET(self):
        #import django_bootstrap2
        #t = dir(django_bootstrap2.application)
        #t = dir(django_bootstrap2.t)
        from base import cache
        t = TestBlog.__name__
        return self.render2('/test/testapplication.html', {'django_bootstrap2': t})
        
        
# And all the following work as expected.
#urlpatterns = patterns(''
#    url(r'^myview1$', 'myapp.views.MyView', name='myview1'),
#    url(r'^myview2$', myapp.views.MyView, name='myview2'),
#    url(r'^myview3$', myapp.views.MyView('foobar'), name='myview3'),
#    url(r'^myotherview$', 'myapp.views.MyOtherView', name='otherview'),
#)


#class BlogHandler(BlogView):
class MainPage(BlogView):
#    def initialize(self, request):
#        BlogView.initialize(self, request)
#        super(MainPage, self).initialize(request)
#        
    def GET(self):
        #super(MainPage, self).initialize(request)
        params = {}
        page = 1
        entries = Entry.all().filter('entrytype =','post').\
    				filter("published =", True).order('-date').\
    				fetch(self.blog.posts_per_page, offset = (page-1) * self.blog.posts_per_page)
        for entry in entries:
            entry.link = '%s/%s' % (self.app_context.current_app, entry.link)

        params['entries'] = entries
        return self.render('index.html', params)

class archive_by_month(BlogView):
	#@cache()
	def GET(self, year, month):
		try:
			page_index=int (self.param('page'))
		except:
			page_index=1

		firstday=datetime(int(year),int(month),1)
		if int(month)!=12:
			lastday=datetime(int(year),int(month)+1,1)
		else:
			lastday=datetime(int(year)+1,1,1)
		entries=db.GqlQuery("SELECT * FROM Entry WHERE date > :1 AND date <:2 AND entrytype =:3 AND published = True ORDER BY date DESC",firstday,lastday,'post')
		entries, links=Pager(query=entries).fetch(page_index)

		return self.render('month',{'entries':entries,'year':year,'month':month,'pager':links})

if 0:
	def initialize(self, request, response):
		BaseRequestHandler.initialize(self,request, response)
		m_pages=Entry.all().filter('entrytype =','page')\
			.filter('published =',True)\
			.filter('entry_parent =',0)\
			.order('menu_order')
		blogroll=Link.all().filter('linktype =','blogroll')
		archives=Archive.all().order('-year').order('-month').fetch(12)
		alltags=Tag.all()
		self.template_vals.update({
						'menu_pages':m_pages,
						'categories':Category.all(),
						'blogroll':blogroll,
						'archives':archives,
						'alltags':alltags,
						'recent_comments':Comment.all().order('-date').fetch(5)
		})

	def m_list_pages(self):
		menu_pages=None
		entry=None
		if self.template_vals.has_key('menu_pages'):
			menu_pages= self.template_vals['menu_pages']
		if self.template_vals.has_key('entry'):
			entry=self.template_vals['entry']
		ret=''
		current=''
		for page in menu_pages:
			if entry and entry.entrytype=='page' and entry.key()==page.key():
				current= 'current_page_item'
			else:
				current= 'page_item'
			#page is external page ,and page.slug is none.
			if page.is_external_page and not page.slug:
				ret+='<li class="%s"><a href="%s" target="%s" >%s</a></li>'%( current,page.link,page.target, page.title)
			else:
				ret+='<li class="%s"><a href="/%s" target="%s">%s</a></li>'%( current,page.link, page.target,page.title)
		return ret

	def sticky_entrys(self):
		return Entry.all().filter('entrytype =','post')\
			.filter('published =',True)\
			.filter('sticky =',True)\
			.order('-date')
			                                      
#def archive_by_month(request, year=None, month=None):
#    @cache()
#	if year and month:
#		try:
#			page_index=int (self.param('page'))
#		except:
#			page_index=1
#
#		firstday=datetime(int(year),int(month),1)
#		if int(month)!=12:
#			lastday=datetime(int(year),int(month)+1,1)
#		else:
#			lastday=datetime(int(year)+1,1,1)
#		entries=db.GqlQuery("SELECT * FROM Entry WHERE date > :1 AND date <:2 AND entrytype =:3 AND published = True ORDER BY date DESC",firstday,lastday,'post')
#		entries,links=Pager(query=entries).fetch(page_index)
#
#		self.render('month',{'entries':entries,'year':year,'month':month,'pager':links})


register_templatetags(['blog.templatetags.blog_tags', 'blog.templatetags.filter', 'app.recurse'])
