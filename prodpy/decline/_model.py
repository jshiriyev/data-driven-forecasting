import numpy

from scipy.stats import linregress

class Model:

	def __init__(self,days):
		"""
		Initializing decline model with days when the rates are measured.

		days 		: rate measured times, array of floats
		"""
		self._days = days

	def __call__(self,rates,**kwargs):

		return self.fit(rates,**kwargs)

	def fit(self,rates,**kwargs):
		"""Fits the decline model to the given rates:

		rates 		: measured flow rates

		Returns the rates for the estimation days.
		"""

		days,kwargs = self.get_days(**kwargs)
		mode,kwargs = self.get_mode(**kwargs)

		args = getattr(self,f"get_{mode}")(rates,**kwargs)

		return getattr(self,f"{mode}")(days,*args,**kwargs)

	def forward(self,*args,**kwargs):
		"""Returns the calculated rates based on the decline attributes and mode:
		
		Decline attributes (*args) are rate0 (q0) and decline0 (d0):

		rate0 		: initial flow rate
		decline0 	: initial decline rate, day**-1

		Decline exponent defines the mode:

		exponent 	: Arps' decline-curve exponent (b)

			b = 0 		-> exponential
			0 < b < 1 	-> hyperbolic
			b = 1 		-> harmonic 

		Rates are calculated for the measurements days or any other input days.
		"""

		days,kwargs = self.get_days(**kwargs)
		mode,kwargs = self.get_mode(**kwargs)

		return getattr(self,f"{mode}")(days,*args,**kwargs)

	def get_days(self,**kwargs):
		"""Returns days for the forward calculations."""
		if kwargs.get('days') is None:
			return self._days,kwargs

		return kwargs.pop('days'),kwargs

	def get_mode(self,**kwargs):
		"""Returns mode based on exponent and mode input."""

		if kwargs.get('mode') is None:
			mode = 'exponential'
		else:
			mode = kwargs.pop('mode')

		exponent = kwargs.get('exponent')

		if exponent is None:
			return mode,kwargs

		if exponent == 0:
			_ = kwargs.pop('exponent')
			return 'exponential',kwargs

		if exponent > 0 and exponent < 1:
			return 'hyperbolic',kwargs

		if exponent == 1:
			_ = kwargs.pop('exponent')
			return 'harmonic',kwargs

	def inverse(self,rates,**kwargs):
		"""Returns decline attributes (q0,d0) based on input rates:
		
		rates 		: measured flow rates
		
		Returned decline attributes are initial-rate and initial-decline values.
		"""

		mode,kwargs = self.get_mode(**kwargs)

		return getattr(self,f"get_{mode}")(rates,**kwargs)

	def get_exponential(self,rates):

		sol = linregress(self._days,numpy.log(rates))

		return numpy.exp(sol.intercept),-sol.slope

	def get_hyperbolic(self,rates,exponent=0.5):

		sol = linregress(self._days,numpy.power(1/rates,exponent))

		return sol.intercept**(-1/exponent),sol.slope/sol.intercept/exponent

	def get_harmonic(self,rates):

		sol = linregress(self._days,1/rates)

		return sol.intercept**(-1),sol.slope/sol.intercept

	@property
	def days(self):

		return self._days

	@staticmethod
	def exponential(days,rate0,decline0):
		"""Exponential decline model: q = q0 * exp(-d0*t) """

		return rate0*numpy.exp(-decline0*days)

	@staticmethod
	def hyperbolic(days,rate0,decline0,exponent=0.5):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """

		return rate0/(1+exponent*decline0*days)**(1/exponent)

	@staticmethod
	def harmonic(days,rate0,decline0):
		"""Harmonic decline model: q = q0 / (1+d0*t) """

		return rate0/(1+decline0*days)

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

	print(dm.inverse(exp,mode='exponential'))
	print(dm.inverse(hyp,mode='hyperbolic'))
	print(dm.inverse(har,mode='harmonic'))

	plt.legend()

	plt.show()


	