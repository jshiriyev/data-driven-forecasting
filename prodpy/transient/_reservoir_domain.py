import numpy as np

from prodpy.resprops import Layer, BlackOil

from prodpy import UnitConversion as uc

class ReservoirDomain(Layer):
	"""A reservoir class for flow calculations."""

	def __init__(self, *args, area: float = np.inf, height: float = 1., **kwargs) -> None:
		"""Initialize the base reservoir class for porous mediaflow calculations.

		Arguments:
		---------
		area (float): in acre.
		height (float): in ft, defaults to 1 ft.

		"""
		super().__init__(*args,**kwargs)
		
		self._fluid = None
		self._pinit = None
		self._tcomp = None

		self.area = area
		self.height = height

	def __repr__(self) -> str:
		"""Return a concise constructor-style representation of the reservoir domain."""

		args = [
			f"area={self.area:.1f} acres",
			f"height={self.height:.1f} ft",
		]

		return f"{type(self).__name__}({', '.join(args)})"

	@staticmethod
	def _validate_positive(name: str, value: float) -> float:
		try:
			value = float(value)
		except (TypeError, ValueError):
			raise ValueError(f"{name} must be a positive finite value.") from None
		
		if value <= 0:
			raise ValueError(f"{name} must be a positive value.")
	
		return value

	@property
	def area(self):
		"""Getter for the reservoir area."""
		return self._area / uc.FT_TO_M**2 / uc.ACRE_TO_FT2

	@area.setter
	def area(self,value):
		"""Setter for the reservoir area."""
		value = self._validate_positive("area", value)
		self._area = value * uc.ACRE_TO_FT2 * uc.FT_TO_M**2

	@property
	def radius(self) -> float:
		"""Circular equivalent drainage radius."""
		return self._radius / uc.FT_TO_M
	
	@property
	def _radius(self) -> float:
		"""Getter for the reservoir equivalent radius in meters."""
		return np.sqrt(self._area / np.pi)

	@property
	def height(self):
		"""Getter for the reservoir height."""
		return self._height / uc.FT_TO_M

	@height.setter
	def height(self,value):
		"""Setter for the reservoir height."""
		value = self._validate_positive("height", value)
		
		if not np.isfinite(value):
			raise ValueError("height must be a finite value.")
	
		self._height = value * uc.FT_TO_M
		
	@property
	def volume(self) -> float:
		"""Getter for the reservoir volume."""
		return self._volume/(uc.FT_TO_M**3)

	@property
	def _volume(self) -> float:
		"""Getter for the reservoir volume in meter**3."""
		return self._area*self._height
	
	@property
	def vpore(self):
		"""Pore volume in ft3."""
		return self._vpore / (uc.FT_TO_M**3)

	@property
	def _vpore(self):
		"""Pore volume in m3."""
		return self._volume * self._poro
	
	def init(self, *args, pinit: float | None = None, tcomp: float | None = None, **kwargs):
		self.fluid = BlackOil(*args, **kwargs)
		self.pinit = pinit
		self.tcomp = tcomp
		
	@property
	def fluid(self):
		return self._fluid
	
	@fluid.setter
	def fluid(self, value):
		if not isinstance(value, BlackOil) and value is not None:
			raise TypeError("fluid must be an instance of BlackOil or None.")
		self._fluid = value
			
	@property
	def pinit(self):
		"""Initial pressure in psi."""
		return None if self._pinit is None else self._pinit/uc.PSI_TO_PA
	
	@pinit.setter
	def pinit(self, value):
		"""Initial pressure in psi."""
		self._pinit = None if value is None else Layer._validate_range(
			value, 0, name="pinit", include_lower_limit = False,
			).item()*uc.PSI_TO_PA

	@property
	def tcomp(self):
		"""Total compressibility in 1/psi"""
		return None if self._tcomp is None else self._tcomp*uc.PSI_TO_PA

	@tcomp.setter
	def tcomp(self, value):
		"""Total compressibility. If value is provided, it is expected in 1/psi;
		if None, it will be computed as the sum of layer and fluid compressibilities."""
		if value is None:
			fluid = self._require_fluid()
			if self._comp is None or fluid._comp is None:
				self._tcomp = None
			else:
				self._tcomp = self._comp + fluid._comp
			return

		value = Layer._validate_range(
			value, 0,
			name = "tcomp",
			include_lower_limit = False,
		)
		
		self._tcomp = value / uc.PSI_TO_PA
			
	def hdiff(self, axis: str = "x", phase: str = "oil") -> float:
		"""Hydraulic diffusivity in ft2/day."""
		return self._hdiff(axis, phase) * uc.DAY_TO_SEC / uc.FT_TO_M**2

	def _hdiff(self, axis: str = "x", phase: str = "oil") -> float:
		"""Hydraulic diffusivity in m2/sec."""
		axis_map = {"x": 0, "y": 1, "z": 2}
		
		try:
			index = axis_map[axis.lower()]
		except KeyError:
			raise ValueError("axis must be one of: 'x', 'y', or 'z'.") from None
		
		fluid = self._require_fluid()
		tcomp = self._require_total_compressibility()
		
		phase_obj = fluid.get_phase(phase)
		
		return (phase_obj._rperm * self._perm[:, index]) / (self._poro * phase_obj._visc * tcomp)

	def _require_fluid(self) -> BlackOil:
		"""Return fluid system if available; otherwise raise a clear error."""
		if self._fluid is None:
			raise ValueError(
				"Fluid system is not initialized. "
				"Call init(...) or assign reservoir.fluid first."
			)
		return self._fluid
	
	def _require_initial_pressure(self) -> np.typing.NDArray:
		"""Return initial pressure in Pa."""
		if self._pinit is None:
			raise ValueError(
				"Initial pressure pinit is not set. "
				"Provide pinit=... before using this method."
			)
		return self._pinit
	
	def _require_total_compressibility(self) -> float:
		"""Return total compressibility in 1/Pa."""
		if self._tcomp is None:
			raise ValueError(
				"Total compressibility tcomp is not set. "
				"Provide tcomp=... or make sure both layer and fluid compressibilities are available."
			)
		return self._tcomp
