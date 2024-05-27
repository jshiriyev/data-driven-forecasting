import datetime

import sys

# sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import time

import pandas as pd

import plotly.graph_objects as go

import streamlit as st

from prodpy import timeview as tv

from prodpy import decline as dc

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

st.session_state = tv.Session(st.session_state).set()
st.session_state = dc.Session(st.session_state).set()

with st.sidebar:

	st.header(
		body = 'Input Data',
		)

	file = st.file_uploader(
		label = 'Upload your input excel file',
		type = ['csv','xlsx'],
		)

	data = tv.Update.load_data(file)

	st.header(
		body = 'Feature Selection',
		)

	datehead = st.selectbox(
		label = "Choose Date Column:",
		options = data.datetimes,
		index = None,
		key = 'datehead',
		)

	if datehead is not None:
		data = data(datehead=datehead)

	ratehead = st.selectbox(
		label = 'Choose Rate Column:',
		options = data.numbers,
		index = None,
		key = 'ratehead',
		)

	nominals = st.multiselect(
		label = "Choose Groupby Columns:",
		options = data.nominals,
		key = 'nominals',
		)

	table = tv.Update.load_table(st.session_state,data)

	st.header(
		body = 'Item Selection:',
		)

	itemname = st.selectbox(
		label = 'Select Item:',
		options = table.items,
		index = None,
		key = 'itemname'
		)

	view = tv.Update.load_view(st.session_state,table)

	st.header(
		body = 'Timeseries View',
		)

	viewlist = st.multiselect(
		label = 'Add to the Plot:',
		options = data.minors(st.session_state.ratehead),
		key = 'viewlist',
		)

	frame = view.frame

displayColumn, modelColumn = st.columns([0.7,0.3],gap='large')

with modelColumn:

	st.header('Decline Curve Analysis')

	analysis = dc.Update.load_analysis(st.session_state)

	st.slider(
		label = "Time Interval:",
		min_value = view.estimate[0],
		max_value = view.estimate[1],
		key = 'estimate',
		on_change = dc.Update.slider,
		args = (st.session_state,),
		)

	analysis = analysis(frame)

	opacity = dc.Update.load_opacity(st.session_state,analysis)

	st.selectbox(
		label = "Decline Mode",
		options = dc.Model.options,
		key = 'mode',
		on_change = dc.Update.mode,
		args = (st.session_state,),
		)

	st.number_input(
		label = 'Decline Exponent %',
		min_value = 0,
		max_value = 100,
		key = 'exponent',
		step = 5,
		on_change = dc.Update.exponent,
		args = (st.session_state,),
		)

	FitGroup = st.button(
		label = "Fit Group",
		help = "Optimize all group items.",
		use_container_width = True,
		)

	if FitGroup:

		st.session_state.models = {}

		progress_text = "Optimization in progress. Please wait."

		bar = st.progress(0.,text=progress_text)
		
		for index,view in enumerate(table,start=1):

			model = dc.Update.best_model(st.session_state,analysis(view.frame))

			st.session_state.models[view.items[0]] = model

			bar.progress(value=index/table.num,text=progress_text)

		time.sleep(1)
	
		bar.empty()

	dc.Update.load_model(st.session_state,analysis)

	st.text_input(
		label = 'Initial Rate',
		key = 'rate0',
		on_change = dc.Update.attributes,
		args = (st.session_state,),
		)

	st.text_input(
		label = 'Initial Decline Rate',
		key = 'decline0',
		on_change = dc.Update.attributes,
		args = (st.session_state,),
		)

	curve_estimate = dc.Update.load_estimate(st.session_state,analysis)

	SaveModelEdit = st.button(
		label = "Save Edits",
		help = "Save decline attribute edits for the item.",
		use_container_width = True,
		)

	if SaveModelEdit:

		if len(st.session_state.models)==0:
			st.warning("Click Fit Group first.")
		else:
			try:
				st.session_state.models[itemname] = dc.Update.user_model(st.session_state)
			except Exception as message:
				st.warning(message)
			else:
				st.success(f"The model for {itemname} is updated.")

	st.markdown("""---""")

	show_forecast = st.checkbox(
		label = "Display Forecasted Rates",
		)

	next_year = datetime.datetime.now().year + 1

	forecast = st.date_input(
		"Forecast Interval",
		# min_value = datetime.date(next_year, 1, 1),
		# max_value = datetime.date(next_year,12,31),
		value = (
			datetime.date(next_year, 1, 1),
			datetime.date(next_year,12,31),
			),
		key = 'forecast',
		format="MM.DD.YYYY",
	)

	forecast_frequency = st.selectbox(
		label = 'Forecast Frequency:',
		options = ("Daily","Monthly","Yearly"),
		key = 'frequency'
		)

	if show_forecast:
		curve_forecast = dc.Update.load_forecast(st.session_state)

	# output = dc.Update.load_download(st.session_state)

	# Download = st.download_button(
	# 	label = 'Download Forecast',
	# 	data = output,
	# 	help = "Download rates for all group items.",
	# 	file_name = f"{table.leadhead}_forecast.csv",
	# 	mime = 'text/csv',
	# 	use_container_width = True,
	# 	)

	# if Download:

	# 	progress_text = "Forecast in progress. Please wait."

	# 	bar2 = st.progress(0.,text=progress_text)
		
	# 	for index,view in enumerate(table,start=1):

	# 		model = dc.Update.best_model(st.session_state,analysis(view.frame))

	# 		st.session_state.models[view.items[0]] = model

	# 		bar2.progress(value=index/table.num,text=progress_text)

	# 	time.sleep(1)
	
	# 	bar2.empty()

with displayColumn:

	if not view.frame.empty:

		st.header(f'{itemname} Rates')

		fig1 = go.Figure()

		data_observed = go.Scatter(
			x = view.frame[datehead],
			y = view.frame[ratehead],
			mode = 'markers',
			marker = dict(opacity=opacity),
			)

		fig1.add_trace(data_observed)

		data_calculated = go.Scatter(
			x = curve_estimate['dates'],
			y = curve_estimate['rates'],
			mode = 'lines',
			line = dict(color="black"),
			)

		fig1.add_trace(data_calculated)

		if show_forecast:
			data_forecast = go.Scatter(
				x = curve_forecast['dates'],
				y = curve_forecast['rates'],
				mode = 'lines',
				line = dict(color="red"),
				)

			fig1.add_trace(data_forecast)

		fig1.update_layout(
			title = f'{st.session_state.ratehead}',
			showlegend = False,
	        )

		st.plotly_chart(fig1,use_container_width=True)

		for ratename in viewlist:

			figI = go.Figure()

			data_vis = go.Scatter(
				x = view.frame[datehead],
				y = view.frame[ratename],
				mode = 'markers',
				marker = dict(opacity=opacity),
				)

			figI.add_trace(data_vis)

			figI.update_layout(
				title = ratename,
				)

			st.plotly_chart(figI,use_container_width=True)
