import numpy as np

class Hyperbolic():
	"""Hyperbolic Decline Model."""

	def __init__(self,Di:float,yi:float,*,b:float=0.5):
		"""Initializes the Hyperbolic decline model.

		Parameters:
		----------
		Di: Initial decline rate (1/time).
		yi: Initial rate.

		b : Arps' decline-curve exponent (0<b<1)

		"""
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
		"""Getter for the Arps' decline-curve exponent."""
		return self._b

	@property
	def mode(self):
		"""Getter for the decline mode."""
		return 'hyp'

	def __call__(self,Di:float,yi:float):
		"""Creates a new instance of the same class when called."""
		return self.__class__(Di,yi,b=self.b)

	def rate(self,x:np.ndarray,*,xi:float=0.):
		"""
		Computes the rate y at x using the hyperbolic decline formula.

		y = yi / (1+b*Di*t)**(1/b)

		Parameters:
		----------
		x : Time values (array-like).
		xi: Initial time (default 0).

		Returns:
		-------
		Array of rate values at given x.

		"""
		return self.yi/(1+self.b*self.Di*(np.asarray(x)-xi))**(1./self.b)

	def cum(self,x:np.ndarray,*,xi:float=0.):
		"""
		Computes cumulative production Np at x.

		Np = yi / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))

		Parameters:
		----------
		x : Time values (array-like).
		xi: Initial time (default 0).

		Returns:
		-------
		Array of cumulative production values.

		"""
		return (self.yi/self.Di)/(1-self.b)*(1-(1+self.b*self.Di*(np.asarray(x)-xi))**(1-1./self.b))

	def linearize(self,y):
		"""Linearizes the y values based on Hyperbolic model."""
		return np.power(1./y,self.b)

	def invert(self,result):
		"""Calculates Di and yi values from linear regression results."""
		return result.slope/result.intercept/self.b,result.intercept**(-1/self.b)