# -*- coding: UTF-8 -*-
'''
Created on Apr 14, 2012

@author: Rabih Kodeih
'''
from lxml.html import tostring
from lxml.html.html5parser import HTMLParser as HTML5Parser
from lxml import etree
from StringIO import StringIO
import webbrowser
import lxml
from utils.file_system import adjoin_paths, write_file,\
    ensure_dir_exists, uniquify_file_name, path_route, dangerous_purge_dir,\
    read_file
import os
from utils.html_css import get_attribs_urls, get_attribs_key_url,\
    set_attribs_key_url
import eventlet
import re
from utils.decorators import log_exceptions
from urlparse import urlparse
from lipsum import MarkupGenerator
import random
import gzip


DELIMITED_SPACER = '   '
ONE_LINERS = set(['meta', 'title', 'link', 'b', 'i'])
CLOSERS = set(['meta', 'link', 'br', 'hr', 'img', 'input'])

#===============================================================================
# Html parsing api
#===============================================================================
@log_exceptions('./../log.txt')
def get_markup(url, retries=3, source_url='n/a'):
    if url in get_markup.being_fetched:
        return None
    from eventlet.green import urllib2
    while retries > 0:
        try:
            get_markup.being_fetched.add(url)
            req = urllib2.Request(url, None, { #@UndefinedVariable
                                                'User-Agent' : 'Mozilla/5.0'
                                              , 'Accept-encoding': 'gzip'})
            rsp = urllib2.urlopen(req) #@UndefinedVariable
            if rsp.info().get('Content-Encoding') == 'gzip':
                #print 'zipped content detected from : %s' % url
                buf = StringIO(rsp.read())
                f = gzip.GzipFile(fileobj=buf)
                res = f.read()
            else:
                res = rsp.read()
            return res
        except:
            print 'could not get http request, retrying : %s' % retries
            retries = retries - 1
    raise Exception('Could not get http request from : %s\nand source url : %s' % (url, source_url))
get_markup.being_fetched = set([])


def tag_is_comment(tag):
    return type(tag) != type('') and type(tag) != type(u'')

def text_is_nonempty(text):
    return text and text.strip() != '' and text.strip != u''

def parse_html_string(markup, html5=False):
    if html5:
        return HTML5Parser().parse(StringIO(markup))
    return etree.parse(StringIO(markup), etree.HTMLParser())

def render_tag(tag):
    try:
        return tag.replace(u'{http://www.w3.org/1999/xhtml}', '')
    except:
        return tag

def render_html_element(e, delimiter='', format_html5=False):
    #===========================================================================
    # docinfo
    #===========================================================================
    if not hasattr(e, 'tag'): 
        docinfo = u'%s\n' % e.docinfo.doctype
        e = e.getroot()
    else:
        docinfo = u''
    pre_tag = u'html:' if format_html5 else u''
    tag = render_tag(e.tag)
    closer = tag in CLOSERS and not text_is_nonempty(e.text) and len(e.getchildren()) == 0 and not format_html5
    one_liner = closer or\
                tag in ONE_LINERS or\
                tag_is_comment(tag) or\
                (tag == 'script' and not text_is_nonempty(e.text)) or\
                (tag == 'div' and (e.text is None or e.text == '') and len(e)==0)
        
    #===========================================================================
    # opening tag
    #===========================================================================
    if tag_is_comment(tag):
        op_tag = u'%s%s' % (delimiter, u'<!--')
    else:
        attribs = u'%s%s' % (u' ', u' '.join([u'%s="%s"' % (k,v) for k, v in e.attrib.iteritems()]))
        if attribs == u' ': attribs = u''
        op_tag = u'%s%s' % (delimiter, u'<%s%s%s%s' % (pre_tag, tag, attribs, u'' if closer else u'>'))
        if not one_liner: op_tag = u'%s\n' % op_tag
    #===========================================================================
    # text
    #===========================================================================
    if text_is_nonempty(e.text):
        text = e.text.strip()
        if not one_liner: text = u'%s%s%s\n' % (delimiter, DELIMITED_SPACER, text)
    else:
        text = u''
    #===========================================================================
    # kids
    #===========================================================================
    kids_text = u''.join([render_html_element(kid, '%s%s' % (delimiter, DELIMITED_SPACER), format_html5) for kid in e])
    #===========================================================================
    # closing tag
    #===========================================================================
    if tag_is_comment(tag):
        cl_tag = u'-->\n'
    else:
        if closer:
            cl_tag = u'/>\n'
        else:
            cl_tag = u'</%s%s>\n' % (pre_tag, tag)
        if not one_liner: cl_tag = u'%s%s' % (delimiter, cl_tag)
    #===========================================================================
    # tail
    #===========================================================================
    if text_is_nonempty(e.tail):
        tail = u'%s%s\n' % (delimiter, e.tail.strip())
    else:
        tail = u''
    return '%s%s%s%s%s%s' % (docinfo, op_tag, text, kids_text, cl_tag, tail)

