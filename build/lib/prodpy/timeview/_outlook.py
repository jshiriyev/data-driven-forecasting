from ._template import Template

class Outlook(Template):

	def __init__(self,*args,leadhead:str=None,datehead:str=None,**kwargs):
		"""Initializes the parent class Template."""
		super().__init__(*args,**kwargs)

		self(leadhead=leadhead,datehead=datehead)

	def __call__(self,*,leadhead:str=None,datehead:str=None):

		self._leadhead = leadhead
		self._datehead = datehead

		return self

	@property
	def leadhead(self):
		return self._leadhead

	@property
	def datehead(self):
		return self._datehead

	def heads(self,*args,**kwargs):
		"""Returns the heads that are in the frame and uses select_dtype arguments."""
		return list(set(self.dheads(*args)+self.dtypes(**kwargs)))

	def dheads(self,*args):
		"""Returns the list of arguments ensuring that they are in the DataFrame."""
		return [head for head in args if head in self._frame.columns]

	def dtypes(self,include=None,exclude=None):
		"""Returns the list of heads by including & excluding the dtypes."""
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

	def unique(self,*args):
		"""Returns the list of unique leads for the given column names."""
		return self.__leads(*args).unique().tolist()

	def toview(self,*args):
		"""Returns Template instance where the leadhead and datehead are defined."""

		if self._datehead is None:
			raise KeyError('Datehead has not been defined!')

	def __leadcolumn(self,*args):
		"""Returns leadhead and leads for the given heads in args."""
		leadhead,leads = self.__leadhead(*args),self.__leads(*args)

		return "Aggregate","" if leadhead is None and leads.empty else leadhead,leads

	def __leadhead(self,*args):
		"""Returns the leadhead based on arguments."""
		dataheads = self.dheads(*args)

		if len(dataheads)==0:
			return

		return " ".join(dataheads)

	def __leads(self,*args):
		"""Returns the leads based on arguments."""
		dataheads = self.dheads(*args)

		if len(dataheads)==0:
			return self.__series()

		return self._frame[dataheads].astype("str").agg(" ".join,axis=1)

	def __toview(self,*args):
		"""Returns Template instance where the leadhead and datehead are defined."""
		frame = self.pull(self._datehead,include=('number',))

		column = self.__leadcolumn(*args)

		frame.insert(0,*column)

		group = frame.groupby([column[0],self._datehead])

		frame = group.sum(self.numbers).reset_index()

		return Template(frame,leadhead=column[0],datehead=self._datehead)

if __name__ == "__main__":

	import pandas as pd

	frame = pd.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	view = Outlook(frame)

	print(view.datetimes)

	print(view.mindate('Date'),type(view.mindate('Date')))
	print(view.maxdate('Date'))

	# print(view.mindate('Date').date())

	# print(Outlook.unique(df,'Field'))
	# print(type(Outlook.unique(df,'Field').tolist()))



