class Analysis():

	def __init__(self,frame,dhead='date',start=None,stop=None):
		"""
		frame 	: panda DataFrame to be used in Decline Curve Analysis

		dhead 	: head of date column that contains production dates
		rhead 	: head of rate column that contains production rates (oil, water, or gas rate)

		start 	: start date of interval where to implement DCA, if None first date is selected
		stop 	: stop  date of interval where to implement DCA, if None last date is selected
		"""

		self._frame = frame

		self._dhead  = dhead

		self._start = start
		self._stop  = stop

	def fit(self,rhead,method='exponential',**kwargs):
		return self.fit_method(*self.preprocess(rhead),method='exponential',**kwargs)

	def preprocess(self,rhead):

		frame = self.trim()

		dates = frame[self._dhead]

		days = dates-dates[0]

		return days,frame[rhead]

	def trim(self):

		t0 = [self.dates>=self.start]
		t1 = [self.dates<=self.stop]

		return self._frame[np.logical_and(t0,t1)]

	@property
	def frame(self):
		return self._frame

	@property
	def dhead(self):
		return self._dhead

	@property
	def dates(self):
		return self._frame[self._dhead]
	
	@property
	def start(self):
		return self._dates[0] if self._start is None else self._start

	@property
	def stop(self):
		return self._dates[-1] if self._stop is None else self._stop

	@staticmethod
	def fit_method(days,rates,method='exponential',**kwargs):
		prop = DCA.inverse(days,rates,method,**kwargs)
		return DCA.forward(days,*prop,method,**kwargs),prop

if __name__ == "__main__":

	import pandas as pd

	df = pd.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	# print(df.columns)

	# print(df['Well'].unique())

	# print(df[df['Well']=='D32'])

	print((df['Date']-df['Date'][0])*5)

	# print(df.head)

	# print(dir(df))