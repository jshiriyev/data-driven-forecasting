import datetime

from ._model import Model

class Session():

	@staticmethod
	def parameters(state,mindate:datetime.date=None,maxdate:datetime.date=None):
		"""MODEL PARAMETERS"""

		if mindate is None:
			mindate = datetime.date(2020,1,1)

		if maxdate is None:
			maxdate = datetime.date(2020,6,1)

		if 'timelims' not in state:
			state['timelims'] = (mindate,maxdate)

		if 'mode' not in state:
		    state['mode'] = Model.mode

		if 'exponent' not in state:
			state['exponent'] = Model.exponent

		if 'rate0' not in state:
			state['rate0'] = str(Model.rate0)

		if 'decline0' not in state:
			state['decline0'] = str(Model.decline0)

		return state