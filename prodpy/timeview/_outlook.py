import datetime

import pandas

class Outlook():

	def __init__(self,frame:pandas.DataFrame=None):
		self._frame = frame

	@property
	def frame(self):
		return self._frame

	def __iter__(self):

		for item in self.items(self.groupkey):
			yield self.filter(**{self.groupkey:item}).frame

	def __call__(self,groupkey):

		self.groupkey = groupkey

		return self
	
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

	def plottable(self,*args):
		"""Return columns with number excluding the arg columns."""
		if self.frame is None:
			return []

		columns = self.frame.select_dtypes(
			include=('number',)).columns

		keys = [arg for arg in args if arg is not None]

		return columns.drop(keys).tolist()

	def get_group(self,groupkey:str,datekey:str,*args):
		"""Groupby (groupkey), and sumup (args) input frame, returning a new frame
		with the given groupkey in the first column, date in the second column, and
		argument columns in the remaining columns."""
		outlook = self.groupby(groupkey,datekey)

		return outlook.sumup(*args).frame

	def get_item(self,datekey:str,*args,**kwargs):
		"""Groupby (kwargs.groupkey), sumup (args) and filters (kwargs.value) input frame
		based on groupkey-value pair of the first optional argument, returning a new frame
		with the given value in the first column, date in the second column, and
		argument columns in the remaining columns."""
		for groupkey,value in kwargs.items():
			break

		outlook = self.groupby(groupkey,datekey)
		outlook = outlook.sumup(*args)

		print(outlook.frame)

		return outlook.filter(**kwargs).frame

	def groupby(self,*args,datekey:str=None):
		"""Groupby the frame for the groupkey (args) and datekey."""
		return self if self.frame is None or datekey is None else Outlook(
			self.frame.groupby(list(args)+[datekey]))

	def sumup(self,*args):
		"""Sums the number columns (args) of grouped frame and resets the index."""
		return Outlook(self.frame[list(args)].sum().reset_index())

	def filter(self,**kwargs):
		"""Filters input frame based on the first positional groupkey-value pair."""
		for groupkey,value in kwargs.items():
			break

		return Outlook(self.frame[self.frame[groupkey]==value].reset_index(drop=True))

	def limits(self,datekey=None):

		if self._frame is None or datekey is None:
			mindate = datetime.date(2020,1,1)
			maxdate = datetime.date(2020,6,1)
		else:
			mindate = self._frame[datekey].min().date()
			maxdate = self._frame[datekey].max().date()

		return (mindate,maxdate)

	def mindate(self,datekey=None):
		if self._frame is None or datekey is None:
			return datetime.date(2020,1,1)
		return self._frame[datekey].min().date()

	def maxdate(self,datekey=None):
		if self._frame is None or datekey is None:
			return datetime.date(2020,6,1)
		return self._frame[datekey].max().date()

if __name__ == "__main__":

	frame = pandas.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.dates)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.items(df,'Field'))
	# print(type(Outlook.items(df,'Field').tolist()))



