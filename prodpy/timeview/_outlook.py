import datetime

import pandas

from ._timeview import TimeView

class Outlook(TimeView):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	def heads(self,*args,include=None,exclude=None):
		"""Returns the list of heads including the dtypes in include, excluding the
		dtypes in exclude and safely dropping heads in args."""

		dtypes = self._frame.select_dtypes(
			include = include,
			exclude = exclude,
			)

		heads = dtypes.columns

		for head in args:
			try:
				heads = heads.drop(head)
			except KeyError:
				pass

		return heads.tolist()

	def leads(self,*args):
		"""Returns series of items for the given groupkeys."""
		return self[list(args)].agg(' '.join,axis=1)

	@property
	def datetimes(self):
		"""Returns the list of column names with datetime format."""
		return self.heads(include=('datetime64',))

	@property
	def numbers(self):
		"""Returns the list of column names with number format."""
		return self.heads(include=('number',))
	
	@property
	def nominals(self):
		"""Returns the list of column names that are categorical by nature."""
		return self.heads(exclude=('number','datetime64'))

	def minors(self,*args):
		"""Return the list of column names with number format, excluding the columns of args."""
		return self.heads(*args,include=('number',))

	def items(self,*args):
		"""Returns the list of items for the given column names."""
		return self.leads(*args).unique().tolist()

	def view(self,*args):
		"""Returns a new frame with the given groupkey (merged args) in the first column,
		date in the second column, and number columns in the rest."""

		leads = self.leads(*args)

		if leads.empty:
			return TimeView()

		dhead = self.datehead

		frame = self[[dhead,*self.numbers]]

		if frame.empty:
			return TimeView()

		hline = "_".join(args)

		pivot = [hline,dhead]

		frame[hline] = leads

		frame = frame[[*pivot,*self.numbers]]
		frame = frame.groupby(pivot).sum(self.numbers)
		frame = frame.reset_index()

		return TimeView(frame)(dhead,hline)

if __name__ == "__main__":

	frame = pandas.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.datetimes)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.items(df,'Field'))
	# print(type(Outlook.items(df,'Field').tolist()))



