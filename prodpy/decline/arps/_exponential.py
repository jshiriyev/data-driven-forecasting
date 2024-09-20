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

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""

		x,yobs = self.xshift(x,yobs,xi)
		x,yobs = x[yobs!=0],yobs[yobs!=0]

		linear = super().regress(x,numpy.log(yobs))

		params = (0.,0.) if linear is None else self.inverse(linear.slope,linear.intercept)
		
		R2 = Exponential(*params).rsquared(x,yobs)

		nonlinear = NonLinResult(*params,R2)

		return Result(linear,nonlinear)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns an exponential model that fits observation values."""
		result = self.regress(x,yobs,xi).nonlinear

		return Exponential(result.decline,result.intercept)

	def inverse(self,m,b):

		return (-m,numpy.exp(b))