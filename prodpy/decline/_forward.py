import numpy

from . import Model

class Forward():

	def __init__(self,model:Model):
		self._model = model

	@property
	def model(self):
		return self._model
	
	@property
	def run(self):
		"""Returns the method based on the class mode."""
		return getattr(self,f"{self.model.mode}")

	def Exponential(self,days:numpy.ndarray):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return self.model.rate0*numpy.exp(-self.__decline(days))

	def Hyperbolic(self,days:numpy.ndarray):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """
		return self.model.rate0/(1+self.model.exponent*self.__decline(days))**(1/self.model.exponent)

	def Harmonic(self,days:numpy.ndarray):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return self.model.rate0/(1+self.__decline(days))

	def __decline(self,days:numpy.ndarray):
		"""Returns the multiplication of decline0 and days."""
		return self.model.decline0*numpy.asarray(days)

if __name__ == "__main__":

	model = Model()

	print(Forward(model).run([1,2,3]))

	fw = Forward(model)

	for d in dir(fw):
		print(d)