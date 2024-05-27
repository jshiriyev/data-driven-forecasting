from ._model import Model

from ._timespan import TimeSpan
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

		span = TimeSpan(analysis.dates)

		bools = span.iswithin(*state.estimate)

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
	def best_model(state,analysis):

		if analysis.frame.empty:
			return

		if Update.flag(state,'estimate','date0','mode','exponent'):
			return

		return analysis.fit(*state.estimate,
			date0=state.date0,mode=state.mode,exponent=state.exponent)

	@staticmethod
	def load_model(state,analysis):

		if not state.optimize:
			return

		model = Update.best_model(state,analysis)

		state['rate0'] = f'{model.rate0:f}'

		state['decline0'] = f'{model.decline0:f}'

	@staticmethod
	def attributes(state):

		state['optimize'] = False

	@staticmethod
	def user_model(state):
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
	def load_estimate(state):
		"""Returns estimated data frame."""

		model = Update.user_model(state)

		return Analysis.run(model,*state.estimate,periods=30)

	@staticmethod
	def load_forecast(state):
		"""Returns forecasted data frame."""

		model = Update.user_model(state)

		return Analysis.run(model,*state.forecast,periods=30)

	@staticmethod
	def load_download(state):
		"""Returns group forecasted data frame."""

		span = TimeSpan.get(*state.forecast,periods=30)

		date = span.series.to_list()

		items,dates,rates = [],[],[]

		for name,model in state.models.items():

			item = [name]*span.size

			days = span.days(model.date0)

			rate = Analysis.predict(model,days).tolist()
			
			items.append(item)
			dates.append(date)
			rates.append(rate)

		frame = Analysis.toframe({"Name":items,"Date":dates,"Rate":rates})

		return frame.to_csv(index=False).encode('utf-8')

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False