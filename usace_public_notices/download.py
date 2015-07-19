import os

from vlermv import cache

from requests import get

DIR = '~/.usace-public-notices'

@cache(DIR, 'subdomain')
def subdomain(site_number):
    url = 'http://www.mvn.usace.army.mil/DesktopModules/ArticleCS/RSS.ashx'
    params = {
        'ContentType': 4,
        'Site': site_number,
        'max': 1,
    }
    return get(url, params = params)

@cache(DIR, 'feed')
def feed(date, site_subdomain, site_number, max = 100000):
    '''
    Get the RSS feed. We can have fun by guessing site numbers.

    :param int site: Site number to be passed as a query parameter
    '''
    url = 'http://www.%s.usace.army.mil/DesktopModules/ArticleCS/RSS.ashx' % site_subdomain
    params = {
        'ContentType': 4,
        'Site': site_number,
        'max': max,
    }
    return get(url, params = params)

@cache(DIR, 'summary')
def summary(url):
    return get(url, verify = False)

@cache(DIR, 'attachment')
def attachment(url):
    return get(url, verify = False)
