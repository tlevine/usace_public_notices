from io import StringIO
from xml.etree.ElementTree import parse as parse_xml_fp

from lxml.html import fromstring as parse_html

from . import subparsers
from ..lib.da_number import da_number

def feed(response):
    rss = parse_xml_fp(StringIO(response.text))
    for link in rss.findall('.//item/link'):
        yield link.findtext('.')

def summary(response):
    html = parse_html(response.text.replace('&nbsp;', ''))
    html.make_links_absolute(response.url)

    title = str(html.xpath('//strong/a/text()')[0])
    body = html.xpath('//div[@class="da_black"]')[0].text_content()
    record = {
        'article_id': subparsers.article_id(response.url),
        'url': response.url,
        'post_date': subparsers.date(html.xpath('//em[contains(text(), "Posted:")]/text()')[0]),
        'expiration_date': subparsers.date(html.xpath('//em[contains(text(), "Expiration date:")]/text()')[0]),
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
