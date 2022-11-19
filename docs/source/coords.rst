Coordinate Transformations
==========================

There are three coordinate systems that must be aligned. The encoders 
report counts that are translated into the telescope attitude. The 
telescope attitude is then transformed into the local horizontal 
coordinate system using alignment data. Finally the altitude and azimuth
are transformed into the J2000 equatorial system using :mod:`astropy`.

The alignment procedure gathers pairs of coordinates for an object 
centered in the eyepiece of the telescope and selected within Stellarium.
The STC sends the RA and Dec of the object, which are translated to Alt and
Azi, forming one half of the pair. The other half is the current telescope
azimuth Theta and elevation Phi. With data from at least 2 stars, the optimal
rotation matrix can be found. Finding the optimal transformation matrix 
given measured pairs of vectors is known as *Wahba's problem*.

The solution to the problem here follows the algorithm laid out by Markley [#]_. 
This method finds the optimal rotation matrix using singular value decomposition 
(SVD). This method has been shown to reliably find the best pure rotation matrix
that connects the given data. Mathematically, given vectors :math:`\vec{x}` and 
:math:`\vec{y} = R_{true} \vec{x}` we want to find :math:`R_{opt}` by 
minimizing the cost function

.. math::

   L = \frac{1}{2} \sum_{i=1}^N \left|\vec{y}_i - R\vec{x}_i\right|^2

where :math:`N` is the number of data points (stars). The data is combined in
a matrix defined by

.. math::

   B = \sum_{i=1}^N w_i \vec{y}_i \otimes \vec{x}_i


where :math:`\otimes` represents the outer product and the :math:`w_i` are weights
that are normalized so that :math:`\sum w_i = 1`. The SVD analysis finds the 
closest pure rotation matrix to this matrix. 

The SVD decomposition is written as

.. math::

   B = U S V^T

where :math:`U` and :math:`V` are orthogonal matrices and :math:`S` is a digonal
matrix with compoents :math:`(s_1, s_2, s_3)` with  :math:`s_1 \ge s_2 \ge s_3`.
The optimal rotation matrix is then given by

.. math::

   R = U S^\prime V^T

where :math:`S^\prime` is a diagonal matrix with compoents :math:`(1, 1, d)` where
:math:`d = \det(U) \det(V) = \pm 1`.

The value of the cost function at the minimum is a kind of :math:`\chi^2` and 
is a function of the singular values

.. math::
   L_{min} = 1 - s_1 - s_2 - d s_3


.. [#] "Attitude Determination using Vector Observations and the Singular Value Decomposition",
       The Journal of Astronautical Sciences, Vol 36, No 3, July-September 1988, pp 245-258

