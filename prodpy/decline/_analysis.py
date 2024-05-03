import pandas

from ._model import Model
from ._heads import Heads

class Analysis():

	def __init__(self,frame,heads:Heads):
		"""
		Initializing decline analysis with dataframe and column keys.

		frame 	: panda DataFrame
		
		dates 	: production dates
		orate 	: oil rates
		grate 	: gas rates
		wrate 	: water rates
		"""

		self._frame = frame
		self._heads = heads

	def fit(self,*args,**kwargs):

		start = kwargs.get('start')
		cease = kwargs.get('cease')

		if start is not None:
			_ = kwargs.pop('start')

		if cease is not None:
			_ = kwargs.pop('cease')

		days,orate = self.preprocess(*args,start,cease)

		dca = Model(days)

		return dca.fit(orate,**kwargs)

	def preprocess(self,*args,start=None,cease=None):

		frame = self.filter(*args)

		frame = self.trim(frame,start,cease)

		dates = frame[self.heads.dates]

		return dates-dates[0],frame[self.heads.orate]

	def filter(self,*args):

		frame = self.frame.groupby(args)

		return frame.groupby(self.heads.dates)[self.numericals].sum()

	def trim(self,frame,start=None,cease=None):
		"""Returns data frame that is in the range of start and cease dates.

		start 	: start date when to start analysis
		cease 	: cease date when to cease analysis
		"""

		if start is not None:
			frame = frame[frame[self.heads.dates]>=start]

		if cease is not None:
			frame = frame[frame[self.heads.dates]<=cease]

		return frame

	@property
	def frame(self):
		return self._frame

	@property
	def heads(self):
		return self._heads

	@property
	def dates(self):
		return self._frame[self._heads.dates]

	@property
	def orate(self):
		return self._frame[self._heads.orate]

	@property
	def grate(self):
		return self._frame[self._heads.grate]
	
	@property
	def wrate(self):
		return self._frame[self._heads.wrate]
	
	@property
	def lrate(self):
		return self.orate+self.wrate
	
	@property
	def wcut(self):
		return self.wrate/(self.wrate+self.orate)*100
	
	@property
	def gor(self):
		return self.grate*1000/self.orate

	@property
	def numericals(self):
		return self.frame.select_dtypes(include='number').columns

	@property
	def categorical(self):
		return self.frame.select_dtypes(exclude='number').columns
	
if __name__ == "__main__":

	import pandas as pd

	df = pd.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	print(df)

	print(df.columns)

	# print(df.groupby('Date').sum('Actual Oil, Mstb/d'))

	# print(df.columns)

	# print(df['Well'].unique())

	# print(df[df['Well']=='D32'])

	# print((df['Date']-df['Date'][0])*5)

	# print(df.head)

	# print(dir(df))