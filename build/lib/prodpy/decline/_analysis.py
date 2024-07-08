import datetime

import pandas

from ._model import Model

from ._timespan import TimeSpan

from ._forward import Curve

from ._optimize import Optimize

class Analysis():

	def __init__(self,datehead:str,ratehead:str):
		"""Initializing the class with date and rate column keys. The date and rate
		values are used for the optimization and forecasting of pandas.DataFrames."""

		self._datehead = datehead
		self._ratehead = ratehead

	@property
	def datehead(self):
		return self._datehead

	@property
	def ratehead(self):
		return self._ratehead

	@property
	def keys(self):
		return list((self._datehead,self._ratehead))
	
	def fit(self,frame:pandas.DataFrame,*args,**kwargs):
		"""Returns optimized model that fits the frame and fit-score (optionally)"""

		return self.ufit(frame,*args,**kwargs)

	def ufit(self,frame:pandas.DataFrame,*args,date0:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the frame and fit-score (optionally)"""

		dates = TimeSpan(frame[self.datehead])

		rates = frame[self.ratehead].to_numpy()

		bools = dates.iswithin(*args)

		dates = dates[bools]
		rates = rates[bools]

		date0 = dates.mindate if date0 is None else date0

		days  = dates.days(date0)

		return Optimize(**kwargs).fit(days,rates,date0)

	def mfit(self,view,*args,**kwargs):
		"""Returns optimized model dictionary that fits the frames."""

		return {item:self.ufit(frame,*args,**kwargs) for item,frame in view}

	def run(self,model:Model,*args,**kwargs):
		"""Forecasts the rates based on the model, and for the pandas.date_range parameters."""

		dates = TimeSpan.get(*args,**kwargs)

		return self.urun(dates.series,model)

	def urun(self,dates:pandas.Series,model:Model):

		days  = TimeSpan(dates).days(model.date0)

		rates = Curve(model).run(days)
		rates = pandas.Series(rates)

		dictionary = {
			self.datehead: dates,
			self.ratehead: rates,
			}

		return pandas.DataFrame(dictionary)

	def mrun(self,models:dict,*args,**kwargs):

		dates = TimeSpan.get(*args,**kwargs)

		for index,(name,model) in enumerate(models.items(),start=1):

			minor = self.urun(dates.series,model)

			minor.insert(0,'Names',name)

			frame = minor.copy() if index==1 else pandas.concat([frame,minor])

		return frame.reset_index(drop=True)

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

	# print(
	# 	Curve.days(5)
	# 	)

	# print(
	# 	Curve.days(datetime.date(2022,2,3),datetime.date(2022,2,7))
	# 	)

	# print(
	# 	Curve.days(datetime.date(2022,2,3),datetime.date(2022,2,7),12)
	# 	)