import datetime

from . import seed, download, parse

def public_notices(sites = seed.sites_medium, today = datetime.date.today()):
    for site_number in sites:
        r1 = download.subdomain(site_number)
        site_subdomain = parse.subdomain(r1)
        if site_subdomain:
            r2 = download.feed(today, site_subdomain, site_number)
            for link in parse.feed(r2):
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
                for _ in attachments:
                    pass
                sys.stdout.write(record['url'] + '\n')
        except Exception as e:
            sys.stderr.write('Aborting site number %d because of an exception\n' % site)

    with ThreadPoolExecutor(threads) as e:
        for site in seed.sites_medium:
            e.submit(f, site)
