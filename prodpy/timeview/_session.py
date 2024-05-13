import datetime

class Session():

	@staticmethod
	def sidebar(state):

		if 'datekey' not in state:
			state['datekey'] = None

		if 'ratekey' not in state:
			state['ratekey'] = None

		if 'groupkey' not in state:
			state['groupkey'] = None

		if 'itemkey' not in state:
			state['itemkey'] = None

		if 'viewkeys' not in state:
			state['viewkeys'] = None

		return state