import math

import numpy as np

from scipy.stats._stats_py import LinregressResult

from ._hyperbolic import BASE_DOC, Hyperbolic

class Exponential(Hyperbolic):
	__doc__ = """
	Exponential Decline Model for forecasting production in oil and gas wells.

	This class represents the exponential decline model, a special case of the 
	Arps decline equations where the hyperbolic exponent `b` is zero. It is used 
	to model the decline in production rate over time, assuming a constant nominal 
	decline rate.

	""" + BASE_DOC

	def __init__(self,*args,**kwargs):
		"""Initializes the exponential decline model."""
		self._b  = 0.

	def d(self,*args):
		"""Calculates the nominal decline factor."""
		return self._di

	def D(self,*args):
		"""Calculates the effective decline factor."""
		return 1-math.exp(-self._di)

	def qt(self,t:np.ndarray):
		"""
		Computes the qt using the exponential decline formula: qt = qi*exp(-di*t)

		"""
		return self._qi*np.exp(-self._di*np.asarray(t))

	def Nt(self,t:np.ndarray):
		"""
		Computes cumulative production: Nt = (qi/di)*(1-exp(-di*t))

		"""
		return (self._qi/self._di)*(1-np.exp(-self._di*np.asarray(t)))

	def Nec(self,qec:float):
		"""Calculates the cumulative production at economic limit."""
		T = self.T(qec)
		r = self.r(qec)

		return self._qi*T*(r-1)/(r*math.log(r))

	def T(self,qec:float):
		"""Calculates the production life."""
		return math.log(self.r(qec))/self._di

	@property
	def mode(self):
		"""Getter for the decline mode."""
		return 'exp'

	def linearize(self,qt:np.ndarray):
		"""Linearizes the qt values based on Exponential model."""
		return np.log(qt)

	def resinvert(self,result:LinregressResult):
		"""Calculates di and qi values from linear regression results."""
		m = result.slope.tolist()
		k = result.intercept.tolist()

		return -m,math.exp(k)
