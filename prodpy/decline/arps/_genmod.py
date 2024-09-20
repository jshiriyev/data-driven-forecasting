import numpy

from scipy._lib._bunch import _make_tuple_bunch

NonLinResult = _make_tuple_bunch('NonLinResult',
	['decline','intercept','rvalue'])

# LinregressResult = _make_tuple_bunch('LinregressResult',
# 	['slope','intercept','rvalue','pvalue','stderr'],
# 	extra_field_names=['intercept_stderr'])

Result = _make_tuple_bunch('Result',['linear','nonlinear'])

class GenModel:
	"""Base class for Arp's decline models: Exponential, 
	Hyperbolic, and Harmonic; main decline attributes are:
	
	Di 		: initial decline rate
	yi 		: initial y value

	The decline exponent defines the mode:
	
	xp 		: Arps' decline-curve exponent (b)

	b = 0. 		-> mode = 'Exponential'
	0 < b < 1.	-> mode = 'Hyperbolic'
	b = 1.		-> mode = 'Harmonic'

	"""

	def __init__(self,Di:float,yi:float,xp:float=None):

		self._Di = Di
		self._yi = yi
		self._xp = xp

	@property
	def Di(self):
		return self._Di

	@property
	def yi(self):
		return self._yi

	@property
	def xp(self):
		return self._xp
	
	@property
	def args(self):
		return self.Di,self.yi,self.xp
	
	def base(self,x:numpy.ndarray):
		return self.Di*numpy.asarray(x)

	def ycal(self,x:numpy.ndarray):
		pass

	def ycum(self,x:numpy.ndarray):
		pass

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray):
		"""Linear regression of x and yobs values"""
		try:
			result = linregress(x,yobs)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
		else:
			return result

	def rvalue(self,x:numpy.ndarray,yobs:numpy.ndarray):

		ssres = numpy.nansum((yobs-self.ycal(x))**2)
		sstot = numpy.nansum((yobs-numpy.nanmean(yobs))**2)

		return 1-ssres/sstot

if __name__ == "__main__":

	bc = GenModel(100,0.005)

	print(bc.yi)
	print(bc.Di)
	print(bc.expo)
	print(bc.base([1,2,3]))