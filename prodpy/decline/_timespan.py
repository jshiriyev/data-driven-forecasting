import datetime

import numpy
import pandas

class TimeSpan:

	def __init__(self,array:pandas.Series):

		self._array = array

	@property
	def array(self):

		return self._array
	
	@staticmethod
	def get(*args,**kwargs):

		index = pandas.DatetimeIndex([])

		for limit in args:

			kwargs['start'],kwargs['end'] = limit

			datetimes = pandas.date_range(**kwargs)

			index = index.append(datetimes)

		return TimeSpan(index.to_series())

	def bools(self,*args):
		"""Returns the bools for the interval that is in between
		start and end dates."""

		array = numpy.zeros(self.array.size,dtype='bool')

		for limit in args:

			later = self.later(limit[0])
			prior = self.prior(limit[1])

			among = numpy.logical_and(later,prior)

			array = numpy.logical_or(array,among)

		return array
	
	def prior(self,date:datetime.date):
		"""Returns the bools for the datetimes that
		is prior to the date."""

		return (self.array.dt.date<=date).to_numpy()

	def later(self,date:datetime.date):
		"""Returns the bools for the datetimes that is
		later than the date."""

		return (self.array.dt.date>=date).to_numpy()

	def days(self,date:datetime.date):
		"""Returns the days passed after the date."""

		delta = (self.array-date)
		delta = delta.to_numpy()
		delta = delta.astype('timedelta64[ns]')
		delta = delta.astype('float64')

		return delta/(24*60*60*1e9)

if __name__ == "__main__":

	times = TimeSpan.get((datetime.date(2021,1,1),datetime.date(2021,2,1)))

	print(times.array.iloc[1])