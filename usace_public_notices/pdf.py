import warnings
import re

from .subparsers import _strip_ws as strip_ws

def parse(text):
    # Parse
    data = {
        'coastal_use_permits': _read_cup_number(text),
        'water_quality_certifications': _read_wqc_number(text),
        'location': _location_of_work(text),
        'character': _character_of_work(text),
    }
    coords = _read_coords(text)
    if len(coords) > 0:
        data['latitude'], data['longitude'] = coords[0]
    if len(coords) > 1:
        warnings.warn('Multible coordinate pairs:\n%s' % coords)
    return data

LOCATION_OF_WORK = re.compile(r'^.*(LOCATION OF WORK|LOCATION):.*$')
CHARACTER_OF_WORK = re.compile(r'^.*(CHARACTER OF WORK|DESCRIPTION):.*$')
def _location_of_work(text):
    lines = text.split('\n')
    in_window = False
    out = []
    for line in lines:
        if re.match(LOCATION_OF_WORK, line):
            in_window = True
        elif re.match(CHARACTER_OF_WORK, line):
            break

        if in_window:
            out.append(line)
    return ''.join(out)

def _character_of_work(text):
    lines = text.split('\n')
    in_window = False
    out = []
    for line in lines:
        if re.match(CHARACTER_OF_WORK, line):
            in_window = True
        elif line == '\n':
            break

        if in_window:
            out.append(line)
    return ''.join(out)

CUP_NUMBER = re.compile(r'\s(P\d{8})[^0-9]')
def _read_cup_number(rawtext):
    return list(sorted(set(re.findall(CUP_NUMBER, rawtext))))

WQC_NUMBER = re.compile(r'WQCApplicationNumber[^0-9]*([0-9-]+)')
def _read_wqc_number(rawtext):
    rawtext = strip_ws(rawtext)
    wqc_numbers = re.findall(WQC_NUMBER, rawtext)

    if len(wqc_numbers) > 1:
        raise AssertionError('Multiple WQC numbers found')
    elif len(wqc_numbers) == 0:
        warnings.warn('No WQC numbers found')
    else:
        no_hyphen = wqc_numbers[0].replace('-', '')
        if len(no_hyphen) == 8:
            return no_hyphen[:6] + '-' + no_hyphen[-2:]
        else:
            warnings.warn('WQC number has the wrong length.')

MINUTE_COORDS = re.compile(r'(?:lat|latitude|long|longitude)?(\d+)[°-](\d+)[\'-]([0-9.]+)[" ]([NW])')
DECIMAL_COORDS = re.compile(r'(?:lat|latitude|long|longitude) ?([0-9.-]+)', flags = re.IGNORECASE)

def _read_coords(rawtext, **kwargs):
    "Get coordinates from the notice."
    rawtext = strip_ws(rawtext)

    rawcoords = re.findall(MINUTE_COORDS, rawtext)
    if len(rawcoords) > 0:
        return _clean_minute_coords(rawcoords, **kwargs)

    rawcoordsd = re.findall(DECIMAL_COORDS, rawtext)
    return _clean_minute_coords(rawcoordsd)

def _clean_minute_coords(rawcoords, decimal = True, verbose = False):
    cleancoords = []
    while len(rawcoords) >= 2:
        _first = rawcoords.pop(0)
        _second = rawcoords.pop(0)

        f = _first[-1]
        s = _second[-1]
        try:
            if f == s == 'N':
                _second = rawcoords.pop(0)
            elif f == s == 'W':
                _first = rawcoords.pop(0)
        except IndexError:
            continue

        if not {f, s} == {'N', 'W'}:
            warnings.warn('Skipping Un-American directions in coordinates %s and %s' % (_first, _second))
            continue
        if f == 'N':
            first = _first
            second = _second
        else:
            first = _second
            second = _first

        # Handle sign
        s = int(second[0])
        if s < 0:
            second = [-s] + list(second[1:3])

        f = int(first[0])
        s = int(second[0])
        if not -90 < f < 90:
            raise ValueError('Strange latitude: %d' % f)
        if not -180 < s < 180:
            raise ValueError('Strange longitude: %d' % s)


        lat = tuple([float(f) for f in first[:3]])
        lng = tuple([-float(s) for s in second[:3]])

        if decimal:
            latlng = tuple([_convert_coords(*foo) for foo in [lat, lng]])
            cleancoords.append(latlng)
        else:
            cleancoords.append((lat, lng))

    return cleancoords

def _convert_coords(degrees, minutes, seconds):
    [degrees, minutes, seconds] = map(float, [degrees, minutes, seconds])

    # Check signs
    for arg in [degrees, minutes, seconds]:
        if arg == 0:
            continue
        elif arg > 0:
            positive = True
            break
        elif arg < 0:
            positive = False
            break
        else:
            raise ValueError('wtf?')
    for arg in [degrees, minutes, seconds]:
        if positive and arg < 0:
            raise ValueError('All arguments must have the same sign.')
        elif not positive and arg > 0:
            raise ValueError('All arguments must have the same sign.')

    return degrees + minutes/60 + seconds/3600
