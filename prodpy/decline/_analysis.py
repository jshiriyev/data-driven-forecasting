import datetime

import pandas as pd

from ._arps import Arps

class Analysis(Arps):

	def __init__(self,*args,**kwargs):

		super().__init__(*args,**kwargs)

	def run(self,dates,*,date0:datetime.date=None,cum:bool=False):
		"""Forecasts the rates based on the model, and for the pd.date_range parameters."""

		dates = TimeSpan.get(*args,**kwargs)

		days  = dates.subtract(model.date0)

		curve = Curve(model).run(days)

		curve.set(dates=dates.series,heads=self.heads)

		return curve

	def fit(self,dates,rates,*,date0:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the frame and fit-score (optionally)"""

		rates = rates.to_numpy()
		bools = dates.iswithin(*args)

		dates,rates = dates[bools],rates[bools]

		date0 = dates.mindate if date0 is None else date0

		days  = dates.subtract(date0)

		return Optimize(**kwargs).fit(days,rates,date0)