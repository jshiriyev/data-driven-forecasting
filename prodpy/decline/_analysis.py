import pandas

from ._model import Model
from ._heads import Heads

class Analysis():

	def __init__(self,frame,dates,**kwargs):
		"""
		Initializing decline analysis with dataframe and column keys.

		frame 	: panda DataFrame
		
		dates 	: production dates
		orate 	: oil rates
		grate 	: gas rates
		wrate 	: water rates

		lrate	: Liquid Rate"
		wcut 	: Water Cut
		gor 	: Gas-Oil Ratio
		"""

		self._frame = frame

		self._heads = Heads(dates,**kwargs)

		self._rates = list(kwargs.values())

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

		frame = self.groupby(*args)

		frame = self.trim(frame,start,cease)

		dates = frame[self.heads.dates]

		return dates-dates[0],frame[self.heads.orate]

	def groupby(self,*args):

		columns = list(args)

		columns.append(self.heads.dates)

		frame_by_group = self._frame.groupby(columns)

		return frame_by_group[self.rates].sum().reset_index()

	def filter(self,frame,**kwargs):

		for key,value in kwargs.items():
			return frame[frame[key]==value]

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
	def rates(self):
		return self._rates
	
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