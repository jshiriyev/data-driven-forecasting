import logging

import numpy

from ._genmod import GenModel

class Hyperbolic(GenModel):
	"""Hyperbolic Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Hyperbolic,self).__init__(*args,**kwargs)
	
	def ycal(self,x:numpy.ndarray):
		"""
		q = q0 / (1+b*D0*t)**(1/b)
		"""
		return self.y0/(1+self.exponent*self.base(x))**(1/self.exponent)

	def ycum(self,x:numpy.ndarray):
		"""
		Np = q0 / ((1-b)*D0)*(1-(1+b*D0*t)**(1-1/b))
		"""
		return (self.y0/self.D0)/(1-self.exponent)*(1-(1+self.exponent*self.base(x))**(1-1/self.exponent))

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray):
		"""Optimization based on hyperbolic decline model."""

		x,yobs = x[yobs!=0],yobs[yobs!=0]

		try:
			LinregressResult = linregress(x,numpy.power(1/yobs,self.exponent))
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
			return 0.,0.,None

		y0 = LinregressResult.intercept**(-1/self.exponent)
		D0 = LinregressResult.slope/LinregressResult.intercept/self.exponent

		return y0,D0,LinregressResult