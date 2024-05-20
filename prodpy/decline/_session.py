import datetime

import streamlit

from ._model import Model

class Session():

	mindate = datetime.date(2020,1,1)
	maxdate = datetime.date(2025,1,1)

	def __init__(self,state:streamlit._SessionStateProxy,model:Model=None,mindate:datetime.date=None,maxdate:datetime.date=None):
		self.state = state

		self.model = Model() if model is None else model

		if mindate is not None:
			self.mindate = mindate

		if maxdate is not None:
			self.maxdate = maxdate
	
	def set(self):

		return self.__call__(
			mode     = self.model.mode,
			exponent = self.model.exponent,
			rate0    = self.model.rate0.__str__(),
			decline0 = self.model.decline0.__str__(),
			mindate  = self.mindate,
			maxdate  = self.maxdate,
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

if __name__ == "__main__":

	ss = Session(mindate=datetime.date(2008,1,1))

	print(ss.mindate)
	print(ss.maxdate)