import re
from io import BytesIO
from xml.etree.ElementTree import parse as parse_xml_fp
import logging

from lxml.html import fromstring as parse_html

from . import subparsers, pdf
from .da_number import da_number

logger = logging.getLogger(__name__)

def subdomain(response):
    rss = parse_xml_fp(BytesIO(response.content))
    domain = rss.findall('.//link')[0].findtext('.')
    m = re.match(r'http://www.([a-z]+).usace.army.mil', domain)
    if m:
        return m.group(1)

def feed(response):
    namespaces = {'dc': 'http://purl.org/dc/elements/1.1/'}
    
    rss = parse_xml_fp(BytesIO(response.content))

    # I guess findtext takes the first one. It would be nice to do this properly though.
    district_code = re.match(r'.*\.([a-z]+).usace.*', rss.findtext('//link')).group(1)
    district_name = rss.findtext('//title').replace(' Public Notices', '')

    for item in rss.findall('.//item'):
        yield {
            'url': item.findtext('link'),
            'permit_application_number': item.findtext('title'),
            'description': item.findtext('description'),
            'district_code': district_code,
            'district_name': district_name,
            'project_manager_name': item.findall('dc:creator', namespaces)[0].findtext('.').replace('.', ' ').title(),
        }

def summary(response):
    html = parse_html(response.content.replace(b'&nbsp;', b''))
    html.make_links_absolute(response.url)

    titles = html.xpath('//strong/a/text()')
    if len(titles) == 1:
        title = str(titles[0])
    else:
        title = ''
        logger.warning('Found no title in %s' % response.url)

    bodies = html.xpath('//div[@class="da_black"]')
    if len(bodies) == 1:
        body = bodies[0].text_content()
    else:
        body = ''
        logger.warning('Found no body in %s' % response.url)

    def xpath(query):
        xs = html.xpath(query)
        if len(xs) == 1:
            return xs[0]
        else:
            logger.warning('Found %d results for "%s", skipping' % (len(xs), query))
            return ''

    record = {
        'article_id': subparsers.article_id(response.url),
    #   'url': response.url,
        'post_date': subparsers.date(xpath('//em[contains(text(), "Posted:")]/text()')),
        'expiration_date': subparsers.date(xpath('//em[contains(text(), "Expiration date:")]/text()')),
    #   'title': title,
        'body': body.strip('\r\n '),
        'attachments': subparsers.attachments(html),
        'hydrologic_unit_codes': subparsers.hucs(body),
        'coastal_use_permits': subparsers.cups(body),
        'water_quality_certifications': subparsers.wqcs(body),
    }

    maybe_pan = da_number(title)
    if maybe_pan:
        record.update(maybe_pan)
        applicant, location, character, leftover = subparsers.body(html, url = response.url)
        record.update({
            'applicant': applicant.strip('\r\n '),
            'location': location.strip('\r\n '),
            'character': character.strip('\r\n '),
        })
    else:
        record.update({
            'applicant': '',
            'location': '',
            'character': '',
        })

    fallbacks = pdf.parse(body)
    for k in fallbacks:
        if not record[k]:
            record[k] = fallbacks[k]
    return record

def attachment(response):
    return {
        'url': response.url,
        'content': response.content,
    }
