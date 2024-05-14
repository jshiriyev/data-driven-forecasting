import streamlit

class Session():

	def __init__(self,state:streamlit._SessionStateProxy):

		self.state = state

	def set(self):

		return self.__call__(
			datekey = None,
			ratekey = None,
			groupkey = None,
			itemkey = None,
			viewlist = [],
			)

	def __call__(self,*args,**kwargs):

		for key in args:
			if isinstance(key,str):
				self.state = self.add(key)
			else:
				raise Warning("The positional arguments must be string!")

		for key,value in kwargs.items():
			self.state = self.add(key,value)

		return self.state

	def add(self,key,value=None):

		if key not in self.state:
			self.state[key] = value

		return self.state