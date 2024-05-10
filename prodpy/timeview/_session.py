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

		if 'viewkey' not in state:
			state['viewkey'] = None

		return state

	@staticmethod
	def scene(state,mindate:datetime.date=None,maxdate:datetime.date=None):
		"""VISUALIZED DATA"""

		if mindate is None:
			mindate = datetime.date(2020,1,1)

		if 'mindate' not in state:
			state['mindate'] = mindate

		if maxdate is None:
			maxdate = datetime.date(2020,6,1)
			
		if 'maxdate' not in state:
			state['maxdate'] = maxdate

		if 'datetimes' not in state:
			state['datetimes'] = None

		if 'rates' not in state:
			state['rates'] = None

		if 'opacity' not in state:
			state['opacity'] = 1.

		if 'fitline' not in state:
			state['fitline'] = None

		return state