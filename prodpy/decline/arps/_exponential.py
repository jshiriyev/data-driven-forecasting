import logging

import numpy

from ._genmod import GenModel,NonLinResult,Result

class Exponential(GenModel):
	"""Exponential Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Exponential,self).__init__(*args,**kwargs)

		self._xp = 0.

	def ycal(self,x:numpy.ndarray):
		"""
		q = qi * exp(-Di*t)
		"""
		return self.yi*numpy.exp(-self.base(x))

	def ycum(self,x:numpy.ndarray):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (self.yi/self.Di)*(1-numpy.exp(-self.base(x)))

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=0.):

		xobs,yobs = x[x>=xi]-xi,yobs[x>=xi]
		xobs,yobs = xobs[yobs!=0],yobs[yobs!=0]

		linear = super().regress(xobs,numpy.log(yobs))

		if linear is None:
			return Result(None,None)

		Di = -linear.slope
		yi = numpy.exp(linear.intercept)
		R2 = Exponential(Di,yi).rvalue(xobs,yobs)

		nonlinear = NonLinResult(Di,yi,R2)

		return Result(linear,nonlinear)

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):

		return self.regress(x,yobs,xi).nonlinear

	@classmethod
	def model(cls,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns an exponential model that fits observation values."""
		nonlinear = self.params(x,yobs,xi)
		return cls(nonlinear.decline,nonlinear.intercept)
