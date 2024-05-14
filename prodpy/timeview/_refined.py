import pandas

class Refined():

	def __init__(self,frame:pandas.DataFrame):

		self._frame = frame

	@property
	def frame(self):
		return self._frame

	@property
	def key(self):
		return self._frame.columns[0]

	def __iter__(self):

		for item in self.items:
			yield self.filter(item)

	def filter(self,value):
		"""Filters input frame based on the first positional groupkey-value pair."""

		frame = self._frame[self._frame[self.key]==value]

		return frame.reset_index(drop=True).drop([self.key],axis=1)

	@property
	def items(self):
		"""Returns list of items in the given frame container."""
		return self._frame[self.key].unique().tolist()

	@property
	def limit(self):
		return (self.mindate,self.maxdate)

	@property
	def mindate(self):
		return self._frame.iloc[:,2].min().date()

	@property
	def maxdate(self):
		return self._frame.iloc[:,2].max().date()
	
	
	
	


