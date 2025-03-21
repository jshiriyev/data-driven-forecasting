import numpy

from scipy.optimize import curve_fit

from ._base import BaseClass

class Exponential(BaseClass):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	@staticmethod
	def rate(x:numpy.ndarray,Di:float,yi:float,*args,xi:float=0.,**kwargs):
		"""
		q = qi * exp(-Di*t)
		"""
		return yi*numpy.exp(-Di*(numpy.asarray(x)-xi))

	@staticmethod
	def cum(x:numpy.ndarray,Di:float,yi:float,*args,xi:float=0.,**kwargs):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (yi/Di)*(1-numpy.exp(-Di*(numpy.asarray(x)-xi)))

	@staticmethod
	def transform(y,*args):

		return numpy.log(y)

	@staticmethod
	def inverse(linear,*args):

		return -linear.slope,numpy.exp(linear.intercept)

	def fit(self,x:numpy.ndarray,y:numpy.ndarray,*args,xi:float=0.,cum:bool=False):
		"""Returns exponential regression results after linearization."""

		x,y = super().fit(x,y,*args,xi=xi)

		linear = self.linregr(x,numpy.log(y))

		p0 = self.inverse(linear)

		forward = getattr(self,"cum" if cum else "rate")

		result = curve_fit(forward,x,y,p0=p0)

		R2 = self.rsquared(forward(x,*result[0]),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(0.,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),
			linear=LinregressResult(**linear),
			)
