from ._timeview import TimeView

class Tableau(TimeView):

	def __init__(self,*args,**kwargs):
		"""
		The frame needs to be structured pandas dataframe, where:

			1st column shows heading items
			2nd column shows datetimes
			3rd column and the rest shows columns in number format.

		The class contains properties and a method that simplifies the
		data visualization process.
		"""
		super().__init__(*args,**kwargs)

	def __iter__(self):

		for item in self.items:
			yield self.view(item)

	@property
	def num(self):
		return len(self.items)

	def view(self,item):
		"""Filters and returns frame based on the item in the heading column."""

		if self.leads.empty:
			return TimeView()(self.leadhead,self.datehead)

		frame = self.get(self.leads==item)

		if frame.empty:
			return TimeView()(self.leadhead,self.datehead)

		frame = frame.reset_index(drop=True)

		return TimeView(frame)(self.leadhead,self.datehead)