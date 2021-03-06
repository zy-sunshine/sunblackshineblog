﻿#coding=utf-8
import logging
import cgi, os,sys,math
import re
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.ext.webapp import template
from weibopy.auth import OAuthHandler
from weibopy.api import API
#from gaesessions import get_current_session
import django
from django import http
from django import shortcuts
from django.template import RequestContext

from blog.models import Entry, Link, Archive, Tag, Category, Comment
#from models import Entry, Link, Archive, Tag, Category, Comment
#import pdb; pdb.set_trace()

from django.core.urlresolvers import reverse
from google.appengine.ext import db

from utils import get_template_uri, get_extra_context, AppContext, register_templatetags

from base import BaseRequestHandler
from base import cache, requires_admin, ajaxonly
from base import urlencode

from base import urldecode

#from google.appengine.api import memcache
from django.core.cache import cache as memcache

#from datetime import datetime ,timedelta
#import base64,random
#_ = lambda x: x
from django.utils.translation import gettext_lazy as _

from datetime import datetime ,timedelta
import base64,random
from django.utils import simplejson
from blog.templatetags import filter  as myfilter

from app.safecode import Image
from app.gmemsess import Session

from google.appengine.ext import zipserve
from base import Pager

#def doRequestHandle(old_handler,new_handler,**args):
#    new_handler.initialize(old_handler.request)
#    return new_handler.GET(**args)

#def doRequestPostHandle(old_handler,new_handler,**args):
#    new_handler.initialize(old_handler.request)
#    return new_handler.POST(**args)

