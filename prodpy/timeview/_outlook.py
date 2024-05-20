import datetime

import pandas

from ._visualized import View

class Outlook():

	_mindate = datetime.date(2020,1,1)
	_maxdate = datetime.date(2030,1,1)

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

		if len(args)==0:
			raise Warning("At least one group key should be provided.")

		group_key = "_".join(args)

		self._frame[group_key] = self._frame[list(args)].agg(' '.join,axis=1)

		by = [group_key,self._datekey]

		frameGroup = self._frame[by+numbers].groupby(by)

		return View(frameGroup.sum(numbers).reset_index())

	@property
	def mindate(self):
		"""Returns the smallest datetime.date observed in the date column."""

		try:
			datekey = self._datekey
		except AttributeError:
			return self._mindate

		try:
			dates = self._frame[datekey]
		except KeyError:
			return self._mindate

		return dates.min().date()-datetime.timedelta(days=1)

	@property
	def maxdate(self):
		"""Returns the largest datetime.date observed in the date column."""

		try:
			datekey = self._datekey
		except AttributeError:
			return self._maxdate

		try:
			dates = self._frame[datekey]
		except KeyError:
			return self._maxdate

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



