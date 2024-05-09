import datetime

import sys

# sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import numpy as np
import pandas as pd

import plotly_express as px
import plotly.graph_objects as go

import streamlit as st

from prodpy.decline import Model

from prodpy.decline import Session
from prodpy.decline import Update

# INPUT FILE PARAMETERS

datecols = [] # columns in date format
numbcols = [] # columns in number format
catgcols = [] # columns in string format
itemlist = [] # filter by elements

date_amin = datetime.date(2020,1,1)
date_amax = datetime.date(2020,6,1)

datetimes = pd.date_range(start=date_amin,end=date_amax)

np.random.seed(0)

rates = np.random.rand(datetimes.size)*1000

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

st.session_state = Session.column1(st.session_state)
st.session_state = Session.column2(st.session_state,datetimes)
st.session_state = Session.column3(st.session_state,date_amin,date_amax)

with st.sidebar:

	st.header('Input Data')

	uploaded_file = st.file_uploader(
		'Upload your input csv or excel file',type=["csv"])

	if uploaded_file is not None:

		df = pd.read_excel(uploaded_file)

		datecols = df.select_dtypes(include=('datetime64',)).columns
		numbcols = df.select_dtypes(include=('number',)).columns
		catgcols = df.select_dtypes(exclude=('number','datetime64')).columns

	st.header('Feature Selection')

	dates_key = st.selectbox("Choose Date Column:",datecols,index=None)
	rates_key = st.selectbox("Choose Rate Column:",numbcols,index=None)

	# dca = decline.Analysis(dates_key,rates_key)

	st.header('Data Filtering')

	group_key = st.selectbox("Group By:",catgcols,index=None)

	if group_key is not None:

		frame = decline.Analysis.groupby(frame,group_key)

		itemlist = frame[group_key].unique()

	displayedItem = st.selectbox("Filter By:",itemlist,index=None)

	if displayedItem is not None:

		frame1 = dca.filter(frame,displayedItem)

		frame2,model = dca.predict(frame1,start=None,cease=None)

	st.header('Timeseries View')

	if rates_key is not None:
		numbcols = numbcols.drop(rates_key)

	graph_key = st.multiselect("Add to the Plot:",numbcols)

displayColumn, modelColumn = st.columns([0.7, 0.3],gap='large')

with displayColumn:

	st.header(f'{displayedItem} Rates')

	plot1 = px.scatter(
		x = st.session_state.datetimes,
		y = rates,
		opacity = st.session_state.opacity
		)

	plot2 = px.line(
		x = st.session_state.datetimes,
		y = st.session_state.fitline
		)

	plot2.update_traces(line_color='black')

	plot3 = go.Figure(data=plot1.data+plot2.data)

	# plot3.update_layout(
	# 	yaxis_title = 'Actual Oil, Mstb/d'
	# 	)

	st.plotly_chart(plot3,use_container_width=True)

with modelColumn:

	st.header('Decline Model Parameters')

	st.slider(
		label = "Time Interval:",
		min_value = date_amin,
		max_value = date_amax,
		key = 'time_interval_selected',
		on_change = Update.time,
		args = (st.session_state,),
		)

	st.selectbox(
		label = "Decline Mode:",
		options = Model.options,
		key = 'mode',
		on_change = Update.mode,
		args = (st.session_state,),
		)

	st.number_input(
		label = 'Decline Exponent %',
		min_value = 0,
		max_value = 100,
		key = 'exponent',
		step = 5,
		on_change = Update.exponent,
		args = (st.session_state,),
		)

	st.button(
		label = 'Optimize',
		use_container_width = True,
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
		on_click = Update.run,
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