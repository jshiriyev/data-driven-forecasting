import datetime

import pandas

from ._timeview import TimeView

class Outlook(TimeView):

	def __init__(self,frame:pandas.DataFrame):
		super().__init__(frame)

	@property
	def datetimes(self):
		"""Returns column names with datetime format."""
		return self._frame.select_dtypes(include=('datetime64',)).columns.tolist()

	@property
	def numbers(self):
		"""Returns column names with number format."""
		return self._frame.select_dtypes(include=('number',)).columns.tolist()
	
	@property
	def nominals(self):
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

		numbers = self.numbers if numbers is None else list(numbers)

		nominal = self._frame[list(args)]

		heading = "_".join(args)

		self._frame[heading] = nominal.agg(' '.join,axis=1)

		heading.append(self.datehead)

		frameGroup = self._frame[[*heading,*numbers]].groupby(heading)

		return frameGroup.sum(numbers).reset_index()

if __name__ == "__main__":

	frame = pandas.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.datetimes)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.items(df,'Field'))
	# print(type(Outlook.items(df,'Field').tolist()))



