import numpy
import pandas

import streamlit

from ._outlook import Outlook

from ._visualized import View

class Update:

	@streamlit.cache_data
	def load_data(file):

		if file is None:
			frame = pandas.DataFrame()
		else:
			frame = pandas.read_excel(file)

		return Outlook(frame)

	@staticmethod
	def load_view(state,data:Outlook):

		if Update.NoneFlag(state,'datekey','ratekey','grouplist'):
			return

		return data(state.datekey).view(
			*state.grouplist,numbers=[state.ratekey]+state.viewlist)

	@staticmethod
	def load_frame(state,group:View):

		if Update.NoneFlag(state,'itemkey'):
			return

		return group.filter(state.itemkey)

	@staticmethod
	def NoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False