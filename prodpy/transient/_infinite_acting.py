import numpy as np
from scipy import special

from prodpy import UnitConversion as uc

from ._base_solver import BaseSolver
from ._pressure_distribution import PressureDistribution

class InfiniteActing(BaseSolver):
    """
    Line-source solution for radial flow in an infinite-acting reservoir.

    The solver evaluates the constant oil-rate analytical solution of the
    diffusivity equation using the exponential-integral form. It inherits the
    main :class:`BaseSolver` assumptions:

    - one borehole;
    - one constant oil-rate constraint;
    - one mobile oil phase in a ``BlackOil`` fluid system;
    - radial analytical flow with scalar effective rock/fluid properties.

    Public inputs use oilfield units: times in days, radial nodes in ft, and
    pressure in psi. Internal calculations use SI units.

    Times outside the line-source validity window are silently masked to
    ``np.nan`` in the returned pressure matrix. Skin is only applied at nodes
    equal to the borehole radius because no skin-depth model is implemented.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __call__(self, times: np.typing.ArrayLike, nodes: np.typing.ArrayLike):
        """
        Evaluate the infinite-acting line-source pressure solution.

        Parameters
        ----------
        times : array-like
            Evaluation times in days. Times outside ``[tmin, tmax]`` are
            retained in the result axes but their pressure rows are set to
            ``np.nan``.
        nodes : array-like
            Radial locations in ft. Nodes must be greater than or equal to the
            borehole radius.

        Returns
        -------
        PressureDistribution
            Pressure distribution in oilfield units through public accessors.
        """
        return super().__call__(times, nodes)

    @property
    def tmin(self):
        """
        Minimum valid line-source time in days.

        Earlier times are affected by finite-wellbore-size effects and are
        masked to ``np.nan`` by :meth:`_correct`.
        """
        return self._tmin / uc.DAY_TO_SEC
    
    @property
    def _tmin(self):
        """Minimum valid line-source time in seconds."""
        borehole = self._require_borehole()
        hdiff = self._scalar_hdiff()

        return 100.0 * borehole._radius**2 / hdiff

    @property
    def tmax(self):
        """
        Maximum valid infinite-acting time in days.

        Later times are affected by the finite drainage area and are masked to
        ``np.nan`` by :meth:`_correct`.
        """
        return self._tmax / uc.DAY_TO_SEC

    @property
    def _tmax(self):
        """Maximum valid infinite-acting time in seconds."""
        hdiff = self._scalar_hdiff()

        return 0.25 * self._radius**2 / hdiff

    def _evaluate(self, solution):
        """
        Compute the pressure matrix for the line-source solution.
        """
        self._require_scalar_analytical_state()
        self._validate_nodes(solution.nodes)

        tD = self.times2tD(self._correct(solution.times))
        rD = self.nodes2rD(solution.nodes)

        theta = self.__theta(
            self.__beta(tD, rD)
        )

        theta = self._apply_skin_at_wellbore(theta, solution.nodes)

        values = self._scalar_pinit() - self._scalar_pcons() * theta

        solution.set_pressure(values, si_unit_flag=True)

        return solution

    def _correct(self, times:np.ndarray):
        """
        Return times with values outside ``[tmin, tmax]`` replaced by ``np.nan``.

        The returned shape matches ``times``. This method intentionally masks
        invalid line-source times instead of raising.
        """
        times = np.asarray(times, dtype=float)

        bound_internal = times >= self.tmin
        bound_external = times <= self.tmax

        valids = np.logical_and(bound_internal,bound_external)

        return np.where(valids, times, np.nan)

    def _validate_nodes(self, nodes: np.typing.ArrayLike) -> None:
        """
        Validate radial nodes for the line-source solution.

        Nodes are supplied in ft and must be finite, positive, and not inside
        the borehole radius.
        """
        nodes = np.asarray(nodes, dtype=float)

        if np.any(~np.isfinite(nodes)):
            raise ValueError("nodes must contain only finite values.")

        if np.any(nodes <= 0.0):
            raise ValueError("nodes must be positive radial distances.")

        borehole = self._require_borehole()
        at_borehole = np.isclose(
            nodes,
            borehole.radius,
            rtol=1e-12,
            atol=1e-12,
        )
        inside_borehole = nodes < borehole.radius

        if np.any(inside_borehole & ~at_borehole):
            raise ValueError(
                "nodes must be greater than or equal to the borehole radius."
            )

    def _apply_skin_at_wellbore(self, theta: np.ndarray, nodes: np.typing.ArrayLike):
        """
        Add skin only to columns located at the borehole radius.
        """
        borehole = self._require_borehole()
        nodes = np.asarray(nodes, dtype=float)
        at_wellbore = np.isclose(
            nodes,
            borehole.radius,
            rtol=1e-12,
            atol=1e-12,
        )

        if not np.any(at_wellbore) or borehole.skin == 0.0:
            return theta

        theta = np.array(theta, copy=True)
        theta[:, at_wellbore.ravel()] = theta[:, at_wellbore.ravel()] + borehole.skin

        return theta

    def _require_scalar_analytical_state(self) -> None:
        """
        Validate scalar rock/fluid properties required by this analytical form.
        """
        self._scalar_hdiff()
        self._scalar_pcons()
        self._scalar_pinit()

    def _scalar_hdiff(self) -> float:
        """Scalar hydraulic diffusivity in m2/s."""
        return self._as_scalar("_hdiff", self._hdiff)

    def _scalar_pcons(self) -> float:
        """Scalar pressure-scaling constant in Pa."""
        return self._as_scalar("_pcons", self._pcons)

    def _scalar_pinit(self) -> float:
        """Scalar initial pressure in Pa."""
        return self._as_scalar("_pinit", self._require_initial_pressure())

    @staticmethod
    def _as_scalar(name: str, value) -> float:
        arr = np.asarray(value, dtype=float)

        if arr.size != 1:
            raise ValueError(
                f"InfiniteActing requires scalar analytical properties; "
                f"{name} has shape {arr.shape}."
            )

        return float(arr.item())
    
    @staticmethod
    def __beta(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        """
        Return the exponential-integral argument ``rD**2 / (4*tD)``.
        """
        return rD ** 2 / (4 * tD)
    
    @staticmethod
    def __theta(
        beta: np.typing.ArrayLike
    ) -> np.typing.NDArray:
        """
        Return dimensionless pressure ``-0.5 * Ei(-beta)``.
        """
        return -1/2*special.expi(-beta)
    
    @staticmethod
    def beta(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        """
        Convenience wrapper for :meth:`beta` with normalized tD/rD arrays.
        """
        tD = PressureDistribution._set_times(tD)
        rD = PressureDistribution._set_nodes(rD)
        return InfiniteActing.__beta(tD, rD)
    
    @staticmethod
    def beta2theta(
        beta: np.typing.ArrayLike
    ) -> np.typing.NDArray:
        """
        Convenience wrapper for :meth:`theta` from beta values.
        """
        beta = np.asarray(beta, dtype=float)

        return InfiniteActing.__theta(beta)
    
    @staticmethod
    def theta(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        """
        Convenience wrapper returning dimensionless pressure from tD and rD.
        """
        tD = PressureDistribution._set_times(tD)
        rD = PressureDistribution._set_nodes(rD)

        beta = InfiniteActing.__beta(tD, rD)
        return InfiniteActing.__theta(beta)
    
    @staticmethod
    def pD(*args, **kwargs) -> np.typing.NDArray:
        """
        Convenience wrapper for dimensionless pressure from tD and rD.
        """
        return InfiniteActing.theta(*args, **kwargs)

    @staticmethod
    def pwD(
        tD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        """
        Dimensionless wellbore pressure for the line-source solution.
        """
        tD = PressureDistribution._set_times(tD).flatten()

        beta = InfiniteActing.__beta(tD, 1.0)
        return InfiniteActing.__theta(beta)