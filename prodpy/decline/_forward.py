import datetime

import numpy
import pandas

from ._model import Model

class Forward():

	def __init__(self,model:Model=None):
		self._model = model

	@property
	def model(self):
		return self._model
	
	def __call__(self,start:datetime.date,end:datetime.date,*,model:Model=None,dayCodeFlag=False):

		method = "run1" if dayCodeFlag else "run2"

		return getattr(self,method)(self.model,start,end)

	@staticmethod
	def run(model:Model,days:numpy.ndarray=None,start:datetime.date=None,end:datetime.date=None,number:int=None,timecode:str=None):
		"""Calculates the theoretical rates for the given days or datetime parameters."""

		if days is None:
			days = Forward.time_range(start,end,number)

		rates = getattr(Forward,f"{model.mode}")(model,days)

		dates = Forward.date_range(None,start,end,number,timecode)

		return {"dates":dates,"rates":rates}

	@staticmethod
	def Exponential(model:Model,days:numpy.ndarray):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return model.rate0*numpy.exp(-model.decline0*days)

	@staticmethod
	def Hyperbolic(model:Model,days:numpy.ndarray):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """
		return model.rate0/(1+model.exponent*model.decline0*days)**(1/model.exponent)

	@staticmethod
	def Harmonic(model:Model,days:numpy.ndarray):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return model.rate0/(1+model.decline0*days)

	@staticmethod
	def time_range(start:datetime.date,end:datetime.date,number:int=None):

		if number is None:
			return numpy.arange((end-start).days)
		
		return numpy.linspace(0,(end-start).days,number)

	@staticmethod
	def date_range(days:numpy.ndarray=None,start:datetime.date=None,end:datetime.date=None,number:int=None,timecode:str=None):
		"""
		Adds days to start calculating new datetimes with the
		  specified timecode. Available timecodes and their meanings
		  are shown below:

		TimeCode	Meaning
		-------- 	-------------
			   h	hour
			   m	minute
			   s	second
			  ms	millisecond
			  us	microsecond

		Returns numpy array of datetimes.
		"""

		if number is None:
			return pandas.date_range(start,end)

		if start is None:
			start = datetime.date(2000,1,1)

		return pandas.date_range(start,end,periods=number,unit="us")

		microsecs = numpy.asarray(days)*24*60*60*1000*1000

		timedelta = numpy.asarray(
			microsecs,dtype=f'timedelta64[us]'
			)

		datetimes = numpy.datetime64(start)+timedelta

		code = 'D' if timecode is None else timecode

		return datetimes.astype(f'datetime64[{code}]')
		

		

		
