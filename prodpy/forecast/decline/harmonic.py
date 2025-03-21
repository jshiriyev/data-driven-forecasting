import numpy

from scipy.optimize import curve_fit

from ._base import BaseClass

class Harmonic(BaseClass):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	@staticmethod
	def rate(x:numpy.ndarray,Di:float,yi:float,*args,xi:float=0.,**kwargs):
		"""
		q = q0 / (1+Di*t)
		"""
		return yi/(1+Di*(numpy.asarray(x)-xi))

	@staticmethod
	def cum(x:numpy.ndarray,Di:float,yi:float,*args,xi:float=0.,**kwargs):
		"""
		Np = q0 / Di * ln(1+Di*t)
		"""
		return (yi/Di)*numpy.log(1+Di*(numpy.asarray(x)-xi))

	@staticmethod
	def transform(y,*args):

		return 1./y

	@staticmethod
	def inverse(linear):

		return linear.slope/linear.intercept,1/linear.intercept

	def fit(self,x:numpy.ndarray,y:numpy.ndarray,*args,xi:float=0.):
		"""Returns harmonic regression results after linearization."""

		linear = Arps.linregr(x,1./y)

		p0 = self.inverse(linear)

		result = curve_fit(Arps.runhar,x,y,p0=p0)

		R2 = Arps.rsquared(Arps.runhar(x,*result[0]),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(1.,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))

