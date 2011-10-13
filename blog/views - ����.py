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
from model import Entry, Link, Archive
from settings import g_blog

from django.core.urlresolvers import reverse

from utils import get_template_uri, get_extra_context, AppContext, register_templatetags
_ = lambda x: x
appContext = AppContext(current_app = 'blog')
def InitBlogData():
	entry=Entry(title=_("Hello world!").decode('utf8'))
	entry.content=_('<p>Welcome to micolog. This is your first post. Edit or delete it, then start blogging!</p>').decode('utf8')
	entry.save(True)
	link=Link(href='http://xuming.net',linktext=_("Xuming's blog").decode('utf8'))
	link.put()

def MainPage(request):
    params = get_extra_context(appContext)
    page = 1
    entries = Entry.all().filter('entrytype =','post').\
				filter("published =", True).order('-date').\
				fetch(g_blog.posts_per_page, offset = (page-1) * g_blog.posts_per_page)
    for entry in entries:
        entry.link = '%s/%s' % (appContext.current_app, entry.link)
    archives=Archive.all().order('-year').order('-month').fetch(12)
    
    params['entries'] = entries
    params['archives'] = archives
    template = get_template_uri(appContext, 'index.html')
    return shortcuts.render_to_response(template_name = template, dictionary = params,
                                        context_instance = RequestContext(request))

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
