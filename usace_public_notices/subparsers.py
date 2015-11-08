import datetime, re
import itertools
import logging

logger = logging.getLogger(__name__)

def date(raw):
    mmddyyyy = re.sub(r'[^:]+: *', '', raw)
    try:
        return datetime.datetime.strptime(mmddyyyy, '%m/%d/%Y').date()
    except ValueError:
        logger.warning('"%s" could not be parsed as a date.' % raw)

HEADINGS = [
    ['NAME OF APPLICANT', 'NAME AND ADDRESS OF APPLICANT', 'NAME',
        'SUBJECT', 'SPONSORSHIP'],
    ['LOCATION OF WORK', 'LOCATION'],
    ['CHARACTER OF WORK', 'PROGRAM DESCRIPTION', 'DESCRIPTION'], 
]
def normalize_headings(text):
    for heading in HEADINGS:
        for variant in heading:
            if variant in text:
                text = text.replace(variant, '\n\n%s:' % variant)
                break

            elif variant + ':' in text.upper():
                text = re.sub(variant + ':', '\n\n%s:' % variant,
                    text, flags = re.IGNORECASE, count = 1)
                break

            elif '\n' + variant in text.upper():
                text = re.sub('\n' + variant, '\n\n%s:' % variant,
                    text, flags = re.IGNORECASE, count = 1)
                break
    return text

def body(html, url = None):
    '''
    Retrieve the "NAME OF APPLICANT", "LOCATION OF WORK", or
    "CHARACTER OF WORK", and anything that's leftover.

    :param html: HTML document
    :type html: lxml ElementTree
    :param str url: A url for debugging messages
    :returns: (applicant, location, character, leftovers)
    :rtype: tuple of four strs
    '''
    result = []
    leftover = ''
    simple_body = normalize_headings(html.xpath('//div[@class="da_black"]')[0].text_content())

    paragraphs = (p.strip() for p in re.split(r'[\r\n]+', simple_body))

    finished_headings = set()
    for paragraph in paragraphs:
        if not paragraph: # Ignore empty paragraphs
            continue

        for i, heading in enumerate(HEADINGS):
            if i in finished_headings:
                continue
            for variant in heading:
                if paragraph.startswith(variant):
                    result.append(re.sub(r'^%s[:\s]*' % variant, '', paragraph))
                    finished_headings.add(i)
                    break
            else:
                continue
            break
        else:
            if len(result) > 0:
                result[-1] += '\n\n' + paragraph
            else:
                leftover += '\n\n' + paragraph

    if len(result) == 0:
        return ('', '', '', leftover)
    elif len(result) == 3:
        return tuple(result + [leftover])
    else:
        def _probably_an_error(b):
            return 'INTRODUCTION' not in b
        if _probably_an_error(simple_body):
            if url:
                msg = 'The body of %s could not be parsed.' % url
            else:
                msg = 'The body could not be parsed.'
            logger.warning(msg)

        return ('', '', '', simple_body)

def attachments(html):
    return set(map(str, html.xpath('//div[@class="da_noticerelated"][descendant::span[contains(text(), "ATTACHMENTS")]]/span/a/@href')))

def article_id(url, ARTICLE_ID =
    re.compile(r'.*/tabid/(\d+)/Article/(\d+)/.*')):
    m = re.match(ARTICLE_ID, url)
    if m:
        return int(m.group(2))
    else:
        raise ValueError('Could not parse article id from this:\n' + url)
