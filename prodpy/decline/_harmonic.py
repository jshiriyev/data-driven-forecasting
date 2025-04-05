import numpy as np

class Harmonic():
	"""Harmonic Decline Model."""

	def __init__(self,Di:float,yi:float,**kwargs):
		"""Initializes the Harmonic decline model.

		Parameters:
		----------
		Di: Initial decline rate (1/time).
		yi: Initial rate.

		"""
		self._Di = Di
		self._yi = yi

	@property
	def Di(self):
		"""Getter for the initial decline rate."""
		return self._Di

	@property
	def yi(self):
		"""Getter for the initial y value."""
		return self._yi

	@property
	def mode(self):
		"""Getter for the decline mode."""
		return 'har'

	def __call__(self,Di:float,yi:float):
		"""Creates a new instance of the same class when called."""
		return self.__class__(Di,yi)

	def rate(self,x:np.ndarray,*,xi:float=0.):
		"""
		Computes the rate y at x using the harmonic decline formula.

		y = yi / (1+Di*(x-xi))

		Parameters:
		----------
		x : Time values (array-like).
		xi: Initial time (default 0).

		Returns:
		-------
		Array of rate values at given x.

		"""
		return self.yi/(1+self.Di*(np.asarray(x)-xi))

	def cum(self,x:np.ndarray,*,xi:float=0.):
		"""
		Computes cumulative production Np at x.

		Np = yi/Di*ln(1+Di*(x-xi))

		Parameters:
		----------
		x : Time values (array-like).
		xi: Initial time (default 0).

		Returns:
		-------
		Array of cumulative production values.

		"""
		return (self.yi/self.Di)*np.log(1+self.Di*(np.asarray(x)-xi))

	def linearize(self,y):
		"""Linearizes the y values based on Harmonic model."""
		return 1./y

	def invert(self,result):
		"""Calculates Di and yi values from linear regression results."""
		return result.slope/result.intercept,1/result.intercept