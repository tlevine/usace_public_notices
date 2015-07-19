import warnings
import re
from io import StringIO
from xml.etree.ElementTree import parse as parse_xml_fp

from lxml.html import fromstring as parse_html

from . import subparsers
from .da_number import da_number

def subdomain(response):
    rss = parse_xml_fp(StringIO(response.text))
    domain = rss.findall('.//link')[0].findtext('.')
    m = re.match(r'http://www.([a-z]+).usace.army.mil', domain)
    if m:
        return m.group(1)

def feed(response):
    rss = parse_xml_fp(StringIO(response.text))
    for link in rss.findall('.//item/link'):
        yield link.findtext('.')

def summary(response):
    html = parse_html(response.text.replace('&nbsp;', ''))
    html.make_links_absolute(response.url)

    titles = html.xpath('//strong/a/text()')
    if len(titles) == 1:
        title = str(titles[0])
    else:
        title = ''
        warnings.warn('Found no title in %s' % response.url)

    bodies = html.xpath('//div[@class="da_black"]')
    if len(bodies) == 1:
        body = bodies[0].text_content()
    else:
        body = ''
        warnings.warn('Found no body in %s' % response.url)

    def xpath(query):
        xs = html.xpath(query)
        if len(xs) == 1:
            return xs[0]
        else:
            warnings.warn('Found %d results for "%s", skipping' % (len(xs), query))
            return ''

    record = {
        'article_id': subparsers.article_id(response.url),
        'url': response.url,
        'post_date': subparsers.date(xpath('//em[contains(text(), "Posted:")]/text()')),
        'expiration_date': subparsers.date(xpath('//em[contains(text(), "Expiration date:")]/text()')),
        'title': title,
        'body': body,
        'attachments': subparsers.attachments(html),
    }

    maybe_pan = da_number(title)
    if maybe_pan:
        record.update(maybe_pan)
        applicant, location, character, leftover = subparsers.body(html, url = response.url)
        record.update({
            'applicant': applicant,
            'location': location,
            'character': character,
        })
    return record

def attachment(response):
    return {
        'url': response.url,
        'content': response.content,
    }
