import logging

import sys

import numpy

from scipy import stats

from scipy._lib._bunch import _make_tuple_bunch

Result = _make_tuple_bunch('Result',
	['b','Di','yi','xi','n','R2','Di_error','yi_error'],
	extra_field_names=['linear'],
	)

LinregressResult = _make_tuple_bunch('LinregressResult',
	['slope','intercept','rvalue','pvalue','stderr'],
	extra_field_names=['intercept_stderr'],
	)

from scipy.optimize import curve_fit

from ._exponential import Exponential
from ._hyperbolic import Hyperbolic
from ._harmonic import Harmonic

class Arps():
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

	def __init__(self,Di,yi,*,b=0.):
		"""Initializes the Arps model based on the decline exponent 'b'."""
		self.model = getattr(sys.modules[__name__],self.b2mode(b))(Di,yi,b=b)

	def run(self,x:numpy.ndarray,*,cum:bool=False,xi:float=0.):
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
		return getattr(self.model,"cum" if cum else "rate")(x,xi=xi)

	def linregress(self,x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.,**kwargs):
		"""Linear regression of x and y values."""
		x,y = self.shift(numpy.asarray(x),numpy.asarray(y),xi=xi)
		x,y = self.nzero(x,y)

		try:
			result = stats.linregress(x,self.model.linearize(y),**kwargs)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
		else:
			return {k: v.tolist() for k, v in result._asdict().items()}

	@staticmethod
	def shift(x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0):
		"""Returns shifted x data to get the yi at xi."""
		return (x, y) if xi==0 else (x[x>=xi]-xi, y[x>=xi])

	@staticmethod
	def nzero(x:numpy.ndarray,y:numpy.ndarray):
		"""Returns the nonzero entries of y for x and y."""
		return (x[~numpy.isnan(y) & (y!=0)],y[~numpy.isnan(y) & (y!=0)])

	def fit(self,x:numpy.ndarray,y:numpy.ndarray,*,xi:float=0.**kwargs):
		"""Returns exponential regression results after linearization."""
		x,y = self.shift(numpy.asarray(x),numpy.asarray(y),xi=xi)
		x,y = self.nzero(x,y)

		linear = self.linregress(x,y)

		kwargs.setdefault('p0',default=self.model.invert(linear))

		result = curve_fit(self.forward,x,y,**kwargs)

		R2,perror = self.process(x,y,result)

		return Result(self.model.b,*result[0].tolist(),xi,x.size,R2,*perror,
			linear=LinregressResult(**linear),
			)

	def forward(self,x:numpy.ndarray,Di:float,yi:float):
		"""Returns either rate or cum methods based on cum flag."""
		return self.model(Di,yi).rate(x)

	def process(self,x:numpy.ndarray,y:numpy.ndarray,result:tuple):
		"""Processes the curve_fit results to compute R-squared and parameter errors."""
		R2 = self.rsquared(self.forward(x,*result[0]),y)

		return R2, numpy.sqrt(numpy.diag(result[1])).tolist()

	@staticmethod
	def rsquared(ycal:numpy.ndarray,yobs:numpy.ndarray):
		"""Returns R-squared value."""
		ssres = numpy.nansum((yobs-ycal)**2)
		sstot = numpy.nansum((yobs-numpy.nanmean(yobs))**2)

		return (1-ssres/sstot).tolist()

	@staticmethod
	def reader(result):
		"""Returns the text that explains the results."""
		string = f"\nDecline mode is {Arps.b2mode(result.b)} and the exponent is {result.b}.\n\n"

		string += f"Linear regression R-squared is {result.linear.rvalue**2:.5f}\n"
		string += f"Non-linear curve fit R-squared is {result.R2:.5f}\n\n"

		string += f"Initial x is {result.xi:.1f}\n"
		string += f"Initial y is {result.yi:.1f}\n"
		string += f"Initial decline rate percentage is {result.Di*100:.1f}%\n\n"

		return string

	def simulate(self,result,prc:float=50.):
		"""prc -> prcentile, prc=0.5 gives mean values."""
		Di = result.Di+stats.t.ppf(prc/100.,result.n-2)*result.Di_error
		yi = result.yi-stats.t.ppf(prc/100.,result.n-2)*result.yi_error

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
			return Arps.b2mode(float(b)),float(b)

		if mode is not None and b is None:
			return mode,Arps.mode2b(mode)

		return Arps.option(mode=None,b=b)

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
