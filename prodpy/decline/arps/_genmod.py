import numpy

class GenModel:
	"""Base Class for Decline Models"""

	def __init__(self,y0:float,D0:float,expo:float=None):

		self._y0 = y0
		self._D0 = D0

		self._expo = expo

	@property
	def y0(self):
		return self._y0

	@property
	def D0(self):
		return self._D0

	@property
	def A0(self):
		return self._D0*365.25

	@property
	def expo(self):
		return self._expo

	@property
	def props(self):
		return self._y0, self._D0, self._expo
	
	def base(self,x:numpy.ndarray):
		return self.D0*numpy.asarray(x)

	def ycal(self,x:numpy.ndarray):
		pass

	def ycum(self,x:numpy.ndarray):
		pass

	def params(self,x:numpy.ndarray,yobs:numpy.ndarray):
		pass

if __name__ == "__main__":

	bc = GenModel(100,0.005)

	print(bc.y0)
	print(bc.D0)
	print(bc.A0)
	print(bc.exponent)
	print(bc.base([1,2,3]))