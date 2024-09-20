import numpy

from scipy.stats import norm

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

	def preproc(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):

		x,yobs = super().preproc(x,yobs,xi)
		x,yobs = x[yobs!=0],yobs[yobs!=0]

		return (x,yobs)

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""

		x,yobs = self.preproc(x,yobs,xi)

		linear = super().regress(x,numpy.log(yobs))

		params = (0.,0.) if linear is None else self.inverse(linear)
		
		R2 = Exponential(*params).rsquared(x,yobs)

		nonlinear = NonLinResult(*params,R2)

		return Result(linear,nonlinear)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None,pct:float=50.):
		"""Returns an exponential model that fits observation values."""

		x,yobs = self.preproc(x,yobs,xi)

		linear = super().regress(x,numpy.log(yobs))

		params = (0.,0.) if linear is None else self.inverse(linear,pct)
		
		return Exponential(*params)

	def inverse(self,linear,pct:float=50.):

		# m,b = self.__statistics(linear.slope,linear.intercept)
		# t,v = self.__statistics(linear.stderr,linear.intercept_stderr)

		m = linear.slope+norm.ppf(pct/100.)*linear.stderr*numpy.sqrt(148)
		b = linear.intercept+norm.ppf(pct/100.)*linear.intercept_stderr*numpy.sqrt(148)

		return (-m,numpy.exp(b))

	def __statistics(self,m,b):

		return (-m,numpy.exp(b))








