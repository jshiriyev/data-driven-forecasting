import datetime

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Model:
	"""Initializes Decline Curve Model with the decline option and attributes.

	Decline option is mode-exponent pair, where exponent defines the mode:

	exponent 	: Arps' decline-curve exponent (b)

		b = 0 		-> mode = 'Exponential'
		0 < b < 100	-> mode = 'Hyperbolic'
		b = 100		-> mode = 'Harmonic' 

	Decline attributes are rate0 (q0) and decline0 (d0):

	rate0 		: initial flow rate
	decline0 	: initial decline rate, day**-1

	The class contains methods to get the correct pair of options.
	"""

	mode 		: str   = None
	exponent 	: float = None

	date0 		: datetime.date = None
	
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

		mode,exponent = self.get_option(
			self.mode,self.exponent)

		rate0 = self.get_rate0(self.rate0)

		decline0 = self.get_decline0(self.decline0)

		object.__setattr__(self,'mode',mode)
		object.__setattr__(self,'exponent',exponent)
		object.__setattr__(self,'rate0',rate0)
		object.__setattr__(self,'decline0',decline0)

	@staticmethod
	def get_option(mode=None,exponent=None):
		"""Returns mode and exponent based on their values."""

		if mode is None and exponent is None:
			return 'Exponential',0

		if mode is None and exponent is not None:
			return Model.get_mode(float(exponent)),float(exponent)

		if mode is not None and exponent is None:
			return mode.capitalize(),Model.get_exponent(mode)

		return Model.get_option(mode=None,exponent=float(exponent))

	@staticmethod
	def get_mode(exponent:float):
		"""Returns mode based on the exponent value."""

		if exponent == 0.:
			return 'Exponential'

		if exponent > 0. and exponent < 100.:
			return 'Hyperbolic'

		if exponent == 100.:
			return 'Harmonic'

		raise Warning("Exponent value needs to be in the range of 0 and 100.")

	@staticmethod
	def get_exponent(mode:str):
		"""Returns exponent based on the mode."""

		if mode.capitalize() == 'Exponential':
			return 0.

		if mode.capitalize() == 'Hyperbolic':
			return 50.

		if mode.capitalize() == 'Harmonic':
			return 100.

		raise Warning("Available modes are Exponential, Hyperbolic, and Harmonic.")

	@staticmethod
	def get_rate0(rate0:float):

		return float(rate0)

	@staticmethod
	def get_decline0(decline0:float):

		decline0 = float(decline0)

		# if decline0 < 0. or decline0 > 1.:
		# 	raise Warning("Initial decline rate (decline0) needs to be in [0., 1.]")

		return decline0

if __name__ == "__main__":

	# import matplotlib.pyplot as plt

	# import numpy as np

	# days = np.linspace(0,100,100)

	model = Model(rate0=5.)

	print(model)

	print(model.rate0)

	print(Model.rate0)

	print(Model.mode)

	mode,exponent = Model.get_option(mode='Exponential',exponent=50.)

	print(mode)
	print(exponent)

	# exp = Model(rate0=10,decline0=0.05)
	# hyp = Model(rate0=10,decline0=0.05,exponent=40.)
	# har = Model(rate0=10,decline0=0.05,exponent=100.)

	# print(exp)

	# plt.plot(days,exp(days=days),label='Exponential')
	# plt.plot(days,hyp(days=days),label='Hyperbolic')
	# plt.plot(days,har(days=days),label='Harmonic')

	# plt.legend()

	# plt.show()

	print(Model.mode)
	print(Model.exponent)
	print(Model.rate0)
	print(Model.decline0)
	print(Model.options)

	print(Model(5,100,5,0.5))