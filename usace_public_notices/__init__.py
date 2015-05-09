import datetime

from . import seed, download, parse

def public_notices(sites = seed.sites_medium, today = datetime.date.today()):
    for site in sites:
        for link in parse.feed(download.feed(today, site)):
            record = parse.summary(download.summary(link))
            xs = record.pop('attachments')
            yield record, (parse.attachment(download.attachment(x)) for x in xs)

def cli():
    from concurrent.futures import ThreadPoolExecutor
    import sys
    threads = 15

    def f(site):
        try:
            for record, attachments in public_notices(sites = [site]):
                sys.stdout.write(record['title'] + '\n')
        except:
            sys.stderr.write('Aborting site number %d because of an exception\n' % site)

    with ThreadPoolExecutor(threads) as e:
        for site in seed.sites_medium:
            e.submit(f, site)
