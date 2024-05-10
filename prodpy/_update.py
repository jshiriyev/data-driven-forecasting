import numpy

class Update():

	@staticmethod
	def opacity(state):

		date_min,date_max = state.time_interval_selected

		cond1 = state.datetimes >= numpy.datetime64(date_min)
		cond2 = state.datetimes <= numpy.datetime64(date_max)

		conds = numpy.logical_and(cond1,cond2)

		state['opacity'] = conds*0.7+0.3