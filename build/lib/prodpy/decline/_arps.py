from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import linregress, t
from scipy.optimize import curve_fit

# Adjust imports to your package structure
try:
    from prodpy.decline import Exponential
    from prodpy.decline import Hyperbolic
    from prodpy.decline import Harmonic
except Exception:
    from ._exponential import Exponential
    from ._hyperbolic import Hyperbolic
    from ._harmonic import Harmonic

Number = float | int
ModelLike = Exponential | Harmonic | Hyperbolic


def _as_array(x: ArrayLike) -> NDArray[np.float64]:
    return np.asarray(x, dtype=float)

def _nzero(x: NDArray[np.float64], y: NDArray[np.float64]) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    mask = (~np.isnan(y)) & (y != 0.0)
    return x[mask], y[mask]

def _shift(x: NDArray[np.float64], y: NDArray[np.float64], *, xi: Number = 0.0) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    if xi == 0:
        return x, y
    mask = x >= xi
    return (x[mask] - xi, y[mask])

@dataclass(frozen=True)
class FitResult:
    b: float
    di: float
    qi: float
    xi: float
    n: int
    r2: float
    di_error: float
    qi_error: float
    linear: object  # scipy.stats._stats_py.LinregressResult, but we avoid private type

class Arps:
    """
    Orchestrator for Arps decline models (Exponential, Hyperbolic, Harmonic).

    Choose model via `b` or `mode`:
      b=0     → Exponential
      0<b<1   → Hyperbolic (b fixed)
      b=1     → Harmonic
      mode in {"exponential"|"exp", "hyperbolic"|"hyp", "harmonic"|"har"}

    Parameters
    ----------
    di : float
        Initial nominal decline (1/time)
    qi : float
        Initial rate
    b  : float, optional
        Arps exponent; ignored if `mode` provided
    mode : str, optional
        Model kind (case-insensitive synonyms accepted)
    """

    _MODE_BY_BOUNDS = {0.0: "Exponential", 1.0: "Harmonic"}
    _B_BY_MODE = {
        "exponential": 0.0, "exp": 0.0,
        "hyperbolic": 0.5,  "hyp": 0.5,   # default b for convenience
        "harmonic": 1.0,    "har": 1.0,
    }
    _CLASS_BY_MODE: Dict[str, type] = {
        "Exponential": Exponential,
        "Hyperbolic": Hyperbolic,
        "Harmonic": Harmonic,
    }

    def __init__(self, di: Number, qi: Number, *, b: Optional[Number] = None, mode: Optional[str] = None):
        self._di = float(di)
        self._qi = float(qi)

        if mode is None and b is None:
            mode, b = "Exponential", 0.0
        elif mode is None and b is not None:
            mode = self.b2mode(float(b))
        elif mode is not None and b is None:
            b = self.mode2b(mode)

        self._b = float(b)  # store b (for Hyperbolic fixed b); ignored by Exp/Harm
        self._mode_name = mode if mode in {"Exponential", "Hyperbolic", "Harmonic"} else self.b2mode(self._b)

        # Construct the underlying model
        cls = self._CLASS_BY_MODE[self._mode_name]
        if cls is Hyperbolic:
            self.model: ModelLike = cls(b=self._b, di=self._di, qi=self._qi)
        else:
            self.model = cls(di=self._di, qi=self._qi)

    # ----------------- mapping helpers -----------------
    @staticmethod
    def b2mode(b: float) -> str:
        return {0.0: "Exponential", 1.0: "Harmonic"}.get(float(b), "Hyperbolic")

    @classmethod
    def mode2b(cls, mode: str) -> float:
        m = cls._B_BY_MODE.get(mode.lower())
        if m is None:
            logging.error("Invalid mode: %s. Use 'exponential'|'hyperbolic'|'harmonic'.", mode)
            raise ValueError("Invalid mode. Use 'exponential'|'hyperbolic'|'harmonic'.")
        return float(m)

    @classmethod
    def option(cls, mode: str | None = None, b: float | None = None) -> Tuple[str, float]:
        if mode is None and b is None:
            return "Exponential", 0.0
        if mode is None:
            return cls.b2mode(float(b)), float(b)  # type: ignore[arg-type]
        if b is None:
            return cls.b2mode(cls.mode2b(mode)), cls.mode2b(mode)
        # both provided → prefer explicit b, but return canonical mode for that b
        return cls.b2mode(b), float(b)

    # ----------------- basic API -----------------
    @property
    def b(self) -> float:
        return self._b

    @property
    def mode(self) -> str:
        # lowercase for API symmetry with your models’ .mode
        return self._mode_name.lower()

    def with_params(self, *, di: Optional[Number] = None, qi: Optional[Number] = None) -> "Arps":
        di = self._di if di is None else float(di)
        qi = self._qi if qi is None else float(qi)
        return Arps(di, qi, b=self._b, mode=self._mode_name)

    # alias to mirror your model API, if desired
    def __call__(self, di: Number, qi: Number) -> "Arps":
        return self.with_params(di=di, qi=qi)

    def run(self, x: ArrayLike, *, xi: Number = 0.0, cum: bool = False) -> NDArray[np.float64]:
        xx = _as_array(x)
        # Shift only for x>=xi
        if xi != 0:
            mask = xx >= xi
            out = np.full_like(xx, np.nan, dtype=float)
            shifted = xx[mask] - xi
            y = self.model.N(shifted) if cum else self.model.q(shifted)
            out[mask] = y
            return out
        return self.model.N(xx) if cum else self.model.q(xx)

    # ----------------- regression & fit -----------------
    def linregress(self, x: ArrayLike, y: ArrayLike, *, xi: Number = 0.0, **kwargs):
        xx, yy = _shift(_as_array(x), _as_array(y), xi=xi)
        xx, yy = _nzero(xx, yy)
        try:
            y_lin = self.model.linearize(yy)
            res = linregress(xx, y_lin, **kwargs)
            return res  # keep native SciPy result
        except Exception as e:
            logging.error("linregress failed: %s", e)
            raise

    def _invert_from_lin(self, linres) -> Tuple[float, float]:
        # Map to appropriate inversion signature
        if isinstance(self.model, Hyperbolic):
            di, qi = self.model.invert(linres.slope, linres.intercept, self.model.b)
        else:
            di, qi = self.model.invert(linres.slope, linres.intercept)
        return float(di), float(qi)

    def fit(self, x: ArrayLike, y: ArrayLike, *, xi: Number = 0.0, p0: Tuple[float, float] | None = None, **kwargs) -> FitResult:
        xx, yy = _shift(_as_array(x), _as_array(y), xi=xi)
        xx, yy = _nzero(xx, yy)

        linres = self.linregress(xx, yy, xi=0.0)  # already shifted above
        if p0 is None:
            p0 = self._invert_from_lin(linres)

        # forward model (rate)
        def fwd(xv, di, qi):
            if isinstance(self.model, Hyperbolic):
                m = self.model.with_params(di=di, qi=qi, b=self.model.b)
            else:
                m = self.model.with_params(di=di, qi=qi)
            return m.q(xv)

        popt, pcov = curve_fit(fwd, xx, yy, p0=p0, **kwargs)
        di_hat, qi_hat = map(float, popt)

        # R²
        ycal = fwd(xx, di_hat, qi_hat)
        r2 = self.rsquared(ycal, yy)

        # parameter std errors
        perr = np.sqrt(np.diag(pcov)) if (pcov is not None and np.all(np.isfinite(pcov))) else np.array([np.nan, np.nan])
        di_err, qi_err = map(float, perr)

        return FitResult(
            b=self._b,
            di=di_hat,
            qi=qi_hat,
            xi=float(xi),
            n=int(xx.size),
            r2=float(r2),
            di_error=di_err,
            qi_error=qi_err,
            linear=linres,
        )

    @staticmethod
    def rsquared(ycal: ArrayLike, yobs: ArrayLike) -> float:
        yc = _as_array(ycal)
        yo = _as_array(yobs)
        ssres = np.nansum((yo - yc) ** 2)
        sstot = np.nansum((yo - np.nanmean(yo)) ** 2)
        return float(1.0 - ssres / sstot) if sstot > 0 else float("nan")

    @staticmethod
    def reader(result: FitResult) -> str:
        mode_name = Arps.b2mode(result.b)
        s = []
        s.append(f"\nDecline mode is {mode_name} and the exponent is {result.b}.\n")
        s.append(f"Linear regression R-squared is {result.linear.rvalue**2:.5f}")
        s.append(f"Non-linear curve fit R-squared is {result.r2:.5f}\n")
        s.append(f"Initial x (xi) is {result.xi:.3f}")
        s.append(f"Initial rate qi is {result.qi:.6g}")
        s.append(f"Initial decline di is {result.di:.6g}\n")
        return "\n".join(s)

    @staticmethod
    def simulate(result: FitResult, prc: float = 50.0) -> Tuple[float, float]:
        """Return one (di, qi) sample at percentile `prc` using fitted std errors (approx t-intervals)."""
        dof = max(result.n - 2, 1)
        tcrit = t.ppf(prc / 100.0, dof)
        di = result.di + tcrit * result.di_error
        qi = result.qi - tcrit * result.qi_error
        return float(di), float(qi)
