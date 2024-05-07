import datetime

import sys

# sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import pandas as pd

import plotly_express as px
import plotly.graph_objects as go

import streamlit as st

from prodpy.decline import Analysis

decline_modes = ['Exponential','Hyperbolic','Harmonic']

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

def get_dca(dates_key=None,rates_key=None):

	if dates_key is None:
		return

	if rates_key is None:
		return

	return Analysis(dates_key,orate=rates_key)

def get_grouped(frame=None,analysis=None,group_key=None):

	if frame is None:
		return

	if analysis is None:
		return

	if group_key is None:
		return

	return analysis.groupby(frame,group_key)

InputDataIsReady = False

with st.sidebar:

	st.header('Input Data')

	uploaded_file = st.file_uploader(
		'Upload your input csv or excel file',type=["csv","xlsx"])

	if uploaded_file is not None:

		df = pd.read_excel(uploaded_file)

		datecols = df.select_dtypes(include=('datetime64',)).columns
		numbcols = df.select_dtypes(include=('number',)).columns
		catgcols = df.select_dtypes(exclude=('number','datetime64')).columns

		st.header('Feature Selection')

		dates_key = st.selectbox("Choose Date Column:",datecols,index=None)
		rates_key = st.selectbox("Choose Rate Column:",numbcols,index=None)

		dca = get_dca(dates_key,rates_key)

		st.header('Data Filtering')

		group_key = st.selectbox("Group By:",catgcols,index=None)

		if group_key is not None:

			frame = get_grouped(df,dca,group_key)

			item_list = frame[group_key].unique()

			item = st.selectbox("Filter By:",item_list,index=None)

			if item is not None:

				frame1 = dca.filter(frame,item)

				frame2,model = dca.predict(frame1,start=None,cease=None)

				InputDataIsReady = True

		st.header('Timeseries View')

		numbcols = numbcols.drop(rates_key)

		graph_key = st.multiselect("Add to the Plot:",numbcols)

column1, column2 = st.columns([0.7, 0.3],gap='large')

with column1 :

	st.header(f'{item} Rates')

	plot1 = px.scatter(frame2,x='Date',y='Actual Oil, Mstb/d')
	plot2 = px.line(frame2,x="Date",y="TRates")

	plot2.update_traces(line_color='black')

	plot3 = go.Figure(data=plot1.data+plot2.data)

	plot3.update_layout(
		yaxis_title = 'Actual Oil, Mstb/d'
		)

	st.plotly_chart(plot3,use_container_width=True)

with column2:

	st.header('Decline Model Parameters')

	slider = st.slider(
		"Time Interval:",
		value=(frame2[dca.heads.dates].iloc[0].date(),
			   frame2[dca.heads.dates].iloc[-1].date())
		)

	mode = st.selectbox("Decline Mode:",decline_modes)

	exponent = st.number_input(label='Decline Curve Exponent',value=0.,step=0.05)

	rate0 = st.text_input(label='Initial Rate',placeholder=str(model.rate0))

	decline0 = st.text_input(label='Initial Decline Rate',placeholder=str(model.decline0))

