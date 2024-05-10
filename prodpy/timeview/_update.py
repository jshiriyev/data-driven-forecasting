import numpy

class Update():

	@staticmethod
	def multirun(state,view):

		state['subs'] = view.items(state.groupkey)

	@staticmethod
	def itemkey(state,view):

		frame1 = dca.filter(frame,displayedItem)

		frame2,model = dca.predict(frame1,start=None,cease=None)

		title = f'{displayedItem} Rates'

	@staticmethod
	def opacity(state):

		date_min,date_max = state.time_interval_selected

		cond1 = state.datetimes >= numpy.datetime64(date_min)
		cond2 = state.datetimes <= numpy.datetime64(date_max)

		conds = numpy.logical_and(cond1,cond2)

		state['opacity'] = conds*0.7+0.3

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False