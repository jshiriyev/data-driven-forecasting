import pandas

import plotly.graph_objects as go

from ._analysis import Analysis

class Diamond(Analysis):

	def __init__(self,datehead:str,ratehead:str):
		"""Initializing the class with date and rate column keys. The date and rate
		values are used for the optimization and forecasting of production data."""

		super().__init__(datehead,ratehead)

	def __call__(self,frame:pandas.DataFrame,figure:go.Figure=None,marker:dict=None,analysis:dict=None,line:dict=None,layout:dict=None):
		"""Quick summary prints and plots for the DCA interpretation at notebook."""

		frame  = self.prepare(frame)
		figure = self.view_measured(frame,figure,**self.dictionary(marker))

		curve  = self.compute(frame,**self.dictionary(analysis))
		figure = self.view_computed(curve.frame,figure,**self.dictionary(line))

		figure = self.layout(figure,**self.dictionary(layout))

		return figure,curve.model

	def prepare(self,frame:pandas.DataFrame):
		"""Returns the columns of the frame related to the estimation and forecasting."""

		return frame[list(self.heads)].groupby([self.datehead]).sum().reset_index()

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

	def compute(self,frame:pandas.DataFrame,fitlims:tuple=None,runlims:tuple=None,**kwargs):
		"""Prints model results and returns fitted curve frame."""

		if fitlims is None:
			return

		if frame.shape[0]<2:
			return pandas.DataFrame({self.datehead:[],self.ratehead:[]})

		model = self.fit(frame,*fitlims,**kwargs) # kwargs = {mode, exponent, and date0}

		runlims = fitlims if runlims is None else runlims

		return self.run(model,*runlims)

	def view_computed(self,frame:pandas.DataFrame,figure:go.Figure=None,**kwargs):
		"""Adds calculated data as a line plot to the figure."""

		if figure is None:
			figure = go.Figure()

		if frame is None:
			return figure

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

		figure.update_layout(
			title = "Production" if title is None else f"{title} - Production",
			yaxis_title = self.ratehead if ylabel is None else ylabel,
			margin = self.dictionary(kwargs.get("margin")),
			showlegend = False,
		)

		return figure

	@staticmethod
	def dictionary(kwargs:dict):
		return {} if kwargs is None else kwargs