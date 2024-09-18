import numpy

from ._generic import GenModel

class Exponential(GenModel):
	"""Exponential Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Exponential,self).__init__(*args,**kwargs)

		self._exponent = 0.

	def rates(self,days:numpy.ndarray):
		"""
		q = q0 * exp(-d0*t)
		"""
		return self.rate0*numpy.exp(-self.base(days))

	def cums(self,days:numpy.ndarray):
		"""
		Np = q0 / d0 * (1-exp(-d0*t))
		"""
		return self.volume0*(1-numpy.exp(-self.base(days)))

	def inverse(self,days:numpy.ndarray,rates:numpy.ndarray):
		"""Optimization based on exponential decline model."""

		days,rates = days[rates!=0],rates[rates!=0]

		try:
			LinregressResult = linregress(days,numpy.log(rates))
		except ValueError:
			return 0.,0.,None

		rate0 = numpy.exp(LinregressResult.intercept)

		decline0 = -LinregressResult.slope

		return rate0,decline0,LinregressResult