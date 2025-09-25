from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Tuple, Union

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import linregress

Number = Union[int, float]

# If you already have these in a shared utils module, import them instead.
def _as_array(t: ArrayLike) -> NDArray[np.float64]:
    return np.asarray(t, dtype=float)


def _validate_positive(name: str, value: Number) -> None:
    if not (value > 0):
        raise ValueError(f"{name} must be > 0, got {value!r}")

@dataclass(frozen=True)
class Exponential:
    """
    Exponential (Arps limit b → 0) decline model.

    q(t) = qi * exp(-di * t)
    d(t) = di
    D(t) = 1 - exp(-di)  (effective decline over Δt = 1)
    N(t) = (qi/di) * (1 - exp(-di * t))

    Economic limit:
      r   = qi / q_ec
      T   = (1/di) * ln(r)
      N_ec   = (qi - q_ec) / di

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
    ) -> "Exponential":
        """Return a new instance with updated parameters (immutability-friendly)."""
        return replace(
            self,
            di=float(di) if di is not None else self.di,
            qi=float(qi) if qi is not None else self.qi,
        )

    def __call__(self, di: Number, qi: Number) -> "Exponential":
        """Configure di, qi and return a new instance (functional style)."""
        return self.with_params(di=di, qi=qi)

    # ---- core formulas ------------------------------------------------------
    def q(self, t: ArrayLike) -> NDArray[np.float64]:
        """Rate q(t)."""
        tt = _as_array(t)
        return self.qi * np.exp(-self.di * tt)

    def d(self, t: ArrayLike) -> NDArray[np.float64]:
        """
        Nominal decline rate d(t) = - (dq/dt) / q = di (constant).
        Returns an array with the same shape as t.
        """
        tt = _as_array(t)
        return np.full_like(tt, self.di, dtype=float)

    def D(self, t: ArrayLike) -> NDArray[np.float64]:
        """
        Effective (continuous) decline over Δt=1 (dimensionless):
        D = 1 - exp(-di), constant.
        Returns an array with the same shape as t.
        """
        tt = _as_array(t)
        val = 1.0 - math.exp(-self.di)
        return np.full_like(tt, val, dtype=float)

    def N(self, t: ArrayLike) -> NDArray[np.float64]:
        """
        Cumulative production N(t) = (qi/di) * (1 - exp(-di * t)).
        """
        tt = _as_array(t)
        return (self.qi / self.di) * (1.0 - np.exp(-self.di * tt))

    # ---- economic limit & life ----------------------------------------------
    def r(self, q_ec: Number) -> float:
        """Rate ratio r = qi / q_ec."""
        _validate_positive("q_ec", q_ec)
        return float(self.qi / q_ec)

    def T(self, q_ec: Number) -> float:
        """
        Producing life until q(t) = q_ec:
        T = (1/di) * ln(qi / q_ec)
        """
        _validate_positive("q_ec", q_ec)
        return math.log(self.r(q_ec)) / self.di

    def N_ec(self, q_ec: Number) -> float:
        """
        Cumulative production at economic limit:
        N_ec = (qi - q_ec) / di
        """
        _validate_positive("q_ec", q_ec)
        return (self.qi - float(q_ec)) / self.di

    @staticmethod
    def _linearize(q: ArrayLike) -> NDArray[np.float64]:
        """
        Exponential linearization: y = ln(q) = ln(qi) - di * t
        """
        qq = _as_array(q)
        if np.any(qq <= 0):
            raise ValueError("All q values must be > 0 for log-linearization.")
        return np.log(qq)

    def linearize(self, q: ArrayLike) -> NDArray[np.float64]:
        """Instance helper: ln(q)."""
        return self._linearize(q)

    @staticmethod
    def invert(slope: Number, intercept: Number) -> Tuple[float, float]:
        """
        Given regression of y = ln(q) vs t, where y = c + m t,
          m  = -di  → di = -m
          c  = ln(qi) → qi = exp(c)
        """
        m = float(slope)
        c = float(intercept)
        di = -m
        qi = math.exp(c)
        _validate_positive("di", di)
        _validate_positive("qi", qi)
        return di, qi

    def fit(self, t: ArrayLike, q: ArrayLike) -> "Exponential":
        """
        Estimate di and qi via log-linear regression:
          regress y = ln(q) on t ⇒ slope=m, intercept=c ⇒ di, qi
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
        return "exponential"

    def __repr__(self) -> str:
        return f"Exponential(di={self.di:.6g}, qi={self.qi:.6g})"