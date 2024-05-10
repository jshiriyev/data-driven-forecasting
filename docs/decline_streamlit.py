import pandas as pd

import plotly_express as px
import plotly.graph_objects as go

import streamlit as st

import sys

# sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

from prodpy import decline
from prodpy import timeview

view = timeview.Outlook()

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

st.session_state = timeview.Session.sidebar(st.session_state)
st.session_state = timeview.Session.scene(st.session_state)

st.session_state = decline.Session.parameters(st.session_state)

@st.cache_data
def get_view(uploaded_file):

	frame = pd.read_excel(uploaded_file)

	view = timeview.Outlook(frame)

	timeview.Update.upload(st.session_state,view)

	return view

with st.sidebar:

	st.header(
		body = 'Input Data',
		)

	uploaded_file = st.file_uploader(
		label = 'Upload your input excel file',
		type = ['xlsx'],
		)

	if uploaded_file is not None:
		view = get_view(uploaded_file)

	st.header(
		body = 'Feature Selection',
		)

	st.selectbox(
		label = "Choose Date Column:",
		options = view.dates,
		index = None,
		key = 'datekey',
		)

	st.selectbox(
		label = 'Choose Rate Column:',
		options = view.numbers,
		index = None,
		key = 'ratekey',
		on_change = timeview.Update.ratekey,
		args = (st.session_state,view),
		)

	st.selectbox(
		label = "Choose Group By Column:",
		options = st.session_state.groups,
		index = None,
		key = 'groupkey',
		on_change = timeview.Update.groupkey,
		args = (st.session_state,view),
		)

	st.button(
		label = 'Calculate All',
		use_container_width = True,
		on_click = decline.Update.multirun,
		args = (st.session_state,),
		)

	st.selectbox(
		label = 'Filter By:',
		options = view.items(st.session_state.groupkey),
		index = None,
		key = 'itemkey',
		)

	st.header(
		body = 'Timeseries View',
		)

	st.multiselect(
		label = 'Add to the Plot:',
		options = view.plottable(st.session_state.ratekey),
		)

displayColumn, modelColumn = st.columns([0.7, 0.3],gap='large')

with displayColumn:

	st.header(f'None Rates')

	fig = go.Figure()

	data1 = go.Scatter(
		x = pd.Series(dtype='datetime64[D]'),
		y = pd.Series(dtype='float64'),
		mode = 'markers',
		opacity = st.session_state.opacity,
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

with modelColumn:

	st.header('Decline Model Parameters')

	st.slider(
		label = "Time Interval:",
		min_value = st.session_state.mindate,
		max_value = st.session_state.maxdate,
		key = 'time_interval_selected',
		on_change = timeview.Update.opacity,
		args = (st.session_state,),
		)

	st.selectbox(
		label = "Decline Mode:",
		options = decline.Model.options,
		key = 'mode',
		on_change = decline.Update.mode,
		args = (st.session_state,),
		)

	st.number_input(
		label = 'Decline Exponent %',
		min_value = 0,
		max_value = 100,
		key = 'exponent',
		step = 5,
		on_change = decline.Update.exponent,
		args = (st.session_state,),
		)

	st.button(
		label = 'Optimize',
		use_container_width = True,
		on_click = decline.Update.optimize,
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
		on_click = decline.Update.run,
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