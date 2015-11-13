import pytest

from .. import pdf

coords_cases = [
    ('Lafourche Parish, LA;POB @ Old LA 1/ LA 3090 Intersection in Fourchon, LA; POE @ LA 3235 in Golden Meadow, LA; Project Centered @ Lat 29-14-50 N / Long 90-12-25 W; Sections 6, 7, 8, 17, 20, 29, 32, 33, T20SR22E;Sections 4, 9, 15, 16, 22, 23, 26, 35, 36, T21S-R22E; Sections 1, 2, 13, 24, 25, 35, 36, T22S-R22E. See plats for additional coordinates.', [(0, 0)])
]
@pytest.mark.parametrize('text, coords', coords_cases)
def test_read_coords(text, coords):
    assert pdf._read_coords(text) == coords
