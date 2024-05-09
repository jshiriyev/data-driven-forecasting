import datetime

import pandas

from ._model import Model

from ._optimize import Optimize

class Analysis():

	def __init__(self,dates,**kwargs):
		"""
		Initializing decline analysis with rate column keys.
		
		dates 	: production dates
		orate 	: oil rate
		grate 	: gas rate
		wrate 	: water rate

		lrate	: Liquid Rate
		wcut 	: Water Cut
		gor 	: Gas-Oil Ratio
		"""
		self._heads = Heads(dates,**kwargs)
		self._rates = list(kwargs.values())

	def fit(self,frame,start:datetime.date=None,cease:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the rates."""

		frame = self.derive(frame,start=start,cease=cease)

		return Optimize(frame['TTimes']).minimize(frame.iloc[:,2].to_numpy(),**kwargs)

	def derive(self,frame,**kwargs):
		"""Returns new frame that is in the range of start and cease dates and newly added days."""

		frame = self.trim(frame,**kwargs)

		delta = Model.datetime2day(frame[self.heads.dates])

		return frame.assign(TTimes=delta.astype('float64'))

	def trim(self,frame,start:datetime.date=None,cease:datetime.date=None):
		"""Trims the frame for the start and cease dates.
		
		start 	: start date when to start analysis
		cease 	: cease date when to cease analysis

		Returns the trimmed dataframe.
		"""
		if start is not None:
			frame = frame[frame[self.heads.dates].dt.date>=start]

		if cease is not None:
			frame = frame[frame[self.heads.dates].dt.date<=cease]

		return frame

	def predict(self,frame,start:datetime.date=None,cease:datetime.date=None,**kwargs):
		"""Returns new frame that is in the range of start and cease dates and newly added days and
		theoretical rates."""

		frame = self.derive(frame,start=start,cease=cease)

		model = Optimize(frame['TTimes']).minimize(frame.iloc[:,2].to_numpy(),**kwargs)

		return frame.assign(TRates=model(frame['TTimes'])),model

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