def builtin_render_html(e):
    res = tostring(doc                         = e, 
                   pretty_print                = True, 
                   include_meta_content_type   = True, 
                   encoding                    = unicode, 
                   method                      = 'html', 
                   with_tail                   = True, 
                   doctype                     = None)
    return res

def create_css_link(url):
    from collections import OrderedDict
    attribs = OrderedDict()
    attribs['rel'] = 'stylesheet'
    attribs['href'] = url
    attribs['type'] = 'text/css'
    attribs['media'] = 'screen'
    return lxml.etree.Element('link', attribs)

def create_js_tag(url):
    from collections import OrderedDict
    attribs = OrderedDict()
    attribs['type'] = 'text/javascript' 
    attribs['src'] = url
    return lxml.etree.Element('script', attribs)

def append_to_tag(node, tag, elem):
    res = node.find(tag)
    #assert isinstance(res, lxml.etree._ElementTree)
    if res != None:
        res.append(elem)
        
def remove_from_parent(e):
    parent = e.getparent()
    if e.tail is not None: 
        previous = e.getprevious()
        if previous is not None:
            previous.tail = (previous.tail if previous.tail else u'') + (e.tail if e.tail else u'')
        elif parent is not None:
            parent.text = (parent.text if parent.text else u'') + (e.tail if e.tail else u'')
    if parent is not None:
        parent.remove(e)
    
def open_in_browser(path):
    url = adjoin_paths('file://', path)
    webbrowser.open(url)

def generate_sample_text(length):
    g = MarkupGenerator()
    res = u''
    while len(res) < length:
        res = u'%s %s' % (res, g.generate_sentence(random.randint(0,1)))
    res = res[:length].strip()
    if res[-2] == u' ': res = res[:-1]
    if res[-1] == u' ': res = res[:-1]
    if res[-1] == ',' : res = res[:-1]
    if len(res) <= 25: res = res.replace(u'.', u'').replace(u',', u'')
    return res
        

