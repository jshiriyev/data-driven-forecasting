import numpy

from scipy.optimize import curve_fit

from ._base import BaseClass

class Harmonic(BaseClass):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	@staticmethod
	def rate(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		q = q0 / (1+Di*t)
		"""
		return yi/(1+Di*(numpy.asarray(x)-xi))

	@staticmethod
	def cumulative(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		Np = q0 / Di * ln(1+Di*t)
		"""
		return (yi/Di)*numpy.log(1+Di*(numpy.asarray(x)-xi))

	@staticmethod
	def inverse(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,**kwargs):
		"""Returns harmonic regression results after linearization."""

		x,y = BaseClass.shift(numpy.asarray(x),numpy.asarray(y),xi)
		x,y = BaseClass.nzero(x,y)

		linear = BaseClass.linregr(x,1./y)

		linfit = linear.slope/linear.intercept,1/linear.intercept

		result = curve_fit(BaseClass.runhar,x,y,p0=linfit)

		R2 = BaseClass.rsquared(BaseClass.runhar(x,*result[0]),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(1.,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))

