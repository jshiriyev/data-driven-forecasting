import numpy

from scipy.optimize import minimize

from ._model import Model

from ._cruncher import Cruncher

class Tank():

	def __init__(self,**kwargs):

		self._initial = Model(**kwargs)

	@property
	def initial(self):
		return self._initial

	def __call__(self,**kwargs):
		"""Defines the current state of the tank by altering only the new properties."""

		self._current = self._initial()

		self._current._M = None

		self._current(inplace=True,**kwargs)

		return self

	@property
	def current(self):
		return self._current
	
	def minimize(self,alter_initial=False,optimizer:dict=None,**kwargs):
		"""
		Minimizes the difference between total drive index and 1 for the current model.

		alter_initial 	: the model index whose parameters will be altered.

		Returns the OptimizeResult where the x includes the optimized values of kwargs keys.
		"""

		initial = self.initial()

		current = self.current()

		keys,values = list(kwargs.keys()),list(kwargs.values())

		def objective(values,keys,initial,current,alter_initial):

			locdict = dict(zip(keys,values))

			if alter_initial:
				initial = initial(**locdict)
				initial.update_fluid_volumes()
			else:
				current = current(**locdict)
				current.update_fluid_volumes()

			total = Cruncher.total_drive_index(initial,current)

			return (total-1)**2

		return minimize(objective,values,args=(keys,initial,current,alter_initial),**(optimizer or {})) # minimize(tank,0,N=1000_000)

	def drive_index(self,which:str="DDI",safe:bool=False):
		"""Returns the drive index for the mbal model with respect to initial state."""
		return Cruncher.drive_index(self.initial,self.current,which,safe)
		
	def total_drive_index(self):
		"""Returns the total drive index for the mbal model with respect to initial state."""
		return Cruncher.total_drive_index(self.initial,self.current)
