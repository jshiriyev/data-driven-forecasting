import numpy
import pandas

from scipy.stats import linregress

from ._model import Model

from ._forward import Forward

class Optimize():

	def __init__(self,mode:str=None,exponent:float=None):

		self._mode,self._exponent = Model.get_option(mode=mode,exponent=exponent)

	@property
	def mode(self):
		return self._mode
	
	@property
	def exponent(self):
		return self._exponent

	def __call__(self,dates:pandas.Series,rates:pandas.Series,**kwargs):
		"""Predicts the decline rates for the measured dates and rates,
		and returns either the model or the rates for the pandas.date_range parameters."""

		days = Forward.days(dates,kwargs.get('start'))

		model = self.minimize(days,rates)

		return model,Forward.run(model,**kwargs)

	def predict(self,days,rates,**kwargs):
		"""Predicts the decline rates for the measured days and rates,
		and returns the rates for the pandas.date_range parameters."""

		model = self.minimize(days,rates)

		return Forward.run(model,**kwargs)

	def minimize(self,days,rates):
		"""Returns decline model based on input rates:
		
		days 		: measurement days, array of floats
		rates 		: measured flow rates, array of floats

		Returns decline model with mode, exponent, and initial rate and decline.
		"""
		rate0,decline0 = self.method(days,rates)

		return Model(
			mode = self.mode,
			exponent = self.exponent,
			rate0 = rate0,
			decline0 = decline0
			)

	@property
	def method(self):
		return getattr(self,f"{self._mode}")

	def Exponential(self,days,rates):
		"""Optimization based on exponential decline model."""
		sol = linregress(days,numpy.log(rates))

		return numpy.exp(sol.intercept),-sol.slope

	def Hyperbolic(self,days,rates):
		"""Optimization based on hyperbolic decline model."""
		sol = linregress(days,numpy.power(1/rates,self.exponent))

		return sol.intercept**(-1/self.exponent),sol.slope/sol.intercept/self.exponent

	def Harmonic(self,days,rates):
		"""Optimization based on harmonic decline model."""
		sol = linregress(days,1/rates)

		return sol.intercept**(-1),sol.slope/sol.intercept

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	import numpy as np

	days = np.linspace(0,100,100)

	exp = Model(mode='exponential',rate0=10,decline0=0.05).rates(days)
	hyp = Model(mode='hyperbolic',rate0=10,decline0=0.05).rates(days)
	har = Model(mode='harmonic',rate0=10,decline0=0.05).rates(days)

	# print(exp)
	# print(hyp)
	# print(har)

	# plt.plot(days,exp,c='b',label='exponential')
	# plt.plot(days,hyp,c='tab:orange',label='hyperbolic')
	# plt.plot(days,har,c='g',label='harmonic')

	# plt.legend()

	# plt.show()

	forecast = np.linspace(100,200)

	fit1 = Optimize.predict(days,exp)
	fit2 = Optimize.predict(days,hyp,mode='hyperbolic',cdays=forecast)
	fit3 = Optimize.predict(days,har,mode='harmonic',cdays=forecast)

	plt.plot(days,exp,label='exponential')
	plt.plot(days,hyp,label='hyperbolic')
	plt.plot(days,har,label='harmonic')

	plt.plot(days,fit1,'b--',label='exponential')
	plt.plot(forecast,fit2,c='tab:orange',linestyle='--',label='hyperbolic')
	plt.plot(forecast,fit3,'g--',label='harmonic')

	print(Optimize.minimize(days,exp,mode='exponential'))
	print(Optimize.minimize(days,hyp,mode='hyperbolic'))
	print(Optimize.minimize(days,har,mode='harmonic'))

	plt.legend()

	plt.show()


	