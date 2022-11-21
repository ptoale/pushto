import unittest
import pushto.stellarium


class TestBinary(unittest.TestCase):

    def test_stc_encode(self):
        data = pushto.stellarium.stc_encode(utc='2022-11-17 16:14:58.967', ra=12, dec=-30)
        self.assertIsInstance(data, bytearray)
        self.assertEqual(len(data), 24)
        self.assertEqual(data[0], 24)
        self.assertEqual(data[1], 0)
        self.assertEqual(data[2], 0)
        self.assertEqual(data[3], 0)
        self.assertEqual(data[4], 216)
        self.assertEqual(data[5], 197)
        self.assertEqual(data[6], 0)
        self.assertEqual(data[7], 228)
        self.assertEqual(data[8], 172)
        self.assertEqual(data[9], 237)
        self.assertEqual(data[10], 5)
        self.assertEqual(data[11], 0)
        self.assertEqual(data[12], 0)
        self.assertEqual(data[13], 0)
        self.assertEqual(data[14], 0)
        self.assertEqual(data[15], 128)
        self.assertEqual(data[16], 171)
        self.assertEqual(data[17], 170)
        self.assertEqual(data[18], 170)
        self.assertEqual(data[19], 234)
        self.assertEqual(data[20], 0)
        self.assertEqual(data[21], 0)
        self.assertEqual(data[22], 0)
        self.assertEqual(data[23], 0)

    def test_stc_decode(self):
        data = bytes([24, 0, 0, 0, 216, 197, 0, 228, 172, 237, 5, 0, 0, 0, 0, 128, 171, 170, 170, 234])
        utc, ra, dec = pushto.stellarium.stc_decode(data)
        self.assertEqual(utc, '2022-11-17 16:14:58.967')
        self.assertAlmostEqual(ra, 12)
        self.assertAlmostEqual(dec, -30)


if __name__ == '__main__':
    unittest.main()
