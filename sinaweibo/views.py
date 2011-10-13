#coding=utf-8
#file:views.py
#@author:carlos
#@date:2011-2-13
#@link:tieniuzai.com
if 0:
    from django import template
    from django.http import HttpResponse
    from django.shortcuts import render_to_response
    from sinaweibo.weibo_factory import SinaWeibo
    
    def get_weibo(request):
        print "1"
        sinat = SinaWeibo("zy.netsec@gmail.com","890529")
        print "2"
        sinat.basicAuth()
        print "3"
        user = sinat.get_myself()
        print "4"
        result = sinat.user_timeline()
        print "5"
        return render_to_response("default/sinaweibo/weibo.html",{'result':result,'user':user})
        
import os
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from weibopy.auth import OAuthHandler
from weibopy.api import API
from gaesessions import get_current_session
import django
from django import http
from django import shortcuts

from django.core.urlresolvers import reverse

from utils import get_template_uri, get_absolute_path, AppContext

appContext = AppContext(current_app = 'sinaweibo')
DELIMITER_AT = ['@', '\s', ':', '：']
delimiter_at_not_regex = ''.join([ '^'+ch.decode('utf8') for ch in DELIMITER_AT ])
delimiter_at_regex = ''.join([ ch.decode('utf8') for ch in DELIMITER_AT ])
CONSUMER_KEY = "2014654983"
CONSUMER_SECRET = "2cffa7fd9faf2e98ea99e652209e3ca0"
def wrapper__at(weibo_list):
    def wrapper(text):
        return re.sub(r'@([%s]+)([%s])' 
            % (delimiter_at_not_regex, 
               delimiter_at_regex), 
               r'<a href="http://weibo.com/n/\1">@\1</a>\2', text)
    for weibo in weibo_list:
        weibo['text'] = wrapper(weibo['text'])
def mainPage(request):
    session = get_current_session()
    access_token_key = session['access_token_key']
    access_token_secret = session['access_token_secret']
    oauth_verifier = request.GET.get('oauth_verifier', '')
    get_absolute_path(request)
    if not access_token_key:
        #params['test'] = reverse('sinaweibo.views.login', args=[], kwargs={})#, current_app=context.current_app)        
        login_url = reverse('sinaweibo.views.login', args=[], kwargs={})
        #return shortcuts.render_to_response('test.html', params)
        return http.HttpResponseRedirect(login_url)
    else:
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.setToken(access_token_key, access_token_secret)
        api = API(auth)
        
        #myself = api.get_user(id=1894001933)
        #screen_name = myself. __getattribute__('screen_name')
        myweibo = []
        myweibo_obj = api.user_timeline(count=20, page=1)
        for weibo in myweibo_obj:
            myweibo.append({'text': weibo.text, 
                            'created_at': weibo.created_at, 
                            'retweeted_status': hasattr(weibo, 'retweeted_status') and weibo.retweeted_status or None,
                            'source': weibo.source})
        wrapper__at(myweibo)
        params = {}
        
        params['user'] = api.verify_credentials()
        params['result'] = myweibo
        template = get_template_uri(appContext, 'weibo.html')
        return shortcuts.render_to_response(template, params)

def login(request):
    '''get a permanent access token'''
    session = get_current_session()
    if not request.GET.get('oauth_token'):
        '''login and save oauth token'''
        cur_url = _get_absolute_path(request)
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, callback = cur_url)
        auth_url = auth.get_authorization_url()
        # 需要保存request_token的信息，留做取access_token用
        session["oauth_token"] = auth.request_token.key
        session["oauth_token_secret"] = auth.request_token.secret
        return http.HttpResponseRedirect(auth_url)
    else:
        ''' Get the access token '''
        oauth_verifier = request.GET.get('oauth_verifier')
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        # 从session中取出request_token的信息
        auth.set_request_token(session["oauth_token"], session["oauth_token_secret"])
        auth.get_access_token(oauth_verifier)
        # save access token
        session['access_token_key'] = auth.access_token.key
        session['access_token_secret'] = auth.access_token.secret
        response = shortcuts.redirect('sinaweibo.views.mainPage')
        return response
        
        
    if 0:
        path = os.path.join(os.path.dirname(__file__), "templates/index.html")
        myself = api.get_user(id=1894001933)
        screen_name = myself. __getattribute__("screen_name")
        self.response.out.write(template.render(path,
                {"name": screen_name}))#dir(api.verify_credentials)}))#api.verify_credentials.name}))#screen_name}))

    if 0:
        params = {}
        params['test'] = 'nothing'
        return shortcuts.render_to_response('test.html', params)

    if 0:
        # add GET para and redirect
        response = shortcuts.redirect('sinaweibo.views.mainPage')
        response['Location'] += '?oauth_verifier=%s' % oauth_verifier
        return response
            