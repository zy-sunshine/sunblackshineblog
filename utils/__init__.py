#from settings import *
import os, logging, re
import django
import settings
#from django.template.loader import find_template
from django.template import TemplateDoesNotExist
from settings import APP_THEME_MAP, THEME_CONFIG, ROOT_PATH, TEMPLATE_ROOT, THEME_ROOT
from settings import get_theme_templates_path, get_theme_static_path

def find_template(context, template):
    logging.debug("++find_template+++++++++++++++++ current_app: %s" % context.current_app)
    path_lst = []
    def has_file(path):
        path_lst.append(path)
        if os.path.exists(path):
            logging.debug('+++TEMPLATE+++ %s' % path)
            return True
        else:
            return False
    if template[0] in ('\\' '/'):
        if has_file(os.path.join(ROOT_PATH, template[1:])):
            return template[1:]
        if has_file(os.path.join(THEME_ROOT, template[1:])):
            return template[1:]
        if has_file(os.path.join(TEMPLATE_ROOT, template[1:])):
            return template[1:]
    else:
        if has_file(os.path.join(TEMPLATE_ROOT, context.current_app, template)):
            return os.path.join(context.current_app, template)
    theme_base = get_theme_templates_path(context.current_app)
    logging.debug('++theme_base+++++ %s' % theme_base)
    logging.debug('+++ %s' % os.path.join(THEME_ROOT, theme_base, template))
    if has_file(os.path.join(THEME_ROOT, theme_base, template)):
        return os.path.join(theme_base, template)
    raise Exception('Cannot find template: %s' % ', '.join(path_lst))
    #raise TemplateDoesNotExist('Cannot find template: "%s" in paths: %s' % (template, str(path_lst)))


def get_template_uri(context, template_file):
    #if not ( re.search('html$', template_file, flags=re.IGNORECASE)
    #        or re.search('htm$', template_file, flags=re.IGNORECASE) ):
    ext = os.path.splitext(template_file)[1]
    if not ext:
        template_file = '%s.html' % template_file
    logging.debug('9++++++++++++%s'%template_file)
    template = find_template(context, template_file)
    return template
    
#    try:
#        t = loader.select_template(['static/directory_index.html',
#                'static/directory_index'])
#    except TemplateDoesNotExist:
#        t = Template(DEFAULT_DIRECTORY_INDEX_TEMPLATE, name='Default directory index template')
#        
    
def get_extra_context(appContext):
    params = {}
    params['appContext'] = appContext
    params['TEMPLATES_BASE'] = get_theme_templates_path(appContext.current_app)
    params['THEME_STATIC'] = get_theme_static_path(appContext.current_app)
    return params
    
class AppContext():
    def __init__(self, current_app):
        self.current_app = current_app
        #self.t_base = APP_TEMPLATE_MAP[current_app] + '/'
        #self.t_base_app = os.path.join(APP_TEMPLATE_MAP[current_app], current_app) + '/'
        id = APP_THEME_MAP[current_app]
        THEME_CONFIG_CUR = THEME_CONFIG[id]
        self.t_base = THEME_CONFIG_CUR['theme_base'] + '/'
        self.t_base_app = self.t_base + '/' + current_app + '/'
        # For base.html 
        # TODO: find a better way
        #self.t_base_template = os.path.join(self.t_base, 'base.html')
        #self.t_base_app_template = os.path.join(self.t_base_app, 'base.html')

def get_absolute_path(request, relative_path = ''):
    relative_path = not relative_path and request.get_full_path() or relative_path
    if hasattr(request, 'build_absolute_uri') and callable(getattr(request, 'build_absolute_uri')):
        return request.build_absolute_uri(relative_path)
    else:
        # For django 0.96 there have no build_absolute_uri method
        #http_base = request.META['HTTP_REFERER']
        http_base = 'http://%s' % request.META['HTTP_HOST']
        http_base = http_base[-1] == '/' and http_base[:-1] or http_base
        return '%s%s' % (http_base, relative_path)
 
def register_templatetags(templatetags):
    for templatetag in templatetags:
        if not django.template.libraries.get(templatetag, None):
            #django.template.add_to_builtins(templatetag)
            django.template.loader.add_to_builtins(templatetag)
