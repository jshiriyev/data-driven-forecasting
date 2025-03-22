from ._frameutils import utils

from ._template import Template

class Outlook(Template):

	def __init__(self,*args,leadhead:str=None,datehead:str=None):
		"""Initializes the parent class Template."""
		super().__init__(*args)

		self(leadhead=leadhead,datehead=datehead)

	def heads(self,*args,**kwargs):
		"""Returns the heads that are in the frame and uses select_dtype arguments."""
		return utils.heads(self.frame,*args,**kwargs)

	def pull(self,*args,**kwargs):
		"""Returns a frame given in the args and included and excluded dtypes."""
		return self._frame[self.heads(*args,**kwargs)]

	def drop(self,*args,**kwargs):
		"""Returns a frame after dropping args, including and excluding dtypes."""
		return self._frame.drop(self.heads(*args,**kwargs),axis=1)

	@property
	def datetimes(self):
		"""Returns the list of column names with datetime format."""
		return utils.heads(self.frame,include=('datetime64',))

	@property
	def numbers(self):
		"""Returns the list of column names with number format."""
		return utils.heads(self.frame,include=('number',))

	@property
	def nominals(self):
		"""Returns the list of column names that are categorical by nature."""
		return utils.heads(self.frame,exclude=('number','datetime64'))

	def unique(self,*args):
		"""Returns the list of unique leads for the given column names."""
		return self.__leads(*args).unique().tolist()

	def view(self,*args):
		"""Returns Template instance where the leadhead and datehead are defined."""

		if self._datehead is None:
			raise KeyError('Datehead has not been defined!')

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



