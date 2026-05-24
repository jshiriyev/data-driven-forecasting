import mpmath as mp
import numpy as np
from scipy.special import iv, kv, ive, kve


class EverdingenHurst:
    @staticmethod
    def pD(
        tD: np.typing.ArrayLike,
        reD: float | None = None,
        boundary: str = "infinite",
        degree: int = 12,
    ) -> np.ndarray:
        """
        Compute pD(tD) for a constant-rate well.

        Parameters
        ----------
        tD : array-like
            Dimensionless time.
        reD : float, optional
            Dimensionless external radius, re / rw. Required when
            boundary is "closed".
        boundary : {"infinite", "closed"}, default "infinite"
            Outer boundary condition.
        degree : int, default 12
            Stehfest inversion degree.
        """
        boundary = _normalize_boundary(boundary)

        if boundary == "infinite":
            return _inverse_laplace_stehfest(
                _pbar_constant_rate_infinite,
                tD,
                degree=degree,
            )

        reD = _validate_reD(reD)

        return _inverse_laplace_stehfest(
            _pbar_constant_rate_closed,
            tD,
            degree=degree,
            reD=reD,
        )

    @staticmethod
    def qD(
        tD: np.typing.ArrayLike,
        reD: float | None = None,
        boundary: str = "closed",
        degree: int = 12,
    ) -> np.ndarray:
        """
        Compute qD(tD) for a constant-pressure well.

        Parameters
        ----------
        tD : array-like
            Dimensionless time.
        reD : float, optional
            Dimensionless external radius, re / rw. Required when
            boundary is "closed".
        boundary : {"infinite", "closed"}, default "closed"
            Outer boundary condition.
        degree : int, default 12
            Stehfest inversion degree.
        """
        boundary = _normalize_boundary(boundary)

        if boundary == "infinite":
            return _inverse_laplace_stehfest(
                _qbar_constant_pressure_infinite,
                tD,
                degree=degree,
            )

        reD = _validate_reD(reD)

        return _inverse_laplace_stehfest(
            _qbar_constant_pressure_closed,
            tD,
            degree=degree,
            reD=reD,
        )


def _normalize_boundary(boundary: str) -> str:
    """
    Validate and normalize the supported outer-boundary names.
    """
    boundary = boundary.lower()

    if boundary not in {"infinite", "closed"}:
        raise ValueError("boundary must be 'infinite' or 'closed'.")

    return boundary


def _validate_reD(reD: float | None) -> float:
    """
    Validate the external radius used by closed-boundary solutions.
    """
    if reD is None:
        raise ValueError("reD is required for a closed outer boundary.")

    reD = float(reD)

    if reD <= 1.0:
        raise ValueError("reD must be greater than 1.")

    return reD


def _pbar_constant_rate_infinite(s: np.ndarray) -> np.ndarray:
    """
    Laplace-space dimensionless well pressure for radial flow with:
        inner boundary: constant rate at rD = 1
        outer boundary: infinite acting reservoir

    The infinite-acting pressure solution is proportional to K0(rD sqrt(s)).
    Applying the constant-rate wellbore boundary gives the finite-wellbore
    Everdingen-Hurst pressure transform.

    Parameters
    ----------
    s : array-like
        Laplace variable.

    Returns
    -------
    np.ndarray
        Laplace transform of pD(tD).
    """
    s = np.asarray(s, dtype=float)
    u = np.sqrt(s)

    return k0_over_k1(u) / (s * u)


def _pbar_constant_rate_closed(s: np.ndarray, reD: float) -> np.ndarray:
    """
    Laplace-space dimensionless well pressure for radial flow with:
        inner boundary: constant rate at rD = 1
        outer boundary: no-flow at rD = reD

    This is the reciprocal transfer function of
    _qbar_constant_pressure_closed after applying a unit constant-rate
    Laplace boundary, qbarD = 1 / s.

    Parameters
    ----------
    s : array-like
        Laplace variable.
    reD : float
        Dimensionless external radius, re / rw.

    Returns
    -------
    np.ndarray
        Laplace transform of pD(tD).
    """
    s = np.asarray(s, dtype=float)
    u = np.sqrt(s)

    pterm, rterm = _constant_pressure_closed_terms(u, reD)

    return (pterm / rterm) / (s * u)


def _qbar_constant_pressure_infinite(s: np.ndarray) -> np.ndarray:
    """
    Laplace-space dimensionless rate for radial flow with:
        inner boundary: constant pressure at rD = 1
        outer boundary: infinite acting reservoir

    Parameters
    ----------
    s : array-like
        Laplace variable.

    Returns
    -------
    np.ndarray
        Laplace transform of qD(tD).
    """
    s = np.asarray(s, dtype=float)
    u = np.sqrt(s)

    return k1_over_k0(u) / u


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

    pterm, rterm = _constant_pressure_closed_terms(u, reD)

    return (rterm / pterm) / u


def _constant_pressure_closed_terms(
    u: np.ndarray, reD: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return the pressure and rate Bessel terms for a closed outer boundary.

    The common exp(-u) factor is omitted from both terms.  It cancels in the
    ratios used by the Laplace-space wellbore pressure and rate solutions.
    """
    u = np.asarray(u, dtype=float)
    reD = float(reD)

    z = u * reD
    eta_scaled = (kve(1, z) / ive(1, z)) * np.exp(-2.0 * u * (reD - 1.0))

    pterm = kve(0, u) + eta_scaled * ive(0, u)
    rterm = kve(1, u) - eta_scaled * ive(1, u)

    return pterm, rterm


def k0_over_k1(z: np.ndarray) -> np.ndarray:
    """
    Stable evaluation of K0(z) / K1(z).

    K0 and K1 share the same exponential decay, so their scaled forms can be
    divided directly.
    """
    z = np.asarray(z, dtype=float)

    return kve(0, z) / kve(1, z)


def k1_over_k0(z: np.ndarray) -> np.ndarray:
    """
    Stable evaluation of K1(z) / K0(z).

    K0 and K1 share the same exponential decay, so their scaled forms can be
    divided directly.
    """
    z = np.asarray(z, dtype=float)

    return kve(1, z) / kve(0, z)


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
