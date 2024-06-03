import os

import pandas

import streamlit

from ._outlook import Outlook

from ._timeview import TimeView

class Request:

	@streamlit.cache_data
	def frame(file):

		if file is None:
			return pandas.DataFrame()

		fmt = os.path.splitext(file.name)[1]

		if fmt == '.xlsx':
			frame = pandas.read_excel(file,sheet_name=0)
		elif fmt == '.csv':
			frame = pandas.read_csv(file)
		elif fmt == '.json':
			frame = pandas.read_json(file)
		elif fmt == '.txt':
			frame = pandas.read_fwf(file,widths=col_widths,header=None)
		elif fmt == '.dta':
			frame = pandas.read_stata(file)
		elif fmt == '.orc':
			frame = pandas.read_orc(file)
		else:
			frame = pandas.DataFrame()

		return frame

	@staticmethod
	def data(frame:pandas.DataFrame):

		return Outlook(frame)

	@staticmethod
	def table(state,data:Outlook):

		if Request.NoneFlag(state,'datehead','ratehead','nominals'):
			return Tableau()(data.leadhead,data.datehead)
		
		view = data(datehead=state.datehead).view(*state.nominals)

		return Tableau(view.frame)(view.leadhead,view.datehead)

	@staticmethod
	def view(state,table):

		if Request.NoneFlag(state,'itemname'):
			return TimeView()(table.leadhead,table.datehead)

		return table.view(state.itemname)

	@staticmethod
	def NoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True
			if len(state[arg])==0:
				return True

		return False