"""
testcases_permit_application_number = [
    ('MVN 2008-0256 EMM', 'MVN-2008-256'),
    ('MVN 2008-00256 EMM', 'MVN-2008-256'),
    ('MVN-2014-00771-1-MR', 'MVN-2014-771'),
    ('MVN-2009-03103', 'MVN-2009-3103'),
    ('MVN02014-02852-WJJ', 'MVN-2014-2852'),
]
@pytest.mark.parametrize('raw, out', testcases_permit_application_number)
def test_permit_application_number(raw, out):
    assert subparsers.permit_application_number(raw)['permit_application_number'] == out
"""

