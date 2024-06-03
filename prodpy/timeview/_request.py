import os

import pandas

import streamlit as st

from ._outlook import Outlook

from ._timeview import TimeView

class Request:

	@staticmethod
	def extension(file):

		if file is None:
			return

		return os.path.splitext(file.name)[1]

	@st.cache_data
	def frame(file,reader='read_csv',**kwargs):

		if file is None:
			return

		return getattr(pandas,reader)(file,**kwargs)

	@staticmethod
	def data(frame:pandas.DataFrame):

		if frame is None:
			frame = pandas.DataFrame()

		return Outlook(frame)

	@staticmethod
	def table(state,data:Outlook):

		if state.datehead is None:
			return TimeView(pandas.DataFrame())

		return data(datehead=state.datehead).toview(*state.nominals)

	@staticmethod
	def view(state,view):

		return view.filter(state.itemname)

	@staticmethod
	def NoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True
			if len(state[arg])==0:
				return True

		return False