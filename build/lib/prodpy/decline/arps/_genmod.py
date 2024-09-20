import logging

import numpy

from scipy._lib._bunch import _make_tuple_bunch

from scipy.stats import linregress

NonLinResult = _make_tuple_bunch('NonLinResult',
	['decline','intercept','rsquared'])

LinregressResult = _make_tuple_bunch('LinregressResult',
	['slope','intercept','rvalue','pvalue','stderr'],
	extra_field_names=['intercept_stderr'])

Result = _make_tuple_bunch('Result',['linear','nonlinear'])

class GenModel:
	"""Base class for Arp's decline models: Exponential, 
	Hyperbolic, and Harmonic; main decline attributes are:
	
	Di 		: initial decline rate
	yi 		: initial y value

	The decline exponent defines the mode:
	
	xp 		: Arps' decline-curve exponent (b)

	b = 0. 		-> mode = 'Exponential'
	0 < b < 1.	-> mode = 'Hyperbolic'
	b = 1.		-> mode = 'Harmonic'

	"""

	def __init__(self,Di:float,yi:float,xp:float=None):

		self._Di = Di
		self._yi = yi
		self._xp = xp

	@property
	def Di(self):
		return self._Di

	@property
	def yi(self):
		return self._yi

	@property
	def xp(self):
		return self._xp
	
	@property
	def props(self):
		return self.Di,self.yi,self.xp
	
	def base(self,x:numpy.ndarray):
		return self.Di*numpy.asarray(x)

	def xshift(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns shifted x data to get the yi at xi."""
		return (x, yobs) if xi is None else (x[x>=xi]-xi, yobs[x>=xi])

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Linear regression of x and yobs values."""

		shifted = self.xshift(x,yobs,xi)

		try:
			result = linregress(*shifted)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
		else:
			return result

	def rsquared(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns R-squared value."""

		x,yobs = self.xshift(x,yobs,xi)

		ssres = numpy.nansum((yobs-self.ycal(x))**2)
		sstot = numpy.nansum((yobs-numpy.nanmean(yobs))**2)

		return 1-ssres/sstot

if __name__ == "__main__":

	bc = GenModel(100,0.005)

	print(bc.yi)
	print(bc.Di)
	print(bc.expo)
	print(bc.base([1,2,3]))