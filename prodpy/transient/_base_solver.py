from abc import ABC, abstractmethod

import numpy as np
from scipy import constants

from prodpy.porsim.prerun import Borehole, Boundary

from prodpy import UnitConversion as uc

from ._pressure_distribution import PressureDistribution
from ._reservoir_domain import ReservoirDomain


class BaseSolver(ReservoirDomain, ABC):
    """
    Shared base for radial analytical diffusivity-equation solvers.

    ``BaseSolver`` extends :class:`ReservoirDomain` with one wellbore and an
    optional collection of external boundary/fault conditions. It intentionally
    keeps the analytical-flow assumptions narrow:

    - one and only one borehole is allowed;
    - the borehole must contain exactly one oil-rate constraint;
    - the reservoir fluid system is a :class:`prodpy.resprops.BlackOil` object;
    - exactly one phase in the black-oil system may be mobile;
    - because the well control is oil-rate, the mobile phase must be oil;
    - radial analytical flow is assumed.

    Public properties use oilfield units. Underscored properties use SI units.

    Parameters
    ----------
    *args
        Positional arguments passed to :class:`ReservoirDomain`.
    **kwargs
        Keyword arguments passed to :class:`ReservoirDomain`.

    Notes
    -----
    ``BaseSolver`` does not add required construction arguments beyond
    ``ReservoirDomain``. Users can assign ``solver.borehole`` or call
    ``solver.set_borehole(...)`` after construction, and may add zero or more
    boundaries with ``solver.add_boundary(...)``.

    Concrete subclasses must implement ``__call__`` and can call
    ``super().__call__(times, nodes)`` to get common readiness checks and a
    prepared :class:`PressureDistribution`.
    """

    REQUIRED_RATE_MODE = "orate"
    REQUIRED_MOBILE_PHASE = "oil"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._borehole: Borehole | None = None
        self._boundaries: list[Boundary] = []

    @abstractmethod
    def __call__(self, times: np.typing.ArrayLike, nodes: np.typing.ArrayLike, *args, **kwargs):
        """
        Prepare and evaluate the analytical solution.

        Subclasses may use this implementation by calling ``super().__call__``.
        The base implementation validates the reservoir/well/fluid state,
        creates a :class:`PressureDistribution`, and delegates the actual
        pressure calculation to ``_evaluate``.

        Parameters
        ----------
        times : array-like
            Evaluation times in days.
        nodes : array-like
            Radial node locations in ft.

        Returns
        -------
        PressureDistribution
            Pressure solution evaluated at the requested times and nodes.
        """
        self._require_ready()

        solution = PressureDistribution(times, nodes)

        return self._evaluate(solution, *args, **kwargs)

    @abstractmethod
    def _evaluate(self, solution: PressureDistribution, *args, **kwargs):
        """Implement the concrete analytical pressure solution."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Borehole management
    # ------------------------------------------------------------------
    @property
    def borehole(self) -> Borehole | None:
        """Single borehole object assigned to the solver."""
        return self._borehole

    @borehole.setter
    def borehole(self, value: Borehole | None) -> None:
        """
        Set the solver borehole.

        ``None`` is allowed only as a delayed-assignment/clearing state. A
        usable solver must have exactly one :class:`Borehole` before
        evaluation.
        """
        if value is None:
            self._borehole = None
            return

        if not isinstance(value, Borehole):
            raise TypeError(
                f"borehole must be a Borehole instance or None; got {type(value).__name__}."
            )

        if value._radius is None:
            raise ValueError("borehole radius must be assigned before using this solver.")

        self._borehole = value

    def set_borehole(self, borehole: Borehole | None = None, **kwargs) -> Borehole:
        """
        Assign the single solver borehole.

        Parameters
        ----------
        borehole : Borehole, optional
            Existing borehole object.
        **kwargs
            Arguments used to create a :class:`Borehole` when ``borehole`` is
            not provided.

        Returns
        -------
        Borehole
            Assigned borehole object.
        """
        if borehole is None:
            borehole = Borehole(**kwargs)
        elif kwargs:
            raise ValueError(
                "Provide either an existing Borehole object or keyword "
                "arguments to create one, not both."
            )

        self.borehole = borehole
        return borehole

    def _require_borehole(self) -> Borehole:
        """Return the assigned borehole, or raise a clear readiness error."""
        if self._borehole is None:
            raise ValueError("Exactly one borehole must be assigned before using this solver.")

        return self._borehole

    def _require_oil_rate_constraint(self):
        """
        Return the sole oil-rate constraint for the assigned borehole.

        ``BaseSolver`` represents constant oil-rate analytical flow. Scheduled
        or mixed-mode well controls should be handled by a more specific solver.
        """
        borehole = self._require_borehole()
        constraints = borehole.constraints

        if len(constraints) != 1:
            raise ValueError(
                "BaseSolver requires exactly one borehole constraint: "
                "a constant oil-rate constraint with mode='orate'."
            )

        constraint = constraints[0]

        if constraint.mode != self.REQUIRED_RATE_MODE:
            raise ValueError(
                "BaseSolver only supports oil-rate-controlled boreholes; "
                f"expected mode='orate', got mode={constraint.mode!r}."
            )

        return constraint

    @property
    def rate(self) -> float:
        """Constant oil-rate constraint in STB/day."""
        return self._require_oil_rate_constraint().limit

    @property
    def _rate(self) -> float:
        """Constant oil-rate constraint in m3/s."""
        return self._require_oil_rate_constraint()._limit

    # ------------------------------------------------------------------
    # Boundary management
    # ------------------------------------------------------------------
    @property
    def boundaries(self) -> tuple[Boundary, ...]:
        """
        Boundary/fault objects assigned to the solver.

        A tuple is returned to prevent accidental list-level modification.
        """
        return tuple(self._boundaries)

    def add_boundary(self, boundary: Boundary | str | None = None, **kwargs) -> Boundary:
        """
        Add a boundary/fault condition container.

        Parameters
        ----------
        boundary : Boundary or str, optional
            Existing :class:`Boundary` object, or a face string such as
            ``"xmin"``. If omitted, ``kwargs`` must contain the arguments needed
            to construct a :class:`Boundary`, including ``face``.
        **kwargs
            Arguments used to create a boundary when ``boundary`` is not an
            existing :class:`Boundary`.
        """
        if boundary is None:
            boundary = Boundary(**kwargs)
        elif isinstance(boundary, str):
            boundary = Boundary(boundary, **kwargs)
        elif kwargs:
            raise ValueError(
                "Provide either an existing Boundary object or construction "
                "arguments, not both."
            )

        if not isinstance(boundary, Boundary):
            raise TypeError(
                f"boundary must be a Boundary instance, face string, or None; "
                f"got {type(boundary).__name__}."
            )

        self._boundaries.append(boundary)
        return boundary

    def remove_boundary(self, boundary: Boundary) -> None:
        """Remove a boundary/fault condition container."""
        self._boundaries.remove(boundary)

    def clear_boundaries(self) -> None:
        """Remove all boundary/fault condition containers."""
        self._boundaries.clear()

    def active_boundaries(self, time_days: float) -> tuple[Boundary, ...]:
        """
        Return boundaries with an active constraint at ``time_days``.
        """
        return tuple(
            boundary
            for boundary in self._boundaries
            if boundary.active_constraint(time_days) is not None
        )

    # ------------------------------------------------------------------
    # Mobile-phase helpers
    # ------------------------------------------------------------------
    @property
    def mobile_phase_name(self) -> str:
        """Name of the sole mobile phase in the BlackOil fluid system."""
        name, _ = self._require_mobile_phase()
        return name

    @property
    def mobile_phase(self):
        """Sole mobile phase object in the BlackOil fluid system."""
        _, phase = self._require_mobile_phase()
        return phase

    def _require_mobile_phase(self):
        """
        Return the sole mobile phase as ``(name, phase)``.

        A phase is considered mobile when any finite relative-permeability
        value is greater than zero. Defined but immobile phases are allowed, but
        they must have zero relative permeability.
        """
        fluid = self._require_fluid()
        mobile = [
            (name, phase)
            for name, phase in fluid.phases.items()
            if self._phase_is_mobile(phase)
        ]

        if len(mobile) != 1:
            names = [name for name, _ in mobile]
            raise ValueError(
                "BaseSolver requires exactly one mobile phase in the BlackOil "
                f"system; found {len(mobile)} mobile phases: {names}."
            )

        name, phase = mobile[0]

        if name != self.REQUIRED_MOBILE_PHASE:
            raise ValueError(
                "BaseSolver is oil-rate controlled, so the sole mobile phase "
                f"must be 'oil'; got {name!r}."
            )

        return name, phase

    @staticmethod
    def _phase_is_mobile(phase) -> bool:
        rperm = np.asarray(phase._rperm, dtype=float)
        finite = np.isfinite(rperm)

        return bool(np.any(finite & (rperm > 0.0)))

    # ------------------------------------------------------------------
    # Radial analytical-flow quantities
    # ------------------------------------------------------------------
    @property
    def radial_permeability(self):
        """Effective radial permeability in mD."""
        return self._radial_permeability / uc.MD_TO_M2

    @property
    def _radial_permeability(self):
        """
        Effective radial permeability in m2.

        For a vertical well this is ``sqrt(kx * ky)``. For horizontal wells,
        the radial plane is taken perpendicular to the borehole axis.
        """
        borehole = self._require_borehole()

        axis_pairs = {
            "x": (1, 2),
            "y": (0, 2),
            "z": (0, 1),
        }
        first, second = axis_pairs[borehole.axis]

        return np.sqrt(self._perm[:, first] * self._perm[:, second])

    def hdiff(self):
        """Hydraulic diffusivity for the mobile oil phase in ft2/day."""
        return self._hdiff * uc.DAY_TO_SEC / uc.FT_TO_M**2

    @property
    def _hdiff(self):
        """
        Hydraulic diffusivity for radial flow of the mobile oil phase in m2/s.
        """
        _, phase = self._require_mobile_phase()
        tcomp = self._require_total_compressibility()

        return (
            phase._rperm
            * self._radial_permeability
            / (self._poro * phase._visc * tcomp)
        )

    @property
    def storage(self):
        """Wellbore storage coefficient in ft3/psi."""
        return self._storage * uc.PSI_TO_PA / uc.FT_TO_M**3

    @property
    def _storage(self):
        """Wellbore storage coefficient in m3/Pa."""
        _, phase = self._require_mobile_phase()

        if phase._rho is None:
            raise ValueError(
                "Mobile oil-phase density must be assigned to compute wellbore storage."
            )

        borehole = self._require_borehole()
        return borehole._area / (phase._rho * constants.g)

    @property
    def pcons(self):
        """Pressure-scaling constant in psi for the constant oil-rate solution."""
        return self._pcons / uc.PSI_TO_PA

    @property
    def _pcons(self):
        """Pressure-scaling constant in Pa for the constant oil-rate solution."""
        _, phase = self._require_mobile_phase()

        return self._rate / (
            2.0
            * np.pi
            * self._radial_permeability
            * self._height
            * phase._mobil
        )

    def CD(self):
        """Dimensionless wellbore storage coefficient."""
        borehole = self._require_borehole()
        tcomp = self._require_total_compressibility()

        volume = self._poro * self._height * borehole._area

        return self._storage / (volume * tcomp)

    def CD2storage(self, CD: np.typing.ArrayLike):
        """Convert dimensionless wellbore storage to ft3/psi."""
        borehole = self._require_borehole()
        tcomp = self._require_total_compressibility()

        volume = self._poro * self._height * borehole._area

        return np.asarray(CD, dtype=float) * volume * tcomp * uc.PSI_TO_PA / uc.FT_TO_M**3

    def tD(self, times: np.typing.ArrayLike):
        """Dimensionless radial-flow time."""
        borehole = self._require_borehole()
        times = np.asarray(times, dtype=float) * uc.DAY_TO_SEC

        return self._hdiff * times / borehole._radius**2

    def tD2times(self, tD: np.typing.ArrayLike):
        """Convert dimensionless time to days."""
        borehole = self._require_borehole()
        tD = np.asarray(tD, dtype=float)

        return tD * borehole._radius**2 / self._hdiff / uc.DAY_TO_SEC

    def rD(self, nodes: np.typing.ArrayLike):
        """Dimensionless radius relative to borehole radius."""
        borehole = self._require_borehole()
        nodes = np.asarray(nodes, dtype=float) * uc.FT_TO_M

        return nodes / borehole._radius

    def rD2nodes(self, rD: np.typing.ArrayLike):
        """Convert dimensionless radius to ft."""
        borehole = self._require_borehole()
        rD = np.asarray(rD, dtype=float)

        return rD * borehole._radius / uc.FT_TO_M

    def pD(self, press: np.typing.ArrayLike):
        """Dimensionless pressure for the constant oil-rate radial solution."""
        pinit = self._require_initial_pressure()
        press = np.asarray(press, dtype=float) * uc.PSI_TO_PA

        return (pinit - press) / self._pcons

    def pD2press(self, pD: np.typing.ArrayLike):
        """Convert dimensionless pressure to psi."""
        pinit = self._require_initial_pressure()
        pD = np.asarray(pD, dtype=float)

        return (pinit - pD * self._pcons) / uc.PSI_TO_PA

    # ------------------------------------------------------------------
    # Readiness
    # ------------------------------------------------------------------
    def _require_ready(self) -> "BaseSolver":
        """
        Validate the common BaseSolver state and return ``self``.
        """
        self._require_fluid()
        self._require_initial_pressure()
        self._require_total_compressibility()
        self._require_borehole()
        self._require_oil_rate_constraint()
        self._require_mobile_phase()

        return self
