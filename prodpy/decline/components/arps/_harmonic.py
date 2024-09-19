import logging

import numpy

from ._genmod import GenModel

class Harmonic(GenModel):
	"""Harmonic Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Harmonic,self).__init__(*args,**kwargs)

		self._exp = 1.

	def ycal(self,x:numpy.ndarray):
		"""
		q = q0 / (1+d0*t)
		"""
		return self.y0/(1+self.base(x))

	def ycum(self,x:numpy.ndarray):
		"""
		Np = q0 / d0 * ln(1+d0*t)
		"""
		return (self.y0/self.d0)*numpy.log(1+self.base(x))

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray):
		"""Optimization based on harmonic decline model."""

		x,yobs = x[yobs!=0],yobs[yobs!=0]

		try:
			LinregressResult = linregress(x,1/yobs)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
			return 0.,0.,None

		y0 = LinregressResult.intercept**(-1)
		d0 = LinregressResult.slope/LinregressResult.intercept

		return y0,d0,LinregressResult