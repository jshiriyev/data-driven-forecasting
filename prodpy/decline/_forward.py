import datetime

import numpy
import pandas

from ._model import Model

class Forward():

	def __init__(self):
		pass

	def __call__(self,model):

		self.model = model

		return self

	def run(self,dates:pandas.DatetimeIndex=None,**kwargs):
		"""Calculates the theoretical rates for the given model and
		dates or pandas.date_range parameters."""
		
		if dates is None
			dates = pandas.date_range(**kwargs)

		days = self.days(dates,kwargs.get('start'))

		return {"dates":dates,"rates":self.method(days)}

	@property
	def method(self):
		return getattr(self,f"{self.model.mode}")

	def Exponential(self,days:numpy.ndarray):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return self.model.rate0*numpy.exp(-self.model.decline0*days)

	def Hyperbolic(self,days:numpy.ndarray):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """
		return self.model.rate0/(1+self.model.exponent*self.model.decline0*days)**(1/self.model.exponent)

	def Harmonic(self,days:numpy.ndarray):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return self.model.rate0/(1+self.model.decline0*days)

	@staticmethod
	def days(dates:pandas.DatetimeIndex,start:datetime.date=None):
		"""Return days calculated from the dates."""
		start = dates[0] if start is None else start
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