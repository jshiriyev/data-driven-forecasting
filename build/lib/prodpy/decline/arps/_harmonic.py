import numpy

from ._genmod import GenModel,NonLinResult,Result

class Harmonic(GenModel):
	"""Harmonic Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Harmonic,self).__init__(*args,**kwargs)

		self._expo = 1.

	def ycal(self,x:numpy.ndarray):
		"""
		q = q0 / (1+Di*t)
		"""
		return self.yi/(1+self.base(x))

	def ycum(self,x:numpy.ndarray):
		"""
		Np = q0 / Di * ln(1+Di*t)
		"""
		return (self.yi/self.Di)*numpy.log(1+self.base(x))

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=0.):
		"""Returns regression results after linearization."""

		x,yobs = self.xshift(x,yobs,xi)
		x,yobs = x[yobs!=0],yobs[yobs!=0]

		linear = super().regress(x,1/yobs)

		params = (0,0) if linear is None else self.inverse(linear.slope,linear.intercept)

		R2 = Harmonic(*params).rsquared(x,yobs)

		nonlinear = NonLinResult(*params,R2)

		return Result(linear,nonlinear)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns an exponential model that fits observation values."""
		result = self.regress(x,yobs,xi).nonlinear
		
		return Harmonic(result.decline,result.intercept)

	def inverse(self,m,b):

		return (m/b,b**(-1))