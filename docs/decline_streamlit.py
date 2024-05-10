import datetime

import numpy as np
import pandas as pd

import plotly_express as px
import plotly.graph_objects as go

import streamlit as st

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

from prodpy import decline

from prodpy import Outlook
from prodpy import Session
from prodpy import Update

data = Outlook(None)

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

st.session_state = Session.sidebar(st.session_state)

st.session_state = Session.scene(st.session_state)

st.session_state = decline.Session.parameters(st.session_state)

with st.sidebar:

	st.header(
		body = 'Input Data',
		)

	st.file_uploader(
		label = 'Upload your input csv or excel file',
		type = ["csv"],
		)

	st.header(
		body = 'Feature Selection',
		)

	st.selectbox(
		label = "Choose Date Column:",
		options = data.dates,
		index = None,
		)

	st.selectbox(
		label = 'Choose Rate Column:',
		options = data.numbers,
		index = None,
		)

	st.header(
		body = 'Data Filtering',
		)

	st.selectbox(
		label = "Group By:",
		options = data.groups,
		index = None,
		)

	st.selectbox(
		label = 'Filter By:',
		options = data.items(),
		index = None,
		)

	st.header(
		body = 'Timeseries View',
		)

	st.multiselect(
		label = 'Add to the Plot:',
		options = data.plottable(),
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
		on_change = Update.opacity,
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