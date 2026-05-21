import mpmath as mp
import numpy as np
from scipy.special import iv, kv, ive, kve

class EverdingenHurst:

    def qD(tD: np.ndarray, reD: float, degree: int = 12) -> np.ndarray:
        """
        Compute qD(tD) for finite radial reservoir under constant well pressure.
        """
        return _inverse_laplace_stehfest(
            _qbar_constant_pressure_closed,
            tD,
            degree = degree,
            reD = reD,
        )

def _pbar_constant_rate_infinite():
    pass

def _pbar_constant_rate_closed():
    pass

def _qbar_constant_pressure_infinite():
    pass

def _qbar_constant_pressure_closed(s: np.ndarray, reD: float) -> np.ndarray:
    """
    Laplace-space dimensionless rate for radial flow with:
        inner boundary: constant pressure at rD = 1
        outer boundary: no-flow at rD = reD

    The solution is written in terms of modified Bessel functions.

    Parameters
    ----------
    s : array-like
        Laplace variable.
    reD : float
        Dimensionless external radius, re / rw.

    Returns
    -------
    np.ndarray
        Laplace transform of qD(tD).
    """
    s = np.asarray(s, dtype=float)
    u = np.sqrt(s)

    eta = k1_over_i1(u * reD)

    numerator = kv(1, u) - eta * iv(1, u)
    denominator = kv(0, u) + eta * iv(0, u)

    return (u / s) * (numerator / denominator)

def _inverse_laplace_stehfest(func, t: np.typing.ArrayLike, degree: int = 12, **kwargs):
    """
    Inverse Laplace transform using mpmath's Stehfest method.
    """

    t = np.asarray(t, dtype=float)

    if np.any(t <= 0):
        raise ValueError("t must be strictly positive.")

    values = [
        mp.invertlaplace(
            lambda s: func(s, **kwargs),
            float(ti),
            method="stehfest",
            degree=degree,
        )
        for ti in t.ravel()
    ]

    result = np.array(values, dtype=float).reshape(t.shape)

    return result.item() if result.ndim == 0 else result

def k1_over_i1(z: np.ndarray) -> np.ndarray:
    """
    Stable evaluation of K1(z) / I1(z).

    For large z, direct scipy.special.kv / iv may underflow or overflow.
    Scaled Bessel functions are used for stability.
    """
    z = np.asarray(z, dtype=float)
    ratio = np.empty_like(z)

    small = z < 50.0
    large = ~small

    ratio[small] = kv(1, z[small]) / iv(1, z[small])

    # K1/I1 = [kve(1,z) exp(-z)] / [ive(1,z) exp(z)]
    #       = [kve(1,z) / ive(1,z)] exp(-2z)
    ratio[large] = (kve(1, z[large]) / ive(1, z[large])) * np.exp(-2.0 * z[large])

    return ratio