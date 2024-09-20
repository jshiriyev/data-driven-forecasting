import numpy

from ._genmod import GenModel
from ._marshal import Marshal

class Arps(GenModel):
	"""Arp's decline class that returns values based on selected exponent."""

	def __init__(self,*args,**kwargs):

		super(Arps,self).__init__(*args,**kwargs)

	@property
	def __model(self):

		return Marshal.model(self.xp)

	def ycal(self,x:numpy.ndarray):

		return self.__model(*self.props).ycal(x)

	def ycum(self,x:numpy.ndarray):

		return self.__model(*self.props).ycum(x)

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns regression results after linearization."""
		return self.__model(*self.props).regress(x,yobs,xi)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns an exponential model that fits observation values."""
		return self.__model(*self.props).model(x,yobs,xi)