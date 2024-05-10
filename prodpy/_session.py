import decline

class Session():

	@staticmethod
	def sidebar(state):
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
	def scene(state,datetimes):
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