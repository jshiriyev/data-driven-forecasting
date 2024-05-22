import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

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

displayColumn, modelColumn = st.columns([0.7,0.3],gap='large')

with modelColumn:

	st.header('Decline Curve Analysis')

	# COLLECTIVE OPTIMIZATION
	# multi_run = st.button(
	# 	label = "Multi Run",
	# 	use_container_width = True,
	# 	)
	# if multi_run:
	# 	pass
	# progress_text = "Optimization in progress. Please wait."
	# bar = st.progress(0,text=progress_text)
	# bar.empty()

	analysis = dc.Update.load_analysis(st.session_state,view)

	st.slider(
		label = "Time Interval:",
		min_value = view.limit[0],
		max_value = view.limit[1],
		key = 'datelim',
		)

	opacity = dc.Update.load_opacity(st.session_state,view)

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

	model = dc.Update.load_model(st.session_state,analysis)

	st.text_input(label='Initial Rate',key='rate0')

	st.text_input(label='Initial Decline Rate',key='decline0')

	curve = dc.Update.load_curve(st.session_state,analysis)

	saveModel = st.button(
		label = "Save Model",
		use_container_width = True,
		)

	if saveModel:
		pass

	st.text("")

	st.button(
		label = "Export Fits",
		use_container_width = True,
		)

with displayColumn:

	if not view.frame.empty:

		st.header(f'{itemname} Rates')

		fig1 = go.Figure()

		data_obs = go.Scatter(
			x = view.frame[datehead],
			y = view.frame[ratehead],
			mode = 'markers',
			marker = dict(opacity=opacity),
			)

		fig1.add_trace(data_obs)

		data_cal = go.Scatter(
			x = curve['dates'],
			y = curve['rates'],
			mode = 'lines',
			line = dict(color="black"),
			)

		fig1.add_trace(data_cal)

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
