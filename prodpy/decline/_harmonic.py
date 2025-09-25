from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Tuple, Union

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import linregress

Number = Union[int, float]

# If you already have shared utils, import from there instead.
def _as_array(t: ArrayLike) -> NDArray[np.float64]:
	return np.asarray(t, dtype=float)

def _validate_positive(name: str, value: Number) -> None:
	if not (value > 0):
		raise ValueError(f"{name} must be > 0, got {value!r}")

@dataclass(frozen=True)
class Harmonic:
	"""
	Harmonic (Arps with b = 1) decline model.

	q(t) = qi / (1 + di * t)
	d(t) = di / (1 + di * t) (nominal)
	D(t) = d(t) / (1 + d(t)) (effective decline over Δt = 1)
	N(t) = (qi/di) * ln(1 + di * t)

	Economic limit:
	  r	  = qi / q_ec
	  T	  = (r - 1) / di
	  N_ec   = (qi/di) * ln(r)

	Notes:
	- di > 0, qi > 0, t >= 0, q_ec > 0
	- Accepts array-like t and returns NumPy arrays.
	"""

	di: float = 1.0
	qi: float = 1.0

	# ---- construction & validation -----------------------------------------
	def __post_init__(self):
		_validate_positive("di", self.di)
		_validate_positive("qi", self.qi)

	def with_params(
		self,
		*,
		di: Number | None = None,
		qi: Number | None = None,
	) -> "Harmonic":
		"""Return a new instance with updated parameters (immutability-friendly)."""
		return replace(
			self,
			di=float(di) if di is not None else self.di,
			qi=float(qi) if qi is not None else self.qi,
		)

	def __call__(self, di: Number, qi: Number) -> "Harmonic":
		"""Configure di, qi and return a new instance (functional style)."""
		return self.with_params(di=di, qi=qi)

	# ---- core formulas ------------------------------------------------------
	def q(self, t: ArrayLike) -> NDArray[np.float64]:
		"""Rate q(t)."""
		tt = _as_array(t)
		return self.qi / (1.0 + self.di * tt)

	# Optional alias for backwards compatibility
	qt = q

	def d(self, t: ArrayLike) -> NDArray[np.float64]:
		"""
		Nominal decline d(t) = - (dq/dt) / q = di / (1 + di * t).
		"""
		tt = _as_array(t)
		return self.di / (1.0 + self.di * tt)

	def D(self, t: ArrayLike) -> NDArray[np.float64]:
		"""
		Effective (continuous) decline over Δt=1 (dimensionless):
		For b=1: D(t) = 1 - (1 + d(t))^{-1} = d(t) / (1 + d(t)).
		"""
		d_nom = self.d(t)
		return d_nom / (1.0 + d_nom)

	def N(self, t: ArrayLike) -> NDArray[np.float64]:
		"""
		Cumulative production N(t) = (qi/di) * ln(1 + di * t).
		"""
		tt = _as_array(t)
		return (self.qi / self.di) * np.log1p(self.di * tt)

	# ---- economic limit & life ----------------------------------------------
	def r(self, q_ec: Number) -> float:
		"""Rate ratio r = qi / q_ec."""
		_validate_positive("q_ec", q_ec)
		return float(self.qi / q_ec)

	def T(self, q_ec: Number) -> float:
		"""
		Producing life until q(t) = q_ec:
		T = (r - 1) / di, where r = qi / q_ec
		"""
		_validate_positive("q_ec", q_ec)
		return (self.r(q_ec) - 1.0) / self.di

	def N_ec(self, q_ec: Number) -> float:
		"""
		Cumulative production at economic limit:
		N_ec = (qi/di) * ln(qi / q_ec) = (qi/di) * ln(r)
		"""
		_validate_positive("q_ec", q_ec)
		return (self.qi / self.di) * math.log(self.r(q_ec))

	# ---- linearization & inversion ------------------------------------------
	@staticmethod
	def _linearize(q: ArrayLike) -> NDArray[np.float64]:
		"""
		Harmonic linearization: y = q^{-1} = (1/qi) + (di/qi) * t
		"""
		qq = _as_array(q)
		if np.any(qq <= 0):
			raise ValueError("All q values must be > 0 for 1/q linearization.")
		return 1.0 / qq

	def linearize(self, q: ArrayLike) -> NDArray[np.float64]:
		"""Instance helper: 1/q."""
		return self._linearize(q)

	@staticmethod
	def invert(slope: Number, intercept: Number) -> Tuple[float, float]:
		"""
		Given regression of y = 1/q vs t, where y = c + m t:
		  c = 1/qi  → qi = 1/c
		  m = di/qi → di = m / c
		"""
		m = float(slope)
		c = float(intercept)
		_validate_positive("intercept (1/qi)", c)
		di = m / c
		qi = 1.0 / c
		_validate_positive("di", di)
		_validate_positive("qi", qi)
		return di, qi

	def fit(self, t: ArrayLike, q: ArrayLike) -> "Harmonic":
		"""
		Estimate di and qi via linear regression on y = 1/q.
		"""
		tt = _as_array(t)
		qq = _as_array(q)
		if tt.shape != qq.shape:
			raise ValueError("t and q must have the same shape")
		y = self.linearize(qq)
		reg = linregress(tt, y)
		di, qi = self.invert(reg.slope, reg.intercept)
		return self.with_params(di=di, qi=qi)

	# ---- convenience / representation ---------------------------------------
	@property
	def mode(self) -> str:
		return "harmonic"

	def __repr__(self) -> str:
		return f"Harmonic(di={self.di:.6g}, qi={self.qi:.6g})"
