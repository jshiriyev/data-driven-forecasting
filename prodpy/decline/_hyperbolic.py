from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Any, Tuple, Union

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import linregress

# -----------------------------
# Shared doc for symbols/units
# -----------------------------
BASE_DOC = r"""
Symbols (Arps):
---------------
b   : Hyperbolic exponent (dimensionless), commonly 0 < b < 1 for hyperbolic
d   : Nominal decline factor
di  : Initial nominal decline rate (1/time)
D   : Effective decline factor
qi  : Initial production rate
q(t): Rate at time t
N(t): Cumulative production to time t
q_ec: Economic limit rate
N_ec: Cumulative production at economic limit
r   : Rate ratio qi / q_ec
t   : Time (same time-unit as di)
T   : Producing life until q(t) = q_ec

Notes:
- di > 0, qi > 0, t >= 0, q_ec > 0
- As b → 0 → exponential, as b → 1 → harmonic
"""

Number = Union[int, float]

def _as_array(t: ArrayLike) -> NDArray[np.float64]:
    """Ensure ndarray[float64]."""
    return np.asarray(t, dtype=float)

def _validate_positive(name: str, value: Number) -> None:
    if not (value > 0):
        raise ValueError(f"{name} must be > 0, got {value!r}")

def _validate_b(b: Number) -> None:
    # Allow [0, 1] with stable limits; you can restrict to (0,1) if desired.
    if not (0.0 <= b <= 1.0):
        raise ValueError(f"b must be in [0, 1], got {b!r}")

