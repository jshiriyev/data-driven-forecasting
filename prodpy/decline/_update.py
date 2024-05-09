import numpy

import decline

class Update():
	
	@staticmethod
	def time(state):

		date_min,date_max = state.time_interval_selected

		cond1 = state.datetimes >= numpy.datetime64(date_min)
		cond2 = state.datetimes <= numpy.datetime64(date_max)

		conds = numpy.logical_and(cond1,cond2)

		state['opacity'] = conds*0.7+0.3

	@staticmethod
	def mode(state):

		exponent = decline.Model.get_exponent(state.mode)

		state['exponent'] = exponent*100

	@staticmethod
	def exponent(state):

		exponent = state.exponent/100.

		mode = decline.Model.get_mode(exponent)

		state['mode'] = mode.capitalize()

	@staticmethod
	def optimize():

		pass

	@staticmethod
	def run(state):

		try:
			float(state.rate0)
		except:
			return

		try:
			float(state.decline0)
		except:
			return

		model = decline.Model(
			mode = state.mode.lower(),
			exponent = state.exponent/100,
			rate0 = float(state.rate0),
			decline0 = float(state.decline0),
			)

		state['fitline'] = model(datetimes=state.datetimes)

	@staticmethod
	def save():
		pass

	@staticmethod
	def export():
		pass