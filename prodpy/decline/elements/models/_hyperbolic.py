import numpy

from ._baseclass import BaseClass

class Hyperbolic(BaseClass):
	"""Hyperbolic Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Hyperbolic,self).__init__(*args,**kwargs)
	
	def rates(self,days:numpy.ndarray):
		"""
		q = q0 / (1+b*d0*t)**(1/b)
		"""
		return self.rate0/(1+self.fraction*self.base(days))**(1/self.fraction)

	def cums(self,days:numpy.ndarray):
		"""
		Np = q0 / ((1-b)*d0)*(1-(1+b*d0*t)**(1-1/b))
		"""
		return self.volume0/(1-self.fraction)*(1-(1+self.fraction*self.base(days))**(1-1/self.fraction))

	def inverse(self,days:numpy.ndarray,rates:numpy.ndarray):
		"""Optimization based on hyperbolic decline model."""

		exponent = self.exponent/100.

		days,rates = days[rates!=0],rates[rates!=0]

		try:
			LinregressResult = linregress(days,numpy.power(1/rates,exponent))
		except ValueError:
			return 0.,0.,None

		rate0 = LinregressResult.intercept**(-1/exponent)

		decline0 = LinregressResult.slope/LinregressResult.intercept/exponent

		return rate0,decline0,LinregressResult