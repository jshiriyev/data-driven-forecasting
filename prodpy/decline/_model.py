import numpy

class Model:

	def __init__(self,days):

		self.days = days

	def __call__(self,rate0,decline0,method="exponential",**kwargs):

		return getattr(Model,f"{method}")(self.days,rate0,decline0,**kwargs)

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
		return getattr(Model,f"inv{method}")(days,rates,**kwargs)

	@staticmethod
	def invexponential(days,rates):
		intercept,slope = Model.fit_line(days,numpy.log(rates))
		return numpy.exp(intercept),-slope

	@staticmethod
	def invhyperbolic(days,rates,exponent=0.5):
		intercept,slope = Model.fit_line(days,numpy.power(1/rates,exponent))
		return intercept**(-1/exponent),slope/intercept/exponent

	@staticmethod
	def invharmonic(days,rates):
		intercept,slope = Model.fit_line(days,1/rates)
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