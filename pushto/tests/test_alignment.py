import unittest
import numpy as np
import pushto.alignment


class TestAngles(unittest.TestCase):

    def test_angles_from_vec(self):
        phi, theta = pushto.alignment.angles_from_vec(np.array([10, 0, 0]))
        self.assertEqual(phi, 0.0)
        self.assertEqual(theta, 0.0)

        phi, theta = pushto.alignment.angles_from_vec(np.array([0, 10, 0]))
        self.assertEqual(phi, 90.0)
        self.assertEqual(theta, 0.0)

        phi, theta = pushto.alignment.angles_from_vec(np.array([0, 0, 10]))
        self.assertEqual(phi, 0.0)
        self.assertEqual(theta, 90.0)

        phi, theta = pushto.alignment.angles_from_vec(np.array([-10, 0, 0]))
        self.assertEqual(phi, 180.0)
        self.assertEqual(theta, 0.0)

        phi, theta = pushto.alignment.angles_from_vec(np.array([0, -10, 0]))
        self.assertEqual(phi, 270.0)
        self.assertEqual(theta, 0.0)

        phi, theta = pushto.alignment.angles_from_vec(np.array([0, 0, -10]))
        self.assertEqual(phi, 0.0)
        self.assertEqual(theta, -90.0)

    def test_vec_from_angles(self):

        vec = pushto.alignment.vec_from_angles(0, 0)
        self.assertEqual(vec[0], 1.0)
        self.assertEqual(vec[1], 0)
        self.assertEqual(vec[2], 0)

        vec = pushto.alignment.vec_from_angles(90, 0)
        self.assertEqual(vec[0], 6.123233995736766e-17)
        self.assertEqual(vec[1], 1.0)
        self.assertEqual(vec[2], 0)

        vec = pushto.alignment.vec_from_angles(0, 90)
        self.assertEqual(vec[0], 6.123233995736766e-17)
        self.assertEqual(vec[1], 0)
        self.assertEqual(vec[2], 1.0)

        vec = pushto.alignment.vec_from_angles(180, 0)
        self.assertEqual(vec[0], -1.0)
        self.assertEqual(vec[1], 1.2246467991473532e-16)
        self.assertEqual(vec[2], 0)

        vec = pushto.alignment.vec_from_angles(270, 0)
        self.assertEqual(vec[0], -1.8369701987210297e-16)
        self.assertEqual(vec[1], -1.0)
        self.assertEqual(vec[2], 0)

        vec = pushto.alignment.vec_from_angles(0, -90)
        self.assertEqual(vec[0], 6.123233995736766e-17)
        self.assertEqual(vec[1], 0)
        self.assertEqual(vec[2], -1.0)


class TestAligner(unittest.TestCase):

    def setUp(self):
        self.aligner = pushto.alignment.Aligner()
        self.t1 = np.array([-0.01716476,  0.10539576, 0.99428221])
        self.t2 = np.array([ 0.53693373, -0.61810711, 0.57414787])
        self.e1 = np.array([ 0.87093425, -0.07661747, 0.48538984])
        self.e2 = np.array([ 0.01218772,  0.0059849,  0.99990782])

    def test_add_star(self):
        phi1, theta1 = pushto.alignment.angles_from_vec(self.t1)
        azi1, alt1 = pushto.alignment.angles_from_vec(self.e1)
        self.aligner.add_star(phi1, theta1, azi1, alt1)
        self.assertEqual(len(self.aligner.stars), 1)
        self.assertEqual(self.aligner.R[0][0], 1)
        self.assertEqual(self.aligner.R[0][1], 0)
        self.assertEqual(self.aligner.R[0][2], 0)
        self.assertEqual(self.aligner.R[1][0], 0)
        self.assertEqual(self.aligner.R[1][1], 1)
        self.assertEqual(self.aligner.R[1][2], 0)
        self.assertEqual(self.aligner.R[2][0], 0)
        self.assertEqual(self.aligner.R[2][1], 0)
        self.assertEqual(self.aligner.R[2][2], 1)

        phi2, theta2 = pushto.alignment.angles_from_vec(self.t2)
        azi2, alt2 = pushto.alignment.angles_from_vec(self.e2)
        self.aligner.add_star(phi2, theta2, azi2, alt2)
        self.assertEqual(len(self.aligner.stars), 2)
        self.assertIsNotNone(self.aligner.R_chi2)

    def test_taki(self):
        phi1, theta1 = pushto.alignment.angles_from_vec(self.t1)
        azi1, alt1 = pushto.alignment.angles_from_vec(self.e1)
        self.aligner.add_star(phi1, theta1, azi1, alt1)
        phi2, theta2 = pushto.alignment.angles_from_vec(self.t2)
        azi2, alt2 = pushto.alignment.angles_from_vec(self.e2)
        self.aligner.add_star(phi2, theta2, azi2, alt2)

        c_alt1, c_azi1 = self.aligner.telescope_to_horizontal(phi1, theta1)
        c_e1 = pushto.alignment.vec_from_angles(c_azi1, c_alt1)
        c_alt2, c_azi2 = self.aligner.telescope_to_horizontal(phi2, theta2)
        c_e2 = pushto.alignment.vec_from_angles(c_azi2, c_alt2)
        d1 = np.degrees(np.arccos(np.dot(self.e1, c_e1))) * 60
        d2 = np.degrees(np.arccos(np.dot(self.e2, c_e2))) * 60

        self.assertEqual(d1, 2835.633463370939)
        self.assertEqual(d2, 3883.149375707308)


if __name__ == '__main__':
    unittest.main()
