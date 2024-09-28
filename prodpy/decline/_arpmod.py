import logging

import numpy

from scipy._lib._bunch import _make_tuple_bunch

from scipy.stats import linregress
from scipy.stats import norm

Result = _make_tuple_bunch('Result',
	['Di','yi','b','rsquared','Di_stderr','yi_stderr','linear'])

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
		return self.getmode(self.b).lower()[:3]

	def option(self,mode:str=None,b:float=None):
		"""Returns mode and exponent based on their values."""
		if mode is None and b is None:
			return 'Exponential',0

		if mode is None and b is not None:
			return self.getmode(float(b)),float(b)

		if mode is not None and b is None:
			return mode,self.getb(mode)

		return self.option(mode=None,b=b)

	def frw(self,Di:float,yi:float,x:numpy.ndarray):
		"""Returns the result of forward calculations:
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		if self.b==0. or self.b==1.:
			return getattr(self,f"frw{self.mode}")(Di,yi,x)

		return getattr(self,f"frw{self.mode}")(self.b,Di,yi,x)

	@staticmethod
	def frwexp(Di:float,yi:float,x:numpy.ndarray):
		"""
		q = qi * exp(-Di*t)
		"""
		return yi*numpy.exp(-Di*numpy.asarray(x))

	@staticmethod
	def frwhyp(b:float,Di:float,yi:float,x:numpy.ndarray):
		"""
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		return yi/(1+b*Di*numpy.asarray(x))**(1./b)

	@staticmethod
	def frwhar(Di:float,yi:float,x:numpy.ndarray):
		"""
		q = q0 / (1+Di*t)
		"""
		return yi/(1+Di*numpy.asarray(x))

	def cum(self,Di:float,yi:float,x:numpy.ndarray):
		"""Returns the result of cumulative calculations."""
		if self.b==0. or self.b==1.:
			return getattr(self,f"cum{self.mode}")(Di,yi,x)

		return getattr(self,f"cum{self.mode}")(self.b,Di,yi,x)

	@staticmethod
	def cumexp(Di:float,yi:float,x:numpy.ndarray):
		"""
		Np = qi / Di * (1-exp(-Di*t))
		"""
		return (yi/Di)*(1-numpy.exp(-Di*numpy.asarray(x)))

	@staticmethod
	def cumhyp(b:float,Di:float,yi:float,x:numpy.ndarray):
		"""
		Np = q0 / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))
		"""
		return (yi/Di)/(1-b)*(1-(1+b*Di*numpy.asarray(x))**(1-1./b))

	@staticmethod
	def cumhar(Di:float,yi:float,x:numpy.ndarray):
		"""
		Np = q0 / Di * ln(1+Di*t)
		"""
		return (yi/Di)*numpy.log(1+Di*numpy.asarray(x))

	def inv(self,x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns the result of inverse calculations."""
		if self.b==0. or self.b==1.:
			return getattr(self,f"inv{self.mode}")(x,y,xi)

		return getattr(self,f"inv{self.mode}")(self.b,x,y,xi)

	@staticmethod
	def invexp(x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""

		x,yobs = self.shift(x,yobs,xi)

		linear = super().regress(x,numpy.log(yobs))

		params = (0.,0.) if linear is None else self.inverse(linear)
		
		R2 = Exponential(*params).rsquared(x,yobs)

		nonlinear = NonLinRegrResult(*params,R2)

		# def inverse()
		# return (-m,numpy.exp(b))

		return Result(linear,nonlinear)

	@staticmethod
	def invhyp(b:float,x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""

		x,yobs = self.shift(x,yobs,xi)

		linear = super().regress(x,numpy.power(1/yobs,self.b))

		params = (0,0) if linear is None else self.inverse(linear)

		R2 = Hyperbolic(*params,self.b).rsquared(x,yobs)

		nonlinear = NonLinRegrResult(*params,R2)

		# def inverse(self,linear,pct:float=50.):
		# return (m/b/self.b, b**(-1/self.b))

		return Result(linear,nonlinear)

	@staticmethod
	def invhar(x:numpy.ndarray,y:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""

		x,yobs = self.shift(x,yobs,xi)

		linear = super().regress(x,1/yobs)

		params = (0,0) if linear is None else self.inverse(linear)

		R2 = Harmonic(*params).rsquared(x,yobs)

		nonlinear = NonLinRegrResult(*params,R2)

		# def inverse()
		# return (m/b,b**(-1))

		return Result(linear,nonlinear)

	@staticmethod
	def getmode(b:float):
		"""Returns mode based on the exponent value."""
		if b == 0.:
			return "Exponential"

		if b == 1.:
			return "Harmonic"

		return "Hyperbolic"

	@staticmethod
	def getb(mode:str):
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
			result = linregress(x,y,**kwargs)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
		else:
			return result

	@staticmethod
	def rsquared(ycal:numpy.ndarray,yobs:numpy.ndarray):
		"""Returns R-squared value."""

		ssres = numpy.nansum((yobs-ycal)**2)
		sstot = numpy.nansum((yobs-numpy.nanmean(yobs))**2)

		return 1-ssres/sstot

	@staticmethod
	def percentile(mean:float,variance:float,perc:float=0.5):
		"""perc -> percentile, perc=0.5 gives mean values"""
		return mean+norm.ppf(perc)*numpy.sqrt(variance)

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	x = numpy.linspace(0,500,5000)

	y1 = Arps(0).frw(0.005,3,x)
	y2 = Arps(0.5).frw(0.005,3,x)
	y3 = Arps(1).frw(0.005,3,x)

	c1 = Arps(0).cum(0.005,3,x)
	c2 = Arps(0.5).cum(0.005,3,x)
	c3 = Arps(1).cum(0.005,3,x)

	plt.semilogy(c1,y1,label='Exponential')
	plt.semilogy(c2,y2,label='Hyperbolic')
	plt.semilogy(c3,y3,label='Harmonic')

	plt.legend()

	plt.show()