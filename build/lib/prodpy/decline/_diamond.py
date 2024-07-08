import pandas

import plotly.graph_objects as go

from ._analysis import Analysis

class Diamond(Analysis):

	def __init__(self,datehead:str,ratehead:str):
		"""Initializing the class with date and rate column keys. The date and rate
		values are used for the optimization and forecasting of production data."""

		super().__init__(datehead,ratehead)

	@staticmethod
	def __empty(kwargs:dict):

		return {} if kwargs is None else kwargs

	def __call__(self,frame:pandas.DataFrame,figure:go.Figure=None,marker:dict=None,analysis:dict=None,line:dict=None,layout:dict=None):
		"""Quick summary prints and plots for the DCA interpretation at notebook."""

		frame  = self.prepare(frame)
		figure = self.view_measured(frame,figure,**self.__empty(marker))

		curve  = self.compute(frame,**self.__empty(analysis))
		figure = self.view_computed(curve,figure,**self.__empty(line))

		self.layout(figure,**self.__empty(layout))

	def prepare(self,frame:pandas.DataFrame):
		"""Returns the columns of the frame related to the estimation and forecasting."""

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

	def compute(self,frame:pandas.DataFrame,fitlims:tuple=None,runlims:tuple=None,printFlag=True,**kwargs):
		"""Prints model results and returns fitted curve frame."""

		if fitlims is None:
			return

		model = self.fit(frame,*fitlims,**kwargs) # kwargs = {mode, exponent, and date0}

		if printFlag:
			print(model)

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
			margin = self.__empty(kwargs.get("margin")),
			showlegend = False,
		)

		figure.show()