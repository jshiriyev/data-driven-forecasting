import datetime

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import numpy as np
import pandas as pd

import plotly_express as px
import plotly.graph_objects as go

import streamlit as st

from prodpy.decline import Analysis
from prodpy.decline import Optimize
from prodpy.decline import Model

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

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

def upload_file():
	pass

# DECLINE RATE MODEL PARAMETERS

if 'selected_time_interval' not in st.session_state:
	st.session_state['selected_time_interval'] = (date_amin,date_amax)

decline_type_options = ['Exponential','Hyperbolic','Harmonic']

if 'mode' not in st.session_state:
    st.session_state['mode'] = 'Exponential'

if 'exponent' not in st.session_state:
	st.session_state['exponent'] = 0.

if 'rate0' not in st.session_state:
	st.session_state['rate0'] = None

if 'decline0' not in st.session_state:
	st.session_state['decline0'] = None

def time_update():

	date_min,date_max = st.session_state.selected_time_interval

	cond1 = st.session_state.datetimes >= np.datetime64(date_min)
	cond2 = st.session_state.datetimes <= np.datetime64(date_max)

	conds = np.logical_and(cond1,cond2)

	st.session_state['opacity'] = conds*0.7+0.3

def mode_update():

	exponent = Model.get_exponent(st.session_state.mode.lower())

	st.session_state['exponent'] = exponent*100

def exponent_update():

	exponent = st.session_state.exponent/100.

	mode = Model.get_mode(exponent)

	st.session_state['mode'] = mode.capitalize()

def optimize_update():

	pass

def run_model_update():

	ss = st.session_state

	try:
		float(ss.rate0)
	except:
		return

	try:
		float(ss.decline0)
	except:
		return

	model = Model(
		float(ss.rate0),
		float(ss.decline0),
		ss.mode.lower(),
		ss.exponent/100,
		)

	ss['fitline'] = model(datetimes=st.session_state.datetimes)

def save_model():
	pass

def export_fits():
	pass

# VISUALIZED DATA

if 'datetimes' not in st.session_state:
	st.session_state['datetimes'] = datetimes

if 'inputrates' not in st.session_state:
	st.session_state['inputrates'] = None

if 'opacity' not in st.session_state:
	st.session_state['opacity'] = 1.

if 'fitline' not in st.session_state:
	st.session_state['fitline'] = None

# DISPLAY SETTINGS

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

	# dca = Analysis(dates_key,rates_key)

	st.header('Data Filtering')

	group_key = st.selectbox("Group By:",catgcols,index=None)

	if group_key is not None:

		frame = analysis.groupby(frame,group_key)

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

	# date_amin = frame2[dca.heads.dates].iloc[0].date()
	# date_amax = frame2[dca.heads.dates].iloc[-1].date()

	slider = st.slider(
		label = "Time Interval:",
		min_value = date_amin,
		max_value = date_amax,
		key = 'selected_time_interval',
		on_change = time_update,
		)

	mode = st.selectbox(
		label = "Decline Mode:",
		options = decline_type_options,
		key = 'mode',
		on_change = mode_update,
		)

	exponent = st.number_input(
		label = 'Decline Exponent %',
		min_value = 0,
		max_value = 100,
		key = 'exponent',
		step = 5,
		on_change = exponent_update,
		)

	st.button(
		label = 'Optimize',
		use_container_width = True,
		)

	rate0 = st.text_input(
		label = 'Initial Rate',
		key = 'rate0',
		) # ,placeholder=str(model.rate0)

	decline0 = st.text_input(
		label='Initial Decline Rate',
		key = 'decline0',
		) # ,placeholder=str(model.decline0)

	st.button(
		label = 'Run Model',
		use_container_width = True,
		on_click = run_model_update,
		)

	st.subheader(r'''
		Save & Export
		''',
		)

	st.button(
		label = "Save Model",
		use_container_width = True,
		)

	st.button(
		label = "Export Fit",
		use_container_width = True,
		)

