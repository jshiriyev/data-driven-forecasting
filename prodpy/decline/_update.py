import numpy

import pandas

from ._analysis import Analysis

from ._model import Model

from ._optimize import Optimize

class Update():

	@staticmethod
	def mode(state):

		exponent = Model.get_exponent(state.mode)

		state['exponent'] = exponent*100

	@staticmethod
	def exponent(state):

		mode = Model.get_mode(state.exponent/100.)

		state['mode'] = mode.capitalize()

	@staticmethod
	def optimize(state):

		if Update.flag(state,'mode','exponent'):
			return

		model = Optimize.minimize(
			mdays = None, 
			rates = None,
			mode = state.mode.lower(),
			exponent = state.exponent/100,
			)

		state['rate0'] = model.rate0

		state['decline0'] = model.decline0

		state['fitline'] = model(datetimes=state.datetimes)

	@staticmethod
	def run(state):

		if Update.flag(state,'mode','exponent'):
			return

		model = Model(
			mode = state.mode.lower(),
			exponent = state.exponent/100,
			rate0 = float(state.rate0),
			decline0 = float(state.decline0),
			)

		state['fitline'] = model(datetimes=state.datetimes)

	@staticmethod
	def multirun(state):

		return

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False

	@staticmethod
	def save(state):
		pass

	@staticmethod
	def export(state):
		pass