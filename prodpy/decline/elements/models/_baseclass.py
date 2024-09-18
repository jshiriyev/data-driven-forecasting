import numpy

class BaseClass:
	"""Base Class for Decline Models"""

	def __init__(self,rate0:float,decline0:float,exponent:float=None):

		self._rate0 = rate0

		self._decline0 = decline0
		self._exponent = exponent

	@property
	def rate0(self):
		return self._rate0

	@property
	def decline0(self):
		return self._decline0

	@property
	def annual0(self):
		return self._decline0*365.25

	@property
	def exponent(self):
		return self._exponent

	@property
	def fraction(self):
		return None if self._exponent is None else self._exponent/100.
	
	@property
	def volume0(self):
		return self._rate0/self._decline0
	
	def base(self,days:numpy.ndarray):
		return self.decline0*numpy.asarray(days)

if __name__ == "__main__":

	bc = BaseClass(100,0.005)

	print(bc.rate0)
	print(bc.decline0)
	print(bc.annual0)
	print(bc.exponent)
	print(bc.fraction)
	print(bc.volume0)
	print(bc.base([1,2,3]))