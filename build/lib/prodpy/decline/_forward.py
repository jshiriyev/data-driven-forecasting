from dataclasses import dataclass,field

import numpy

import pandas

from ._model import Model

@dataclass(frozen=True)
class Curve:

	model : Model

	dates : numpy.ndarray = field(init=False,repr=False)
	rates : numpy.ndarray = field(init=False,repr=False)

	heads : tuple[str] = field(
		init = False,
		repr = False,
		default = (
			"datehead",
			"ratehead",
			),
		)

	def set(self,**kwargs):

		for key,value in kwargs.items():
			object.__setattr__(self,key,value)

		return self

	@property
	def get(self):
		"""Returns the method based on the class mode."""
		return getattr(self,f"{self.model.mode}")
	
	def run(self,days:numpy.ndarray):
		"""Runs the decline method and saves to self dates and rates."""
		return self.set(dates=days,rates=self.get(days))

	def Exponential(self,days:numpy.ndarray):
		"""Exponential decline model: q = q0 * exp(-d0*t) """
		return self.model.rate0*numpy.exp(-self.base(self.model,days))

	def Hyperbolic(self,days:numpy.ndarray):
		"""Hyperbolic decline model: q = q0 / (1+b*d0*t)**(1/b) """

		exponent = self.model.exponent/100.

		return self.model.rate0/(1+exponent*self.base(self.model,days))**(1/exponent)

	def Harmonic(self,days:numpy.ndarray):
		"""Harmonic decline model: q = q0 / (1+d0*t) """
		return self.model.rate0/(1+self.base(self.model,days))

	@property
	def frame(self):
		return pandas.DataFrame({
			self.heads[0] : self.dates,
			self.heads[1] : self.rates,
			})

	@staticmethod
	def base(model:Model,days:numpy.ndarray):
		"""Returns the multiplication of decline0 and days."""
		return model.decline0*numpy.asarray(days)

if __name__ == "__main__":

	model = Model()

	print(Curve(model).run([1,2,3]))

	fw = Curve(model)

	for d in dir(fw):
		print(d)