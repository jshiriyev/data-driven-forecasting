import datetime

from ._model import Model

class Session():

	def __init__(self,state,mindate:datetime.date=None,maxdate:datetime.date=None):

		self._state = state

		self._mindate = datetime.date(2020,1,1) if mindate is None else mindate
		self._maxdate = datetime.date(2020,6,1) if maxdate is None else maxdate

	def __call__(self,**kwargs):

		for key,value in kwargs.items():
			self.add(self._state,key,value)

		return self._state

	@property
	def mindate(self):
		return self._mindate
	
	@property
	def maxdate(self):
		return self._maxdate
	
	@property
	def timelims(self):
		return (self._mindate,self._maxdate)
	
	@staticmethod
	def parameters(state,mindate:datetime.date=None,maxdate:datetime.date=None):
		"""MODEL PARAMETERS"""

		if mindate is None:
			mindate = datetime.date(2020,1,1)

		if maxdate is None:
			maxdate = datetime.date(2020,6,1)

		state = Session.add(state,'tlim',(mindate,maxdate))
		state = Session.add(state,'mode',Model.mode)
		state = Session.add(state,'exponent',Model.exponent)
		state = Session.add(state,'rate0',str(Model.rate0))
		state = Session.add(state,'decline0',str(Model.decline0))

		return state

	@staticmethod
	def add(state,key,value=None):

		if key not in state:
			state[key] = value

		return state