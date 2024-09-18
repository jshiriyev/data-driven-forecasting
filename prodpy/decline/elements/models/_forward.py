import numpy

from ._baseclass import BaseClass

from ._exponential import Exponential
from ._hyperbolic import Hyperbolic
from ._harmonic import Harmonic

class Forward(BaseClass):

	def __init__(self,*args,**kwargs):

		super(Forward,self).__init__(*args,**kwargs)

	@property
	def params(self):
		return (self.rate0,self.decline0,self.exponent)

	def __model(self):

		if self.fraction==0.:
			return Exponential(*self.params)
		elif self.fraction==1.:
			return Harmonic(*self.params)
		elif self.fraction>0. and self.fraction<1.:
			return Hyperbolic(*self.params)

	def rates(self,days:numpy.ndarray):

		self.__model.rates(days)

	def cums(self,days:numpy.ndarray):

		self.__model.cums(days)

	@staticmethod
	def Rsquared(model:Model,days:numpy.ndarray,rates:numpy.ndarray):

		curve = Curve(model).run(days)

		ssres = numpy.nansum((rates-curve)**2)
		sstot = numpy.nansum((rates-numpy.nanmean(rates))**2)

		return 1-ssres/sstot

