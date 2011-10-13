#encoding=utf8
#file:views.py
#@author:carlos
#@date:2011-2-13
#@link:tieniuzai.com
from django import template
from django.http import HttpResponse
from django.shortcuts import render_to_response
from sinaweibo.weibo_factory import SinaWeibo

def get_weibo(request):
		sinat = SinaWeibo("ÄúµÄĞÂÀËÎ¢²©ÕÊºÅ","ÃÜÂë")
		sinat.basicAuth()
		user = sinat.get_myself()
		result = sinat.user_timeline()
		return render_to_response("sinaweibo/weibo.html",{'result':result,'user':user})