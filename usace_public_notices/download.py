import os

from django.conf import settings
import vlermv

from helpers import get

def cache(subdir, key_transformer = vlermv.transformers.magic):
    d = os.path.join(settings.IMPORT_DIR, 'public_notices', subdir)
    return vlermv.cache(d, key_transformer = key_transformer)

@cache('feed', key_transformer = vlermv.transformers.archive(position = 'right'))
def feed(site, max = 100000):
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

@cache('summary')
def summary(url):
    return get(url)

@cache('attachment')
def attachment(url):
    return get(url)
