from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template
#from admin.views import *
from admin.views import admin_main, admin_entries, admin_categories, admin_comments
from admin.views import admin_link, admin_entry, admin_status, admin_authors, admin_import
from admin.views import admin_tools, admin_plugins, admin_plugins_action, admin_do_action
from admin.views import Upload, FileManager, getMedia, admin_sitemap
from admin.views import admin_setup, admin_category

from admin.views import UploadEx, setlanguage, admin_links

urlpatterns = patterns('')
urlpatterns += patterns('admin.views',
    (r'^/{0,1}$',admin_main),
    (r'^/setup',admin_setup),
    (r'^/entries/(post|page)',admin_entries),
    (r'^/links',admin_links),
    (r'^/categories',admin_categories),
    (r'^/comments',admin_comments),
    (r'^/link',admin_link),
    (r'^/category',admin_category),
    (r'^/(post|page)',admin_entry),
    (r'^/status',admin_status),
    (r'^/authors',admin_authors),
#    (r'^/author',admin_author),
    (r'^/import',admin_import),
    (r'^/tools',admin_tools),
    (r'^/plugins/(\w+)',admin_plugins_action),
    (r'^/plugins',admin_plugins),
    (r'^/sitemap',admin_sitemap),
#    (r'^/export/micolog.xml',WpHandler),
    (r'^/do/(\w+)',admin_do_action),
    (r'^/lang',setlanguage),
#    (r'^/theme/edit/(\w+)',admin_ThemeEdit),
#    
    (r'^/uploadex', UploadEx),
    (r'^/upload', Upload),
    (r'^/filemanager', FileManager),
    (r'^/media/([^/]*)/{0,1}.*',getMedia),
#    (r'^.*',Error404),
)

