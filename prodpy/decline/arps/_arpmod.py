import numpy

from ._genmod import GenModel
from ._marshal import Marshal

class Arps(GenModel):

	def __init__(self,*args,**kwargs):

		super(Arps,self).__init__(*args,**kwargs)

	def __model(self):

		return Marshal.model(self.xp)(*self.props)

	def ycal(self,x:numpy.ndarray):

		return self.__model.ycal(x)

	def ycum(self,x:numpy.ndarray):

		return self.__model.ycum(x)

	def param(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):

		yi,Di,linear = self.__model.param(x,yobs)

		nonlinear = NonLinResult(Di,yi,self.rvalue(x,yobs))

		return Score(linear,nonlinear)

	@classmethod
	def model(cls,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns an exponential model that fits observation values."""
		yi,Di,_ = self.param(x,yobs,xi)
		return cls(yi=yi,Di=Di,xp=0.)

