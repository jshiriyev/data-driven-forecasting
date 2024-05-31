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

	def leadhead(self,*args):
		"""by ensure that the provided heads are in the DataFrame"""
		return " ".join([head for head in args if head in self.frame.columns])

	def leads(self,*args):
		"""Returns series of items for the given groupkeys."""
		return self.get(list(args)).astype("str").agg(" ".join,axis=1)

	def items(self,*args):
		"""Returns the list of unique leads for the given column names."""
		return self.leads(*args).unique().tolist()

	def _toview(self,*args):
		"""Returns a new frame with the given groupkey (merged args) in the first column,
		date in the second column, and number columns in the rest."""

		frame = self.get([self.datehead,*self.numbers])

		if frame.empty:
			return TimeView(frame)

		if len(args)==0:

			group = frame.groupby([self.datehead])
			frame = group.sum(self.numbers)
			frame = frame.reset_index()

			return TimeView(frame)("Cum.",self.datehead)

		leads = self.leads(*args)

		if leads.empty:
			return TimeView()

		leadhead = " ".join(args)

		frame.loc[:,(leadhead,)] = leads

		group = frame.groupby([leadhead,self.datehead])
		frame = group.sum(self.numbers)
		frame = frame.reset_index()

		return TimeView(frame)(leadhead,self.datehead)

	def toview(self,*args):

		heads = [head for head in args if head in self.frame.columns]

		leadhead = " ".join(heads)

		leadhead = list(leadhead if len(leadhead)==0 else [leadhead])
		datehead = list([self.datehead])

		leads =  self.frame[heads].astype("str").agg(" ".join,axis=1)

		# Select numeric columns
		numheads = frame.select_dtypes(include=['number']).columns.tolist()

		if len(leadhead)>0:
			frame.insert(0,leadhead[0],leads)

		sidehead = leadhead+datehead

		keephead = sidehead+numheads

		# Select combined heads and numeric columns, ensuring no duplicates
		frame = frame[keephead]

		# Group the frame based on heads
		group = frame.groupby(sidehead)

		frame = group.sum(numheads)

		return TimeView(frame.reset_index())(leadhead[0],datehead[0])

if __name__ == "__main__":

	import pandas as pd

	frame = pd.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.datetimes)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.items(df,'Field'))
	# print(type(Outlook.items(df,'Field').tolist()))



