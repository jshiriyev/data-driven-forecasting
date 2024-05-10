import datetime

from ._model import Model

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

	def __call__(self):

		pass

	def fit(self,frame,start:datetime.date=None,cease:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the rates."""

		days,rates = self.derive(frame,start=start,cease=cease)

		return Optimize(days).minimize(rates,**kwargs)

	def derive(self,frame,**kwargs):
		"""Returns new frame that is in the range of start and cease dates and newly added days."""

		frame = self.trim(frame[self.keys],**kwargs)

		days = Model.datetime2day(frame[self.datekey])

		rates = frame[self.ratekey].to_numpy()

		return days,rates

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