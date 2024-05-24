import datetime

import numpy
import pandas

from ._limit import Limit

class Interval():

	def __init__(self,*args):

		self.limits = args

	def __iter__(self):

		for limit in self.limits:
			yield limit

	def dates(self,**kwargs):

		index = pandas.DatetimeIndex([])

		for limit in self.limits:
			index.append(limit.dates(**kwargs))

		return index.to_series()

	def bools(self,datetimes:pandas.Series):
		"""Returns the bools for the interval that is in between
		start and end dates."""

		array = numpy.zeros(datetimes.size,dtype='bool')

		for limit in self.limits:

			among = limit.bools(datetimes)

			array = numpy.logical_or(
				array,among
				)

		return array
