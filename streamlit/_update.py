import base64

import streamlit as st

import streamlit.components.v1 as components

from ._model import Model

from ._analysis import Analysis

class Update():

	@staticmethod
	def slider(state):

		state['date0'] = state.estimate[0]
		state['optimize'] = True

	@staticmethod
	def mode(state):

		state['exponent'] = Model.get_exponent(state.mode)
		state['optimize'] = True

	@staticmethod
	def exponent(state):

		state['mode'] =  Model.get_mode(state.exponent)
		state['optimize'] = True

	@staticmethod
	def optimize_group(state):

		if table.empty:
			st.warning("No data to optimize.")

		else:

			st.session_state.models = {}

			optimization_text = "Optimization in progress. Please wait."

			bar1 = st.progress(0.,text=optimization_text)
			
			for index,scene in enumerate(table,start=1):

				model = dc.Update.load_best_model(
					st.session_state,analysis(scene.frame)
					)

				st.session_state.models[scene.items[0]] = model

				bar1.progress(value=index/table.num,text=optimization_text)

			time.sleep(1)
		
			bar1.empty()

			st.success(f"Models for {table.leadhead.replace("_"," ")} are calculated.")

	@staticmethod
	def model(state,model:Model):

		if model is None:
			return
		
		state['rate0'] = f'{model.rate0:f}'
		state['decline0'] = f'{model.decline0:f}'

	@staticmethod
	def attributes(state):

		state['optimize'] = False

	@staticmethod
	def save_edits(state):

		if itemname is None:
			st.warning("No item is selected.")
		else:
			try:
				st.session_state.models[itemname] = dc.Update.load_user_model(st.session_state)
			except Exception as message:
				st.warning(message)
			else:
				st.success(f"The model for {itemname} is updated.")

	@staticmethod
	def forecast_show(state):

		if forecast_show:
			xaxis_range = [
				min(st.session_state.forecast[0],view.limit[0]),
				max(st.session_state.forecast[1],view.limit[1])
				]
		else:
			xaxis_range = list(view.limit)

	@staticmethod
	def forecast(state):

		if len(forecast)!=2:
			st.warning("Input start and end of the forecast period.")

	def forecast_frequency(state):

		freq = getattr(pandas.offsets,forecast_frequency)._prefix

	def forecast_group(state):

		if len(st.session_state.models)==0:
			st.warning('No model to forecast.')
		else:

			forecast_text = "Forecast in progress. Please wait."

			bar2 = st.progress(0.,text=forecast_text)

			for index,(name,model) in enumerate(st.session_state.models.items(),start=1):

				minor = analysis.run(model,forecast,freq=freq)

				minor.insert(0,'Names',name)

				if index==1:
					frame = minor.copy()
				else:
					frame = pandas.concat([frame,minor])

				frame = pandas.concat([frame,minor])

				bar2.progress(value=index/len(st.session_state.models),text=forecast_text)

			time.sleep(1)

			output = frame.to_csv(index=False).encode('utf-8')

			components.html(
				dc.Update.load_download(output,f"{table.leadhead}_forecast.csv"),
				height=0,
			)

			bar2.empty()

	@staticmethod
	def flag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False