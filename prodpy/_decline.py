import numpy
import pandas

class DCA():

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

	def curve(self,rhead,method='exponential',exponent=None):

		xvals,rates = self.preprocess(rhead)

		param = getattr(self,f"{method}_param")(xvals,rates)

		return getattr(self,f"{method}_curve")(xvals,*param)

	def param(self,rhead,method='exponential',exponent=None):

		xvals,rates = self.preprocess(rhead)

		return getattr(self,f"{method}_param")(xvals,rates)

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

	def preprocess(self,rhead):

		frame = self.trim()

		dates = frame[self._dhead]

		xvals = dates-dates[0]
		rates = frame[rhead]

		return xvals,rates

	def trim(self):

		t0 = [self.dates>=self.start]
		t1 = [self.dates<=self.stop]

		return self._frame[np.logical_and(t0,t1)]

	@staticmethod
	def exponential_curve(xvals,rate0,decline):
		return rate0*numpy.exp(-decline*xvals)

	@staticmethod
	def hyperbolic_curve(xvals,rate0,decline,exponent=0.5):
		return rate0/(1+exponent*decline*xvals)**(1/exponent)

	@staticmethod
	def harmonic_curve(xvals,rate0,decline):
		return rate0/(1+decline*xvals)

	@staticmethod
	def exponential_param(xvals,rates):
		
		A = numpy.zeros((2,2))
		b = numpy.zeros((2,1))

		A[0,0] = len(xvals)
		A[0,1] = -np.sum(xvals)
		A[1,0] = np.sum(xvals)
		A[1,1] = -np.sum(xvals**2)

		b[0,0] = numpy.sum(numpy.log(rates))
		b[1,0] = numpy.sum(numpy.log(rates)*xvals)

		sol = numpy.linalg.solve(A,b).flatten()

		return numpy.exp(sol[0]),sol[1]

	@staticmethod
	def hyperbolic_param(xvals,rates,exponent=0.5):
		return

	@staticmethod
	def harmonic_param(xvals,rates):
		return
	
	