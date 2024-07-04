import pandas

import plotly.graph_objects as go

class Diamond():

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

	def print(self,analysis,frame,limit_estimate=None,limit_forecast=None,frame_title=None,yaxis_title=None,**kwargs):

		frame = frame[self.keys]

		frame = frame.groupby([self.datehead]).sum().reset_index()

		figure = go.Figure()

		figure = self.measured(figure,frame)

		if limit_estimate is not None:

			model,R2value = analysis.fit(frame,limit_estimate,**kwargs)

			print(model)

			print(f"R-squared is {R2value:.2f} (from non-linearized data)")

			if limit_forecast is None:

			    limit_forecast = limit_estimate
			    
			curve = analysis.run(model,limit_forecast)

			figure = self.computed(figure,curve,color="crimson")

		frame_title = "Hasilat" if frame_title is None else f"{frame_title} - Hasilat"

		if yaxis_title is None:
			
			yaxis_title = self.ratehead

		figure.update_layout(
			title = frame_title,
			yaxis_title = yaxis_title,
			margin = dict(l=0,r=50,t=30,b=50,pad=0),
			showlegend = False,
		)

		figure.show()