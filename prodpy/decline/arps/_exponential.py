import logging

import numpy

from ._genmod import GenModel

class Exponential(GenModel):
	"""Exponential Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Exponential,self).__init__(*args,**kwargs)

		self._exp = 0.

	def ycal(self,x:numpy.ndarray):
		"""
		q = q0 * exp(-D0*t)
		"""
		return self.y0*numpy.exp(-self.base(x))

	def ycum(self,x:numpy.ndarray):
		"""
		Np = q0 / D0 * (1-exp(-D0*t))
		"""
		return (self.y0/self.D0)*(1-numpy.exp(-self.base(x)))

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray):
		"""Optimization based on exponential decline model."""

		x,yobs = x[yobs!=0],yobs[yobs!=0]

		try:
			LinregressResult = linregress(x,numpy.log(yobs))
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
			return 0.,0.,None

		y0 = numpy.exp(LinregressResult.intercept)
		D0 = -LinregressResult.slope

		return y0,D0,LinregressResult