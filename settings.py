#coding=utf-8
import os

ROOT_PATH = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_engine', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sunshineblog',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'  # i.e., Mountain View

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
#LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE='zh-cn'
### TODO: remove it will cause many problem of circle import ?
#LANGUAGE_CODE='zh_CN'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
## MEDIA_URL is prefix in url, MEDIA_ROOT is file path on server.
MEDIA_ROOT =  os.path.join(ROOT_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/static/'
THEME_MEDIA_URL = '/theme_static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Whether to append trailing slashes to URLs.
APPEND_SLASH = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = '719u8z@p0x1ckx(-u&t&bg@m1@t3at65di94+d!+pl2q%i+4#z'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    #'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    #'django.core.context_processors.media',
    #'django.core.context_processors.request',
    'context_processors.common',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.cache.CacheMiddleware', # cache each GET POST have no parameter page
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'gaesessions.DjangoSessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)
# option of cache middleware
#CACHE_MIDDLEWARE_SECONDS
#CACHE_MIDDLEWARE_KEY_PREFIX
#CACHE_MIDDLEWARE_ANONYMOUS_ONLY 
ROOT_URLCONF = 'urls'
THEME_CONFIG = {}
THEME_CONFIG[1] = {}
THEME_CONFIG_ID_LIST = [2, 3]
THEME_CONFIG[1]['title'] = 'Pixel'
THEME_CONFIG[1]['apps'] = 'blog'
THEME_CONFIG[1]['theme_base'] = 'Pixel/pixel-zh_cn'
THEME_CONFIG[1]['templates'] = 'templates'
THEME_CONFIG[1]['static'] = ''

THEME_CONFIG[2] = {}
THEME_CONFIG[2]['title'] = 'default'
THEME_CONFIG[2]['apps'] = 'blog'
THEME_CONFIG[2]['theme_base'] = 'default'
THEME_CONFIG[2]['templates'] = 'templates'
THEME_CONFIG[2]['static'] = ''

THEME_CONFIG[3] = {}
THEME_CONFIG[3]['title'] = ''
THEME_CONFIG[3]['apps'] = 'admin sinaweibo home'
THEME_CONFIG[3]['theme_base'] = ''
THEME_CONFIG[3]['templates'] = ''
THEME_CONFIG[3]['static'] = ''


TEMPLATE_ROOT = os.path.join(ROOT_PATH, 'templates')
THEME_ROOT = os.path.join(ROOT_PATH, 'themes')
APP_THEME_MAP = {}
for id in THEME_CONFIG_ID_LIST:
    THEME_CONFIG_CUR = THEME_CONFIG[id]
    
    for app in THEME_CONFIG_CUR['apps'].split():
        APP_THEME_MAP[app] = id

### TODO: join path for URL optimise
def get_theme_static_path(app_name):
    if APP_THEME_MAP.has_key(app_name):
        id = APP_THEME_MAP[app_name]
        THEME_CONFIG_CUR = THEME_CONFIG[id]
        static_path = os.path.join(THEME_MEDIA_URL, THEME_CONFIG_CUR['theme_base'], app_name, THEME_CONFIG_CUR['static'])
        static_path = os.path.normpath(static_path).replace('\\', '/')
        return static_path + '/'
    else:
        return MEDIA_URL
    
def get_theme_templates_path(app_name):
    if APP_THEME_MAP.has_key(app_name):
        id = APP_THEME_MAP[app_name]
        THEME_CONFIG_CUR = THEME_CONFIG[id]
        templates_path = os.path.join(THEME_CONFIG_CUR['theme_base'], app_name, THEME_CONFIG_CUR['templates'])
        templates_path = os.path.normpath(templates_path).replace('\\', '/')
        return templates_path + '/'
    else:
        return app_name

TEMPLATE_DIRS = (
    THEME_ROOT,
    TEMPLATE_ROOT,
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.admin',
    #'django.contrib.sessions',
    #'django.contrib.contenttypes',
    #'django.contrib.sites',
    #'django.contrib.messages',
    #'home',
    #'bookmark',
    'django_mongodb_engine',
    'djangotoolbox',
    #'query',
    #'embedded',
    'blog',
    #'sinaweibo',
    #'admin',
    #'tests',
    #'configs',
)
#
#ALL_TEMPLATE_CUR = ''
# map value is relative to 'static' and or? 'templates' directory
#ALL_TEMPLATE_MAP = {
#    '': '',
#    'redbusiness': 'redbusiness',
#    'Pixel': 'Pixel/pixel-en',
#    'default': 'default',
#}

# APP_TEMPLATE_MAP[context.current_app] to get the current app template type
#APP_TEMPLATE_MAP = {'home': ALL_TEMPLATE_MAP[ALL_TEMPLATE_CUR],
#                    'bookmark': ALL_TEMPLATE_MAP[ALL_TEMPLATE_CUR],
#                    'blog': ALL_TEMPLATE_MAP['Pixel'],
#                    #'blog': ALL_TEMPLATE_MAP['default'],
#                    'sinaweibo': ALL_TEMPLATE_MAP[ALL_TEMPLATE_CUR],
#                    'admin' : ALL_TEMPLATE_MAP[ALL_TEMPLATE_CUR],
#                    }

#TEMPLATE_BASE = TEMPLATE_MAP[TEMPLATE_CUR]
#TEMPLATE_BASE_APP = {}
#for app in APP_LIST:
#    TEMPLATE_BASE_APP[app] = os.path.join(TEMPLATE_MAP[TEMPLATE_CUR], app)
#app = 'blog'
#TEMPLATE_BASE_APP[app] = os.path.join(TEMPLATE_MAP['Pixel'], app)


SITE_CONFIG = {
    'title': 'Sunshine Blog',
    'author_email': 'zy.netsec@gmail.com',
    'author_name': 'Glenn Zhang',
    'author_blog': 'http://hi.baidu.com/sunblackshine',
    'feedurl': 'http://this_is_feedurl',
    'enable_memcache': True,
}

LANGUAGES = (
('zh_CN', u'Chinese'),
('en_US', u'English'),
('ds_AR', u'Spanish'),
('it_IT', u'Italian'),
('ja',    u'Japanese'),
)

#from django.utils.translation import activate

#activate(configs.get_g_blog().language)

#activate(g_blog.language)
#import configs
#LANGUAGE_CODE=configs.get_g_blog().language

#CACHE_BACKEND = 'file:///var/tmp/django_cache'
CACHE_BACKEND = 'file://E:/tmp/django_cache?timeout=30&max_entries=400'

SITE_ID = 1