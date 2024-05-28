import datetime

import pandas

from ._model import Model

from ._timespan import TimeSpan

from ._forward import Forward

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

	def __call__(self,frame):

		self.frame = frame

		return self

	@property
	def dates(self):
		return self.frame[self._datehead]

	@property
	def span(self):
		return TimeSpan(self.dates)

	@property
	def rates(self):
		return self.frame[self._ratehead]
	
	def fit(self,*args,date0:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the rates."""

		bools = self.span.iswithin(*args)
		
		span = self.span[bools]

		rates = self.rates[bools].to_numpy()

		date0 = span.mindate if date0 is None else date0

		return Optimize(**kwargs).fit(span.days(date0),rates,date0)

	@staticmethod
	def run(model:Model,*args,**kwargs):
		"""Forecasts the rates based on the model, and for the pandas.date_range parameters."""

		span = TimeSpan.get(*args,**kwargs)
		
		days = span.days(model.date0)

		rates = Forward(model).run(days)
		
		dictionary = {
			"Dates": span.series,
			"Rates": rates,
			}

		return pandas.DataFrame(dictionary)

	@staticmethod
	def multirun(models:dict,*args,**kwargs):

		span = TimeSpan.get(*args,**kwargs)

		frame = pandas.DataFrame(columns=['Names','Dates','Rates'])

		for name,model in models.items():

			days = span.days(model.date0)

			rates = Forward(model).run(days)

			dictionary = {
				"Names" : name,
				"Dates" : span.series,
				"Rates" : rates,
				}

			minor = pandas.DataFrame(dictionary)

			frame = pandas.concat([frame,minor])

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
	# 	Forward.days(5)
	# 	)

	# print(
	# 	Forward.days(datetime.date(2022,2,3),datetime.date(2022,2,7))
	# 	)

	# print(
	# 	Forward.days(datetime.date(2022,2,3),datetime.date(2022,2,7),12)
	# 	)