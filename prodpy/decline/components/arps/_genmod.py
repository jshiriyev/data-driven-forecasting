import numpy

class GenModel:
	"""Base Class for Decline Models"""

	def __init__(self,y0:float,d0:float,exp:float=None):

		self._y0 = y0
		self._d0 = d0

		self._exp = exp

	@property
	def y0(self):
		return self._y0

	@property
	def d0(self):
		return self._d0

	@property
	def decline0(self):
		return self._d0

	@property
	def annual0(self):
		return self._d0*365.25

	@property
	def exp(self):
		return self._exp

	@property
	def exponent(self):
		return self._exp

	@property
	def data(self):
		return self._y0, self._d0, self._exp
	
	def base(self,x:numpy.ndarray):
		return self.d0*numpy.asarray(x)

	def ycal(self,x:numpy.ndarray):
		pass

	def ycum(self,x:numpy.ndarray):
		pass

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray):
		pass

if __name__ == "__main__":

	bc = GenModel(100,0.005)

	print(bc.y0)
	print(bc.decline0)
	print(bc.annual0)
	print(bc.exponent)
	print(bc.base([1,2,3]))