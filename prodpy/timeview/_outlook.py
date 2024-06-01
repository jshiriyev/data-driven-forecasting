from ._timeview import TimeView

class Outlook(TimeView):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	def heads(self,*args,**kwargs):
		return list(set(self.dheads(*args)+self.dtypes(**kwargs)))

	def dheads(self,*args):
		"""Returns the list of arguments ensuring that they are in the DataFrame."""
		return [head for head in args if head in self._frame.columns]

	def dtypes(self,include=None,exclude=None):
		"""Returns the list of heads including the dtypes in include,
		excluding the dtypes in exclude"""
		return [] if include is None and exclude is None else self._frame.select_dtypes(
			include=include,exclude=exclude).columns.tolist()

	def pull(self,*args,**kwargs):
		"""Returns a frame given in the args and included and excluded dtypes."""
		return self._frame[self.heads(*args,**kwargs)]

	def drop(self,*args,**kwargs):
		"""Returns a frame after dropping args and included and excluded dypes."""
		return self._frame.drop(self.heads(*args,**kwargs),axis=1)

	@property
	def datetimes(self):
		"""Returns the list of column names with datetime format."""
		return self.dtypes(include=('datetime64',))

	@property
	def numbers(self):
		"""Returns the list of column names with number format."""
		return self.dtypes(include=('number',))

	@property
	def nominals(self):
		"""Returns the list of column names that are categorical by nature."""
		return self.dtypes(exclude=('number','datetime64'))

	def leadhead(self,*args):
		"""by ensure that the provided heads are in the DataFrame"""
		return " ".join(self.dheads(*args))

	def leads(self,*args):
		"""Returns series of items for the given groupkeys."""

		heads = self.heads(*args)

		if len(heads)==0:
			return pandas.Series(['Amount']*self._frame.shape[0],name='Aggregate')

		series = self.pull(*args).astype("str").agg(" ".join,axis=1)

		series.name = self.leadhead(*args)

		return series

	def items(self,*args):
		"""Returns the list of unique leads for the given column names."""
		return self.leads(*args).unique().tolist()

	def toview(self,*args):
		"""Returns TimeView instance where the leadhead and datehead are defined."""

		leads = self.leads(*args)

		frame = self.pull(self._datehead,include=('number',))
		frame.insert(0,leads.name,leads.values)

		group = frame.groupby([leads.name,self._datehead])

		frame = group.sum(frame.columns[2:].tolist())

		return TimeView(frame.reset_index())(leads.name,self._datehead)

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



