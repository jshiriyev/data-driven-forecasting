import numpy

from scipy.optimize import curve_fit

from ._base import BaseClass

class Hyperbolic(BaseClass):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	@staticmethod
	def rate(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,b:float=0.5):
		"""
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		return yi/(1+b*Di*(numpy.asarray(x)-xi))**(1./b)

	@staticmethod
	def cumulative(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,b:float=0.5):
		"""
		Np = q0 / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))
		"""
		return (yi/Di)/(1-b)*(1-(1+b*Di*(numpy.asarray(x)-xi))**(1-1./b))
	
	@staticmethod
	def inverse(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,b:float=0.5):
		"""Returns hyperbolic regression results after linearization."""

		x,y = BaseClass.shift(numpy.asarray(x),numpy.asarray(y),xi)
		x,y = BaseClass.nzero(x,y)

		linear = BaseClass.linregr(x,numpy.power(1/y,b))

		linfit = linear.slope/linear.intercept/b,linear.intercept**(-1/b)

		result = curve_fit(lambda x,Di,yi: BaseClass.runhyp(x,Di,yi,b=b),x,y,p0=linfit)

		R2 = BaseClass.rsquared(BaseClass.runhyp(x,*result[0],b=b),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(b,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))
