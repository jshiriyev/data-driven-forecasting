import pandas

import plotly.graph_objects as go

from ._analysis import Analysis

class Diamond():

	def __init__(self,datehead:str,ratehead:str,score_flag:bool=False):
		"""Initializing the class with date and rate column keys. The date and rate
		values are used for the optimization and forecasting of pandas.DataFrames."""

		self._datehead = datehead
		self._ratehead = ratehead

		self._analysis = Analysis(*self.keys)

		self._analysis.score_flag = score_flag

	@property
	def datehead(self):
		return self._datehead

	@property
	def ratehead(self):
		return self._ratehead

	@property
	def keys(self):
		return list((self._datehead,self._ratehead))

	@property
	def analysis(self):
		return self._analysis

	def measured(self,figure:go.Figure,frame:pandas.DataFrame,**kwargs):

		figure.add_trace(
			go.Scatter(
				x = frame[self.datehead],
				y = frame[self.ratehead],
				mode = 'markers',
				marker = kwargs,
			)
		)

		return figure

	def computed(self,figure:go.Figure,frame:pandas.DataFrame,**kwargs):

		figure.add_trace(
			go.Scatter(
				x = frame[self.datehead],
				y = frame[self.ratehead],
				mode = 'lines',
				line = kwargs,
			)
		)

		return figure

	def print(self,frame,estimate_limit=None,forecast_limit=None,frame_title=None,yaxis_title=None,**kwargs):

		frame = frame[self.keys]

		frame = frame.groupby([self.datehead]).sum().reset_index()

		figure = go.Figure()

		figure = self.measured(figure,frame)

		if estimate_limit is not None:

			self.print_forecast(figure,frame,estimate_limit,forecast_limit,**kwargs)

		frame_title = "Hasilat" if frame_title is None else f"{frame_title} - Hasilat"

		yaxis_title = self.ratehead if yaxis_title is None else yaxis_title

		figure.update_layout(
			title = frame_title,
			yaxis_title = yaxis_title,
			margin = dict(l=0,r=50,t=30,b=50,pad=0),
			showlegend = False,
		)

		figure.show()

	def print_forecast(self,figure,frame,estimate_limit,forecast_limit=None,**kwargs):

		model = self._analysis.fit(frame,estimate_limit,**kwargs)

		if self._analysis.score_flag:
			model,R2value = model

		print(model)

		if self._analysis.score_flag:
			print(f"R-squared is {R2value:.2f} (from non-linear data)\n\n")

		forecast_limit = estimate_limit if forecast_limit is None else forecast_limit

		curve = self._analysis.run(model,forecast_limit)

		figure = self.computed(figure,curve,color="crimson")