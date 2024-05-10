import numpy

from scipy.stats import linregress

from ._model import Model

class Optimize:

	@staticmethod
	def predict(mdays,rates,**kwargs):
		"""Predicts the decline rates for the given measured rates,
		and returns the rates for the calculation days."""

		mode,exponent,kwargs = Optimize.get_option(**kwargs)

		rate0,decline0 = getattr(Optimize,f"{mode}")(mdays,rates,exponent=exponent)

		model = Model(mode=mode,exponent=exponent,rate0=rate0,decline0=decline0)

		if kwargs.get('cdays') is None and kwargs.get('datetimes') is None:
			kwargs['cdays'] = mdays

		return model(**kwargs)

	@staticmethod
	def minimize(mdays,rates,**kwargs):
		"""Returns decline model based on input rates:
		
		mdays 		: measurement days, array of floats
		rates 		: measured flow rates, array of floats

		**kwargs 	: decline mode and exponent

		Returns decline model with mode, exponent, and initial rate and decline.
		"""
		mode,exponent,kwargs = Optimize.get_option(**kwargs)

		rate0,decline0 = getattr(Optimize,f"{mode}")(mdays,rates,exponent=exponent)

		return Model(mode=mode,exponent=exponent,rate0=rate0,decline0=decline0)

	@staticmethod
	def exponential(days,rates,**kwargs):
		"""Optimization based on exponential decline model."""
		sol = linregress(days,numpy.log(rates))

		return numpy.exp(sol.intercept),-sol.slope

	@staticmethod
	def hyperbolic(days,rates,exponent=0.5):
		"""Optimization based on hyperbolic decline model."""
		sol = linregress(days,numpy.power(1/rates,exponent))

		return sol.intercept**(-1/exponent),sol.slope/sol.intercept/exponent

	@staticmethod
	def harmonic(days,rates,**kwargs):
		"""Optimization based on harmonic decline model."""
		sol = linregress(days,1/rates)

		return sol.intercept**(-1),sol.slope/sol.intercept

	@staticmethod
	def get_option(**kwargs):
		"""Returns decline option (mode and exponent) and remaining kwargs."""

		m,kwargs = Optimize.pop_dict(kwargs,'mode')
		e,kwargs = Optimize.pop_dict(kwargs,'exponent')

		output = Model.get_option(m,e,**kwargs)

		if len(output)>2:
			return output

		return *output,{}

	@staticmethod
	def pop_dict(kwargs,key,default=None):
		"""Returns the value of kwargs[key] and kwargs. If the key is not
		in the dictionary, default value and kwargs will be returned."""

		if kwargs.get(key) is None:
			return default,kwargs

		value = kwargs.pop(key)
		
		return value,kwargs


if __name__ == "__main__":

	import matplotlib.pyplot as plt

	import numpy as np

	mdays = np.linspace(0,100,100)

	exp = Model(mode='exponential',rate0=10,decline0=0.05).rates(mdays)
	hyp = Model(mode='hyperbolic',rate0=10,decline0=0.05).rates(mdays)
	har = Model(mode='harmonic',rate0=10,decline0=0.05).rates(mdays)

	# print(exp)
	# print(hyp)
	# print(har)

	# plt.plot(mdays,exp,c='b',label='exponential')
	# plt.plot(mdays,hyp,c='tab:orange',label='hyperbolic')
	# plt.plot(mdays,har,c='g',label='harmonic')

	# plt.legend()

	# plt.show()

	forecast = np.linspace(100,200)

	fit1 = Optimize.predict(mdays,exp)
	fit2 = Optimize.predict(mdays,hyp,mode='hyperbolic',cdays=forecast)
	fit3 = Optimize.predict(mdays,har,mode='harmonic',cdays=forecast)

	plt.plot(mdays,exp,label='exponential')
	plt.plot(mdays,hyp,label='hyperbolic')
	plt.plot(mdays,har,label='harmonic')

	plt.plot(mdays,fit1,'b--',label='exponential')
	plt.plot(forecast,fit2,c='tab:orange',linestyle='--',label='hyperbolic')
	plt.plot(forecast,fit3,'g--',label='harmonic')

	print(Optimize.minimize(mdays,exp,mode='exponential'))
	print(Optimize.minimize(mdays,hyp,mode='hyperbolic'))
	print(Optimize.minimize(mdays,har,mode='harmonic'))

	plt.legend()

	plt.show()


	