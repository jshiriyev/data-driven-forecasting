import datetime

import pandas

from ._refined import Refined

class Outlook():

	def __init__(self,frame:pandas.DataFrame=None):

		self._frame = frame

	@property
	def frame(self):
		return self._frame
	
	@property
	def dates(self):
		"""Returns column names with datetime format."""
		return [] if self.frame is None else self.frame.select_dtypes(
			include=('datetime64',)).columns.tolist()

	@property
	def numbers(self):
		"""Returns column names with number format."""
		return [] if self.frame is None else self.frame.select_dtypes(
			include=('number',)).columns.tolist()
	
	@property
	def groups(self):
		"""Returns column names that are categorical by nature."""
		return [] if self.frame is None else self.frame.select_dtypes(
			exclude=('number','datetime64')).columns.tolist()

	def items(self,groupkey:str=None):
		"""Returns list of items in the given column specified with groupkey."""
		return [] if self.frame is None or groupkey is None else self.frame[groupkey].unique().tolist()

	def secondary(self,*args):
		"""Return columns with number excluding the arg columns."""
		if self.frame is None:
			return []

		columns = self.frame.select_dtypes(
			include=('number',)).columns

		keys = [arg for arg in args if arg is not None]

		return columns.drop(keys).tolist()

	def refine(self,*args,groupkey:str=None,datekey:str=None):
		"""Groupby (groupkey), and sumup (args) input frame, returning a new frame
		with the given groupkey in the first column, date in the second column, and
		argument columns in the remaining columns."""

		datekey = self.datekey(datekey)

		if self._frame is None or groupkey is None or datekey is None:
			return self

		numbers = self.numbers if len(args)==0 else list(args)

		columns = [groupkey,datekey]+numbers

		frameGroup = self.frame[columns].groupby([groupkey,datekey])

		return Refined(frameGroup.sum(numbers).reset_index())

	def datekey(self,datekey=None):

		if datekey is not None:
			return datekey

		if len(self.dates)>0:
			return self.dates[0]

	def limits(self,datekey=None):

		return (self.mindate(datekey),self.maxdate(datekey))

	def mindate(self,datekey=None):

		datekey = self.datekey(datekey)

		if self._frame is None or datekey is None:
			return datetime.date(2020,1,1)

		return self._frame[datekey].min().date()

	def maxdate(self,datekey=None):

		datekey = self.datekey(datekey)

		if self._frame is None or datekey is None:
			return datetime.date(2020,6,1)

		return self._frame[datekey].max().date()

	@staticmethod
	def argNoneFlag(*args):

		for arg in args:
			if arg is None:
				return True

		return False

if __name__ == "__main__":

	frame = pandas.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.dates)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.items(df,'Field'))
	# print(type(Outlook.items(df,'Field').tolist()))



