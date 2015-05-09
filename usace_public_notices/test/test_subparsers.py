import datetime, itertools, os, pickle

import lxml.html
import pytest

from .. import subparsers

def response(filename):
    with open(os.path.join(os.path.dirname(__file__), 'fixtures', filename), 'rb') as fp:
        obj = pickle.load(fp)
    return obj

testcases_date = [
    ('Posted: 7/19/2013', datetime.date(2013, 7, 19)),
    ('Expiration date: 8/11/2013', datetime.date(2013, 8, 11)),
    ('Posted: 6/27/2013', datetime.date(2013, 6, 27)),
    ('Expiration date: 7/25/2013', datetime.date(2013, 7, 25)),
    ('Expiration date: ', None),
]
@pytest.mark.parametrize('raw,result', testcases_date)
def test_date(raw, result):
    assert subparsers.date(raw) == result

fixtures_summary_paragraph = [
    (response('mvn-1998-4529-eoo.aspx'), 'Aberdeen', '-90.613245', '12 wide', None),
    (response('mvn-2013-2749-eoo.aspx'), 
        ['Services, ℅ Howard Rubinow', '3900 North Causewa'],
        ['Hero Cut off ', 'Hydrologic Unit C'],
        'No jurisdictional wetlands', None),
    (response('mvn-2014-01527-cj.aspx'), 'c/o Gulf South', '08090301',
        '0.0039 of an acre of', None),
    (response('mvn-2014-00771-1-mr.aspx'),
       'c/o Pangaea', '08070201', '24.4 acres', 'ASH SLOUGH ADDENDUM'),
    (response('mvn-2015-00695-cd.aspx'),
        '', '', '', None),
    (response('mvn-2006-00473-ma.aspx'),
        '', '', '', None),
    (response('mvn-2014-00677-wll.aspx'),
        '', '', '', None),
    (response('mvn-2011-0184-wll.aspx'),
        '', '', '', None),
]

@pytest.mark.parametrize('response, a_member, l_member, c_member, u_member',
                         fixtures_summary_paragraph)
def test_body(response, a_member, l_member, c_member, u_member):
    html = lxml.html.fromstring(response.text)
    x = subparsers.body(html)

    assert len(x) == 4, 'Tuple of applicant, location, character, uncategorized'

    msg = 'Result should at least not be empty. (%s)' % response.url
    assert any(x), msg

    def _check_many(a, b):
        if isinstance(a, str):
            assert a in b
        else:
            for aa in a:
                assert aa in b
    applicant, location, character, uncategorized = x
    _check_many(a_member, applicant)
    _check_many(l_member, location)
    _check_many(c_member, character)
    if u_member:
        _check_many(u_member, uncategorized)
    else:
        assert uncategorized == ''

def test_normalize_headings():
    original = 'W: -91.27153) Along the east bank of the Lower Atchafalaya River and Deer Island Pass in St. Mary Parish, Louisiana,\r\n \r\nCharacter of Work \xa0\xa0This proposal is a modification to a previously authorized maintenance dredging project to include an additional 7 acres (80,000 cubic yards) of dredging from the chan'
    assert 'CHARACTER OF WORK:' in subparsers.normalize_headings(original)

testcases_attachments = [
    (response('mvn-2014-00771-1-mr.aspx'),
        {'http://www.mvn.usace.army.mil/Portals/56/docs/regulatory/publicnotices/2014_00771_1_PNall.pdf'}),
]
@pytest.mark.parametrize('response, result', testcases_attachments)
def test_attachments(response, result):
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(response.url)
    assert subparsers.attachments(html) == result

testcases_article_id = [
    ('http://www.mvn.usace.army.mil/Missions/Regulatory/PublicNotices/tabid/9321/Article/586732/mvn-2015-00847-mr.aspx', 586732),
    ('http://www.mvn.usace.army.mil/Missions/Regulatory/PublicNotices/tabid/9321/Article/586606/mvn-2014-00771-1-mr.aspx', 586606),
    ('http://www.mvn.usace.army.mil/Missions/Regulatory/PublicNotices/tabid/9321/Article/586510/mvn-2015-00695-cd.aspx', 586510),
    ('http://www.mvn.usace.army.mil/Missions/Regulatory/PublicNotices/tabid/9321/Article/586270/mvn-2011-0184-wll.aspx', 586270),
    ('http://www.mvn.usace.army.mil/Missions/Regulatory/PublicNotices/tabid/9321/Article/586657/mvn-2014-02046-ma.aspx', 586657),
    ('http://www.spd.usace.army.mil/Missions/Regulatory/PublicNoticesandReferences/tabid/10390/Article/565189/clean-water-act-interpretive-rule-for-404f1a.aspx', 565189),
]
@pytest.mark.parametrize('raw, out', testcases_article_id)
def test_article_id(raw, out):
    assert subparsers.article_id(raw) == out
