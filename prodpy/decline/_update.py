from ._model import Model

from ._analysis import Analysis

class Update():

	# @staticmethod
	# def multirun(state,group,bar):

	# 	models = {}

	# 	for index,frame in enumerate(group):

	# 		model = analyze.fit(frame,
	# 			mode = state.mode.lower(),
	# 			exponent = state.exponent,
	# 		)

	# 		models[itemkey] = model

	# 		bar.progress(index+1,text=progress_text)

	# 	time.sleep(1)

	@staticmethod
	def load_analysis(state,view):

		analysis = Analysis(
			state.datehead,
			state.ratehead,
			)

		return analysis(view.frame)

	@staticmethod
	def slider(state):

		state['optimize'] = True

	@staticmethod
	def load_opacity(state,view):

		if view.frame.empty:
			return

		bools = Analysis.get_bools(
			view.dates,*state.datelim
			)

		return bools*0.7+0.3

	@staticmethod
	def mode(state):

		state['exponent'] = Model.get_exponent(state.mode)
		state['optimize'] = True

	@staticmethod
	def exponent(state):

		state['mode'] =  Model.get_mode(state.exponent)
		state['optimize'] = True

	@staticmethod
	def load_model(state,analysis):

		if not state.optimize:
			return

		if analysis.frame.empty:
			return

		if Update.flag(state,'datelim','mode','exponent'):
			return

		model = analysis.fit(
			mode 		= state.mode,
			exponent 	= state.exponent,
			start 		= state.datelim[0],
			end 		= state.datelim[1],
			)

		state['rate0'] = f'{model.rate0:f}'

		state['decline0'] = f'{model.decline0:f}'

	@staticmethod
	def attributes(state):

		state['optimize'] = False

	@staticmethod
	def load_curve(state,analysis):

		if analysis.frame.empty:
			return

		if Update.flag(state,'datelim','mode','exponent','rate0','decline0'):
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

	# @staticmethod
	# def save(state):
	# 	pass

	# @staticmethod
	# def export(state):
	# 	pass

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False