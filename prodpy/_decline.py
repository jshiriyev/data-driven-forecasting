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

	@staticmethod
	def forward(days,rate0,decline0,method="exponential",**kwargs):
		return getattr(DCA,f"{method}")(days,rate0,decline0,**kwargs)

	@staticmethod
	def exponential(days,rate0,decline0):
		return rate0*numpy.exp(-decline0*days)

	@staticmethod
	def hyperbolic(days,rate0,decline0,exponent=0.5):
		return rate0/(1+exponent*decline0*days)**(1/exponent)

	@staticmethod
	def harmonic(days,rate0,decline0):
		return rate0/(1+decline0*days)

	@staticmethod
	def inverse(days,rates,method='exponential',**kwargs):
		return getattr(DCA,f"inv{method}")(days,rates,**kwargs)

	@staticmethod
	def invexponential(days,rates):
		intercept,slope = DCA.fit_line(days,numpy.log(rates))
		return numpy.exp(intercept),-slope

	@staticmethod
	def invhyperbolic(days,rates,exponent=0.5):
		intercept,slope = DCA.fit_line(days,numpy.power(1/rates,exponent))
		return intercept**(-1/exponent),slope/intercept/exponent

	@staticmethod
	def invharmonic(days,rates):
		intercept,slope = DCA.fit_line(days,1/rates)
		return intercept**(-1),slope/intercept

	@staticmethod
	def fit_line(xvals,yvals):

		A = numpy.zeros((2,2))
		b = numpy.zeros((2,1))

		A[0,0] = len(xvals)
		A[0,1] = np.sum(xvals)
		A[1,0] = np.sum(xvals)
		A[1,1] = np.sum(xvals**2)

		b[0,0] = numpy.sum(numpy.log(yvals))
		b[1,0] = numpy.sum(numpy.log(yvals)*xvals)

		return numpy.linalg.solve(A,b).flatten()