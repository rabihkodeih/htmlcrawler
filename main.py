# -*- coding: UTF-8 -*-
'''
Created on Apr 27, 2012

@author: Rabih Kodeih
'''
from utils.decorators import measureExecutionTime
from htmlcrawler.hc import Site


@measureExecutionTime
def crawl(site): 
    site.purge()
    site.crawl()

if __name__ == '__main__':


    s = Site(home_page_url='http://www.ibm.com',
             site_name='snoak',
             www_path='./../output/www', 
             depth=1, 
             fetch_resources=True,
             process_inline_js=False, 
             process_embedded_css=False, 
             remove_comments=False, 
             remove_ns_tags=False, 
             randomize_text=False,
             open_home_page_in_browser=True)
    
    crawl(s)






























#===============================================================================
# Pipeline
#===============================================================================
#markup ='''
#<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
#<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">
#    <head>
# <meta http-equiv="Content-Type" content="text/html; charset=windows-1256"></meta>
#        <title>testing</title>
#        <link rel="stylesheet" href="style.css" type="text/css" media="screen" />
#        <script type="text/javascript" src="some_source.js"></script> 
#        <script type="text/javascript">
#        <!--
#        alert('hello world!');
#        // -->
#        </script>
#        
#        <style type="text/css">
#            
#        body { 
#                 background-color: #FF00FF;
#                   color: blue;  }</style>
#    <div><p><!-- this is comment 1 -->some tail</p></div>
#    </head>
#<body>
#<p>blabla & </p>
#    <div><script src='rabih.js'>var x=99; alert(x);</script></div>
#  <div class='clear-fix'>
#    some div text
#  <p>some <i>paragraph</i> text 1 <b>and</b> text 2</p>
#<p>some paragraph text 2</p>
#end of div
#<!-- this is comment 2 -->
#        <style type="text/css">div { color: red;  }</style>
#        <style type="text/css"></style>
#        <link rel="alternate" type="application/rss+xml" title="Flex.org RSS Feed" href="http://flex.org/feed/" />
# </div>
#   </body>
#</html>
#'''
#markup = read_file('../stealer/output/markup.html')