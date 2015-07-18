import os

from vlermv import cache

from requests import get

DIR = '~/.usace-public-notices'
@cache(DIR, 'feed')
def feed(date, site, max = 100000):
    '''
    Get the RSS feed. We can have fun by guessing site numbers.

    :param int site: Site number to be passed as a query parameter
    '''
    url = 'http://www.sam.usace.army.mil/DesktopModules/ArticleCS/RSS.ashx'
    params = {
        'ContentType': 4,
        'Site': site,
        'max': max,
    }
    return get(url, params = params)

@cache(DIR, 'summary')
def summary(url):
    return get(url)

@cache(DIR, 'attachment')
def attachment(url):
    return get(url)
