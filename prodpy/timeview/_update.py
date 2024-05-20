import os

import numpy
import pandas

import streamlit

from ._outlook import Outlook

from ._itemview import ItemView

class Update:

	@streamlit.cache_data
	def load_data(file):

		frame = pandas.DataFrame() # DEFAULT

		if file is None:
			return Outlook(frame)

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

		return Outlook(frame)

	@staticmethod
	def load_view(state,data:Outlook):

		if Update.NoneFlag(state,'datehead','ratehead','pilelist'):
			frame = pandas.DataFrame()
		else:
			frame = data(state.datehead).view(*state.pilelist)

		return ItemView(frame)

	@staticmethod
	def load_frame(state,view:ItemView):

		if Update.NoneFlag(state,'itemname'):
			frame = pandas.DataFrame()
		else:
			frame = view.filter(state.itemname)

		return frame

	@staticmethod
	def NoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True
			if len(state[arg])==0:
				return True

		return False