import datetime

from ._model import Model

from ._forward import Forward

from ._optimize import Optimize

class Analysis():

	def __init__(self,datekey,ratekey,**kwargs):
		"""
		Initializing decline analysis with date and rate column keys.
		The rate values is used for decline calculations.
		
		Other rate arguments may include following keys:

		orate 	: oil rate
		grate 	: gas rate
		wrate 	: water rate

		lrate	: Liquid Rate
		wcut 	: Water Cut
		gor 	: Gas-Oil Ratio
		"""
		self._datekey = datekey
		self._ratekey = ratekey

		for key,value in kwargs.items():
			setattr(self,key,value)

	def fit(self,frame,start:datetime.date=None,end:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the rates."""

		days,rates = self.derive(frame,start=start,end=end)

		return Optimize(days).minimize(rates,**kwargs)

	def derive(self,frame,**kwargs):
		"""Returns new frame that is in the range of start and end dates and newly added days."""

		frame = self.trim(frame[self.keys],**kwargs)

		days = Model.datetime2day(frame[self.datekey])

		rates = frame[self.ratekey].to_numpy()

		return days,rates

	def trim(self,frame,start:datetime.date=None,end:datetime.date=None):
		"""Trims the frame for the start and end dates.
		
		start 	: start date when to start analysis
		end 	: end date when to end analysis

		Returns the trimmed dataframe.
		"""
		if start is not None:
			frame = frame[frame[self.heads.dates].dt.date>=start]

		if end is not None:
			frame = frame[frame[self.heads.dates].dt.date<=end]

		return frame

	@property
	def datekey(self):
		return self._datekey

	@property
	def ratekey(self):
		return self._ratekey

	@property
	def keys(self):
		return [self._datekey,self._ratekey]
	
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