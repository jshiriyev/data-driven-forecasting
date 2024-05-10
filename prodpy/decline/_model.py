from dataclasses import dataclass, field

import datetime

import numpy
import pandas

@dataclass(frozen=True)
class Model:
	"""Initializes Decline Curve Model with the decline option and attributes.

	Decline option is mode-exponent pair, where exponent defines the mode:

	exponent 	: Arps' decline-curve exponent (b)

		b = 0 		-> mode = 'exponential'
		0 < b < 1 	-> mode = 'hyperbolic'
		b = 1 		-> mode = 'harmonic' 

	Decline attributes are rate0 (q0) and decline0 (d0):

	rate0 		: initial flow rate
	decline0 	: initial decline rate, day**-1

	Rates are calculated for the calculation days.
	"""

	mode 		: str   = None
	exponent 	: float = None
	rate0 		: float = 0.
	decline0 	: float = 0.

	options 	: tuple[str] = field(
		init = False,
		repr = False,
		default = (
			'Exponential',
			'Hyperbolic',
			'Harmonic',
			)
		)

	def __post_init__(self):
		"""Assigns corrected mode and exponent values."""
		
		mode,exponent = self.get_option(self.mode,self.exponent)

		object.__setattr__(self,'mode',mode)
		object.__setattr__(self,'exponent',exponent)

	def __call__(self,*,cdays=None,datetimes=None,**kwargs): # WILL NEED CORRECTION
		"""Calculates rates for the given calculation days or datetimes."""
	
		cdays = self.datetime2day(datetimes,**kwargs) if cdays is None else cdays

		if kwargs.get('datetime0') is None:
			return self.rates(cdays)

		return self.day2datetime(cdays,**kwargs),self.rates(cdays)

	def rates(self,cdays,*,mode=None):
		"""Returns the theoretical rates based on class attributes and mode."""
		locmode = self.mode if mode is None else mode
		return getattr(self,f"{locmode.lower()}")(cdays)

	def exponential(self,cdays):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return self.rate0*numpy.exp(-self.decline0*cdays)

	def hyperbolic(self,cdays):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """
		return self.rate0/(1+self.exponent*self.decline0*cdays)**(1/self.exponent)

	def harmonic(self,cdays):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return self.rate0/(1+self.decline0*cdays)

	@staticmethod
	def get_option(mode=None,exponent=None,**kwargs):
		"""Returns mode and exponent based on their values."""

		if mode is None and exponent is None:
			return Model.get_return('exponential',0,**kwargs)

		elif mode is None and exponent is not None:
			return Model.get_return(Model.get_mode(exponent),exponent,**kwargs)

		elif mode is not None and exponent is None:
			return Model.get_return(mode,Model.get_exponent(mode),**kwargs)

		return Model.get_option(mode=None,exponent=exponent,**kwargs)

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

		if mode.lower() == 'exponential':
			return 0.

		if mode.lower() == 'hyperbolic':
			return 0.5

		if mode.lower() == 'harmonic':
			return 1.

		raise Warning("Available modes are exponential, hyperbolic, and harmonic.")

	@staticmethod
	def get_return(*args,**kwargs):
		"""Returns args when kwargs is empty, both (args and kwargs) otherwise."""
		if len(kwargs)==0:
			return *args,

		return *args,kwargs

	@staticmethod
	def datetime2day(datetimes:pandas.Series,*,datetime0=None,**kwargs):
		"""Calculates days for the given datetime series."""

		if datetime0 is None:
			datetime0 = datetimes[0]

		timedelta = (datetimes-datetime0).to_numpy()

		timedelta = timedelta.astype('timedelta64[us]')

		return timedelta.astype('float64')/(24*60*60*1000*1000)

	@staticmethod
	def day2datetime(days:numpy.ndarray,*,datetime0=None,timecode=None):
		"""
		Adds days to datetime0 calculating new datetimes with the
		  specified timecode. Available timecodes and their meanings
		  are shown below:

		TimeCode	Meaning
		-------- 	-------------
			   h	hour
			   m	minute
			   s	second
			  ms	millisecond
			  us	microsecond

		Returns numpy array of datetimes.
		"""

		if datetime0 is None:
			datetime0 = datetime.date(2000,1,1)

		ustimes = numpy.asarray(days)*24*60*60*1000*1000

		timedelta = numpy.asarray(ustimes,dtype=f'timedelta64[us]')
		datetimes = numpy.datetime64(datetime0)+timedelta

		code = 'D' if timecode is None else timecode

		return datetimes.astype(f'datetime64[{code}]')

if __name__ == "__main__":

	# import matplotlib.pyplot as plt

	# import numpy as np

	# days = np.linspace(0,100,100)

	print(Model.get_option(cdays=55,exponent=0.5,name='empty'))

	mode,exponent = Model.get_option('exponential',0.5)

	print(mode)
	print(exponent)

	mode,exponent,kwargs = Model.get_option('exponential',0.5,days=55)

	print(mode)
	print(exponent)
	print(kwargs)

	# exp = Model(rate0=10,decline0=0.05)
	# hyp = Model(rate0=10,decline0=0.05,exponent=0.4)
	# har = Model(rate0=10,decline0=0.05,exponent=1.0)

	# print(exp)

	# plt.plot(days,exp(days=days),label='exponential')
	# plt.plot(days,hyp(days=days),label='hyperbolic')
	# plt.plot(days,har(days=days),label='harmonic')

	# plt.legend()

	# plt.show()

	print(Model.mode)
	print(Model.exponent)
	print(Model.rate0)
	print(Model.decline0)
	print(Model.options)

	print(Model(5,1,5,5))