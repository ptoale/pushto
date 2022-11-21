#!/usr/bin/env python
"""
Telescope alignment.

Provides:
    - Aligner


Solves Wahba's problem using single value decomposition (SVD) as outlined in Markley paper.

Markley paper:
The Journal of Astronautical Sciences, Vol 36, No 3, July-September 1988, pp 245-258


Telescope coordinates: not aligned
    theta: elevation angle, measured from reference plane
    phi: azimuthal angle, measured CW around reference plane
    (0, 0): direction telescope is pointing when Arduino starts
    
Horizontal coordinates: aligned with zenith and horizon
    altitude: elevation angle, measured from horizon
    azimuth: azimuthal angle, measured CW from North
    (0, 0): North on the horizon

"""
import numpy as np


def vec_from_angles(phi, theta):
    """
    Create a direction unit vector from elevation and azimuthal angles.

    :param phi: azimuthal angle, in degrees
    :type phi: float
    :param theta: elevation angle, in degrees
    :type theta: float

    :return: unit direction vector
    :rtype: :obj:`np.ndarray`

    """
    phi = np.radians(phi)
    theta = np.radians(theta)

    "direction vector"
    return np.array([np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), np.sin(theta)])


def angles_from_vec(v):
    """
    Create elevation and azimuthal angles from a direction vector.
    
    :param v: direction vector
    :type v: :obj:`np.ndarray`

    :return: azimuthal angle, elevation angle in degrees
    :rtype: list

    """
    norm = np.linalg.norm(v)
    theta = np.arcsin(v[2]/norm)
    phi = np.arctan2(v[1], v[0])
    
    while phi < 0:
        phi += 2*np.pi
        
    return np.degrees(phi), np.degrees(theta)


class Aligner(object):
    """
    Aligner class
        - calculates transformation matrix
        - transforms between telescope <-> horizontal
        
    :param n_stars: max number of stars to use, optional
    :type n_stars: int
    
    """

    def __init__(self, n_stars=None):
        self.n_stars = n_stars
        self.stars = None
        self.R = None
        self.R_inv = None
        self.R_chi2 = None
        self.corr = None
        self.reset()
        
    def add_star(self, phi, theta, azi, alt, weight=1):
        """
        Add an alignment star. Rotation matrix is calculated for every added
        star after the second one.
        
        :param phi: azimuthal angle of telescope in degrees
        :type phi: float
        :param theta: polar angle of telescope in degrees
        :type theta: float
        :param azi: azimuth in degrees
        :type azi: float
        :param alt: altitude in degrees
        :type alt: float
        :param weight: weight of data point, defaults to 1
        :type weight: float

        """
        
        if self.n_stars and len(self.stars) == self.n_stars:
            return

        v1 = vec_from_angles(phi, theta)
        v2 = vec_from_angles(azi, alt)
        self.stars.append([v1, v2, weight])
        self.update()

    def reset(self):
        """
        Reset the alignment.
        """
        self.stars = []
        self.R = np.identity(3)
        self.R_inv = np.identity(3)
        self.R_chi2 = None
        self.corr = None

    def update(self):
        """
        Calculate the correction matrix using the known stars.
        
        Called automatically when stars are added.
        """
        if len(self.stars) < 2:
            return

        "Calculate the B matrix"
        norm = 0
        bm = 0
        for star in self.stars:
            v1 = star[0]
            v2 = star[1]
            w = star[2]
            norm += w
            bm += w*np.outer(v2, v1)
        bm /= norm

        "Get the single value decomposition"
        u, s, vh = np.linalg.svd(bm)
        
        "Calculate the optimal rotation matrix and the likelihood of it"
        d = np.linalg.det(u)*np.linalg.det(vh.T)
        a_opt = np.matmul(u, np.matmul(np.diag([1, 1, d]), vh))
        l_opt = 1 - s[0] - s[1] - d*s[2]
        ps = np.diag([(1-s[0])/(s[1]+d*s[2])**2, (1-s[1])/(s[0]+d*s[2])**2, (1-d*s[2])/(s[0]+s[1])**2])/len(self.stars)
        ph = np.matmul(vh.T, np.matmul(ps, vh))
        
        "Update the values"
        self.R = a_opt
        self.R_inv = np.linalg.inv(self.R)
        self.R_chi2 = l_opt
        self.corr = ph

    def telescope_to_horizontal(self, phi, theta):
        """
        Transform from telescope to horizontal.
        
        :param phi: azimuthal angle in degrees
        :type phi: float
        :param theta: elevation angle in degrees
        :type theta: float

        :return: azimuth and altitude in degrees
        :rtype: list(float)

        """
        v1 = vec_from_angles(phi, theta)
        v2 = np.squeeze(np.asarray(np.matmul(self.R, v1)))
        return angles_from_vec(v2)

    def horizontal_to_telescope(self, azi, alt):
        """
        Transform from horizontal to telescope.
        
        :param azi: azimuth in degrees
        :type azi: float
        :param alt: altitude in degrees
        :type alt: float

        :return: elevation and azimuthal angles in degrees
        :rtype: list(float)

         """
        v1 = vec_from_angles(azi, alt)
        v2 = np.matmul(self.R_inv, v1)
        return angles_from_vec(v2)
