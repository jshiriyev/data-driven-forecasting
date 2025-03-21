import numpy

from scipy.optimize import curve_fit

from ._base import BaseClass

class Exponential(BaseClass):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	@staticmethod
	def rate(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		q = qi * exp(-Di*t)
		"""
		return yi*numpy.exp(-Di*(numpy.asarray(x)-xi))

	@staticmethod
	def cumulative(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (yi/Di)*(1-numpy.exp(-Di*(numpy.asarray(x)-xi)))

	def fit(self):

		return 

	@staticmethod
	def inverse(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,**kwargs):
		"""Returns exponential regression results after linearization."""

		x,y = Arps.shift(numpy.asarray(x),numpy.asarray(y),xi)
		x,y = Arps.nzero(x,y)

		linear = Arps.linregr(x,numpy.log(y))

		linfit = -linear.slope,numpy.exp(linear.intercept)

		result = curve_fit(Arps.runexp,x,y,p0=linfit)

		R2 = Arps.rsquared(Arps.runexp(x,*result[0]),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(0.,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))