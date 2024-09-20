import logging

import numpy

from ._genmod import GenModel,NonLinResult,Result

class Hyperbolic(GenModel):
	"""Hyperbolic Decline Model"""

	def __init__(self,*args,**kwargs):

		super(Hyperbolic,self).__init__(*args,**kwargs)
	
	def ycal(self,x:numpy.ndarray):
		"""
		q = q0 / (1+b*Di*t)**(1/b)
		"""
		return self.yi/(1+self.xp*self.base(x))**(1/self.xp)

	def ycum(self,x:numpy.ndarray):
		"""
		Np = q0 / ((1-b)*Di)*(1-(1+b*Di*t)**(1-1/b))
		"""
		return (self.yi/self.Di)/(1-self.xp)*(1-(1+self.xp*self.base(x))**(1-1/self.xp))

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=0.):
		"""Returns regression results after linearization."""

		x,yobs = self.xshift(x,yobs,xi)
		x,yobs = x[yobs!=0],yobs[yobs!=0]

		linear = super().regress(x,numpy.power(1/yobs,self.xp))

		params = (0,0) if linear is None else self.inverse(linear.slope,linear.intercept)

		R2 = Hyperbolic(*params,self.xp).rsquared(x,yobs)

		nonlinear = NonLinResult(*params,R2)

		return Result(linear,nonlinear)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):
		"""Returns an exponential model that fits observation values."""
		result = self.regress(x,yobs,xi).nonlinear
		
		return Hyperbolic(result.decline,result.intercept,self.xp)

	def inverse(self,m,b):

		return (m/b/self.xp, b**(-1/self.xp))