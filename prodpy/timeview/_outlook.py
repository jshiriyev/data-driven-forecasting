from ._timeview import TimeView

class Outlook(TimeView):

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

	def heads(self,*args,**kwargs):
		"""Returns the heads that are in the frame and uses select_dtype arguments."""
		return list(set(self.dheads(*args)+self.dtypes(**kwargs)))

	def dheads(self,*args):
		"""Returns the list of arguments ensuring that they are in the DataFrame."""
		return [head for head in args if head in self._frame.columns]

	def dtypes(self,include=None,exclude=None):
		"""Returns the list of heads including the dtypes in include,
		excluding the dtypes in exclude."""
		return [] if include is None and exclude is None else self._frame.select_dtypes(
			include=include,exclude=exclude).columns.tolist()

	def pull(self,*args,**kwargs):
		"""Returns a frame given in the args and included and excluded dtypes."""
		return self._frame[self.heads(*args,**kwargs)]

	def drop(self,*args,**kwargs):
		"""Returns a frame after dropping args, including and excluding dtypes."""
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

	def leads(self,*args):
		"""Returns the leadhead and leads."""
		dheads = self.dheads(*args)

		column = 'Aggregate' if len(dheads) == 0 else " ".join(dheads)
		
		series = self.frame[dheads].astype("str")
		series = series.agg(" ".join,axis=1)

		return column,series

	def items(self,*args):
		"""Returns the list of unique leads for the given column names."""
		return self.leads(*args).unique().tolist()

	def toview(self,*args):
		"""Returns TimeView instance where the leadhead and datehead are defined."""

		column,series = self.leads(*args)

		frame = self.pull(self._datehead,include=('number',))
		frame.insert(0,column,series)

		group = frame.groupby([column,self._datehead])

		frame = group.sum(frame.columns[2:].tolist())

		timeview = TimeView(frame.reset_index())

		return timeview(column,self._datehead)

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



