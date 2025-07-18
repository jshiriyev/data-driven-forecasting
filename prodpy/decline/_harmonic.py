import math

import numpy as np

from scipy.stats._stats_py import LinregressResult

from ._hyperbolic import BASE_DOC, Hyperbolic

class Harmonic():
	__doc__ = """
	Harmonic Decline Model for forecasting production in oil and gas wells.

	This class represents the harmonic form of the Arps decline model, which 
    is a specific case of the hyperbolic model with a hyperbolic exponent `b = 1`.

	""" + BASE_DOC

	def __init__(self,*args,**kwargs):
		"""Initializes the harmonic decline model."""
		self._b = 1.

	def d(self,t:np.ndarray):
		"""Calculates the nominal decline factor."""
		return self._di/(1+self._di*t)

	def D(self,*args):
		"""Calculates the effective decline factor."""
		return self.d(t)/(1+self.d(t))

	def qt(self,t:np.ndarray):
		"""
		Computes the qt using the harmonic decline formula: qt = qi / (1+di*(t-ti))

		"""
		return self._qi/(1+self._di*np.asarray(t))

	def Nt(self,t:np.ndarray,*,ti:float=0.):
		"""
		Computes cumulative production: Nt = qi/di*ln(1+di*(t-ti))

		"""
		return (self._qi/self._di)*np.log(1+self._di*np.asarray(t))

	def Nec(self,qec:float):
		"""Calculates the cumulative production at economic limit."""
		T = self.T(qec)
		r = self.r(qec)

		return self._qi*T*math.log(r)/(r-1)

	def T(self,qec:float):
		"""Calculates the production life."""
		return (self.r(qec)-1)/self._di

	@property
	def mode(self):
		"""Getter for the decline mode."""
		return 'har'

	def linearize(self,qt:np.ndarray):
		"""Linearizes the qt values based on Harmonic model."""
		return 1./qt

	def resinvert(self,result:LinregressResult):
		"""Calculates di and qi values from linear regression results."""
		m = result.slope.tolist()
		k = result.intercept.tolist()

		return m/k,1/k