#===============================================================================
# SitePage class
#===============================================================================
class SitePage(object):
    def __init__(self, page_url, site_path, use_html5=False, 
                 process_inline_js=True, process_embedded_css=True,
                 fetch_resources=True, remove_comments=True, remove_ns_tags=True,
                 randomize_text=False):
        self.pool = eventlet.GreenPool(10000)
        self.page_url = page_url
        self.site_path = site_path
        self.tree_root = None
        self.use_html5 = use_html5
        parsed = urlparse(self.page_url)
        self.index_path = adjoin_paths(self.site_path, parsed.hostname, parsed.path, 'index.html')
        self.process_inline_js = process_inline_js
        self.process_embedded_css = process_embedded_css
        self.fetch_resouces = fetch_resources
        self.remove_comments = remove_comments
        self.remove_ns_tags = remove_ns_tags
        self.randomize_text = randomize_text
        
    def parse_markup(self):
        print 'fetching page               : %s' % self.page_url
        
        markup = get_markup(self.page_url)
        
        print 'done fetching               : %s' % self.page_url
        self.tree_root = parse_html_string(markup, html5=self.use_html5)
        #assert isinstance(self.tree_root, lxml.etree._ElementTree)
        return self.tree_root
    
    def process_text(self):
        for attrib in ['text', 'tail']:
            res = [r for r in self.tree_root.xpath('//body//*') if text_is_nonempty(getattr(r, attrib))
                   and r.tag in ['p', 'a', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'tr', 'span']]
            for node in res: 
                setattr(node, attrib, u' | '.join([generate_sample_text(len(r)) for r in node.text.split('|')]))
                try: node.attrib['title'] = generate_sample_text(len(node.attrib['title']))
                except: pass
    
    @log_exceptions('./../log.txt')
    def main_logic(self, open_when_done=False):
        print 'getting resources for page  : %s' % self.page_url
        # process links, script sources and images, flash and other media
        if self.fetch_resouces:
            self.fetch_external_resources()

        # wait for all blocking IO threads to finish fetching external resources
        self.pool.waitall()

        # lorem ipsify text
        if self.randomize_text:
            self.process_text()

        # process imbedded css
        if self.process_embedded_css:
            self.process_internal_asset('//style', adjoin_paths(os.path.dirname(self.index_path), 
                                                            'imbedded_css'), 'imbedded.css', 'head', create_css_link)     
        
        # process inline js
        if self.process_inline_js:
            self.process_internal_asset('//body//script', adjoin_paths(os.path.dirname(self.index_path), 
                                                            'inline_js'), 'inline.js', 'body', create_js_tag)
        
        # remove comments
        if self.remove_comments:
            self.filter_comments(True)
        
        # process noscript tags
        if self.remove_ns_tags:
            self.process_noscript_tags()
        
        # render html
        html_output = render_html_element(self.tree_root, format_html5=self.use_html5)
        #print html_output
        
        ensure_dir_exists(os.path.dirname(self.index_path))
        write_file(self.index_path, html_output)

        print 'done getting resources      : %s' % self.page_url
        if open_when_done: open_in_browser(self.index_path)

    def markup_path(self, path):
        #print adjoin_paths('http://',
        #                   os.path.basename(self.site_root_path),
        #                   path_route(path, `))
        return path_route(path, os.path.dirname(self.index_path))

    @log_exceptions('./../log.txt')
    def fetch_resource(self, r, key, is_binary, is_attrib_url):
        if is_attrib_url:
            resource_path = get_attribs_key_url(r.attrib, key)
        else:
            resource_path = r.attrib[key]
        if not (resource_path.startswith('http://') or resource_path.startswith('https://')):
            parsed = urlparse(self.page_url)
            resource_path = parsed.scheme + '://' + adjoin_paths(parsed.hostname, resource_path)
        for res in re.findall('/<!--.*?-->', resource_path): resource_path = resource_path.replace(res, '')
        resource_path = resource_path.replace('http:///', 'http://')
        resource_path = resource_path.replace('https:///', 'https://')
        print 'fetching :', resource_path
        file_content = get_markup(resource_path, source_url=self.page_url)
        print 'done     : %s' % resource_path
        parsed = urlparse(resource_path)
        internal_path = adjoin_paths(self.site_path, parsed.hostname, parsed.path)
        ensure_dir_exists(os.path.dirname(internal_path))
        if file_content: write_file(internal_path, file_content, is_binary)
        markup_path = self.markup_path(internal_path)
        if is_attrib_url:
            set_attribs_key_url(r.attrib, key, markup_path)
        else:
            r.attrib[key] = markup_path
        if internal_path.endswith('.css'):
            self.process_css_urls(internal_path, resource_path)

    def filter_comments(self, remove=False):
        res = self.tree_root.xpath('//comment()')
        if remove:
            for r in res:
                remove_from_parent(r)
        return res

    @log_exceptions('./../log.txt')
    def process_internal_asset(self, selector, asset_path, asset_file, t_tag, new_cl): 
        res = self.tree_root.xpath(selector)
        file_content = u'\n\n'.join(u'\n'.join([l for l in (r.text if r.text else u'').split('\n')]).strip() for r in res)
        for r in res: 
            remove_from_parent(r)
            r.text = None
            try: 
                assert r.attrib.has_key('src')
                append_to_tag(self.tree_root, 'head', r)
            except:
                remove_from_parent(r)
        unique_file_name = uniquify_file_name(asset_path, asset_file)
        internal_path = adjoin_paths(asset_path, unique_file_name)
        ensure_dir_exists(asset_path)
        write_file(internal_path, file_content)
        append_to_tag(self.tree_root, t_tag, new_cl(self.markup_path(internal_path)))
        if asset_file.endswith('.css'):
            self.process_css_urls(internal_path, self.page_url)
    
    def process_noscript_tags(self):
        res = self.tree_root.xpath('//noscript')
        for r in res:
            remove_from_parent(r)
    
    def fetch_external_resources(self):
        res = self.tree_root.xpath('//body//link')
        for r in res:
            remove_from_parent(r)
            append_to_tag(self.tree_root, 'head', r)
        res = self.tree_root.xpath('//link')        
        for r in res:
            try:
                assert r.attrib['href'].endswith('.css')
                assert r.attrib['rel'] == 'stylesheet'
            except:
                remove_from_parent(r)
        
        debug = False
        
        # process links
        res1 = [r for r in self.tree_root.xpath('//link') if r.attrib.has_key('href') and r.attrib['href'].endswith('.css')]
        if debug: res1 = []
        for r in res1:
            self.pool.spawn(self.fetch_resource, r, 'href', False, False)
        
        # process script sources
        res2 = [r for r in self.tree_root.xpath('//script') if r.attrib.has_key('src')]
        if debug: res2 = []
        for r in res2:
            self.pool.spawn(self.fetch_resource, r, 'src', False, False)
        
        # process extract images, flash and other media
        res3 =[r for r in self.tree_root.xpath('//*[@src]') if r.tag != 'script']
        if debug: res3 = []
        for r in res3:
            self.pool.spawn(self.fetch_resource, r, 'src', True, False)
        
        # process url-inner-attribute resources
        temp = [r for r in self.tree_root.xpath('//*') if get_attribs_urls(r.attrib) != {}]
        if debug: temp = []
        res4 = []
        for r in temp:
            for k in get_attribs_urls(r.attrib).iterkeys():
                res4.append((r, k))
        for r, k in res4:
            self.pool.spawn(self.fetch_resource, r, k, True, True)
    
    @log_exceptions('./../log.txt')    
    def process_css_urls(self, local_css_path_file, online_css_path_file):
        if online_css_path_file is None: return
        content = read_file(local_css_path_file)
        res = [r for r in re.findall('url\(\'?\"?(.*?)\'?\"?\)', content) if (r.find(':') == -1 
                                                                          and r.find(';') == -1
                                                                          and r.find(',') == -1)]
        def _cl(r):
            if r.startswith('http://'): raise Exception('Unhandled css parse case')
            if r.startswith('https://'): raise Exception('Unhandled css parse case')
            online_path_file = adjoin_paths(os.path.dirname(online_css_path_file.split('?')[0]), r)
            online_file = os.path.basename(online_path_file).split('?')[0]
            local_path_file = adjoin_paths(os.path.dirname(local_css_path_file), r)
            ensure_dir_exists(os.path.dirname(local_path_file))
            print 'fetching :', online_file
            for res in re.findall('/<!--.*?-->', online_file): online_file = online_file.replace(res, '')
            file_content = get_markup(online_path_file, source_url=self.page_url)
            print 'done     : %s' % online_file
            if file_content: write_file(local_path_file, file_content, True)
        for k in res:
            self.pool.spawn(_cl, k)


