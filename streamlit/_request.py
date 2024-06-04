import base64

from ._model import Model

from ._analysis import Analysis

class Request():

	@staticmethod
	def analysis(state):

		return Analysis(state.datehead,state.ratehead)

	@staticmethod
	def opacity(state,analysis):

		if analysis.frame.empty:
			return

		bools = analysis.span.iswithin(state.estimate)

		return bools*0.7+0.3

	@staticmethod
	def best_model(state,analysis):

		if not state.optimize:
			return

		if analysis.frame.empty:
			return

		if Request.flag(state,'estimate','date0','mode','exponent'):
			return

		return analysis.fit(state.estimate,
			date0=state.date0,mode=state.mode,exponent=state.exponent)

	@staticmethod
	def user_model(state):
		"""Returns user model based on the frontend selections."""

		if Request.flag(state,'mode','exponent','date0','rate0','decline0'):
			return

		return Model(
				mode = state.mode,
			exponent = state.exponent,
			   date0 = state.date0,
			   rate0 = float(state.rate0),
			decline0 = float(state.decline0),
			)

	@staticmethod
	def estimate_curve(state):
		"""Returns estimated data frame."""

		model = Request.user_model(state)

		if model is None:
			return

		return Analysis.run(model,state.estimate,periods=30)

	@staticmethod
	def forecast_curve(state):
		"""Returns forecasted data frame."""

		if len(state.forecast)!=2:
			return

		model = Request.user_model(state)

		if model is None:
			return

		return Analysis.run(model,state.forecast,periods=30)

	@staticmethod
	def forecast_frame(state,models):
		"""Returns group forecasted data frame."""

		return Analysis.multirun(
			models,state.forecast,periods=30
			)

	@staticmethod
	def forecast_file(state,models):
		"""Returns group forecasted data csv file."""

		frame = Request.forecast_frame(state,models)

		return frame.to_csv(index=False).encode('utf-8')

	@staticmethod
	def download_link(report:str,filename:str):
		"""
		Generates a link to download the given report.
		
		Params:
		------
		report	 : The csv string to be downloaded.
		filename : Filename and extension of file. e.g. mydata.csv,
		
		Returns:
		-------
		(str)	 : The anchor tag to download object_to_download

		"""

		try:
			# some strings <-> bytes conversions necessary here
			b64 = base64.b64encode(report.encode()).decode()
		except AttributeError as e:
			b64 = base64.b64encode(report).decode()

		dl_link = f"""
		<html>
		<head>
		<title>Start Auto Download file</title>
		<script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
		<script>
		$('<a href="data:text/csv;base64,{b64}" download="{filename}">')[0].click()
		</script>
		</head>
		</html>
		"""
		return dl_link

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False