class BasePublicPage(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
        m_pages=Entry.all().filter(entrytype = 'page') \
            .filter(published = True)\
            .filter(entry_parent = 0)\
            .order_by('menu_order')
        blogroll=Link.all().filter(linktype = 'blogroll')
        #archives=Archive.all().order_by('-year').order_by('-month').fetch(12)
        archives=Archive.all().order_by('-year', '-month')[0:12]
        alltags=Tag.all()
        self.template_vals.update({
                        'menu_pages':m_pages,
                        'categories':Category.all(),
                        'blogroll':blogroll,
                        'archives':archives,
                        'alltags':alltags,
                        'recent_comments':Comment.all().order_by('-date')[0:5]#.fetch(5)
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
                ret+='<li class="%s"><a href="/blog/%s" target="%s">%s</a></li>'%( current,page.link, page.target,page.title)
        return ret

    def sticky_entrys(self):
        return Entry.all().filter(entrytype = 'post')\
            .filter(published = True)\
            .filter(sticky = True)\
            .order_by('-date')

class MainPage(BasePublicPage):
    def __init__(self):
        BasePublicPage.__init__(self)
    def initialize(self, request):
        BasePublicPage.initialize(self, request)
    def HEAD(self,page=1):
        if self.blog.allow_pingback:
            self.response.headers['X-Pingback']="%s/rpc"%str(self.blog.baseurl)
    def GET(self,page=1):
        postid=self.param('p')
        if postid:
            #try:
            if 1:
                postid=int(postid)
                #return doRequestHandle(self,SinglePost(self.request),postid=postid)  #singlepost.get(postid=postid)
                self.response = SinglePost(self.request, postid=postid)
                return
            #except:
            else:
                self.error(404)
                return
        if self.blog.allow_pingback:
            self.response.headers['X-Pingback']="%s/rpc"%str(self.blog.baseurl)
        self.doget(page)

    def POST(self):
        postid=self.param('p')
        if postid:
            try:
                postid=int(postid)
                #doRequestPostHandle(self,SinglePost(),postid=postid)  #singlepost.get(postid=postid)
                self.response = SinglePost(self.request, postid=postid)
            except:
                self.error(404)


    @cache()
    def doget(self,page):
        page=int(page)
        #entrycount=self.blog.postscount()
        entrycount=Entry.postscount()
        max_page = entrycount / self.blog.posts_per_page + ( entrycount % self.blog.posts_per_page and 1 or 0 )

        if page < 1 or page > max_page:
            return self.error(404)

        offset_start = (page-1) * self.blog.posts_per_page
        offset_end = offset_start + self.blog.posts_per_page
        entries = Entry.all().filter(entrytype = 'post').\
                filter(published = True).order_by('-date')[offset_start:offset_end]#.\
                #fetch(self.blog.posts_per_page, offset = (page-1) * self.blog.posts_per_page)
        #import pdb; pdb.set_trace()

        show_prev =entries and  (not (page == 1))
        #show_prev = True
        show_next =entries and  (not (page == max_page))
        #show_next = True
        #print page,max_page,self.blog.entrycount,self.blog.posts_per_page


        self.render('index',{'entries':entries,
                           'show_prev' : show_prev,
                        'show_next' : show_next,
                        'pageindex':page,
                        'ishome':True,
                        'pagecount':max_page,
                        'postscounts':entrycount
                            })


class entriesByCategory(BasePublicPage):
    def __init__(self):
        BasePublicPage.__init__(self)
    def initialize(self, request):
        BasePublicPage.initialize(self, request)
    @cache()
    def GET(self,slug=None):
        if not slug:
             self.error(404)
             return
        try:
            page_index=int(self.param('page'))
        except:
            page_index=1
        slug=urldecode(slug)

        cats=Category.all().filter(slug = slug)[0:1]#.fetch(1)
        if cats:
            entries=Entry.all().filter(published = True).filter(categorie_keys = cats[0].key()).order_by("-date")
            entries,links=Pager(query=entries,items_per_page=20).fetch(page_index)
            self.render('category',{'entries':entries,'category':cats[0],'pager':links})
        else:
            self.error(404,slug)

class archive_by_month(BasePublicPage):
    def __init__(self):
        BasePublicPage.__init__(self)
    def initialize(self, request):
        BasePublicPage.initialize(self, request)
    @cache()
    def GET(self,year,month):
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
        entries,links=Pager(query=entries).fetch(page_index)

        self.render('month',{'entries':entries,'year':year,'month':month,'pager':links})

class entriesByTag(BasePublicPage):
    def __init__(self):
        BasePublicPage.__init__(self)
    def initialize(self, request):
        BasePublicPage.initialize(self, request)
    @cache()
    def GET(self,slug=None):
        if not slug:
             self.error(404)
             return
        try:
            page_index=int (self.param('page'))
        except:
            page_index=1
        import urllib
        slug=urldecode(slug)

        entries=Entry.all().filter(published = True).filter(tags = slug).order_by("-date")
        entries,links=Pager(query=entries,items_per_page=20).fetch(page_index)
        self.render('tag',{'entries':entries,'tag':slug,'pager':links})



class SinglePost(BasePublicPage):
    def __init__(self):
        BasePublicPage.__init__(self)
    def initialize(self, request):
        BasePublicPage.initialize(self, request)
    def HEAD(self,slug=None,postid=None):
        if self.blog.allow_pingback:
            self.response.headers['X-Pingback']="%s/rpc"%str(self.blog.baseurl)

    @cache()
    def GET(self,slug=None,postid=None):
        if postid:
            postid = int(postid)
            entries = Entry.all().filter(published = True).filter(post_id = postid)[0:1]#.fetch(1)
        else:
            slug=urldecode(slug)
            entries = Entry.all().filter(published = True).filter(link = slug)[0:1]#.fetch(1)
        if not entries or len(entries) == 0:
            self.error(404)
            return

        mp=self.paramint("mp",1)

        entry=entries[0]
        if entry.is_external_page:
            self.redirect(entry.external_page_address,True)
        if self.blog.allow_pingback and entry.allow_trackback:
            self.response.headers['X-Pingback']="%s/rpc"%str(self.blog.baseurl)
        entry.readtimes += 1
        entry.put()
        self.entry=entry


        comments=entry.get_comments_by_page(mp,self.blog.comments_per_page)


##        commentuser=self.request.cookies.get('comment_user', '')
##        if commentuser:
##            commentuser=commentuser.split('#@#')
##        else:
        commentuser=['','','']

        comments_nav=self.get_comments_nav(mp,entry.purecomments().count())

        if entry.entrytype=='post':
            self.render('single',
                        {
                        'entry':entry,
                        'relateposts':entry.relateposts,
                        'comments':comments,
                        'user_name':commentuser[0],
                        'user_email':commentuser[1],
                        'user_url':commentuser[2],
                        'checknum1':random.randint(1,10),
                        'checknum2':random.randint(1,10),
                        'comments_nav':comments_nav,
                        })

        else:
            self.render('page',
                        {'entry':entry,
                        'relateposts':entry.relateposts,
                        'comments':comments,
                        'user_name':commentuser[0],
                        'user_email':commentuser[1],
                        'user_url':commentuser[2],
                        'checknum1':random.randint(1,10),
                        'checknum2':random.randint(1,10),
                        'comments_nav':comments_nav,
                        })

    def POST(self,slug=None,postid=None):
        '''handle trackback'''
        error = '''<?xml version="1.0" encoding="utf-8"?>
<response>
<error>1</error>
<message>%s</message>
</response>
'''
        success = '''<?xml version="1.0" encoding="utf-8"?>
<response>
<error>0</error>
</response>
'''

        if not self.blog.allow_trackback:
            self.response.out.write(error % "Trackback denied.")
            return
        self.response.headers['Content-Type'] = "text/xml"
        if postid:
            entries = Entry.all().filter(published = True).filter(post_id = postid)[0:1]#.fetch(1)
        else:
            slug=urldecode(slug)
            entries = Entry.all().filter(published = True).filter(link = slug)[0:1]#.fetch(1)

        if not entries or len(entries) == 0 :#or  (postid and not entries[0].link.endswith(self.blog.default_link_format%{'post_id':postid})):
            self.response.out.write(error % "empty slug/postid")
            return
        #check code ,rejest spam
        entry=entries[0]
        logging.info(self.request.remote_addr+self.request.path+" "+entry.trackbackurl)
        #key=self.param("code")
        #if (self.request.uri!=entry.trackbackurl) or entry.is_external_page or not entry.allow_trackback:
        #import cgi
        from urlparse import urlparse
        param=urlparse(self.request.uri)
        code=param[4]
        param=cgi.parse_qs(code)
        if param.has_key('code'):
            code=param['code'][0]

        if  (not str(entry.key())==code) or entry.is_external_page or not entry.allow_trackback:
            self.response.out.write(error % "Invalid trackback url.")
            return


        coming_url = self.param('url')
        blog_name = myfilter.do_filter(self.param('blog_name'))
        excerpt = myfilter.do_filter(self.param('excerpt'))
        title = myfilter.do_filter(self.param('title'))

        if not coming_url or not blog_name or not excerpt or not title:
            self.response.out.write(error % "not enough post info")
            return

        import time
        #wait for half second in case otherside hasn't been published
        time.sleep(0.5)

##        #also checking the coming url is valid and contains our link
##        #this is not standard trackback behavior
##        try:
##
##            result = urlfetch.fetch(coming_url)
##            if result.status_code != 200 :
##                #or ((self.blog.baseurl + '/' + slug) not in result.content.decode('ascii','ignore')):
##                self.response.out.write(error % "probably spam")
##                return
##        except Exception, e:
##            logging.info("urlfetch error")
##            self.response.out.write(error % "urlfetch error")
##            return

        comment = Comment.all().filter(entry = entry).filter(weburl = coming_url).get()
        if comment:
            self.response.out.write(error % "has pinged before")
            return

        comment=Comment(author=blog_name,
                content="...<strong>"+title[:250]+"</strong> " +
                        excerpt[:250] + '...',
                weburl=coming_url,
                entry=entry)

        comment.ip=self.request.remote_addr
        comment.ctype=COMMENT_TRACKBACK
        try:
            comment.save()

            memcache.delete("/"+entry.link)
            self.write(success)
            self.blog.tigger_action("pingback_post",comment)
        except:
            self.response.out.write(error % "unknow error")

    def get_comments_nav(self,pindex,count):

        maxpage=count / self.blog.comments_per_page + ( count % self.blog.comments_per_page and 1 or 0 )
        if maxpage==1:
            return {'nav':"",'current':pindex}

        result=""

        if pindex>1:
            result="<a class='comment_prev' href='"+self.get_comments_pagenum_link(pindex-1)+"'>«</a>"

        minr=max(pindex-3,1)
        maxr=min(pindex+3,maxpage)
        if minr>2:
            result+="<a class='comment_num' href='"+self.get_comments_pagenum_link(1)+"'>1</a>"
            result+="<span class='comment_dot' >...</span>"

        for  n in range(minr,maxr+1):
            if n==pindex:
                result+="<span class='comment_current'>"+str(n)+"</span>"
            else:
                result+="<a class='comment_num' href='"+self.get_comments_pagenum_link(n)+"'>"+str(n)+"</a>"
        if maxr<maxpage-1:
            result+="<span class='comment_dot' >...</span>"
            result+="<a class='comment_num' href='"+self.get_comments_pagenum_link(maxpage)+"'>"+str(maxpage)+"</a>"

        if pindex<maxpage:
            result+="<a class='comment_next' href='"+self.get_comments_pagenum_link(pindex+1)+"'>»</a>"

        return {'nav':result,'current':pindex,'maxpage':maxpage}

    def get_comments_pagenum_link(self,pindex):
        url=str(self.entry.link)
        if url.find('?')>=0:
            return "/"+url+"&mp="+str(pindex)+"#comments"
        else:
            return "/"+url+"?mp="+str(pindex)+"#comments"

class FeedHandler(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    @cache(time=600)
    def GET(self,tags=None):
        entries = Entry.all().filter(entrytype = 'post').filter(published = True).order_by('-date')[0:10]#.fetch(10)
        if entries and entries[0]:
            last_updated = entries[0].date
            last_updated = last_updated.strftime("%a, %d %b %Y %H:%M:%S +0000")
        for e in entries:
            e.formatted_date = e.date.strftime("%a, %d %b %Y %H:%M:%S +0000")
        self.response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
        self.render2('/admin/views/rss.xml',{'entries':entries,'last_updated':last_updated})

class CommentsFeedHandler(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    @cache(time=600)
    def GET(self,tags=None):
        comments = Comment.all().order_by('-date').filter(ctype = 0)[0:10]#.fetch(10)
        if comments and comments[0]:
            last_updated = comments[0].date
            last_updated = last_updated.strftime("%a, %d %b %Y %H:%M:%S +0000")
        for e in comments:
            e.formatted_date = e.date.strftime("%a, %d %b %Y %H:%M:%S +0000")
        self.response.headers['Content-Type'] = 'application/rss+xml; charset=UTF-8'
        self.render2('views/comments.xml',{'comments':comments,'last_updated':last_updated})

## TODO: move it to Site range
class SitemapHandler(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    @cache(time=36000)
    def GET(self,tags=None):
        urls = []
        def addurl(loc,lastmod=None,changefreq=None,priority=None):
            url_info = {
                'location':   loc,
                'lastmod':    lastmod,
                'changefreq': changefreq,
                'priority':   priority
            }
            urls.append(url_info)

        addurl(self.blog.baseurl,changefreq='daily',priority=0.9 )

        entries = Entry.all().filter(published = True).order_by('-date')[0:self.blog.sitemap_entries]#.fetch(self.blog.sitemap_entries)

        for item in entries:
            loc = "%s/%s" % (self.blog.baseurl, item.link)
            addurl(loc,item.mod_date or item.date,'never',0.6)

        if self.blog.sitemap_include_category:
            cats=Category.all()
            for cat in cats:
                loc="%s/category/%s"%(self.blog.baseurl,cat.slug)
                addurl(loc,None,'weekly',0.5)

        if self.blog.sitemap_include_tag:
            tags=Tag.all()
            for tag in tags:
                loc="%s/tag/%s"%(self.blog.baseurl, urlencode(tag.tag))
                addurl(loc,None,'weekly',0.5)


##        self.response.headers['Content-Type'] = 'application/atom+xml'
        self.render('/admin/views/sitemap.xml', {'urlset':urls}, content_type='text/xml')#, content_type='application/xhtml+xml')

class Error404(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    @cache(time=36000)
    def GET(self,slug=None):
        self.error(404)

class Post_comment(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    #@printinfo
    def POST(self,slug=None):
        useajax=self.param('useajax')=='1'
        logging.debug('+++++++++++++++++++++++1')
        name=self.param('author')
        email=self.param('email')
        url=self.param('url')

        key=self.param('key')
        content=self.param('comment')
        parent_id=self.paramint('parentid',0)
        reply_notify_mail=self.parambool('reply_notify_mail')

        sess=Session(self,timeout=180)
        if not self.is_login:
            #if not (self.request.cookies.get('comment_user', '')):
            #try:
            if 1:
                check_ret=True
                if self.blog.comment_check_type in (1,2)  :
                    checkret=self.param('checkret')
                    check_ret=(int(checkret) == sess['code'])
                elif self.blog.comment_check_type ==3:
                    import app.gbtools as gb
                    checknum=self.param('checknum')
                    checkret=self.param('checkret')
                    check_ret=eval(checknum)==int(gb.stringQ2B( checkret))

                if not check_ret:
                    if useajax:
                        self.write(simplejson.dumps((False,-102,_('Your check code is invalid .')),ensure_ascii = False))
                    else:
                        self.error(-102,_('Your check code is invalid .'))
                    return
            #except:
            if 0:
                if useajax:
                    self.write(simplejson.dumps((False,-102,_('Your check code is invalid .')),ensure_ascii = False))
                else:
                    self.error(-102,_('Your check code is invalid .'))
                return
        sess.invalidate()
        content=content.replace('\n','<br />')
        content=myfilter.do_filter(content)
        name=cgi.escape(name)[:20]
        url=cgi.escape(url)[:100]
        if not (name and email and content):
            if useajax:
                self.write(simplejson.dumps((False,-101,_('Please input name, email and comment .'))))
            else:
                self.error(-101,_('Please input name, email and comment .'))
        else:
            comment=Comment(author=name,
                            content=content,
                            email=email,
                            reply_notify_mail=reply_notify_mail,
                            entry=Entry.get(key))
            if url:
                try:
                    if not url.lower().startswith(('http://','https://')):
                        url = 'http://' + url
                    comment.weburl=url
                except:
                    comment.weburl=None

            #name=name.decode('utf8').encode('gb2312')


            info_str='#@#'.join([urlencode(name),urlencode(email),urlencode(url)])

             #info_str='#@#'.join([name,email,url.encode('utf8')])
            cookiestr='comment_user=%s;expires=%s;path=/;'%( info_str,
                       (datetime.now()+timedelta(days=100)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
                       
                       )
            comment.ip=self.request.remote_addr

            if parent_id:
                comment.parent=Comment.get_by_id(parent_id)

            comment.no=comment.entry.commentcount+1
            #try:
            if 1:
                comment.save()
                memcache.delete("/"+comment.entry.link)

                self.response.headers.add_header( 'Set-Cookie', cookiestr)
                if useajax:
                    comment_c=self.get_render('comment',{'comment':comment})
                    self.write(simplejson.dumps((True,comment_c.decode('utf8')),ensure_ascii = False))
                else:
                    self.redirect(self.referer+"#comment-"+str(comment.key().id()))

                comment.entry.removecache()
                memcache.delete("/feed/comments")
            #except:
            if 0:
                if useajax:
                    self.write(simplejson.dumps((False,-102,_('Comment not allowed.'))))
                else:
                    self.error(-102,_('Comment not allowed .'))


class ChangeTheme(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    @requires_admin
    def GET(self,slug=None):
       theme=self.param('t')
       self.blog.theme_name=theme
       self.blog.get_theme()
       self.redirect('/')


class do_action(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    def GET(self,slug=None):

        try:
            func=getattr(self,'action_'+slug)
            if func and callable(func):
                func()
            else:
                self.error(404)
        except BaseException,e:
            self.error(404)

    def POST(self,slug=None):
        try:
            func=getattr(self,'action_'+slug)
            if func and callable(func):
                func()
            else:
                self.error(404)
        except:
             self.error(404)

    @ajaxonly
    def action_info_login(self):
        if self.login_user:
            self.write(simplejson.dumps({'islogin':True,
                                         'isadmin':self.is_admin,
                                         'name': self.login_user.nickname()}))
        else:
            self.write(simplejson.dumps({'islogin':False}))

    #@hostonly
    @cache()
    def action_proxy(self):
        result=urlfetch.fetch(self.param("url"), headers=self.request.headers)
        if result.status_code == 200:
            self.response.headers['Expires'] = 'Thu, 15 Apr 3010 20:00:00 GMT'
            self.response.headers['Cache-Control'] = 'max-age=3600,public'
            self.response.headers['Content-Type'] = result.headers['Content-Type']
            self.response.out.write(result.content)
        return

    def action_getcomments(self):
        key=self.param('key')
        entry=Entry.get(key)
        comments=Comment.all().filter(entry = key)

        commentuser=self.request.cookies.get('comment_user', '')
        if commentuser:
            commentuser=commentuser.split('#@#')
        else:
            commentuser=['','','']


        vals={
            'entry':entry,
            'comments':comments,
            'user_name':commentuser[0],
            'user_email':commentuser[1],
            'user_url':commentuser[2],
            'checknum1':random.randint(1,10),
            'checknum2':random.randint(1,10),
            }
        html=self.get_render('comments',vals)

        self.write(simplejson.dumps(html.decode('utf8')))

    def action_test(self):
        self.write(settings.LANGUAGE_CODE)
        self.write(_("this is a test"))


#class getMedia(webapp.RequestHandler):
#    def GET(self,slug):
#        media=Media.get(slug)
#        if media:
#            self.response.headers['Expires'] = 'Thu, 15 Apr 3010 20:00:00 GMT'
#            self.response.headers['Cache-Control'] = 'max-age=3600,public'
#            self.response.headers['Content-Type'] = str(media.mtype)
#            self.response.out.write(media.bits)
#            a=self.request.get('a')
#            if a and a.lower()=='download':
#                media.download+=1
#                media.put()
#


class CheckImg(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    def GET(self):
        img = Image()
        imgdata = img.create()
        sess=Session(self,timeout=900)
        if not sess.is_new():
            sess.invalidate()
            sess=Session(self,timeout=900)
        sess['code']=img.text
        sess.save()
        self.response.headers['Content-Type'] = "image/png"
        self.response.out.write(imgdata)


class CheckCode(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    def GET(self):
        sess=Session(self,timeout=900)
        num1=random.randint(1,10)
        num2=random.randint(1,10)
        code="<span style='font-size:13px;color:red'>%d + %d =</span>"%(num1,num2)
        sess['code']=num1+num2
        sess.save()
        #self.response.headers['Content-Type'] = "text/html"
        self.response.out.write(code)

class Other(BaseRequestHandler):
    def __init__(self):
        BaseRequestHandler.__init__(self)
    def initialize(self, request):
        BaseRequestHandler.initialize(self,request)
    def GET(self,slug=None):
        if not self.blog.tigger_urlmap(slug,page=self):
            self.error(404)

    def POST(self,slug=None):
        content=self.blog.tigger_urlmap(slug,page=self)
        if content:
            self.write(content)
        else:
            self.error(404)

def getZipHandler(**args):
    return ('/xheditor/(.*)',zipserve.make_zip_handler('''D:\\work\\micolog\\plugins\\xheditor\\xheditor.zip'''))











###################################################################################
#
#class MainPage(BlogView):
##    def initialize(self, request):
##        BlogView.initialize(self, request)
##        super(MainPage, self).initialize(request)
##        
#    def GET(self):
#        #super(MainPage, self).initialize(request)
#        params = {}
#        page = 1
#        entries = Entry.all().filter('entrytype =','post').\
#                    filter("published =", True).order_by('-date').\
#                    fetch(self.blog.posts_per_page, offset = (page-1) * self.blog.posts_per_page)
#        for entry in entries:
#            entry.link = '%s/%s' % (self.app_context.current_app, entry.link)
#
#        params['entries'] = entries
#        return self.render('index.html', params)
#
#class archive_by_month(BlogView):
#    #@cache()
#    def GET(self, year, month):
#        try:
#            page_index=int (self.param('page'))
#        except:
#            page_index=1
#
#        firstday=datetime(int(year),int(month),1)
#        if int(month)!=12:
#            lastday=datetime(int(year),int(month)+1,1)
#        else:
#            lastday=datetime(int(year)+1,1,1)
#        entries=db.GqlQuery("SELECT * FROM Entry WHERE date > :1 AND date <:2 AND entrytype =:3 AND published = True ORDER BY date DESC",firstday,lastday,'post')
#        entries, links=Pager(query=entries).fetch(page_index)
#
#        return self.render('month',{'entries':entries,'year':year,'month':month,'pager':links})
#

register_templatetags(['blog.templatetags.blog_tags', 'blog.templatetags.filter', 'app.recurse'])
