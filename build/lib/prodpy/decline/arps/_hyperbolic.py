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

	def preproc(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None):

		x,yobs = super().preproc(x,yobs,xi)
		x,yobs = x[yobs!=0],yobs[yobs!=0]

		return (x,yobs)

	def regress(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=0.):
		"""Returns regression results after linearization."""

		x,yobs = self.preproc(x,yobs,xi)

		linear = super().regress(x,numpy.power(1/yobs,self.xp))

		params = (0,0) if linear is None else self.inverse(linear)

		R2 = Hyperbolic(*params,self.xp).rsquared(x,yobs)

		nonlinear = NonLinResult(*params,R2)

		return Result(linear,nonlinear)

	def model(self,x:numpy.ndarray,yobs:numpy.ndarray,xi:float=None,pct:float=50.):
		"""Returns an exponential model that fits observation values."""
		x,yobs = self.preproc(x,yobs,xi)

		linear = super().regress(x,numpy.power(1/yobs,self.xp))

		params = (0.,0.) if linear is None else self.inverse(linear,pct)
		
		return Hyperbolic(*params,self.xp)

	def inverse(self,linear,pct:float=50.):

		m = linear.slope+norm.ppf(pct/100.)*linear.stderr
		b = linear.intercept+norm.ppf(pct/100.)*linear.intercept_stderr

		return (m/b/self.xp, b**(-1/self.xp))