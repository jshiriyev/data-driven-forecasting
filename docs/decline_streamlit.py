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

	uploaded_file = st.file_uploader(
		label = 'Upload your input excel file',
		type = ['xlsx'],
		)

	data = tv.Update.load_data(uploaded_file)

	st.header(
		body = 'Feature Selection',
		)

	datekey = st.selectbox(
		label = "Choose Date Column:",
		options = data.dates,
		index = None,
		key = 'datekey',
		)

	data = data(datekey)

	ratekey = st.selectbox(
		label = 'Choose Rate Column:',
		options = data.numbers,
		index = None,
		key = 'ratekey',
		)

	grouplist = st.multiselect(
		label = "Choose Groupby Columns:",
		options = data.groups,
		key = 'grouplist',
		)

	view = tv.Update.load_view(st.session_state,data)

	if view is None:
		viewitems = []
	else:
		viewitems = view.items

	itemkey = st.selectbox(
		label = 'Select Item:',
		options = viewitems,
		index = None,
		key = 'itemkey',
		)

	st.header(
		body = 'Timeseries View',
		)

	print(data.minors(st.session_state.ratekey))

	viewlist = st.multiselect(
		label = 'Add to the Plot:',
		options = data.minors(st.session_state.ratekey),
		key = 'viewlist',
		)

displayColumn, modelColumn = st.columns([0.7, 0.3],gap='large')

with modelColumn:

	st.header('Decline Curve Analysis')

	dryRun = st.button(
		label = "Dry Run",
		use_container_width = True,
		)
	
	if dryRun:
		pass

	progress_text = "Optimization in progress. Please wait."

	bar = st.progress(0,text=progress_text)

	bar.empty()

	data_date_limit = data.limit

	user_date_limit = st.slider(
		label = "Time Interval:",
		min_value = data_date_limit[0],
		max_value = data_date_limit[1],
		value = data_date_limit,
		# key = 'time_interval_selected',
		# on_change = tv.Update.opacity,
		# args = (st.session_state,),
		)

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

	autoFit = st.button(
		label = 'Auto Fit',
		use_container_width = True,
		)

	if autoFit:
		dc.Update.optimize(st.session_state)

	st.text_input(
		label = 'Initial Rate',
		key = 'rate0',
		) # ,placeholder=str(model.rate0)

	st.text_input(
		label='Initial Decline Rate',
		key = 'decline0',
		) # ,placeholder=str(model.decline0)

	# model = dc.Update.forward(st.session_state)

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

	if view is not None:

		frame = tv.Update.load_frame(view,st.session_state)

		st.header(f'{view.key} Rates')

		fig1 = go.Figure()

		data_obs = go.Scatter(
			x = frame.iloc[:,0],
			y = frame.iloc[:,1],
			mode = 'markers',
			# opacity = st.session_state.opacity,
			)

		fig1.add_trace(data_obs)

		x,y = model(datetimes=frame.iloc[:,0],datetime0=None)

		data_cal = go.Scatter(
			# x = pd.Series(dtype='datetime64[D]'),
			# y = pd.Series(dtype='float64'),
			x = x,
			y = y,
			mode = 'lines',
			line = dict(color="black"),
			)

		fig1.add_trace(data_cal)

		fig1.update_layout(
			title = f'{itemkey} Rates',
	        xaxis_title = frame.columns[0],
	        yaxis_title = frame.columns[1],
	        )

		st.plotly_chart(fig1,use_container_width=True)

		for index in range(2,frame.shape[1]):

			figure = go.Figure()

			data_vis = go.Scatter(
				x = frame.iloc[:,0],
				y = frame.iloc[:,index],
				mode = 'markers',
				# opacity = st.session_state.opacity,
				)

			figure.add_trace(data_vis)

			figure.update_layout(
				xaxis_title = frame.columns[0],
	        	yaxis_title = frame.columns[index],
				)

			st.plotly_chart(figure,use_container_width=True)
