import os

import pandas

import streamlit

from ._outlook import Outlook
from ._tableau import Tableau

from ._timeview import TimeView

class Update:

	@streamlit.cache_data
	def load_data(file):

		if file is None:
			return Outlook()

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

		return Outlook(frame)

	@staticmethod
	def load_table(state,data:Outlook):

		if Update.NoneFlag(state,'datehead','ratehead','nominals'):
			return Tableau()(data.leadhead,data.datehead)
		
		view = data(datehead=state.datehead).view(*state.nominals)

		return Tableau(view.frame)(view.leadhead,view.datehead)

	@staticmethod
	def load_view(state,table:Tableau):

		if Update.NoneFlag(state,'itemname'):
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