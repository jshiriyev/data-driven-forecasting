import datetime

import pandas

from ._visualized import View

class Outlook():

	def __init__(self,frame:pandas.DataFrame):
		self._frame = frame

	def __call__(self,datekey:str):
		self._datekey = datekey

		return self

	@property
	def frame(self):
		return self._frame
	
	@property
	def dates(self):
		"""Returns column names with datetime format."""
		return self._frame.select_dtypes(include=('datetime64',)).columns.tolist()

	@property
	def numbers(self):
		"""Returns column names with number format."""
		return self._frame.select_dtypes(include=('number',)).columns.tolist()
	
	@property
	def groups(self):
		"""Returns column names that are categorical by nature."""
		return self._frame.select_dtypes(exclude=('number','datetime64')).columns.tolist()

	def items(self,*args):
		"""Returns list of items for the given groupkeys."""

		try:
			group = self._frame[list(args)]
		except KeyError:
			return []

		return group.agg(' '.join,axis=1).unique().tolist()

	def minors(self,*args):
		"""Return columns with number excluding the columns of args."""

		columns = self._frame.select_dtypes(include=('number',)).columns

		for key in args:
			try:
				columns = columns.drop(key)
			except KeyError:
				pass

		return columns.tolist()

	def view(self,*args,numbers:list[str]=None):
		"""Returns a new frame with the given groupkey (merged args) in the first column,
		date in the second column, and number columns in the rest."""

		if numbers is None:
			numbers = self.numbers

		group_key = " ".join(args)

		self._frame[group_key] = self._frame[list(args)].agg(' '.join,axis=1)

		columns = [group_key,self._datekey]+numbers

		frameGroup = self._frame[columns].groupby(
			[group_key,self._datekey]
		)

		return View(frameGroup.sum(numbers).reset_index())

	@property
	def mindate(self):
		"""Returns the smallest datetime.date observed in the date column."""
		try:
			dates = self._frame[self._datekey]
		except KeyError:
			return datetime.date(2020,1,1)

		return dates.min().date()-datetime.timedelta(days=1)

	@property
	def maxdate(self):
		"""Returns the largest datetime.date observed in the date column."""
		try:
			dates = self._frame[self._datekey]
		except KeyError:
			return datetime.date(2030,1,1)

		return dates.max().date()+datetime.timedelta(days=1)

	@property
	def limit(self):
		"""Returns the datetime.date limits observed in the date column."""
		return (self.mindate,self.maxdate)

if __name__ == "__main__":

	frame = pandas.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.dates)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.items(df,'Field'))
	# print(type(Outlook.items(df,'Field').tolist()))



