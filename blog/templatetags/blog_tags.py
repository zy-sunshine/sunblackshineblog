#!/usr/bin/env python
# -- coding utf-8 --

import os
from django.template.loader_tags import ExtendsNode, IncludeNode, BlockContext, BlockNode, ConstantIncludeNode
from django.template.loader import get_template
import django
if django.VERSION[1] >= 3: # >= 1.3
    from django.template.base import Library, Node, TextNode
    from django.template.base import TemplateSyntaxError, TemplateDoesNotExist
    from django.template.loader_tags import BaseIncludeNode
else: # <= 1.2
    from django.template import Library, Node, TextNode
    from django.template import TemplateSyntaxError, TemplateDoesNotExist
    from django.template import Node as BaseIncludeNode
    

    
register = Library()
BLOCK_CONTEXT_KEY = 'block_context'

class ExtendsNode_v2(ExtendsNode):
    must_be_first = True

    def __init__(self, nodelist, varlist, template_dirs=None):
        self.nodelist = nodelist
        self.varlist = varlist
        self.template_dirs = template_dirs
        self.blocks = dict([(n.name, n) for n in nodelist.get_nodes_by_type(BlockNode)])

    def __repr__(self):
        return "<ExtendsNode_v2: extends %s>" % \
            ' '.join([ var['type'] == 'var' and var['value'].token or var['value'] for var in self.varlist ])

    def render(self, context):
        parent_name = os.path.join(*[ var['type'] == 'var' and var['value'].resolve(context) or var['value'] for var in self.varlist ])
        ExtendsNode.__init__(self, nodelist = self.nodelist, parent_name = parent_name, parent_name_expr = None)
        return ExtendsNode.render(self, context)

def do_extends(parser, token):
    """
    Signal that this template extends a parent template.

    This tag may be used in two ways: ``{% extends "base" %}`` (with quotes)
    uses the literal value "base" as the name of the parent template to extend,
    or ``{% extends variable %}`` uses the value of ``variable`` as either the
    name of the parent template to extend (if it evaluates to a string) or as
    the parent tempate itelf (if it evaluates to a Template object).
    """
    bits = token.split_contents()
    #if len(bits) != 2:
    #    raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    #parent_name, parent_name_expr = None, None
    varlist = []
    for bit in bits[1:]:
        if bit[0] in ('"', "'") and bit[-1] == bit[0]:
            varlist.append({'value': bit[1:-1], 'type': 'string'})
        else:
            varlist.append({'value': parser.compile_filter(bit), 'type': 'var'})
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(ExtendsNode) or nodelist.get_nodes_by_type(ExtendsNode_v2):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return ExtendsNode_v2(nodelist, varlist)

class IncludeNode_v2(BaseIncludeNode):
    def __init__(self, pathlist, *args, **kwargs):
        self.pathlist = pathlist
        self.args = args
        self.kwargs = kwargs
        #super(IncludeNode, self).__init__(*args, **kwargs)
        #self.template_name = template_name

    def render(self, context):
        template_name = os.path.join(*[ path['type'] == 'var' and path['value'].resolve(context) or path['value'] for path in self.pathlist ])
        if django.VERSION[1] >= 3: # >= 1.3
            superIncludeNode = ConstantIncludeNode(template_name, *self.args, **self.kwargs)
        else: # <= 1.2
            superIncludeNode = ConstantIncludeNode(template_name)
        return superIncludeNode.render(context)

        
def do_include(parser, token):
    """
    Loads a template and renders it with the current context. You can pass
    additional context using keyword arguments.

    Example::

        {% include "foo/some_include" %}
        {% include "foo/some_include" with bar="BAZZ!" baz="BING!" %}

    Use the ``only`` argument to exclude the current context when rendering
    the included template::

        {% include "foo/some_include" only %}
        {% include "foo/some_include" with bar="1" only %}
    """
    bits = token.split_contents()
    #if len(bits) < 2:
    #    raise TemplateSyntaxError("%r tag takes at least one argument: the name of the template to be included." % bits[0])
    options = {}
    #remaining_bits = bits[2:]
    keywords = ['with', 'only']
    sub = 0
    has_find = False
    for sub in range(len(bits)):
        if bits[sub] in keywords:
            has_find = True
            break
    pathlist = has_find and bits[1:sub] or bits[1:]
    remaining_bits = has_find and bits[sub:] or []
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more '
                                      'than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % bits[0])
        elif option == 'only':
            value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' %
                                      (bits[0], option))
        options[option] = value
    isolated_context = options.get('only', False)
    namemap = options.get('with', {})
    #path = bits[1]
    pathlist_s = []
    for path in pathlist:
        if path[0] in ('"', "'") and path[-1] == path[0]:
            pathlist_s.append({'value': path[1:-1], 'type': 'string'})
        else:
            pathlist_s.append({'value': parser.compile_filter(path), 'type': 'var'})
    return IncludeNode_v2(pathlist = pathlist_s, extra_context=namemap,
                       isolated_context=isolated_context)
    #        return ConstantIncludeNode(path[1:-1], extra_context=namemap,
    #                                   isolated_context=isolated_context)
    #return IncludeNode(parser.compile_filter(bits[1]), extra_context=namemap,
    #                   isolated_context=isolated_context)


register.tag('extends_v2', do_extends)
register.tag('include_v2', do_include)
