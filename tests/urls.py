from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('')
urlpatterns += patterns('tests.views',
    (r'^/$', 'MainPage'),
    (r'^/blog/$', 'TestBlog'),
    #(r'^/$', 'MainPage'),
    #(r'^/(\d{4})/(\d{1,2})', 'archive_by_month'),
    #('/media/([^/]*)/{0,1}.*',getMedia),
	#('/checkimg/', CheckImg),
	#('/checkcode/', CheckCode),
	#('/skin',ChangeTheme),
	#('/feed', FeedHandler),
	#('/feed/comments',CommentsFeedHandler),
	#('/sitemap', SitemapHandler),
	#('/post_comment',Post_comment),
	#('/page/(?P<page>\d+)', MainPage),
	#('/category/(.*)',entriesByCategory),
	
	#('/tag/(.*)',entriesByTag),
	##('/\?p=(?P<postid>\d+)',SinglePost),

	#('/do/(\w+)', do_action),
	#('/e/(.*)',Other),
	#('/([\\w\\-\\./%]+)', SinglePost),
	#('.*',Error404),
	(r'^/application', 'TestApplication')
)
