import datetime

from . import seed, download, parse

def public_notices(sites = seed.sites_short, today = datetime.date.today()):
    for site in sites():
        for link in parse.feed(download.feed(today, site)):
            record = parse.summary(download.summary(link))
            xs = record.pop('attachments')
            args = record, (parse.attachment(download.attachment(x)) for x in xs)
            yield record['article_id'], args
