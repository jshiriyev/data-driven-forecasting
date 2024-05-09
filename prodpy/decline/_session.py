import decline

class Session():

	@staticmethod
	def column1(state):
		"""INPUT DATA"""

		if 'datekey' not in state:
			state['datekey'] = None

		if 'ratekey' not in state:
			state['ratekey'] = None

		if 'groupkey' not in state:
			state['groupkey'] = None

		if 'itemkey' not in state:
			state['itemkey'] = None

		if 'viewlist' not in state:
			state['viewlist'] = None

		return state

	@staticmethod
	def column2(state,datetimes):
		"""VISUALIZED DATA"""

		if 'datetimes' not in state:
			state['datetimes'] = datetimes

		if 'rates' not in state:
			state['rates'] = None

		if 'opacity' not in state:
			state['opacity'] = 1.

		if 'fitline' not in state:
			state['fitline'] = None

		return state

	@staticmethod
	def column3(state,date_amin,date_amax):
		"""MODEL PARAMETERS"""

		if 'time_interval' not in state:
			state['time_interval'] = (date_amin,date_amax)

		if 'time_interval_selected' not in state:
			state['time_interval_selected'] = (date_amin,date_amax)

		if 'mode' not in state:
		    state['mode'] = decline.Model.mode

		if 'exponent' not in state:
			state['exponent'] = decline.Model.exponent

		if 'rate0' not in state:
			state['rate0'] = str(decline.Model.rate0)

		if 'decline0' not in state:
			state['decline0'] = str(decline.Model.decline0)

		return state