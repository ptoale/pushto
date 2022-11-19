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

def vec_from_angles(theta, phi):
    """
    Create a direction unit vector from a elevation and azimuthal angle.
    
    Args:
        theta: elevation angle in degrees
        phi:   azimuthal angle in degrees
        
    Returns:
        unit vector in an np.array
    """
    theta = np.radians(theta)
    phi = np.radians(phi)
        
    "direction vector"
    return np.array([np.cos(theta)*np.cos(phi), np.cos(theta)*np.sin(phi), np.sin(theta)])

def angles_from_vec(v):
    """
    Create elevation and azimuthal angles from a direction vector.
    
    Args:
        v: direction vector in an np.array
        
    Returns:
        elevation angle in degrees, azimuthal angle in degrees
        
    """
    norm = np.linalg.norm(v)
    theta = np.arcsin(v[2]/norm)
    phi = np.arctan2(v[1], v[0])
    
    while phi < 0:
        phi += 2*np.pi
        
    return np.degrees(theta), np.degrees(phi)


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
        self.reset()
        
    def add_star(self, theta, phi, alt, azi, weight=1):
        """
        Add an alignment star. Rotation matrix is calculated for every added
        star after the second one.
        
        :param theta: polar angle of telescope in degrees
        :type theta: float
        :param phi: azimuthal angle of telescope in degrees
        :type phi: float
        :param alt: altitude in degrees
        :type alt: float
        :param azi: azimuth in degrees
        :type azi: float
        :param weight: weight of data point, defaults to 1
        :type weight: float

        """
        
        if self.n_stars and len(self.stars) == self.n_stars:
            return

        v1 = vec_from_angles(theta, phi)
        v2 = vec_from_angles(alt, azi)
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

    def update(self):
        """
        Calculate the correction matrix using the known stars.
        
        Called automatically when stars are added.
        """
        if len(self.stars) < 2:
            return

        "Calculate the B matrix"
        norm = 0
        B = 0
        for star in self.stars:
            v1 = star[0]
            v2 = star[1]
            w = star[2]
            norm += w
            B += w*np.outer(v2, v1)
        B /= norm

        "Get the single value decomposition"
        u, s, vh = np.linalg.svd(B)
        
        "Calculate the optimal rotation matrix and the likelihood of it"
        d = np.linalg.det(u)*np.linalg.det(vh.T)
        Aopt = np.matmul(u, np.matmul(np.diag([1,1,d]), vh))
        L_Aopt = 1 - s[0] - s[1] - d*s[2]
        Ps = np.diag([(1-s[0])/(s[1]+d*s[2])**2, (1-s[1])/(s[0]+d*s[2])**2, (1-d*s[2])/(s[0]+s[1])**2])/len(self.stars)
        Ph = np.matmul(vh.T, np.matmul(Ps, vh))
        
        "Update the values"
        self.R = Aopt
        self.R_inv = np.linalg.inv(self.R)
        self.R_chi2 = L_Aopt
        self.corr = Ph


    def telescope_to_horizontal(self, theta, phi):
        """
        Transform from telescope to horizontal.
        
        :param theta: elevation angle in degrees
        :type theta: float
        :param phi: azimuthal angle in degrees
        :type phi: float
            
        :return: altitude and azimuth in degrees
        :rtype: list(float)

        """
        v1 = vec_from_angles(theta, phi)
        v2 = np.squeeze(np.asarray(np.matmul(self.R, v1)))
        return angles_from_vec(v2)

    def horizontal_to_telescope(self, alt, azi):
        """
        Transform from horizontal to telescope.
        
        :param alt: altitude in degrees
        :type alt: float
        :param azi: azimuth in degrees
        :type azi: float
            
        :return: elevation and azimuthal angles in degrees
        :rtype: list(float)

         """
        v1 = vec_from_angles(alt, azi)        
        v2 = np.matmul(self.R_inv, v1)
        return angles_from_vec(v2)


if __name__ == '__main__':

    
    "pick some directions, from Taki paper"
    t1 = np.array([-0.01716476,  0.10539576, 0.99428221])
    t2 = np.array([ 0.53693373, -0.61810711, 0.57414787])
    e1 = np.array([ 0.87093425, -0.07661747, 0.48538984])
    e2 = np.array([ 0.01218772,  0.0059849,  0.99990782])
    
    "generate a third direction"
    "this does not improve the results!"
    t3 = np.cross(t1, t2)
    t3 /= np.linalg.norm(t3)
    e3 = np.cross(e1, e2)
    e3 /= np.linalg.norm(e3)
    
    "get the angles"
    theta1, phi1 = angles_from_vec(t1)
    theta2, phi2 = angles_from_vec(t2)
    theta3, phi3 = angles_from_vec(t3)
    alt1, azi1 = angles_from_vec(e1)
    alt2, azi2 = angles_from_vec(e2)
    alt3, azi3 = angles_from_vec(e3)

    "create the aligner and add the stars"    
    aligner = Aligner()
    aligner.add_star(theta1, phi1, alt1, azi1)
    aligner.add_star(theta2, phi2, alt2, azi2)
    #aligner.add_star(theta3, phi3, alt3, azi3)

    "check the results"
    c_alt1, c_azi1 = aligner.telescope_to_horizontal(theta1, phi1)
    c_e1 = vec_from_angles(c_alt1, c_azi1)
    c_alt2, c_azi2 = aligner.telescope_to_horizontal(theta2, phi2)
    c_e2 = vec_from_angles(c_alt2, c_azi2)
    #c_alt3, c_azi3 = aligner.telescope_to_horizontal(theta3, phi3)
    #c_e3 = vec_from_angles(c_alt3, c_azi3)
    d1 = np.degrees(np.arccos(np.dot(e1, c_e1)))*60
    d2 = np.degrees(np.arccos(np.dot(e2, c_e2)))*60
    #d3 = np.degrees(np.arccos(np.dot(e3, c_e3)))*60

    "print the results"
    print('------------------------')
    print('Inputs:')
    print('------------------------')
    print(' star 1: theta={:6.2f} phi={:6.2f} alt={:6.2f} azi={:6.2f}'.format(theta1, phi1, alt1, azi1))
    print(' star 2: theta={:6.2f} phi={:6.2f} alt={:6.2f} azi={:6.2f}'.format(theta2, phi2, alt2, azi2))
    #print(' star 3: theta={:6.2f} phi={:6.2f} alt={:6.2f} azi={:6.2f}'.format(theta3, phi3, alt3, azi3))
    print('------------------------')
    print('Optimal rotation matrix:')
    print('------------------------')
    print(aligner.R)
    print('------------------------')
    print('Quality checks:')
    print('------------------------')
    print(' chi2= %s' % aligner.R_chi2)
    print(' 1-det= %s' % (np.linalg.det(aligner.R) - 1))
    print(' Rinv-Rtpose:')
    print(np.linalg.inv(aligner.R) - aligner.R.T)
    print(' Correlation matrix in horizontal-frame:')
    print(aligner.corr)
    print('------------------------')
    print('Reconstruced angle error:')
    print('------------------------')
    print(" del1= {:.2f}'".format(d1))
    print(" del2= {:.2f}'".format(d2))
    #print(" del3= {:.2f}'".format(d3))
    
    
