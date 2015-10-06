'''
Created on Apr 15, 2012

@author: Rabih Kodeih
'''

import re
from re import DOTALL


#===============================================================================
# Html and CSS parsing
#===============================================================================
def parseBackGroundColorRgbTuple(html_input):
    try:
        res = re.search("< *style *type *= *\"text/CSS\" *>.+?</ *style *>", html_input, DOTALL)
        style_sec = html_input[res.start() : res.end()]
        res = re.search("html *{.*?}", style_sec, DOTALL)
        html_css = style_sec[res.start() : res.end()]
        res = re.search("background-color *: *rgb *\(.*?\) *;", html_css, DOTALL)
        bgc_entry = html_css[res.start() : res.end()]
        res = re.search("\( *[0-9]+ *, *[0-9]+ *, *[0-9]+ *\)", bgc_entry, DOTALL)
        return eval(bgc_entry[res.start() : res.end()])
    except:
        return (200,255,255)

def parseSize(html_input):
    try:
        res = re.search("< *screensize.*?/>|< *screensize.*?>.*</ *screensize *>", html_input, DOTALL)
        sz_sec = html_input[res.start() : res.end()]
        res = re.search("[0-9]+ *, *[0-9]+", sz_sec, DOTALL)
        return eval('(%s)' % sz_sec[res.start() : res.end()])
    except:
        return (650, 420)

def parseTransparencyValue(html_input):
    try:
        res = re.search("< *transparency.*?/>|< *transparency.*?>.*</ *transparency *>", html_input, DOTALL)
        tr_sec = html_input[res.start() : res.end()]
        res = re.search("[0-9]+", tr_sec, DOTALL)
        return eval(tr_sec[res.start() : res.end()])
    except:
        return 255
    

def get_attribs_urls(attribs):
    res = {}
    try:
        for k, v in attribs.iteritems():
            s = re.search('url\(.+?\)', v)
            if s:
                res[k] = v[s.start() + 5 : s.end() - 2]
    finally:
        return res

def get_attribs_key_url(attribs, key):
    v = attribs[key]
    s = re.search('url\(.+?\)', v)
    if s:
        return v[s.start() + 5 : s.end() - 2]
    return None

def set_attribs_key_url(attribs, key, target_url):
    v = attribs[key]
    s = re.search('url\(.+?\)', v)
    if s:
        attribs[key] = v[:s.start() + 5] + target_url + v[s.end() - 2:]

    
#===============================================================================
# Special Chars
#===============================================================================
class SpecialChars(object):
    LESS_THAN = '&#60;'
    GREATER_THAN = '&#62;'
    COPYRIGHT = '&#169;'


#===============================================================================
# css
#===============================================================================
class css(object):
    PADDING = 'padding'
    BORDER = 'border'
    BORDER_TOP = 'border-top'
    BORDER_BOTTOM = 'border-bottom'
    BORDER_LEFT = 'border-left'
    BORDER_RIGHT = 'border-right'
    BORDER_RADIUS = 'border-radius'
    BOX_SHADOW = 'box-shadow'
    BACKGROUND = 'background'
    BACKGROUND_COLOR = 'background-color'
    CLEAR = 'clear'
    COLOR = 'color'
    CONTENT = 'content'
    DISPLAY = 'display'
    FLOAT = 'float'
    FONT = 'font'
    FONT_SIZE = 'font-size'
    FONT_FAMILY = 'font-family'
    FONT_STYLE = 'font-style'
    HEIGHT = 'height'
    LINE_HEIGHT = 'line-height'
    LIST_STYLE_TYPE = 'list-style-type'
    MARGIN = 'margin'
    MARGIN_TOP = 'margin-top'
    MARGIN_BOTTOM = 'margin-bottom'
    MARGIN_LEFT = 'margin-left'
    MARGIN_RIGHT = 'margin-right'
    OVERFLOW = 'overflow'
    PADDING = 'padding'
    PADDING_TOP = 'padding-top'
    PADDING_BOTTOM = 'padding-bottom'
    PADDING_LEFT = 'padding-left'
    PADDING_RIGHT = 'padding-right'
    TEXT_ALIGN = 'text-align'
    TEXT_DECORATION = 'text-decoration'
    VISIBILITY = 'visibility'
    WIDTH = 'width'
