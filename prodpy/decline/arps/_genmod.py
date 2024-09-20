import numpy

from scipy._lib._bunch import _make_tuple_bunch

Score = _make_tuple_bunch('Score',['linear','nonlinear'])

class GenModel:
	"""Base class for Arp's decline models: Exponential, 
	Hyperbolic, and Harmonic; main decline attributes are:

	yi 		: initial y value
	Di 		: initial decline rate

	The decline exponent defines the mode:
	
	xp 		: Arps' decline-curve exponent (b)

	b = 0. 		-> mode = 'Exponential'
	0 < b < 1.	-> mode = 'Hyperbolic'
	b = 1.		-> mode = 'Harmonic'

	"""

	def __init__(self,yi:float,Di:float,xp:float=None):

		self._yi = yi 
		self._Di = Di
		self._xp = xp

	@property
	def yi(self):
		return self._yi

	@property
	def Di(self):
		return self._Di

	@property
	def xp(self):
		return self._xp
	
	@property
	def args(self):
		return self._yi,self._Di,self._xp
	
	def base(self,x:numpy.ndarray):
		return self.Di*numpy.asarray(x)

	def ycal(self,x:numpy.ndarray):
		pass

	def ycum(self,x:numpy.ndarray):
		pass

	def prepare(self,xobs:numpy.ndarray,yobs:numpy.ndarray,xi:float=0):
		pass

	def regress(self,xobs:numpy.ndarray,yobs:numpy.ndarray):
		"""Linear regression of xobs and yobs values"""
		try:
			result = linregress(xobs,yobs)
		except Exception as exception:
			logging.error("Error occurred: %s", exception)
		else:
			return result

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray,x0:float=None):
		pass

	@classmethod
	def model(cls,x:numpy.ndarray,yobs:numpy.ndarray,x0:float=None):
		"""Returns an exponential model that fits observation values."""
		yi,Di,_ = self.params(x,yobs,x0)
		return cls(yi=yi,Di=Di,xp=0.)

if __name__ == "__main__":

	bc = GenModel(100,0.005)

	print(bc.yi)
	print(bc.Di)
	print(bc.expo)
	print(bc.base([1,2,3]))