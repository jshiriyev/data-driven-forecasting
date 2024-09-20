import numpy

from scipy.stats import norm

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

	def preproc(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):

		x,yobs = super().preproc(x,yobs,xi)
		x,yobs = x[yobs!=0],yobs[yobs!=0]

		return (x,yobs)

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=0.):
		"""Returns regression results after linearization."""

		x,yobs = self.preproc(x,yobs,xi)

		linear = super().regress(x,1/yobs)

		params = (0,0) if linear is None else self.inverse(linear)

		R2 = Harmonic(*params).rsquared(x,yobs)

		nonlinear = NonLinResult(*params,R2)

		return Result(linear,nonlinear)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None,pct:float=50.):
		"""Returns an exponential model that fits observation values."""
		x,yobs = self.preproc(x,yobs,xi)

		linear = super().regress(x,1/yobs)

		params = (0.,0.) if linear is None else self.inverse(linear,pct)
		
		return Harmonic(*params)

	def inverse(self,linear,pct:float=50.):

		m = linear.slope+norm.ppf(pct/100.)*linear.stderr
		b = linear.intercept+norm.ppf(pct/100.)*linear.intercept_stderr

		return (m/b,b**(-1))