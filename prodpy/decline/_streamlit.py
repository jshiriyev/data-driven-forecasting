import datetime

import os

import sys

# sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import matplotlib.pyplot as plt

import pandas as pd

import streamlit as st

from prodpy.decline import Analysis

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

# def file_selector(folder_path='.'):

#     filenames = os.listdir(folder_path)

#     selected_filename = st.selectbox('Select a file', filenames)

#     return os.path.join(folder_path, selected_filename)

# def get_welldata(well_name):

# 	return df[df['Well']==well_name]

with st.sidebar:

	st.header('User Input Features')

	uploaded_file = st.file_uploader(
		'Upload your input csv or excel file',type=["csv","xlsx"])

	if uploaded_file is not None:

		df = pd.read_excel(uploaded_file)

		# st.text_input('You selected:', value=f"{os.path.basename(filepath)}",disabled=True)

		numbers = df.select_dtypes(include=('number',))

		orate_key = st.selectbox("Oil Rates:",numbers.columns,index=None)

		datetime = df.select_dtypes(include=('datetime64',))

		dates_key = st.selectbox("Dates:",datetime.columns,index=None)

		if orate_key is not None and dates_key is not None:

			dca = Analysis(dates_key,orate=orate_key)

		category = df.select_dtypes(exclude=('number','datetime64'))

		group_key = st.selectbox("Group By:",category.columns,index=None)

		# st.write(f"{os.path.basename(filepath)}")
		if group_key is not None:

			item_list = df[group_key].unique()

			item = st.selectbox("Current stock:",item_list,index=None)

			frame1 = dca.get(df,**{group_key:item})

			print(frame1)

			frame2 = dca.predict(frame1)

if item is not None:

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

	fig, ax1 = plt.subplots(nrows=1)

	# fig.set_figheight(15)
	ax1.scatter(frame1['Date'],frame1['Actual Oil, Mstb/d'],s=1)
	ax1.plot(frame2['Date'],frame2['TRates'],color='k',label='Exponential Decline')
	# ax1.scatter(wdf['Date'],orate,s=1)
	ax1.set_ylabel('Oil Rate, MSTB/d')

	# ax2.scatter(wdf['Date'],lrate,s=1)
	# ax2.set_ylabel('Liquid Rate, MSTB/d')

	# ax3.scatter(wdf['Date'],gor,s=1)
	# ax3.set_ylabel('GOR, SCF/STB')

	# ax4.scatter(wdf['Date'],wcut,s=1)
	# ax4.set_ylabel('Water Cut, %')

	# ax5.scatter(wdf['Date'],grate,s=1)
	# ax5.set_ylabel('Gas Rate, MMSCF/d')

	# ax6.scatter(wdf['Date'],wrate,s=1)
	# ax6.set_ylabel('Water Rate, MSTB/d')

	st.pyplot(fig)