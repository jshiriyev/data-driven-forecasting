import datetime

import numpy
import pandas

class TimeSpan:

	def __init__(self,series:pandas.Series):

		self._series = series

	@property
	def series(self):

		return self._series

	@property
	def size(self):

		return self._series.size

	def days(self,date:datetime.date):
		"""Returns the days passed after the date."""

		delta = self.series-date

		delta = delta.to_numpy()
		delta = delta.astype('timedelta64[ns]')
		delta = delta.astype('float64')

		return delta/(24*60*60*1e9)

	def between(self,*args):
		"""Returns the bools for the interval that is in between
		start and end dates."""

		bools = numpy.zeros(self.size,dtype='bool')

		for limit in args:

			later = self.later(limit[0])
			prior = self.prior(limit[1])

			among = numpy.logical_and(later,prior)

			bools = numpy.logical_or(bools,among)

		return bools
	
	def prior(self,date:datetime.date):
		"""Returns the bools for the datetimes that
		is prior to the date."""

		return (self.series.dt.date<=date).to_numpy()

	def later(self,date:datetime.date):
		"""Returns the bools for the datetimes that is
		later than the date."""

		return (self.series.dt.date>=date).to_numpy()

	@staticmethod
	def get(*args,**kwargs):
		"""Static TimeSpan constructor from limits."""

		index = pandas.DatetimeIndex([])

		for limit in args:

			kwargs['start'],kwargs['end'] = limit

			space = pandas.date_range(**kwargs)
			index = index.append(space)

		return TimeSpan(index.to_series())

if __name__ == "__main__":

	span = TimeSpan.get(
		(datetime.date(2021,1,1),datetime.date(2021,2,1)),
		(datetime.date(2024,1,1),datetime.date(2024,2,1)),
		periods=4
	)

	print(span.series)