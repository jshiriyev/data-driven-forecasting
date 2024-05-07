import datetime

import os

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import matplotlib.pyplot as plt

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

			item = st.selectbox("Current stock:",item_list,index=None)

			if item is not None:
				frame1 = dca.filter(frame,item)

				frame2,model = dca.predict(frame1,start=None,cease=None)

				InputDataIsReady = True

if InputDataIsReady:

	column1, column2 = st.columns([0.7, 0.3])
	
	with column1 :

		# st.header('Oil Rate')
		# st.header('Liquid Rate')
		# st.header('Gas Oil Ratio')
		# st.header('Water Cut')
		# st.header('Gas Rate')
		# st.header('Water Rate')

		# orate = wdf['Actual Oil, Mstb/d']
		# grate = wdf['Actual Gas, MMscf/d']
		# wrate = wdf['Actual Water, Mstb/d']
		# lrate = orate+wrate
		# wcut  = wrate/(wrate+orate)*100
		# gor   = grate*1000/orate

		st.header(f'{item} Rates')

		plot1 = px.scatter(frame2,x='Date',y='Actual Oil, Mstb/d')
		plot2 = px.line(frame2,x="Date",y="TRates")

		plot2.update_traces(line_color='black')

		plot3 = go.Figure(data=plot1.data+plot2.data)

		plot3.update_layout(
			yaxis_title = 'Actual Oil, Mstb/d'
			)

		st.plotly_chart(plot3)

		# st.scatter_chart(
		#     frame2,
		#     x='Date',
		#     y='Actual Oil, Mstb/d',
		# )

		# st.line_chart(frame2, x="Date", y="TRates")

		# fig, ax1 = plt.subplots(nrows=1)

		# # fig.set_figheight(15)
		# ax1.scatter(frame1['Date'],frame1['Actual Oil, Mstb/d'],s=1)
		# ax1.plot(frame2['Date'],frame2['TRates'],color='k',label='Exponential Decline')
		# # ax1.scatter(wdf['Date'],orate,s=1)
		# ax1.set_ylabel('Oil Rate, MSTB/d')

		# # ax2.scatter(wdf['Date'],lrate,s=1)
		# # ax2.set_ylabel('Liquid Rate, MSTB/d')

		# # ax3.scatter(wdf['Date'],gor,s=1)
		# # ax3.set_ylabel('GOR, SCF/STB')

		# # ax4.scatter(wdf['Date'],wcut,s=1)
		# # ax4.set_ylabel('Water Cut, %')

		# # ax5.scatter(wdf['Date'],grate,s=1)
		# # ax5.set_ylabel('Gas Rate, MMSCF/d')

		# # ax6.scatter(wdf['Date'],wrate,s=1)
		# # ax6.set_ylabel('Water Rate, MSTB/d')

		# st.pyplot(fig)

	with column2:

		st.header('Decline Model Inputs')

		slider = st.slider(
			"Select Time Interval:",
			value=(frame2[dca.heads.dates].iloc[0].date(),
				   frame2[dca.heads.dates].iloc[-1].date())
			)

		rate0 = st.text_input(label='Initial Rate',placeholder=str(model.rate0))

		try:
			float(rate0)
		except:
			pass

		decline0 = st.text_input(label='Initial Decline Rate',placeholder=str(model.decline0))

		try:
			float(decline0)
		except:
			pass

		mode = st.selectbox("Choose Decline Mode:",decline_modes)

		exponent = st.number_input(label='Decline Curve Exponent',value=0.,step=0.05)

