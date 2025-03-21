import numpy

from scipy.optimize import curve_fit

from ._base import BaseClass

class Hyperbolic(BaseClass):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	@staticmethod
	def rate(x:numpy.ndarray,Di:float,yi:float,b:float,*,xi:float=0.):
		"""
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		return yi/(1+b*Di*(numpy.asarray(x)-xi))**(1./b)

	@staticmethod
	def cum(x:numpy.ndarray,Di:float,yi:float,b:float,*,xi:float=0.):
		"""
		Np = q0 / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))
		"""
		return (yi/Di)/(1-b)*(1-(1+b*Di*(numpy.asarray(x)-xi))**(1-1./b))

	@staticmethod
	def transform(y,b):

		return numpy.power(1/y,b)

	@staticmethod
	def inverse(linear,b):

		return linear.slope/linear.intercept/b,linear.intercept**(-1/b)
	
	def fit(self,x:numpy.ndarray,y:numpy.ndarray,b:float,*,xi:float=0.):
		"""Returns hyperbolic regression results after linearization."""

		linear = Arps.linregr(x,numpy.power(1/y,b))

		p0 = self.inverse(linear,b)

		result = curve_fit(lambda x,Di,yi: Arps.runhyp(x,Di,yi,b=b),x,y,p0=p0)

		R2 = Arps.rsquared(Arps.runhyp(x,*result[0],b=b),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(b,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))
