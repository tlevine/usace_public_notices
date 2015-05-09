import re

def da_number(raw):
    m = re.match(r'([A-Z]+)[^0-9]*([0-9]+)[ -]([0-9]+)((?:[ -][0-9]+)?)((?:[ -][A-Z]+)?)', raw)
    if m:
        # m.group(4) is addendum number
        # m.group(5) is some subdivision. Maybe parish?
        args = (m.group(1), int(m.group(2)), int(m.group(3)))
        return {
        #   'permit_application_number': '%s-%d-%d' % args,
            'district': m.group(1),
            'year': int(m.group(2)),
            'local_da_number': int(m.group(3)),
            'addendum': m.group(4).lstrip(' -'),
            'district_engineer': m.group(5).lstrip(' -'),
        }
