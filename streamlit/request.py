import os

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import pandas

import streamlit as st

from prodpy import timeview as tv

class Request:

	@st.cache_data
	def data(file,**kwargs):

		extent = Request.extent(file)
		reader = Request.reader(extent)

		if reader is None:
			frame = pandas.DataFrame()
		else:
			frame = reader(file,**kwargs)

		return tv.Outlook(frame)

	@staticmethod
	def extent(file):

		if file is None:
			return

		return os.path.splitext(file.name)[1]

	@staticmethod
	def reader(extent:str):

		if extent is None:
			return

		if extent == '.csv':
			return pandas.read_csv

		if extent == '.xlsx':
			return pandas.read_excel

		st.warning(f"{extent} can not be handled at the moment.")

	@staticmethod
	def view(data,*args):

		if data.datehead is None:
			return tv.TimeView(pandas.DataFrame())

		return data.toview(*args)