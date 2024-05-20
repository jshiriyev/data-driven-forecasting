import datetime

import pandas

class Outlook():

	_mindate = datetime.date(2020,1,1)
	_maxdate = datetime.date(2030,1,1)

	def __init__(self,frame:pandas.DataFrame):
		self._frame = frame

	def __call__(self,datehead:str):
		self._datehead = datehead

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

		for head in args:
			try:
				columns = columns.drop(head)
			except KeyError:
				pass

		return columns.tolist()

	def view(self,*args,numbers:list[str]=None):
		"""Returns a new frame with the given groupkey (merged args) in the first column,
		date in the second column, and number columns in the rest."""

		try:
			datehead = self._datehead
		except AttributeError:
			raise Warning("Date head needs to be defined to group the data.")

		if len(args)==0:
			raise Warning("At least one group head should be provided.")

		if numbers is None:
			numbers = self.numbers

		batch = "_".join(args)

		groupby = [batch,self._datehead]
		blended = self._frame[list(args)].agg(' '.join,axis=1)

		self._frame[batch] = blended

		frameGroup = self._frame[groupby+numbers].groupby(groupby)

		return frameGroup.sum(numbers).reset_index()

	@property
	def mindate(self):
		"""Returns the smallest datetime.date observed in the date column."""

		try:
			datehead = self._datehead
		except AttributeError:
			return self._mindate

		try:
			dates = self._frame[datehead]
		except KeyError:
			return self._mindate

		return dates.min().date()-datetime.timedelta(days=1)

	@property
	def maxdate(self):
		"""Returns the largest datetime.date observed in the date column."""

		try:
			datehead = self._datehead
		except AttributeError:
			return self._maxdate

		try:
			dates = self._frame[datehead]
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



