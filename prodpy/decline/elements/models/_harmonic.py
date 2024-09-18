import numpy

from ._baseclass import BaseClass

class Harmonic(BaseClass):
	"""Harmonic Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Harmonic,self).__init__(*args,**kwargs)

		self._exponent = 100.

	def rates(self,days:numpy.ndarray):
		"""
		q = q0 / (1+d0*t)
		"""
		return self.rate0/(1+self.base(days))

	def cums(self,days:numpy.ndarray):
		"""
		Np = q0 / d0 * ln(1+d0*t)
		"""
		return self.volume0*numpy.log(1+self.base(days))

	def inverse(self,days:numpy.ndarray,rates:numpy.ndarray):
		"""Optimization based on harmonic decline model."""

		days,rates = days[rates!=0],rates[rates!=0]

		try:
			LinregressResult = linregress(days,1/rates)
		except ValueError:
			return 0.,0.,None

		rate0 = LinregressResult.intercept**(-1)

		decline0 = LinregressResult.slope/LinregressResult.intercept

		return rate0,decline0,LinregressResult