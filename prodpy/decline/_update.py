import base64

from ._model import Model

from ._analysis import Analysis

class Update():

	@staticmethod
	def load_analysis(state):

		return Analysis(state.datehead,state.ratehead)

	@staticmethod
	def slider(state):

		state['date0'] = state.estimate[0]
		state['optimize'] = True

	@staticmethod
	def load_opacity(state,analysis):

		if analysis.frame.empty:
			return

		bools = analysis.span.iswithin(state.estimate)

		return bools*0.7+0.3

	@staticmethod
	def mode(state):

		state['exponent'] = Model.get_exponent(state.mode)
		state['optimize'] = True

	@staticmethod
	def exponent(state):

		state['mode'] =  Model.get_mode(state.exponent)
		state['optimize'] = True

	@staticmethod
	def load_best_model(state,analysis):

		if analysis.frame.empty:
			return

		if Update.flag(state,'estimate','date0','mode','exponent'):
			return

		return analysis.fit(state.estimate,
			date0=state.date0,mode=state.mode,exponent=state.exponent)

	@staticmethod
	def model(state,analysis,itemname):

		if not state.optimize:
			return

		model = Update.load_best_model(state,analysis)

		if model is None:
			return
		
		state['rate0'] = f'{model.rate0:f}'

		state['decline0'] = f'{model.decline0:f}'

	@staticmethod
	def attributes(state):

		state['optimize'] = False

	@staticmethod
	def load_user_model(state):
		"""Returns user model based on the frontend selections."""

		if Update.flag(state,'mode','exponent','date0','rate0','decline0'):
			return

		return Model(
				mode = state.mode,
			exponent = state.exponent,
			   date0 = state.date0,
			   rate0 = float(state.rate0),
			decline0 = float(state.decline0),
			)

	@staticmethod
	def load_estimate_curve(state):
		"""Returns estimated data frame."""

		model = Update.load_user_model(state)

		if model is None:
			return

		return Analysis.run(model,state.estimate,periods=30)

	@staticmethod
	def load_forecast_curve(state):
		"""Returns forecasted data frame."""

		if len(state.forecast)!=2:
			return

		model = Update.load_user_model(state)

		if model is None:
			return

		return Analysis.run(model,state.forecast,periods=30)

	@staticmethod
	def load_forecast_file(state,models):
		"""Returns group forecasted data frame."""

		frame = Analysis.multirun(
			models,state.forecast,periods=30
			)

		return frame.to_csv(index=False).encode('utf-8')

	@staticmethod
	def load_download(report:str,filename:str):
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