#===============================================================================
# Site class
#===============================================================================
class Site(object):
    def __init__(self, home_page_url, site_name, www_path, depth=1,
                 process_inline_js=True, process_embedded_css=True, 
                 fetch_resources=True, remove_comments=True, remove_ns_tags=True,
                 open_home_page_in_browser=False, randomize_text=False):
        self.home_page_url = home_page_url
        self.depth = depth
        self.site_name = site_name
        self.site_path = adjoin_paths(os.path.realpath(www_path), self.site_name)
        self.pool = eventlet.GreenPool(10000)
        self.being_crawled = set([])
        self.process_inline_js = process_inline_js
        self.process_embedded_css = process_embedded_css
        self.fetch_resources = fetch_resources
        self.remove_comments = remove_comments
        self.remove_ns_tags = remove_ns_tags
        self.open_home_page_in_browser = open_home_page_in_browser
        self.randomize_text = randomize_text
    
    def purge(self):
        print 'Purging site : %s' % self.site_name
        print 'located at : %s' % self.site_path
        dangerous_purge_dir(self.site_path)
        
    def crawl(self):
        print 'Started crawling site : %s\n' % self.site_name
        self.crawl_page(self.home_page_url, self.depth)
        self.pool.waitall() 
        print '\n\nOK, site crawled to specified depth.'
    
    def crawl_page(self, page_url, depth):
        if depth == 0: return
        is_home_page = page_url == self.home_page_url
        page_url = (page_url + '/') if not page_url.endswith('/') else page_url
        if page_url in self.being_crawled: return
        print '\ncrawling page               : %s' % page_url
        self.being_crawled.add(page_url)
        p = SitePage(page_url, self.site_path, 
                     process_inline_js=self.process_inline_js, 
                     process_embedded_css=self.process_embedded_css,
                     fetch_resources=self.fetch_resources,
                     remove_comments=self.remove_comments,
                     remove_ns_tags=self.remove_ns_tags,
                     randomize_text=self.randomize_text)
        ast = p.parse_markup()
        for a in ast.xpath('//a'):
            if not a.attrib.has_key('href'): continue
            a_url = a.attrib['href'].strip()
            if urlparse(page_url).hostname == urlparse(a_url).hostname:
                self.pool.spawn(self.crawl_page, a_url, depth-1)
                parsed = urlparse(a_url)
                p1 = adjoin_paths(self.site_path, parsed.hostname, parsed.path, 'index.html')
                a.attrib['href'] = p.markup_path(p1)
            else:
                a.attrib['href'] = '#'
            #print '>>> ', a.attrib['href']
        self.pool.spawn(p.main_logic, open_when_done=self.open_home_page_in_browser and is_home_page) 
        return








