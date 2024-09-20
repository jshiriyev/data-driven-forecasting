import logging

import numpy

from scipy._lib._bunch import _make_tuple_bunch

from ._genmod import GenModel

NonLinResult = _make_tuple_bunch('NonLinResult',
	['decline','intercept','rvalue'])

# LinregressResult = _make_tuple_bunch('LinregressResult',
# 	['slope','intercept','rvalue','pvalue','stderr'],
# 	extra_field_names=['intercept_stderr'])

class Exponential(GenModel):
	"""Exponential Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Exponential,self).__init__(*args,**kwargs)

		self._xp = 0.

	def y(self,x:numpy.ndarray):
		"""
		q = qi * exp(-Di*t)
		"""
		return self.yi*numpy.exp(-self.base(x))

	def ycum(self,x:numpy.ndarray):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (self.yi/self.Di)*(1-numpy.exp(-self.base(x)))

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray,x0:float=None):

		return self.__invert(x,yobs,x0)[:2]

	@classmethod
	def model(cls,x:numpy.ndarray,yobs:numpy.ndarray,x0:float=None):
		"""Returns an exponential model that fits observation values."""

		yi,Di,linear = self.__invert(x,yobs,x0)

		nonlinear = 

		return cls(yi=yi,Di=Di,expo=0.)

	def regress(self,xobs:numpy.ndarray,yobs:numpy.ndarray,x0:float=0.):

		xobs,yobs = xobs[yobs!=0],yobs[yobs!=0]

		linear = super().regress(xobs-x0,numpy.log(yobs))

		if linear is None:
			return Score(None,None)

		yi = numpy.exp(linear.intercept)
		Di = -linear.slope
		R2 = Exponential(yi,Di).rvalue(xobs-x0,yobs)

		nonlinear = NonLinResult(yi,Di,R2)

		return Score(linear,nonlinear)
