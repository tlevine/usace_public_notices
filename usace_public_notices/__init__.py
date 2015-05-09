'''
In this directory and below we put nothing specific to Django.
We expose data to Django as a few generators below.
'''

from . import seed, download, parse


def public_notices(sites = seed.sites_short):
    for site in sites():
        for link in parse.feed(download.feed(str(site))):
            record = parse.summary(download.summary(link))
            xs = record.pop('attachments')
            args = record, (parse.attachment(download.attachment(x)) for x in xs)
            yield record['article_id'], args

def project_managers(sites = seed.sites_short):
    raise NotImplementedError
    for site in sites():
        for link in parse.feed(download.feed(site)):
            yield do_something_with(download.summary(link))
