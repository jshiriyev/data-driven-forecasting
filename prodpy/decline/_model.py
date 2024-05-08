from dataclasses import dataclass

import datetime

import numpy

@dataclass
class Model:
	"""Initializes Decline Curve Model with the decline attributes and mode.
	
	Decline attributes are rate0 (q0) and decline0 (d0):

	rate0 		: initial flow rate
	decline0 	: initial decline rate, day**-1

	Decline exponent defines the mode:

	exponent 	: Arps' decline-curve exponent (b)

		b = 0 		-> mode = 'exponential'
		0 < b < 1 	-> mode = 'hyperbolic'
		b = 1 		-> mode = 'harmonic' 

	Rates are calculated for the input days.
	"""

	rate0 		: float
	decline0 	: float
	mode 		: str 	= None
	exponent 	: float = None

	def __post_init__(self):
		"""Assigns mode and exponent."""
		self.mode,self.exponent = self.get_kwargs(self.mode,self.exponent)

	def __call__(self,*,days=None,datetimes=None,datetime0:datetime.date=None,code='D'):

		if datetimes is not None:
			datetime0 = None

		if days is None:
			days = time-datetime0

		rates = self.get_rates(days)

		
			return rates

		datetimes = self.get_times(days,datetime0,**kwargs)

		return rates,datetimes

	def get_days(self,datetimes,datetime0=None):
		if datetime0 is None:
			datetime0 = datetimes[0]
		return (datetimes-datetime0).astype('timedelta[D]')

	def get_rates(self,days,*,mode=None):
		"""Returns the theoretical rates based on class attributes and mode."""
		locmode = self.mode if mode is None else mode
		return getattr(self,f"{locmode}")(days)

	def exponential(self,days):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return self.rate0*numpy.exp(-self.decline0*days)

	def hyperbolic(self,days):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """
		return self.rate0/(1+self.exponent*self.decline0*days)**(1/self.exponent)

	def harmonic(self,days):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return self.rate0/(1+self.decline0*days)

	@staticmethod
	def get_kwargs(mode=None,exponent=None):
		"""Returns mode and exponent based on their values."""

		if mode is None and exponent is None:
			return 'exponential',0

		elif mode is None and exponent is not None:
			return Model.get_mode(exponent),exponent

		elif mode is not None and exponent is None:
			return mode,Model.get_exponent(mode)

		return mode,exponent

	@staticmethod
	def get_mode(exponent:float):
		"""Returns mode based on the exponent value."""
		if exponent == 0.:
			return 'exponential'

		if exponent > 0. and exponent < 1.:
			return 'hyperbolic'

		if exponent == 1.:
			return 'harmonic'

		raise Warning("Exponent value needs to be in the range of 0 and 1.")

	@staticmethod
	def get_exponent(mode:str):
		"""Returns exponent based on the mode."""

		if mode == 'exponential':
			return 0.

		if mode == 'hyperbolic':
			return 0.5

		if mode == 'harmonic':
			return 1.

		raise Warning("Available modes are exponential, hyperbolic, and harmonic.")

	@staticmethod
	def get_datetimes(days:list,datetime0:datetime.datetime,code='D'):
		"""Adds days to datetime0 after doing the conversion according to code.

		Available code and their meanings are shown below:

			Code	Meaning
			   h	hour
			   m	minute
			   s	second
			  ms	millisecond
			  us	microsecond

		Returns array of datetime in the datetime code specified.
		"""
		conversion_factors = {
			'D'  : 1,
			'h'  : 24,
			'm'  : 24*60 ,
			's'  : 24*60*60,
			'ms' : 24*60*60*1000 ,
			'us' : 24*60*60*1000*1000,
			}

		factor = conversion_factors.get(code)

		if factor is None:
		    raise ValueError(f"Invalid time code. Valid options are: {list(conversion_factors)}")

		timearray = np.array(days)*factor

		timedelta = np.asarray(timearray,dtype=f'timedelta64[{code}]')

		datetimes = np.datetime64(datetime0)+timedelta

		return datetimes.astype(f'datetime64[{code}]')

if __name__ == "__main__":

	import matplotlib.pyplot as plt

	import numpy as np

	days = np.linspace(0,100,100)

	print(Model.get_kwargs('exponential',0.3))

	exp = Model(rate0=10,decline0=0.05)
	hyp = Model(rate0=10,decline0=0.05,exponent=0.4)
	har = Model(rate0=10,decline0=0.05,exponent=1.0)

	print(exp)

	plt.plot(days,exp(days),label='exponential')
	plt.plot(days,hyp(days),label='hyperbolic')
	plt.plot(days,har(days),label='harmonic')

	plt.legend()

	plt.show()


	