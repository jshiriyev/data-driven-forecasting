import numpy

import pandas

from ._model import Model

from ._analysis import Analysis

class Update():

	@staticmethod
	def multirun(state,group,bar):

		models = {}

		for index,frame in enumerate(group):

			model = analyze.fit(frame,
				mode = state.mode.lower(),
				exponent = state.exponent,
			)

			models[itemkey] = model

			bar.progress(index+1,text=progress_text)

		time.sleep(1)

	@staticmethod
	def load_analysis(state,frame,title,limit):

		analysis = Analysis(state.datehead,state.ratehead)

		analysis = analysis(frame)

		analysis._title = title
		analysis._limit = limit

		if not analysis.frame.empty:
			state.datelim = analysis.limit

		return analysis

	@staticmethod
	def load_opacity(state,analysis):

		if analysis.frame.empty:
			return

		dates = analysis.frame[analysis.datehead]

		bools = Analysis.get_bools(dates,*state.datelim)

		return numpy.asarray(bools,'float32')

	@staticmethod
	def load_model(state,analysis):

		if analysis.frame.empty:
			return Model()

		if Update.flag(state,'mode','exponent'):
			return Model()

		model = analysis.fit(
			mode 		= state.mode,
			exponent 	= state.exponent,
			start 		= state.datelim[0],
			end 		= state.datelim[1],
			)

		state.rate0 = str(model.rate0)

		state.decline0 = str(model.decline0)

		return model

	@staticmethod
	def mode(state):

		state['exponent'] = Model.get_exponent(state.mode)

	@staticmethod
	def exponent(state):

		state['mode'] =  Model.get_mode(state.exponent)

	@staticmethod
	def load_curve(state,analysis):

		if analysis.frame.empty:
			return

		if Update.flag(state,'mode','exponent'):
			return

		start,end = state.datelim

		model = Model(
			mode 		= state.mode,
			exponent 	= state.exponent,
			rate0 		= float(state.rate0),
			decline0 	= float(state.decline0),
			date0 		= start,
		)

		return analysis.run(model,start=start,end=end,periods=30)

	@staticmethod
	def save(state):
		pass

	@staticmethod
	def export(state):
		pass

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False