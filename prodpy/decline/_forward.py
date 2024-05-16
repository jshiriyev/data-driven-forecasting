import datetime

import numpy
import pandas

from ._model import Model

class Forward():

	def __init__(self,*args,**kwargs):
		self._model = Model(*args,**kwargs)

	@property
	def model(self):
		return self._model

	def __call__(self,**kwargs):
		return self.run(self.model,**kwargs)

	@property
	def method(self):
		return getattr(self,f"{self._model.mode}")

	@staticmethod
	def run(model:Model,**kwargs):
		"""Calculates the theoretical rates for the given model and pandas.date_range parameters."""
		dates = pandas.date_range(**kwargs)

		curve = getattr(Forward,f"{model.mode}")

		return {"dates":dates,"rates":curve(model,Forward.days(dates))}

	@staticmethod
	def Exponential(model:Model,days:numpy.ndarray):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return model.rate0*numpy.exp(-model.decline0*days)

	@staticmethod
	def Hyperbolic(model:Model,days:numpy.ndarray):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """
		return model.rate0/(1+model.exponent*model.decline0*days)**(1/model.exponent)

	@staticmethod
	def Harmonic(model:Model,days:numpy.ndarray):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return model.rate0/(1+model.decline0*days)

	@staticmethod
	def days(dates:pandas.DatetimeIndex,start:datetime.date=None):
		"""Return days calculated from the dates."""
		
		if start is None:
			start = dates[0]

		start = numpy.datetime64(start)

		delta = (dates-start).to_numpy().astype('timedelta64[ns]')

		return delta.astype('float64')/(24*60*60*1e9)

if __name__ == "__main__":

	import datetime

	print(
		Forward.days(5)
		)

	print(
		Forward.days(datetime.date(2022,2,3),datetime.date(2022,2,7))
		)

	print(
		Forward.days(datetime.date(2022,2,3),datetime.date(2022,2,7),12)
		)