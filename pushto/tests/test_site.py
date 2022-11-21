import unittest
from astropy.time import Time
import pushto.site


class TestLocation(unittest.TestCase):

    def setUp(self):
        self.location = pushto.site.Location(lat=0, lon=0, elev=0)
        self.utc = Time('2022-11-17 16:14:58.967', format='iso')

    def test_horizontal_to_equatorial(self):
        ra, dec = self.location.horizontal_to_equatorial(0, 0, utc=self.utc)
        self.assertAlmostEqual(ra, 23.9581745)
        self.assertAlmostEqual(dec, 89.8693265)

    def test_equatorial_to_horizontal(self):
        azi, alt = self.location.equatorial_to_horizontal(ra=23.9581745, dec=89.8693265, utc=self.utc)
        self.assertAlmostEqual(azi, 0)
        self.assertAlmostEqual(alt, 0)


if __name__ == '__main__':
    unittest.main()
