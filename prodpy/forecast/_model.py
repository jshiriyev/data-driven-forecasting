import datetime

from dataclasses import dataclass, field

from scipy.stats._stats_py import LinregressResult

from .arps._arpmod import Arps

from .arps._marshal import Marshal

modes = 'Exponential','Hyperbolic','Harmonic'
	
import os
import sys

def Arps(critical_params:tuple,pressures:numpy.ndarray,temperature:float,derivative:bool=False,method:str="direct_method"):
	"""
	Dynamically calculates z-factor based on the specified method.

	Parameters:
	    critical_params (tuple): tuple of (pcrit in psi, tcrit in Rankine)

	    pressures (numpy.ndarray): Array of pressure values (psi) to calculate z-factor for.
	    temperature (float): The temperature value (Rankine) at which to calculate z-factor.
	    
	    method_name (str): The name of the method to use:
	    	(e.g., 'direct_method', 'dranchuk_abu_kassem', 'dranchuk_purvis_robinson', 'hall_yarborough').
	    
	Returns:
	    numpy.ndarray: Z-factor, and if derivative is True, Z-prime values calculated for each pressure.
	    
	"""
	sys.path.append(os.path.dirname(__file__))

	method_parts = method.split('_')

	method_class = method_parts[0].capitalize()+''.join(word.capitalize() for word in method_parts[1:])

	# Import the correct method class dynamically
	try:
		module = __import__(method)
		mclass = getattr(module,method_class)
	except (ImportError, AttributeError):
		raise ValueError(f"Method '{method}' not found or invalid.")

	# Create an instance of the class and calculate z-factor
	method_instance = mclass(critical_params,temperature)

	return method_instance(pressures,derivative)

@dataclass(frozen=True)
class Model:

	d0 			: datetime.date = None

	score 		: dict = field(
		init = False,
		repr = False,
		default_factory = dict,
		)

	def __post_init__(self):
		"""Assigns corrected mode and exponent values."""

		mode,expo = Marshal.option(self.mode,self.expo)

		object.__setattr__(self,'mode',mode)
		object.__setattr__(self,'expo',expo)

		object.__setattr__(self,'y0',float(self.y0))
		object.__setattr__(self,'D0',float(self.D0))

	def __str__(self):

		string = "\n"

		string += f"Decline mode is {self.mode} and the exponent is {self.expo}%.\n"

		string += "\n"

		if self.score.get("LinregressResult") is not None:
			string += f"Linear regression R-squared is {self.score["LinregressResult"].rvalue**2:.2f}\n"

		if self.score.get("NonlinearRsquared") is not None:
			string += f"Non-linear fit R-squared is {self.score["NonlinearRsquared"]:.2f}\n\n"

		string += f"Initial date is {self.d0}\n"
		string += f"Production rate is {self.y0:.1f}\n"
		string += f"Annual decline percentage is {self.D0*365.25*100:.1f}%\n"

		string += "\n"

		return string

	@classmethod
	def fit(cls,x:numpy.ndarray,yobs:numpy.ndarray,d0=None):
		"""Inversely calculates decline model, and returns decline model
		with mode, expo, d0, y0 and D0.
		"""
		y0,D0,LinRegRes = self.minimize(x,)

		model = cls(mode=self.mode,expo=self.expo,d0=d0,y0=y0,D0=D0)

		model.score["LinRegressResult"] = LinRegRes

		model.score["NonLinRsquared"] = self.Rsquared(model,x)

		return model

if __name__ == "__main__":

	# import matplotlib.pyplot as plt

	# import numpy as np

	# x = np.linspace(0,100,100)

	model = Model(y0=5.)

	print(model)

	print(model.y0)

	print(Model.y0)

	print(Model.mode)

	model.score["name"] = "last"

	print(model.score["name"])
	# print(Model.score)

	mode,expo = Model.get_option(mode='Exponential',expo=50.)

	print(mode)
	print(expo)

	# exp = Model(y0=10,D0=0.05)
	# hyp = Model(y0=10,D0=0.05,expo=40.)
	# har = Model(y0=10,D0=0.05,expo=100.)

	# print(exp)

	# plt.plot(x,exp(x=x),label='Exponential')
	# plt.plot(x,hyp(x=x),label='Hyperbolic')
	# plt.plot(x,har(x=x),label='Harmonic')

	# plt.legend()

	# plt.show()

	print(Model.mode)
	print(Model.expo)
	print(Model.y0)
	print(Model.D0)
	print(Model.options)

	print(Model(5,100,5,0.5))