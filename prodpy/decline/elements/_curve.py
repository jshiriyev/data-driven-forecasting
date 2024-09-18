from dataclasses import dataclass,field

import numpy

import pandas

from ._model import Model

from .forward._forward import Forward

@dataclass(frozen=True)
class Curve:

	model : Model

	def set(self,**kwargs):
		"""Sets the values to the property, otherwise it is a frozen dataclass. """
		for key,value in kwargs.items():
			object.__setattr__(self,key,value)

		return self

	@property
	def forward(self):
		return Forward(*self.model.params)

	def rates(self,days:numpy.ndarray):
		"""Returns the method based on the class mode."""
		return self.forward.rates(days)

	def cums(self,days:numpy.ndarray):
		"""Returns the method based on the class mode."""
		return self.forward.cums(days)

if __name__ == "__main__":

	model = Model()

	print(Curve(model).run([1,2,3]))

	fw = Curve(model)

	for d in dir(fw):
		print(d)