from ._model import Model

class Session():

	@staticmethod
	def parameters(state,mindate,maxdate):
		"""MODEL PARAMETERS"""

		if 'time_interval' not in state:
			state['time_interval'] = (mindate,maxdate)

		if 'time_interval_selected' not in state:
			state['time_interval_selected'] = (mindate,maxdate)

		if 'mode' not in state:
		    state['mode'] = Model.mode

		if 'exponent' not in state:
			state['exponent'] = Model.exponent

		if 'rate0' not in state:
			state['rate0'] = str(Model.rate0)

		if 'decline0' not in state:
			state['decline0'] = str(Model.decline0)

		return state