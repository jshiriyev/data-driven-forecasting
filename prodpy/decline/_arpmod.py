import logging

import numpy

from scipy._lib._bunch import _make_tuple_bunch

from scipy.optimize import curve_fit

from scipy.stats import linregress
from scipy.stats import norm
from scipy.stats import t as tstat

Result = _make_tuple_bunch('Result',
	['b','Di','yi','xi','n','R2','Di_error','yi_error'],
	extra_field_names=['linear'])

LinregressResult = _make_tuple_bunch('LinregressResult',
	['slope','intercept','rvalue','pvalue','stderr'],
	extra_field_names=['intercept_stderr'])

class Arps:
	"""Class for Arp's decline models: Exponential, 
	Hyperbolic, and Harmonic; main decline attributes are:
	
	Di 		: initial decline rate
	yi 		: initial y value

	The decline exponent defines the mode:
	
	b 		: Arps' decline-curve exponent

	b = 0. 		-> mode = 'Exponential'
	0 < b < 1.	-> mode = 'Hyperbolic'
	b = 1.		-> mode = 'Harmonic'

	"""

	modes = 'Exponential','Hyperbolic','Harmonic'

	def __init__(self,b=0.):

		self._b = b

	@property
	def b(self):
		return self._b

	@property
	def mode(self):
		return self.get_mode(self.b).lower()[:3]

	def run(self,x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.):
		"""Returns the result of forward calculations."""
		return getattr(self,f"run{self.mode}")(x,Di,yi,xi=xi,b=self.b)

	@staticmethod
	def runexp(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		q = qi * exp(-Di*t)
		"""
		return yi*numpy.exp(-Di*(numpy.asarray(x)-xi))

	@staticmethod
	def runhyp(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,b:float=0.5):
		"""
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		return yi/(1+b*Di*(numpy.asarray(x)-xi))**(1./b)

	@staticmethod
	def runhar(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		q = q0 / (1+Di*t)
		"""
		return yi/(1+Di*(numpy.asarray(x)-xi))

	def cum(self,x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.):
		"""Returns the result of cumulative calculations."""
		return getattr(self,f"cum{self.mode}")(x,Di,yi,xi=xi,b=self.b)

	@staticmethod
	def cumexp(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (yi/Di)*(1-numpy.exp(-Di*(numpy.asarray(x)-xi)))

	@staticmethod
	def cumhyp(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,b:float=0.5):
		"""
		Np = q0 / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))
		"""
		return (yi/Di)/(1-b)*(1-(1+b*Di*(numpy.asarray(x)-xi))**(1-1./b))

	@staticmethod
	def cumhar(x:numpy.ndarray,Di:float,yi:float,*,xi:float=0.,**kwargs):
		"""
		Np = q0 / Di * ln(1+Di*t)
		"""
		return (yi/Di)*numpy.log(1+Di*(numpy.asarray(x)-xi))

	def inv(self,x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.):
		"""Returns regression results after linearization."""
		return getattr(self,f"inv{self.mode}")(x,y,xi=xi,b=self.b)

	@staticmethod
	def invexp(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,**kwargs):
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

	@staticmethod
	def invhyp(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,b:float=0.5):
		"""Returns hyperbolic regression results after linearization."""

		x,y = Arps.shift(numpy.asarray(x),numpy.asarray(y),xi)
		x,y = Arps.nzero(x,y)

		linear = Arps.linregr(x,numpy.power(1/y,b))

		linfit = linear.slope/linear.intercept/b,linear.intercept**(-1/b)

		result = curve_fit(lambda x,Di,yi: Arps.runhyp(x,Di,yi,b=b),x,y,p0=linfit)

		R2 = Arps.rsquared(Arps.runhyp(x,*result[0],b=b),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(b,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))

	@staticmethod
	def invhar(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,**kwargs):
		"""Returns harmonic regression results after linearization."""

		x,y = Arps.shift(numpy.asarray(x),numpy.asarray(y),xi)
		x,y = Arps.nzero(x,y)

		linear = Arps.linregr(x,1./y)

		linfit = linear.slope/linear.intercept,1/linear.intercept

		result = curve_fit(Arps.runhar,x,y,p0=linfit)

		R2 = Arps.rsquared(Arps.runhar(x,*result[0]),y).tolist()

		perror = numpy.sqrt(numpy.diag(result[1]))

		linear = {k: v.tolist() for k, v in linear._asdict().items()}

		return Result(1.,*result[0].tolist(),xi,x.size,R2,*perror.tolist(),linear=LinregressResult(**linear))

	@staticmethod
	def get_option(mode:str=None,b:float=None):
		"""Returns mode and exponent based on their values."""
		if mode is None and b is None:
			return 'Exponential',0

		if mode is None and b is not None:
			return Arps.get_mode(float(b)),float(b)

		if mode is not None and b is None:
			return mode,Arps.get_b(mode)

		return Arps.get_option(mode=None,b=b)

	@staticmethod
	def get_mode(b:float):
		"""Returns mode based on the exponent value."""
		if b == 0.:
			return "Exponential"

		if b == 1.:
			return "Harmonic"

		return "Hyperbolic"

	@staticmethod
	def get_b(mode:str):
		"""Returns exponent based on the mode."""
		if mode.lower() in ('exponential','exp'):
			return 0.

		if mode.lower() in ('hyperbolic','hyp'):
			return 0.5

		if mode.lower() in ('harmonic','har'):
			return 1.

		logging.error("Error occurred: %s", "Available modes are Exponential, Hyperbolic, and Harmonic.")

	@staticmethod
	def shift(x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns shifted x data to get the yi at xi."""
		return (x, y) if xi is None else (x[x>=xi]-xi, y[x>=xi])

	@staticmethod
	def nzero(x:numpy.ndarray,y:numpy.ndarray):
		"""Returns the nonzero entries of y for x and y."""
		return (x[~numpy.isnan(y) & (y!=0)],y[~numpy.isnan(y) & (y!=0)])

	@staticmethod
	def linregr(x:numpy.ndarray,y:numpy.ndarray,**kwargs):
		"""Linear regression of x and y values."""

		try:
			linear = linregress(x,y,**kwargs)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
		else:
			return linear

	@staticmethod
	def rsquared(ycal:numpy.ndarray,yobs:numpy.ndarray):
		"""Returns R-squared value."""

		ssres = numpy.nansum((yobs-ycal)**2)
		sstot = numpy.nansum((yobs-numpy.nanmean(yobs))**2)

		return 1-ssres/sstot

	@staticmethod
	def model(result:Result,prc:float=50.):
		"""prc -> prcentile, prc=0.5 gives mean values"""

		Di = result.Di+tstat.ppf(prc/100.,result.n-2)*result.Di_error
		yi = result.yi-tstat.ppf(prc/100.,result.n-2)*result.yi_error

		return Di,yi

	@staticmethod
	def reader(result:Result):

		string = f"\nDecline mode is {Arps.get_mode(result.b)} and the exponent is {result.b}.\n\n"

		string += f"Linear regression R-squared is {result.linear.rvalue**2:.5f}\n"
		string += f"Non-linear curve fit R-squared is {result.R2:.5f}\n\n"

		string += f"Initial x is {result.xi:.1f}\n"
		string += f"Initial y is {result.yi:.1f}\n"
		string += f"Initial decline rate percentage is {result.Di*100:.1f}%\n\n"

		return string

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15.]
	y = [1000,963,927,897,852,826,792,750,727,693,659,646,618,588,567,541]

	plt.scatter(x,y)

	b = 1.

	result = Arps(b).inv(x,y)

	print(Arps.reader(result))

	p10 = Arps.model(result,prc=10.)
	p50 = Arps.model(result,prc=50.)
	p90 = Arps.model(result,prc=90.)

	fit10 = Arps(b).run(x,*p10)
	fit50 = Arps(b).run(x,*p50)
	fit90 = Arps(b).run(x,*p90)

	plt.style.use('_mpl-gallery')

	# plt.plot(x,fit10,label='p10')
	plt.plot(x,fit50,label='p50',color='k')
	plt.fill_between(x,fit10,fit90,color='b',alpha=.2,linewidth=0)
	# plt.plot(x,fit90,label='p90')
	
	# plt.legend()

	plt.show()