from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from prodpy.decline._arps import Arps
from prodpy.transient._everdingen_hurst import EverdingenHurst


class Fetkovich:
    """
    Generate Fetkovich type-curve families.

    The radial-flow family converts the closed-boundary, constant-pressure
    Everdingen-Hurst rate solution into Fetkovich decline variables:

        qDd = qD * (ln(reD) - 0.5)
        tDd = tD / {0.5 * (reD**2 - 1) * (ln(reD) - 0.5)}

    The decline family returns the Arps dimensionless decline curves used as
    Fetkovich type-curve reference lines.

    Symbols
    -------
    tD : float or array-like
        Radial-flow dimensionless time.
    qD : float or array-like
        Radial-flow dimensionless rate.
    tDd : float or array-like
        Fetkovich decline dimensionless time.
    qDd : float or array-like
        Fetkovich decline dimensionless rate.
    reD : float
        Dimensionless drainage radius, re / rw.
    b_factor : float
        Arps decline exponent. ``0`` is exponential, ``1`` is harmonic, and
        values between them are hyperbolic.
    """

    @staticmethod
    def radial_constant_pressure(
        tDd: ArrayLike,
        reD: float,
        degree: int = 12,
    ) -> float | np.ndarray:
        """
        Return the finite-radial Fetkovich constant-pressure rate curve.

        Parameters
        ----------
        tDd : array-like
            Fetkovich decline dimensionless time. Values must be finite and
            strictly positive.
        reD : float
            Dimensionless drainage radius, ``re / rw``. Must be finite and
            greater than ``exp(0.5)`` so the Fetkovich rate and time scales are
            positive.
        degree : int, default 12
            Stehfest inversion degree passed to
            :meth:`prodpy.transient.EverdingenHurst.qD`.

        Returns
        -------
        float or np.ndarray
            Fetkovich decline dimensionless rate, ``qDd``. A scalar is returned
            when ``tDd`` is scalar; otherwise an array matching ``tDd`` shape is
            returned.

        Raises
        ------
        ValueError
            If ``tDd`` is not strictly positive or ``reD`` does not produce a
            positive Fetkovich scale.
        """
        tDd = Fetkovich._as_positive_array("tDd", tDd)
        reD = Fetkovich._validate_reD(reD)
        tD = Fetkovich.tDd_to_tD(tDd, reD)
        qD = EverdingenHurst.qD(tD, reD, boundary="closed", degree=degree)

        return Fetkovich.qD_to_qDd(qD, reD)

    @staticmethod
    def arps_decline(tDd: ArrayLike, b_factor: float = 0) -> float | np.ndarray:
        """
        Return an Arps dimensionless decline reference curve.

        Parameters
        ----------
        tDd : array-like
            Fetkovich decline dimensionless time. Values must be finite and
            nonnegative.
        b_factor : float, default 0
            Arps decline exponent. ``0`` returns the exponential limit, ``1``
            returns the harmonic limit, and intermediate values return the
            hyperbolic curve.

        Returns
        -------
        float or np.ndarray
            Arps dimensionless decline rate, ``qDd``.

        Raises
        ------
        ValueError
            If ``tDd`` is negative or ``b_factor`` is outside ``[0, 1]``.
        """
        tDd = Fetkovich._as_nonnegative_array("tDd", tDd)
        b_factor = Fetkovich._validate_b_factor(b_factor)

        if np.isclose(b_factor, 0.0, atol=1e-12):
            qDd = Arps.exp.qDd(tDd)
        elif np.isclose(b_factor, 1.0, atol=1e-12):
            qDd = Arps.har.qDd(tDd)
        else:
            qDd = Arps.hyp.qDd(b_factor, tDd)

        return Fetkovich._as_float_result(qDd)

    @staticmethod
    def curve(
        tDd: ArrayLike,
        reD: float,
        degree: int = 12,
    ) -> tuple[float | np.ndarray, float | np.ndarray]:
        """
        Return ``(tDd, qDd)`` for a finite-radial Fetkovich type curve.

        This is a plotting convenience around
        :meth:`radial_constant_pressure`.
        """
        tDd = Fetkovich._as_positive_array("tDd", tDd)
        qDd = Fetkovich.radial_constant_pressure(tDd, reD, degree=degree)

        return Fetkovich._as_float_result(tDd), qDd

    @staticmethod
    def qD_to_qDd(qD: ArrayLike, reD: float) -> float | np.ndarray:
        """
        Convert radial-flow dimensionless rate ``qD`` to Fetkovich ``qDd``.

        The conversion is ``qDd = qD * (ln(reD) - 0.5)``.
        """
        qD = np.asarray(qD, dtype=float)
        return Fetkovich._as_float_result(qD * Fetkovich._rate_scale(reD))

    @staticmethod
    def qDd_to_qD(qDd: ArrayLike, reD: float) -> float | np.ndarray:
        """
        Convert Fetkovich decline dimensionless rate ``qDd`` to radial ``qD``.

        The conversion is ``qD = qDd / (ln(reD) - 0.5)``.
        """
        qDd = np.asarray(qDd, dtype=float)
        return Fetkovich._as_float_result(qDd / Fetkovich._rate_scale(reD))

    @staticmethod
    def tD_to_tDd(tD: ArrayLike, reD: float) -> float | np.ndarray:
        """
        Convert radial-flow dimensionless time ``tD`` to Fetkovich ``tDd``.
        """
        tD = np.asarray(tD, dtype=float)
        return Fetkovich._as_float_result(tD / Fetkovich._time_scale(reD))

    @staticmethod
    def tDd_to_tD(tDd: ArrayLike, reD: float) -> float | np.ndarray:
        """
        Convert Fetkovich decline dimensionless time ``tDd`` to radial ``tD``.
        """
        tDd = np.asarray(tDd, dtype=float)
        return Fetkovich._as_float_result(tDd * Fetkovich._time_scale(reD))

    @staticmethod
    def _rate_scale(reD: float) -> float:
        """
        Fetkovich rate scaling factor, ``ln(reD) - 0.5``.
        """
        reD = Fetkovich._validate_reD(reD)
        return np.log(reD) - 0.5

    @staticmethod
    def _time_scale(reD: float) -> float:
        """
        Fetkovich time scaling factor.

        tDd = tD / scale

        where:

            scale = 0.5 * (reD**2 - 1) * [ln(reD) - 0.5]

        """
        reD = Fetkovich._validate_reD(reD)
        return 0.5 * (reD**2 - 1.0) * Fetkovich._rate_scale(reD)

    @staticmethod
    def _validate_reD(reD: float) -> float:
        """
        Validate the drainage radius used by Fetkovich transforms.
        """
        reD = float(reD)

        if not np.isfinite(reD):
            raise ValueError("reD must be finite for Fetkovich decline scaling.")

        if reD <= np.exp(0.5):
            raise ValueError(
                "reD must be greater than exp(0.5) so ln(reD) - 0.5 is positive."
            )

        return reD

    @staticmethod
    def _validate_b_factor(b_factor: float) -> float:
        """
        Validate the Arps decline exponent used by reference curves.
        """
        b_factor = float(b_factor)

        if not np.isfinite(b_factor):
            raise ValueError("b_factor must be finite.")

        if not 0.0 <= b_factor <= 1.0:
            raise ValueError("b_factor must be in [0, 1].")

        return b_factor

    @staticmethod
    def _as_positive_array(name: str, values: ArrayLike) -> np.ndarray:
        """
        Return finite values as a float array and require all values to be > 0.
        """
        values = np.asarray(values, dtype=float)

        if np.any(~np.isfinite(values)):
            raise ValueError(f"{name} must contain only finite values.")

        if np.any(values <= 0.0):
            raise ValueError(f"{name} must be strictly positive.")

        return values

    @staticmethod
    def _as_nonnegative_array(name: str, values: ArrayLike) -> np.ndarray:
        """
        Return finite values as a float array and require all values to be >= 0.
        """
        values = np.asarray(values, dtype=float)

        if np.any(~np.isfinite(values)):
            raise ValueError(f"{name} must contain only finite values.")

        if np.any(values < 0.0):
            raise ValueError(f"{name} must be nonnegative.")

        return values

    @staticmethod
    def _as_float_result(values: ArrayLike) -> float | np.ndarray:
        """
        Return scalar arrays as Python floats and preserve shaped arrays.
        """
        values = np.asarray(values, dtype=float)
        return values.item() if values.ndim == 0 else values
