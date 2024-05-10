import numpy

from ._model import Model

class Update():

	@staticmethod
	def mode(state):

		exponent = Model.get_exponent(state.mode)

		state['exponent'] = exponent*100

	@staticmethod
	def exponent(state):

		exponent = state.exponent/100.

		mode = Model.get_mode(exponent)

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

		model = Model(
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