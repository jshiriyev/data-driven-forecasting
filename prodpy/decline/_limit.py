import datetime

import numpy
import pandas

class Limit():

	def __init__(self,start:datetime.date,end:datetime.date):

		self.start,self.end = start,end

	def dates(self,**kwargs):

		kwargs['start'],kwargs['end'] = self.start,self.end

		return pandas.date_range(**kwargs)

	def bools(self,datetimes:pandas.Series):

		later = self.later(datetimes)
		prior = self.prior(datetimes)

		return numpy.logical_and(later,prior)

	def prior(self,datetimes:pandas.Series):
		"""Returns the bools for the datetimes that
		is prior to the end date."""

		return (datetimes.dt.date<=self.end).to_numpy()

	def later(self,datetimes:pandas.Series):
		"""Returns the bools for the datetimes that is
		later than the start date."""

		return (datetimes.dt.date>=self.start).to_numpy()

	@property
	def days(self):

		return (self.end-self.start).days