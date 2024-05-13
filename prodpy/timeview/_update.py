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

	@streamlit.cache_data
	def load_view(data,state):
		"""
		It should be dependent on the followings:

			datekey
			ratekey
			groupkey

			itemkey
			viewlist
		"""

		if Update.argNoneFlag(state,'datekey','ratekey','groupkey'):
			x = pandas.Series(dtype='datetime64[D]')
			y = pandas.Series(dtype='float64')
			return x,y

		items = data.items(state.groupkey)

		frame = data.get_item(state.datekey,state.ratekey,**{state.groupkey:items[0]})

		x = frame[state.datekey]
		y = frame[state.ratekey]

		return x,y

	@staticmethod
	def argNoneFlag(state,*args):

		for arg in args:
			if state[arg] is None:
				return True

		return False