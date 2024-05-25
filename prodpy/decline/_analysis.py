import datetime

import numpy
import pandas

from ._model import Model

from ._timespan import TimeSpan

from ._forward import Forward

from ._optimize import Optimize

class Analysis():

	def __init__(self,datehead,ratehead):
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
		return [self._datehead,self._ratehead]

	def __call__(self,frame):

		self.frame = frame

		return self

	@property
	def title(self):
		return self._title
	
	@property
	def limit(self):
		return self._limit
	
	def fit(self,start:datetime.date=None,end:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the rates."""

		dates = self.frame[self.datehead]

		date0 = self.get_date0(dates,start)
		bools = self.get_bools(dates,start,end)

		mdays = self.get_days(dates[bools],date0)
		
		rates = self.frame[self.ratehead][bools].to_numpy()

		return Optimize(**kwargs).fit(mdays,rates,date0=date0)

	def run(self,model:Model,**kwargs):
		"""Forecasts the rates based on the model, and for the pandas.date_range parameters."""

		try:
			dates = self.get_datetimes(**kwargs)
		except ValueError:
			dates = self.get_datetimes(start=model.date0,**kwargs)

		cdays = self.get_days(dates,start=model.date0)
		rates = self.get_rates(model,cdays)

		return {"dates":dates,"rates":rates}

	@staticmethod
	def get_datetimes(**kwargs):

		return pandas.date_range(**kwargs)

	@staticmethod
	def get_rates(model,days):

		return Forward(model).run(days)

	@staticmethod
	def get_date0(dates:pandas.Series,start:datetime.date=None):
		"""Returns the first date based on start and dates."""
		return dates.iloc[0].date() if start is None else start

	@staticmethod
	def get_dateL(dates:pandas.Series,end:datetime.date=None):
		"""Returns the last date based on end and dates."""
		return dates.iloc[-1].date() if end is None else end

	@staticmethod
	def get_bools(dates:pandas.Series,start:datetime.date=None,end:datetime.date=None):
		"""Returns the bools for the interval that is in between start and end dates."""
		upper = Analysis.get_bools_upper(dates,start)
		lower = Analysis.get_bools_lower(dates,end)

		return numpy.logical_and(upper,lower)

	@staticmethod
	def get_bools_upper(dates:pandas.Series,start:datetime.date=None):
		"""Returns the bools for the interval that is after the start date."""
		return numpy.ones(dates.shape,dtype='bool') if start is None else (dates.dt.date>=start).to_numpy()

	@staticmethod
	def get_bools_lower(dates:pandas.Series,end:datetime.date=None):
		"""Returns the bools for the interval that is before the end date."""
		return numpy.ones(dates.shape,dtype='bool') if end is None else (dates.dt.date<=end).to_numpy()

	@staticmethod
	def get_days(dates:pandas.Series,start:datetime.date=None):
		"""Returns days calculated from the dates and start date."""
		start = numpy.datetime64(Analysis.get_date0(dates,start))

		delta = (dates-start)
		delta = delta.to_numpy()
		delta = delta.astype('timedelta64[ns]')
		delta = delta.astype('float64')

		return delta/(24*60*60*1e9)

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