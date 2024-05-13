import pandas as pd

import plotly.graph_objects as go

import streamlit as st

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

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

	ratekey = st.selectbox(
		label = 'Choose Rate Column:',
		options = data.numbers,
		index = None,
		key = 'ratekey',
		)

	groupkey = st.selectbox(
		label = "Choose Group By Column:",
		options = data.groups,
		index = None,
		key = 'groupkey',
		)
	
	# st.button(
	# 	label = 'Calculate All',
	# 	use_container_width = True,
	# 	# on_click = dc.Update.multirun,
	# 	# args = (st.session_state,),
	# 	)

	itemkey = st.selectbox(
		label = 'Filter By:',
		options = data.items(st.session_state.groupkey),
		index = None,
		key = 'itemkey',
		)

	st.header(
		body = 'Timeseries View',
		)

	viewlist = st.multiselect(
		label = 'Add to the Plot:',
		options = data.plottable(st.session_state.ratekey),
		key = 'viewlist',
		)

displayColumn, modelColumn = st.columns([0.7, 0.3],gap='large')

with modelColumn:

	st.header('Decline Model Parameters')

	data_date_limits = data.limits(st.session_state.datekey)

	user_date_limits = st.slider(
		label = "Time Interval:",
		min_value = data_date_limits[0],
		max_value = data_date_limits[1],
		value = data_date_limits,
		# key = 'time_interval_selected',
		# on_change = tv.Update.opacity,
		# args = (st.session_state,),
		)

	st.selectbox(
		label = "Decline Mode:",
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

	st.button(
		label = 'Optimize',
		use_container_width = True,
		on_click = dc.Update.optimize,
		args = (st.session_state,),
		)

	st.text_input(
		label = 'Initial Rate',
		key = 'rate0',
		) # ,placeholder=str(model.rate0)

	st.text_input(
		label='Initial Decline Rate',
		key = 'decline0',
		) # ,placeholder=str(model.decline0)

	st.button(
		label = 'Run Model',
		use_container_width = True,
		on_click = dc.Update.run,
		args = (st.session_state,),
		)

	st.subheader(r'''Save & Export''',)

	st.button(
		label = "Save Model",
		use_container_width = True,
		)

	st.button(
		label = "Export Fits",
		use_container_width = True,
		)

with displayColumn:

	st.header(f'None Rates')

	fig = go.Figure()

	x,y = tv.Update.load_view(data,st.session_state)

	data1 = go.Scatter(
		x = pd.Series(dtype='datetime64[D]'),
		y = pd.Series(dtype='float64'),
		mode = 'markers',
		# opacity = st.session_state.opacity,
		)

	fig.add_trace(data1)

	data2 = go.Scatter(
		x = pd.Series(dtype='datetime64[D]'),
		y = pd.Series(dtype='float64'),
		mode = 'lines',
		line = dict(color="black"),
		)

	fig.add_trace(data2)

	fig.update_layout(
		title = 'None Rates',
        xaxis_title = 'Date Time',
        yaxis_title = 'Actual Oil, Mstb/d'
        )