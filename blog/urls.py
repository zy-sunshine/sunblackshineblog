from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template
from blog.views import *
urlpatterns = patterns('')
urlpatterns += patterns('blog.views',
    (r'^/$', MainPage),
    (r'^/(\d{4})/(\d{1,2})$', archive_by_month),
    #('/media/([^/]*)/{0,1}.*',getMedia),
	('/checkimg/', CheckImg),
	#('/skin',ChangeTheme),
	('/feed', FeedHandler),
	#('/feed/comments',CommentsFeedHandler),
	(r'^/sitemap', SitemapHandler),
	(r'^/post_comment',Post_comment),
	#(r'^/page/(?P<page>\d+)', MainPage),
	(r'^/category/(.*)',entriesByCategory),
	
	#('/tag/(.*)',entriesByTag),
	#(r'^/\?p=(?P<postid>\d+)',SinglePost),
	(r'^/p=(?P<postid>\d+)',SinglePost),

	#('/do/(\w+)', do_action),
	('/e/(.*)',Other),
	('/([\\w\\-\\./%]+)', SinglePost),
	#('.*',Error404),
)
