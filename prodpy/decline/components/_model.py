import datetime

from dataclasses import dataclass, field

from scipy.stats._stats_py import LinregressResult

from ._marshal import Marshal

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

	score 		: dict = field(
		init = False,
		repr = False,
		default_factory = dict,
		)

	def __post_init__(self):
		"""Assigns corrected mode and exponent values."""

		mode,exponent = Marshal.option(self.mode,self.exponent)

		rate0 = Marshal.rate0(self.rate0)

		decline0 = Marshal.decline0(self.decline0)

		object.__setattr__(self,'mode',mode)
		object.__setattr__(self,'exponent',exponent)
		object.__setattr__(self,'rate0',rate0)
		object.__setattr__(self,'decline0',decline0)

	@property
	def data(self):
		"""Returns the model parameters, q0, d0, and b."""
		return (self.rate0,self.decline0,self.exponent)

	def __str__(self):

		string = "\n"

		string += f"Decline mode is {self.mode} and the exponent is {self.exponent}%.\n"

		string += "\n"

		if self.score.get("LinregressResult") is not None:
			string += f"Linear regression R-squared is {self.score["LinregressResult"].rvalue**2:.2f}\n"

		if self.score.get("NonlinearRsquared") is not None:
			string += f"Non-linear fit R-squared is {self.score["NonlinearRsquared"]:.2f}\n\n"

		string += f"Initial date is {self.date0}\n"
		string += f"Production rate is {self.rate0:.1f}\n"
		string += f"Annual decline percentage is {self.decline0*365.25*100:.1f}%\n"

		string += "\n"

		return string

if __name__ == "__main__":

	# import matplotlib.pyplot as plt

	# import numpy as np

	# days = np.linspace(0,100,100)

	model = Model(rate0=5.)

	print(model)

	print(model.rate0)

	print(Model.rate0)

	print(Model.mode)

	model.score["name"] = "last"

	print(model.score["name"])
	# print(Model.score)

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