import plotly.graph_objects as go

class Diamond():

	@staticmethod
	def measured(frame,xhead:str,yhead:str,**kwargs):

		return go.Scatter(
			x = frame[xhead],
			y = frame[yhead],
			mode = 'markers',
			marker = kwargs,
		)

	@staticmethod
	def computed(frame,xhead:str,yhead:str,**kwargs):

		return go.Scatter(
			x = frame[xhead],
			y = frame[yhead],
			mode = 'lines',
			line = kwargs,
		)