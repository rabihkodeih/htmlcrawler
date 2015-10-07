# htmlcrawler
This a simple html crawler that will crawl any website and download all of its contents up to a certain depth.

As an example of crawling the ibm site, we first create a site object with the desired config then apply a crawl operation:

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
             open_home_page_in_browser=False)
    s.purge() # this will delete any previous results
    s.crawl()

When done, the resuls will be written to the path specified in the www_path param which is './../output/www' in this case.

##Installation
Clone repository.

##Dependencies
* lxml (https://pypi.python.org/pypi/lxml)
* html5lib (https://pypi.python.org/pypi/html5lib)
