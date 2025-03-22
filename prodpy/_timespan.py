import datetime

import numpy as np
import pandas as pd

class TimeSeries():
	"""A class to represent a time series with enforced sorting."""

	def __init__(self,series:pd.Series):
		"""Initializes the TimeSeries object and ensures the series is sorted."""
		self._series = series.sort_values().reset_index(drop=True)

	@property
	def series(self):
		"""Returns the sorted time series."""
		return self._series

	def __getitem__(self,key):
		"""Returns a new TimeSeries object with a subset of the data.
		
		key: Indexing key to retrieve a subset of the series.

        Returns:
        -------
        TimeSeries: A new TimeSeries object containing the subset.

		"""
		return TimeSeries(self._series[key])

	@property
	def mindate(self):
		"""Returns the first date."""
		return self._series.iloc[0].date()

	@property
	def maxdate(self):
		"""Returns the last date."""
		return self._series.iloc[-1].date()

	@property
	def limit(self):
		"""Returns the limits (min,max) in the span."""
		return (self.mindate,self.maxdate)
	
	@property
	def size(self):
		"""Returns the size of the time-series."""
		return self._series.size

	def subtract(self,date:datetime.date):
		"""Returns the days passed after the date."""
		delta = self._series-np.datetime64(date)
		delta = delta.to_numpy()
		delta = delta.astype('timedelta64[ns]')
		delta = delta.astype('float64')

		return delta/(24*60*60*1e9)

	def within(self,*args):
		"""Returns a subset of the TimeSeries where values satisfy the 'iswithin' condition."""
		return self[self.iswithin(*args)]

	def iswithin(self,*args):
		"""Returns the bools for the interval that is within multiple date limits."""
		bools = np.zeros(self.size,dtype='bool')

		for start,end in args:
			later = self.islater(start)
			prior = self.isprior(end)
			bools = np.logical_or(bools,np.logical_and(later,prior))

		return bools

	def prior(self,date:datetime.date):
		"""Returns the dates that are prior to the date."""
		return self[self.isprior(date)]
	
	def isprior(self,date:datetime.date):
		"""Returns the bools for the datetimes that is prior to the date."""
		return (self.series.dt.date<=date).to_numpy()

	def later(self,date:datetime.date):
		"""Returns the dates that are later than the specified date."""
		return self[self.islater(date)]

	def islater(self,date:datetime.date):
		"""Returns the bools for the datetimes that is later than the date."""
		return (self.series.dt.date>=date).to_numpy()

	@staticmethod
	def get(*args,**kwargs):
		"""Constructs a TimeSeries object from multiple date limits.
		
		Parameters:
		----------
        *args    : Tuples of (start, end) date limits.
        **kwargs : Additional keyword arguments for `pd.date_range`.

        Returns:
        -------
        TimeSeries: A TimeSeries object containing the combined date ranges.
		
		"""
		index = pd.DatetimeIndex([])

		for start,end in args:

			space = pd.date_range(start=start,end=end,**kwargs)
			index = index.append(space)

		return TimeSeries(pd.Series(index).reset_index(drop=True))

if __name__ == "__main__":

	span = TimeSeries.get(
		(datetime.date(2021,1,1),datetime.date(2021,2,1)),
		(datetime.date(2024,1,1),datetime.date(2024,2,1)),
		periods=4
	)

	print(span.series)