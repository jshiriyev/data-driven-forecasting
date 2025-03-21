import logging

import numpy

from scipy._lib._bunch import _make_tuple_bunch

from scipy.stats import linregress
from scipy.stats import t as tstat

Result = _make_tuple_bunch('Result',
	['b','Di','yi','xi','n','R2','Di_error','yi_error'],
	extra_field_names=['linear'])

LinregressResult = _make_tuple_bunch('LinregressResult',
	['slope','intercept','rvalue','pvalue','stderr'],
	extra_field_names=['intercept_stderr'])

class BaseClass():
	"""Base class for Arp's decline models: Exponential, Hyperbolic, and Harmonic.

	Attributes:
	----------
	Di (float)	: initial decline rate
	yi (float)	: initial y value

	The decline exponent defines the mode:
	
	b (float)	: Arps' decline-curve exponent

	b = 0. 		-> mode = 'Exponential'
	0 < b < 1.	-> mode = 'Hyperbolic'
	b = 1.		-> mode = 'Harmonic'

	"""

	def __init__(self,Di,yi,b=0.):

		self._Di = Di
		self._yi = yi
		self._b  = b

	@property
	def Di(self):
		"""Getter for the initial decline rate."""
		return self._Di

	@property
	def yi(self):
		"""Getter for the initial y value."""
		return self._yi

	@property
	def b(self):
		"""Getter for the decline exponent."""
		return self._b

	@property
	def mode(self):
		"""Getter for the decline mode: 'exp', 'hyp', or 'har'."""
		return self.b2mode(self.b).lower()[:3]

	def run(self,x:numpy.ndarray,cum:bool=False,**kwargs):
		"""Runs the decline model for a given x value.
        
        Arguments:
        ---------
        x (float array): The input value for the decline function.
        cum (bool, optional): If True, uses the cum function; otherwise, uses the rate function.
        **kwargs: Additional arguments passed to the selected function.
        
        Returns:
        -------
        y (float array): The result of the decline calculation.
        """
		forward = getattr(self,"cum" if cum else "rate")

		return forward(x,self.Di,self.yi,self.b,**kwargs)

	def fit(self,x:numpy.ndarray,y:numpy.ndarray,*args,xi:float=0.):

		x,y = self.shift(numpy.asarray(x),numpy.asarray(y),xi)
		x,y = self.nzero(x,y)
		
		return x,y

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
	def reader(result:Result):
		"""Returns the text that explains the results."""
		string = f"\nDecline mode is {BaseClass.b2mode(result.b)} and the exponent is {result.b}.\n\n"

		string += f"Linear regression R-squared is {result.linear.rvalue**2:.5f}\n"
		string += f"Non-linear curve fit R-squared is {result.R2:.5f}\n\n"

		string += f"Initial x is {result.xi:.1f}\n"
		string += f"Initial y is {result.yi:.1f}\n"
		string += f"Initial decline rate percentage is {result.Di*100:.1f}%\n\n"

		return string

	@staticmethod
	def simulate(result:Result,prc:float=50.):
		"""prc -> prcentile, prc=0.5 gives mean values."""
		Di = result.Di+tstat.ppf(prc/100.,result.n-2)*result.Di_error
		yi = result.yi-tstat.ppf(prc/100.,result.n-2)*result.yi_error

		return Di,yi

	@staticmethod
	def b2mode(b:float):
		"""Determine decline mode based on the exponent value."""
    	return {0.0: "Exponential", 1.0: "Harmonic"}.get(b, "Hyperbolic")

	@staticmethod
	def mode2b(mode:str):
		"""Returns exponent value based on the decline mode."""
		mode_map = {
	        "exponential": 0.0, "exp": 0.0,
	        "hyperbolic" : 0.5, "hyp": 0.5,
	        "harmonic"   : 1.0, "har": 1.0,
	    }

	    b = mode_map.get(mode.lower())

	    if b is not None:
	    	return b

		logging.error(f"Invalid mode: {mode}. Available modes are 'Exponential', 'Hyperbolic', and 'Harmonic'.")

		raise ValueError("Invalid mode. Available modes are 'Exponential', 'Hyperbolic', and 'Harmonic'.")

	@staticmethod
	def option(mode:str=None,b:float=None):
		"""Returns mode and exponent based on their values."""
		if mode is None and b is None:
			return 'Exponential',0

		if mode is None and b is not None:
			return BaseClass.b2mode(float(b)),float(b)

		if mode is not None and b is None:
			return mode,BaseClass.mode2b(mode)

		return BaseClass.option(mode=None,b=b)

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15.]
	y = [1000,963,927,897,852,826,792,750,727,693,659,646,618,588,567,541]

	plt.scatter(x,y)

	b = 1.

	result = BaseClass(b).inv(x,y)

	print(BaseClass.reader(result))

	p10 = BaseClass.model(result,prc=10.)
	p50 = BaseClass.model(result,prc=50.)
	p90 = BaseClass.model(result,prc=90.)

	fit10 = BaseClass(b).run(x,*p10)
	fit50 = BaseClass(b).run(x,*p50)
	fit90 = BaseClass(b).run(x,*p90)

	plt.style.use('_mpl-gallery')

	# plt.plot(x,fit10,label='p10')
	plt.plot(x,fit50,label='p50',color='k')
	plt.fill_between(x,fit10,fit90,color='b',alpha=.2,linewidth=0)
	# plt.plot(x,fit90,label='p90')
	
	# plt.legend()

	plt.show()
