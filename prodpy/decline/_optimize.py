import numpy

from scipy.stats import linregress

from ._model import Model

class Optimize:

	def __init__(self,days):
		"""
		Initializing decline model with days when the rates are measured.

		days 		: rate measured times, array of floats
		"""
		self._days = days

	def __call__(self,rates,**kwargs):
		"""Returns the theoretical rates based on the optimized attributes."""
		return self.predict(rates,**kwargs)

	def predict(self,rates,**kwargs):
		"""Predicts the decline rates for the given measured rates:

		rates 		: measured flow rates

		**kwargs 	: estimation days (optional), and decline mode and exponent

		Returns the rates for the estimation days.
		"""

		days,kwargs = self.get_days(**kwargs)

		return self.minimize(rates,**kwargs)(days)

	def minimize(self,rates,**kwargs):
		"""Returns decline model based on input rates:
		
		rates 		: measured flow rates

		**kwargs 	: decline mode and exponent

		Returns decline model with initial-rate, initial-decline, mode and exponent.
		"""

		mode,exponent = Model.get_kwargs(**kwargs)

		rate0,decline0 = getattr(self,f"{mode}")(rates,exponent=exponent)

		return Model(rate0,decline0,mode=mode,exponent=exponent)

	def exponential(self,rates,**kwargs):
		"""Optimization based on exponential decline model."""
		sol = linregress(self._days,numpy.log(rates))

		return numpy.exp(sol.intercept),-sol.slope

	def hyperbolic(self,rates,exponent=0.5):
		"""Optimization based on hyperbolic decline model."""
		sol = linregress(self._days,numpy.power(1/rates,exponent))

		return sol.intercept**(-1/exponent),sol.slope/sol.intercept/exponent

	def harmonic(self,rates,**kwargs):
		"""Optimization based on harmonic decline model."""
		sol = linregress(self._days,1/rates)

		return sol.intercept**(-1),sol.slope/sol.intercept

	@property
	def days(self):
		return self._days

	def get_days(self,**kwargs):
		"""Returns days for the forward calculations."""
		if kwargs.get('days') is None:
			return self._days,kwargs

		return kwargs.pop('days'),kwargs

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	import numpy as np

	days = np.linspace(0,100,100)

	forecast = np.linspace(100,200)

	dm = Model(days)

	exp = dm.forward(10,0.05,mode='exponential')
	hyp = dm.forward(10,0.05,mode='hyperbolic')
	har = dm.forward(10,0.05,mode='harmonic')

	fit1 = dm(exp)
	fit2 = dm(hyp,mode='hyperbolic',days=forecast)
	fit3 = dm(har,mode='harmonic',days=forecast)

	# plt.plot(days,exp,label='exponential')
	# plt.plot(days,hyp,label='hyperbolic')
	# plt.plot(days,har,label='harmonic')

	plt.plot(days,fit1,'b--',label='exponential')
	plt.plot(forecast,fit2,c='tab:orange',linestyle='--',label='hyperbolic')
	plt.plot(forecast,fit3,'g--',label='harmonic')

	print(dm.minimize(exp,mode='exponential'))
	print(dm.minimize(hyp,mode='hyperbolic'))
	print(dm.minimize(har,mode='harmonic'))

	plt.legend()

	plt.show()


	