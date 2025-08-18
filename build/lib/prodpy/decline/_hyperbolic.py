import math

import numpy as np

from scipy.stats._stats_py import LinregressResult

BASE_DOC = """
	Dictionary:
	----------
	b   = Hyperbolic exponent
	d   = Nominal decline factor
	di  = Initial decline factor (1/time)
	D   = Effective decline factor
	qi  = Initial production rate
	qt  = Production rate at time t
	Nt  = Cumulative production at time t
	Nec = Cumulative production at economic limit
	r   = Rate ratio qi/qec, where qec is the economic limit rate.
	t   = Time
	T   = Estimated producing life of the well.

"""

class Hyperbolic():
	__doc__ = """
	Hyperbolic Decline Model for production forecasting in oil and gas wells.

	This class implements the Arps hyperbolic decline model, which is commonly 
    used to describe oil and gas production decline when the rate of decline 
    slows over time. It generalizes the exponential model by introducing a 
    hyperbolic exponent `b` (0 < b < 1), which allows for curvature in the 
    decline trend.

	""" + BASE_DOC

	def __init__(self,*,b:float=0.5):
		"""Initializes the hyperbolic decline model."""
		self._b = float(b)

	@property
	def b(self):
		"""Getter for the Arps' hyperbolic exponent."""
		return self._b

	def __call__(self,di:float,qi:float):
		"""Creates a new instance of the same class when called."""
		self.di,self.qi = di,qi

		return self

	def d(self,t:np.ndarray):
		"""Calculates the nominal decline factor."""
		return self._di/(1+self._b*self._di*np.asarray(t))

	@property
	def di(self):
		"""Getter for the initial decline rate."""
		return self._di

	@di.setter
	def di(self,value):
		"""Setter for the initial decline rate."""
		self._di = float(value)

	def D(self,t:np.ndarray):
		"""Calculates the effective decline factor."""
		return 1-(self.d(t)*self._b+1)**(-1/self._b)

	@property
	def qi(self):
		"""Getter for the initial production rate."""
		return self._qi

	@qi.setter
	def qi(self,value):
		"""Setter for the initial production rate."""
		self._qi = float(value)

	def qt(self,t:np.ndarray):
		"""
		Computes the qt using the hyperbolic decline formula: qt = qi / (1+b*di*t)**(1/b)

		"""
		return self._qi/(1+self._b*self._di*np.asarray(t))**(1./self._b)

	def Nt(self,t:np.ndarray):
		"""
		Computes cumulative production: Nt = qi / ((1-b)*di)*(1-(1+b*di*t)**(1-1/b))

		"""
		return (self._qi/self._di)/(1-self._b)*(1-(1+self._b*self._di*np.asarray(t))**(1-1./self._b))

	def Nec(self,qec:float):
		"""Calculates the cumulative production at economic limit."""
		T = self.T(qec)
		r = self.r(qec)

		return (self._qi*T*self._b)/(1-self._b)*(((1/r)**self._b-(1/r))/(1-(1/r)**self._b))

	def r(self,qec:float):
		"""Mehtod for the calculation of qi/qec ratio."""
		return self._qi/qec

	def T(self,qec:float):
		"""Calculates the production life."""
		return (self.r(qec)**self._b-1)/(self._b*self._di)

	@property
	def mode(self):
		"""Getter for the decline mode."""
		return 'hyp'

	def linearize(self,qt:np.ndarray):
		"""Linearizes the flow rates based on hyperbolic model."""
		return np.power(1./qt,self.b)

	def resinvert(self,result:LinregressResult):
		"""Calculates di and qi values from linear regression results."""
		m = result.slope.tolist()
		k = result.intercept.tolist()

		return m/k/self._b,k**(-1/self._b)

if __name__ == "__main__":

	print(help(Hyperbolic))