@dataclass(frozen=True)
class Hyperbolic():
    """
    Hyperbolic (Arps) decline model.

    q(t) = qi / (1 + b * di * t)^(1/b),    for 0 < b < 1
    Limits:
      - Exponential (b → 0): q(t) = qi * exp(-di * t)
      - Harmonic    (b → 1): q(t) = qi / (1 + di * t)

    """ + BASE_DOC

    b: float = 0.5
    di: float = 1.0
    qi: float = 1.0

    # ---- construction & validation -----------------------------------------
    def __post_init__(self):
        _validate_b(self.b)
        _validate_positive("di", self.di)
        _validate_positive("qi", self.qi)

    def with_params(self, *, di: Number | None = None, qi: Number | None = None, b: Number | None = None) -> "Hyperbolic":
        """Return a new instance with updated parameters (immutability-friendly)."""
        return replace(self,
            di=float(di) if di is not None else self.di,
            qi=float(qi) if qi is not None else self.qi,
            b=float(b) if b is not None else self.b)

    def __call__(self, di: Number, qi: Number) -> "Hyperbolic":
        """Configure di, qi and return a new instance (functional style)."""
        return self.with_params(di=di, qi=qi)

    def q(self, t: ArrayLike) -> NDArray[np.float64]:
        """Rate q(t)."""
        tt = _as_array(t)
        b, di, qi = self.b, self.di, self.qi

        with np.errstate(over="ignore", invalid="ignore"):
            return qi / np.power(1.0 + b * di * tt, 1.0 / b)

    def d(self, t: ArrayLike) -> NDArray[np.float64]:
        """
        Nominal decline rate d(t) = - (dq/dt) / q.
        For hyperbolic: d(t) = di / (1 + b * di * t)
        """
        tt = _as_array(t)
        b, di = self.b, self.di

        return di / (1.0 + b * di * tt)

    def D(self, t: ArrayLike) -> NDArray[np.float64]:
        """
        Effective (continuous) decline over Δt=1 (dimensionless).
        For a nominal d(t), the effective over unit time is: D = 1 - exp(-∫ d dt) over 1 time unit.
        For practical workflows people often use: D = 1 - (1 + b d)^(-1/b) when d is (locally) nominal.
        """
        d_nom, b = self.d(t), self.b
        with np.errstate(over="ignore", invalid="ignore"):
            return 1.0 - np.power(1.0 + b * d_nom, -1.0 / b)

    def N(self, t: ArrayLike) -> NDArray[np.float64]:
        """
        Cumulative production N(t).
        Hyperbolic (0<b<1): N(t) = (qi/di)/(1-b) * [1 - (1 + b*di*t)^(1 - 1/b)]

        """
        tt = _as_array(t)
        b, di, qi = self.b, self.di, self.qi

        with np.errstate(over="ignore", invalid="ignore"):
            return (qi / di) / (1.0 - b) * (1.0 - np.power(1.0 + b * di * tt, 1.0 - 1.0 / b))

    def r(self, q_ec: Number) -> float:
        """Rate ratio r = qi / q_ec."""
        _validate_positive("q_ec", q_ec)
        return float(self.qi / q_ec)

    def T(self, q_ec: Number) -> float:
        """
        Producing life until q(t)=q_ec.
        Hyperbolic: T = ((qi/q_ec)^b - 1) / (b*di)

        """
        _validate_positive("q_ec", q_ec)
        b, di, r = self.b, self.di, self.r(q_ec)

        return (r**b - 1.0) / (b * di)

    def N_ec(self, q_ec: Number) -> float:
        """
        Cumulative production at economic limit.
        Uses your closed-form with r and T; handled robustly for limits.
        """
        _validate_positive("q_ec", q_ec)
        b = self.b
        T = self.T(q_ec)
        r = self.r(q_ec)

        # Your original compact expression:
        # N_ec = (qi*T*b)/(1-b) * ( (r^{-b} - r^{-1}) / (1 - r^{-b}) )
        r_m_b = r ** (-b)
        r_m_1 = r ** (-1.0)
        num = r_m_b - r_m_1
        den = 1.0 - r_m_b
        return (self.qi * T * b) / (1.0 - b) * (num / den)

    # ---- linearization & inversion ------------------------------------------
    @staticmethod
    def _linearize(q: ArrayLike, b: Number) -> NDArray[np.float64]:
        """
        Return q^{-b} for linear regression vs t.
        For hyperbolic: q^{-b} = qi^{-b} * (1 + b*di*t)
        """
        _validate_b(b)
        qq = _as_array(q)
        with np.errstate(over="ignore", invalid="ignore"):
            return np.power(qq, -float(b))

    def linearize(self, q: ArrayLike) -> NDArray[np.float64]:
        """Instance helper: q^{-b} with current b."""
        return self._linearize(q, self.b)

    @staticmethod
    def invert(slope: Number, intercept: Number, b: Number) -> Tuple[float, float]:
        """
        Given regression of y = q^{-b} vs t, where y = c + m t,
        di = m / (b * c), qi = c^{-1/b}
        """
        _validate_b(b)
        c = float(intercept)
        m = float(slope)
        _validate_positive("intercept (qi^{-b})", c)
        di = m / (b * c)
        qi = c ** (-1.0 / b)
        return di, qi

    def fit(self, t: ArrayLike, q: ArrayLike) -> "Hyperbolic":
        """
        Estimate di and qi via linearization (b fixed):
        regress y = q^{-b} on t ⇒ slope=m, intercept=c ⇒ di, qi
        """
        tt = _as_array(t)
        qq = _as_array(q)
        if tt.shape != qq.shape:
            raise ValueError("t and q must have the same shape")
        y = self.linearize(qq)
        reg = linregress(tt, y)
        di, qi = self.invert(reg.slope, reg.intercept, self.b)
        return self.with_params(di=di, qi=qi)

    # ---- convenience / representation ---------------------------------------
    @property
    def mode(self) -> str:
       """Getter for the decline mode."""
       return 'hyperbolic'

    def __repr__(self) -> str:
        return f"Hyperbolic(b={self.b:.6g}, di={self.di:.6g}, qi={self.qi:.6g})"

if __name__ == "__main__":

    print(help(Hyperbolic))