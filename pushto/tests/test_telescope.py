import unittest
import pushto.telescope


class TestEncoders(unittest.TestCase):

    def test_convert(self):
        enc = pushto.telescope.Encoders(phi_npr=360, theta_npr=360, flip_phi=False, flip_theta=True)

        phi, theta = enc.convert(0, 0)
        self.assertEqual(phi, 0)
        self.assertEqual(theta, 0)

        phi, theta = enc.convert(1, 1)
        self.assertEqual(phi, 1.0)
        self.assertEqual(theta, -1.0)

        phi, theta = enc.convert(89, 89)
        self.assertEqual(phi, 89.0)
        self.assertEqual(theta, -89.0)

        phi, theta = enc.convert(90, 90)
        self.assertEqual(phi, 90.0)
        self.assertEqual(theta, -90.0)

        phi, theta = enc.convert(91, 91)
        self.assertEqual(phi, 271.0)
        self.assertEqual(theta, -89.0)

        phi, theta = enc.convert(179, 179)
        self.assertEqual(phi, 359.0)
        self.assertEqual(theta, -1.0)

        phi, theta = enc.convert(180, 180)
        self.assertEqual(phi, 0.0)
        self.assertEqual(theta, 0.0)

        phi, theta = enc.convert(181, 181)
        self.assertEqual(phi, 1.0)
        self.assertEqual(theta, 1.0)

        phi, theta = enc.convert(269, 269)
        self.assertEqual(phi, 89.0)
        self.assertEqual(theta, 89.0)

        phi, theta = enc.convert(270, 270)
        self.assertEqual(phi, 270.0)
        self.assertEqual(theta, 90.0)

        phi, theta = enc.convert(271, 271)
        self.assertEqual(phi, 271.0)
        self.assertEqual(theta, 89.0)

        phi, theta = enc.convert(359, 359)
        self.assertEqual(phi, 359.0)
        self.assertEqual(theta, 1.0)


class TestPointingModel(unittest.TestCase):

    def test_apply(self):
        pm = pushto.telescope.PointingModel()
        phi, theta = pm.apply(0, 0)
        self.assertEqual(phi, 0)
        self.assertEqual(theta, 0)


if __name__ == '__main__':
    unittest.main()
