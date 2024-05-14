import numpy
import pandas

import streamlit

from ._outlook import Outlook

class Update():

	@streamlit.cache_data
	def load_data(file):

		if file is None:
			return Outlook()

		frame = pandas.read_excel(file)

		return Outlook(frame)

	def load_group(data,state):

		if Update.argNoneFlag(state,'datekey','ratekey','groupkey'):
			return

		group = data.refine(
			state.ratekey,
			*state.viewlist,
			groupkey = state.groupkey,
			datekey = state.datekey,
			)

		return group

	def load_frame(group,state):

		return group.filter(state.itemkey)

	@staticmethod
	def argNoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False