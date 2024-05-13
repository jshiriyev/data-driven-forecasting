import numpy
import pandas

import streamlit

from ._outlook import Outlook

class Update():

	@streamlit.cache_data
	def load_file(file):

		if file is None:
			return Outlook()

		frame = pandas.read_excel(file)

		return Outlook(frame)

	def load_view(view,state):

		if Update.argNoneFlag(state,'datekey','ratekey','groupkey'):
			x = pandas.Series(dtype='datetime64[D]')
			y = pandas.Series(dtype='float64')
			return x,y

		items = view.items(state.groupkey)

		frame = view.get_item(state.datekey,state.ratekey,**{state.groupkey:items[0]})

		x = frame[state.datekey]
		y = frame[state.ratekey]

		return x,y

	@staticmethod
	def argNoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False