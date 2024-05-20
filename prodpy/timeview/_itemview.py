import datetime

import pandas

class ItemView():

	_mindate = datetime.date(2020,1,1)
	_maxdate = datetime.date(2030,1,1)

	def __init__(self,frame:pandas.DataFrame):
		"""
		The frame needs to be structured pandas dataframe, where:

			1st column shows batch items
			2nd column shows datetimes
			3rd column and the rest shows columns in number format.

		The class contains properties and a method that simplifies the
		data visualization process.
		"""
		self._frame = frame

	@property
	def frame(self):
		return self._frame

	@property
	def empty(self):
		return self._frame.empty
	
	@property
	def batch(self):
		return None if self.empty else self._frame.columns[0]

	def __iter__(self):

		for item in self.items:
			yield self.filter(item)

	def filter(self,item):
		"""Filters and returns frame based on the item in the batch column."""

		if self.empty:
			return self._frame

		conds = self._frame[self.batch]==item
		frame = self._frame[conds]

		frame = frame.reset_index(drop=True)
		frame = frame.drop([self.batch],axis=1)

		frame.title = item.replace("_"," ")

		return frame

	@property
	def items(self):
		"""Returns list of items in the given frame container."""
		return [] if self.empty else self._frame[self.batch].unique().tolist()

	@property
	def mindate(self):
		"""Returns the earliest date of the frame. If the frame is empty,
		the class attribute is returned."""

		if self.empty:
			return self._mindate

		_mindate = self._frame.iloc[:,2].min().date()

		return _mindate-datetime.timedelta(days=1)

	@property
	def maxdate(self):
		"""Returns the latest date of the frame. If the frame is empty,
		the class attribute is returned."""
		
		if self.empty:
			return self._maxdate

		_maxdate = self._frame.iloc[:,2].max().date()

		return _maxdate+datetime.timedelta(days=1)

	@property
	def limit(self):
		"""Returns the earliest and latest dates of the frame. If the
		frame is empty, the class attributes are returned."""
		return (self.mindate,self.maxdate)
	
	
	
	


