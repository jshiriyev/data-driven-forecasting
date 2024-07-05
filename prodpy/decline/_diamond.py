import pandas

import plotly.graph_objects as go

from ._analysis import Analysis

class Diamond(Analysis):

	def __init__(self,datehead:str,ratehead:str):
		"""Initializing the class with date and rate column keys. The date and rate
		values are used for the optimization and forecasting of pandas.DataFrames."""

		super().__init__(datehead,ratehead)

	def __call__(self,frame:pandas.DataFrame,figure:go.Figure=None,estimate:tuple=None,forecast:tuple=None,title:str=None,ylabel:str=None,**kwargs):
		"""Quick summary prints and plots for the quick summary of DCA at notebook."""

		frame  = self.prepare(frame)
		figure = self.view_measured(frame,figure)

		if estimate is not None:

			curve  = self.compute(frame,estimate,forecast,**kwargs)
			figure = self.view_computed(curve,figure,color="crimson")

		self.layout(figure,title=title,ylabel=ylabel)

	def prepare(self,frame:pandas.DataFrame):
		"""Returns the columns of the frame related to the computations."""

		return frame[self.keys].groupby([self.datehead]).sum().reset_index()

	def view_measured(self,frame:pandas.DataFrame,figure:go.Figure=None,**kwargs):
		"""Adds measured data as a scatter plot to the figure."""

		if figure is None:
			figure = go.Figure()

		figure.add_trace(
			go.Scatter(
				x = frame[self.datehead],
				y = frame[self.ratehead],
				name = "Cum. Production",
				mode = 'markers',
				marker = kwargs,
			)
		)

		return figure

	def compute(self,frame:pandas.DataFrame,estimate:tuple,forecast:tuple=None,**kwargs):
		"""Prints model results and returns fitted curve frame."""

		model = self.fit(frame,estimate,**kwargs); print(model)

		forecast = estimate if forecast is None else forecast

		return self.run(model,forecast)

	def view_computed(self,frame:pandas.DataFrame,figure:go.Figure=None,**kwargs):
		"""Adds calculated data as a line plot to the figure."""

		if figure is None:
			figure = go.Figure()

		figure.add_trace(
			go.Scatter(
				x = frame[self.datehead],
				y = frame[self.ratehead],
				name = "Dec. Curve",
				mode = 'lines',
				line = kwargs,
			)
		)

		return figure

	def layout(self,figure:go.Figure,title:str=None,ylabel:str=None,**kwargs):
		"""Updates the figure layout."""

		if len(kwargs)==0:
			kwargs = dict(l=0,r=50,t=30,b=50,pad=0)

		figure.update_layout(
			title = "Production" if title is None else f"{title} - Production",
			yaxis_title = self.ratehead if ylabel is None else ylabel,
			margin = kwargs,
			showlegend = False,
		)

		figure.show()