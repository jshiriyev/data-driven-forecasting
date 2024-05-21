import datetime

import pandas

from ._timeview import TimeView

class ItemView(TimeView):

	def __init__(self,frame:pandas.DataFrame):
		"""
		The frame needs to be structured pandas dataframe, where:

			1st column shows heading items
			2nd column shows datetimes
			3rd column and the rest shows columns in number format.

		The class contains properties and a method that simplifies the
		data visualization process.
		"""
		super().__init__(frame)
	
	@property
	def heading(self):
		return None if self.empty else self._frame.columns[0]

	@property
	def items(self):
		"""Returns list of items in the given frame container."""
		return [] if self.empty else self._frame[self.heading].unique().tolist()

	def __iter__(self):

		for item in self.items:
			yield self.filter(item)

	def filter(self,item):
		"""Filters and returns frame based on the item in the heading column."""

		frame = self._frame

		if not self.empty:
			frame = frame[frame[self.heading]==item]
			frame = frame.reset_index(drop=True)
			frame = frame.drop([self.heading],axis=1)

		timeview = TimeView(frame)(self._datehead)

		timeview.title = item.replace("_"," ")

		return timeview
	
	
	
	


