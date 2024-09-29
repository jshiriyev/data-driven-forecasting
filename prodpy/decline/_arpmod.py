import logging

import numpy

from scipy._lib._bunch import _make_tuple_bunch

from scipy.stats import linregress
from scipy.stats import norm

Result = _make_tuple_bunch('Result',
	['b','Di','yi','xi','n','R2','Di_error','yi_error','linear'])

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

	def option(self,mode:str=None,b:float=None):
		"""Returns mode and exponent based on their values."""
		if mode is None and b is None:
			return 'Exponential',0

		if mode is None and b is not None:
			return self.get_mode(float(b)),float(b)

		if mode is not None and b is None:
			return mode,self.get_b(mode)

		return self.option(mode=None,b=b)

	def frw(self,Di:float,yi:float,x:numpy.ndarray,xi:float=0.):
		"""Returns the result of forward calculations."""
		inp = (Di,yi,x,xi) if self.b==0. or self.b==1. else (Di,yi,x,xi,self.b)
		return getattr(self,f"frw{self.mode}")(*inp)

	@staticmethod
	def frwexp(Di:float,yi:float,x:numpy.ndarray,xi:float=0.):
		"""
		q = qi * exp(-Di*t)
		"""
		return yi*numpy.exp(-Di*(numpy.asarray(x)-xi))

	@staticmethod
	def frwhyp(Di:float,yi:float,x:numpy.ndarray,xi:float=0.,b:float=0.5):
		"""
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		return yi/(1+b*Di*(numpy.asarray(x)-xi))**(1./b)

	@staticmethod
	def frwhar(Di:float,yi:float,x:numpy.ndarray,xi:float=0.):
		"""
		q = q0 / (1+Di*t)
		"""
		return yi/(1+Di*(numpy.asarray(x)-xi))

	def cum(self,Di:float,yi:float,x:numpy.ndarray,xi:float=0.):
		"""Returns the result of cumulative calculations."""
		inp = (Di,yi,x,xi) if self.b==0. or self.b==1. else (Di,yi,x,xi,self.b)
		return getattr(self,f"cum{self.mode}")(*inp)

	@staticmethod
	def cumexp(Di:float,yi:float,x:numpy.ndarray,xi:float=0.):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (yi/Di)*(1-numpy.exp(-Di*(numpy.asarray(x)-xi)))

	@staticmethod
	def cumhyp(Di:float,yi:float,x:numpy.ndarray,xi:float=0.,b:float=0.5):
		"""
		Np = q0 / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))
		"""
		return (yi/Di)/(1-b)*(1-(1+b*Di*(numpy.asarray(x)-xi))**(1-1./b))

	@staticmethod
	def cumhar(Di:float,yi:float,x:numpy.ndarray,xi:float=0.):
		"""
		Np = q0 / Di * ln(1+Di*t)
		"""
		return (yi/Di)*numpy.log(1+Di*(numpy.asarray(x)-xi))

	def inv(self,x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""
		inp = (x,y,xi) if self.b==0. or self.b==1. else (x,y,xi,self.b)
		return getattr(self,f"inv{self.mode}")(*inp)

	@staticmethod
	def invexp(x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns exponential regression results after linearization."""

		x,y = Arps.shift(x,y,xi)
		x,y = Arps.nzero(x,y)

		n,df = x.size,x.size-2

		linear = Arps.regress(x,numpy.log(y))

		Sxx = numpy.nansum((x-np.nanmean(x))**2)

		Di,yi = -linear.slope,numpy.exp(linear.intercept)

		ycal = Arps.frwexp(Di,yi,x)

		R2 = Arps.rsquared(ycal,y)

		s2 = numpy.sum((ycal-y)**2)/df

		Di_error = numpy.sqrt(s2/Sxx)
		yi_error = numpy.sqrt(s2/n/Sxx*numpy.nansum(x**2))

		return Result(0.,Di,yi,xi,n,R2,Di_error,yi_error,linear)

	@staticmethod
	def invhyp(x:numpy.ndarray,y:numpy.ndarray,xi:float=None,b:float=0.5):
		"""Returns hyperbolic regression results after linearization."""

		x,y = Arps.shift(x,y,xi)
		x,y = Arps.nzero(x,y)

		n,df = x.size,x.size-2

		linear = Arps.regress(x,numpy.power(1/y,b))

		Sxx = numpy.nansum((x-np.nanmean(x))**2)

		Di,yi = linear.slope/linear.intercept/b,linear.intercept**(-1/b)

		ycal = Arps.frwhyp(Di,yi,x,b=b)

		R2 = Arps.rsquared(ycal,y)

		s2 = numpy.sum((ycal-y)**2)/df

		R2 = Hyperbolic(*params,self.b).rsquared(x,yobs)

		Di_error = numpy.sqrt(s2/Sxx)
		yi_error = numpy.sqrt(s2/n/Sxx*numpy.nansum(x**2))

		return Result(b,Di,yi,xi,n,R2,Di_error,yi_error,linear)

	@staticmethod
	def invhar(x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns harmonic regression results after linearization."""

		x,y = Arps.shift(x,y,xi)
		x,y = Arps.nzero(x,y)

		n,df = x.size,x.size-2

		linear = Arps.regress(x,1./y)

		Sxx = numpy.nansum((x-np.nanmean(x))**2)

		Di,yi = linear.slope/linear.intercept,1/linear.intercept

		ycal = Arps.frwhar(Di,yi,x)

		R2 = Arps.rsquared(ycal,y)

		s2 = numpy.sum((ycal-y)**2)/df

		Di_error = numpy.sqrt(s2/Sxx)
		yi_error = numpy.sqrt(s2/n/Sxx*numpy.nansum(x**2))

		return Result(1.,Di,yi,xi,n,R2,Di_error,yi_error,linear)

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
	def regress(x:numpy.ndarray,y:numpy.ndarray,**kwargs):
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
	def model(result:Result,perc:float=0.5):
		"""perc -> percentile, perc=0.5 gives mean values"""

		Di = result.Di+tstat.ppf(prc,result.df)*result.Di_error
		yi = result.yi+tstat.ppf(prc,result.df)*result.yi_error

		return Di,yi

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	x = numpy.linspace(0,500,5000)

	y1 = Arps(0).frw(0.005,3,x,xi=50)
	y2 = Arps(0.5).frw(0.005,3,x,xi=50)
	y3 = Arps(1).frw(0.005,3,x,xi=50)

	# c1 = Arps(0).cum(0.005,3,x)
	# c2 = Arps(0.5).cum(0.005,3,x)
	# c3 = Arps(1).cum(0.005,3,x)

	plt.plot(x,y1,label='Exponential')
	plt.plot(x,y2,label='Hyperbolic')
	plt.plot(x,y3,label='Harmonic')

	plt.legend()

	plt.show()