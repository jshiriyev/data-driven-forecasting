import numpy as np

from prodpy import UnitConversion as uc

from ._fluid import Fluid

class BlackOil:
    """
    One-, two-, or three-phase black-oil fluid system.

    ``BlackOil`` groups oil, gas, and/or water :class:`Fluid` objects and
    enforces phase-saturation consistency. At least one phase must be present.
    Public properties use oilfield units and underscored capillary-pressure
    properties use SI units, matching the convention used by the main
    ``resprops`` classes.

    Capillary-pressure sign conventions
    -----------------------------------
    pcow
        Oil-water capillary pressure, ``po - pw``.
    pcgo
        Gas-oil capillary pressure, ``pg - po``.
    pcgw
        Gas-water capillary pressure, ``pg - pw``.

    These are algebraic phase-pressure differences. Saturation-dependent
    capillary-pressure correlations such as Brooks-Corey and Van Genuchten
    remain in :mod:`prodpy.resprops.capip`.
    """

    DEFAULT_SATURATION_TOLERANCE = 1e-12

    def __init__(
        self,
        oil: Fluid | None = None,
        gas: Fluid | None = None,
        water: Fluid | None = None,
        *,
        saturation_tolerance: float = DEFAULT_SATURATION_TOLERANCE,
    ) -> None:
        self.saturation_tolerance = saturation_tolerance

        self._oil = self._validate_phase(oil, name="oil")
        self._gas = self._validate_phase(gas, name="gas")
        self._water = self._validate_phase(water, name="water")

        self.validate_phases()
        self.validate_saturations()

    def __repr__(self):
        """Return a concise constructor-style representation."""
        return (
            f"{type(self).__name__}("
            f"oil={self.oil!r}, "
            f"gas={self.gas!r}, "
            f"water={self.water!r})"
        )

    @property
    def saturation_tolerance(self):
        """Tolerance used when checking that phase saturations do not exceed 1."""
        return self._saturation_tolerance

    @saturation_tolerance.setter
    def saturation_tolerance(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("saturation_tolerance must be convertible to float.") from exc

        if value < 0 or not np.isfinite(value):
            raise ValueError("saturation_tolerance must be a non-negative finite value.")

        self._saturation_tolerance = value

    @property
    def oil(self):
        """Oil-phase :class:`Fluid` object."""
        return self._oil

    @oil.setter
    def oil(self, value):
        self._replace_phase("oil", value)

    @property
    def gas(self):
        """Gas-phase :class:`Fluid` object."""
        return self._gas

    @gas.setter
    def gas(self, value):
        self._replace_phase("gas", value)

    @property
    def water(self):
        """Water-phase :class:`Fluid` object."""
        return self._water

    @water.setter
    def water(self, value):
        self._replace_phase("water", value)

    @property
    def so(self):
        """Oil saturation, or None when oil is absent."""
        return None if self.oil is None else self.oil.satur

    @property
    def sg(self):
        """Gas saturation, or None when gas is absent."""
        return None if self.gas is None else self.gas.satur

    @property
    def sw(self):
        """Water saturation, or None when water is absent."""
        return None if self.water is None else self.water.satur

    @property
    def satur(self):
        """Dictionary of public phase saturations."""
        return {
            "oil": self.so,
            "gas": self.sg,
            "water": self.sw,
        }

    @property
    def total_saturation(self):
        """Total phase saturation after NumPy broadcasting."""
        saturations = self._broadcast_saturations()
        total = np.zeros_like(saturations[0], dtype=float)

        for saturation in saturations:
            total = total + saturation

        return total
    
    @property
    def comp(self):
        """Saturation-weighted fluid compressibility in 1/psi."""
        return None if self._comp is None else self._comp * uc.PSI_TO_PA

    @property
    def _comp(self):
        """
        Saturation-weighted fluid compressibility in 1/Pa.

        The mixture value is calculated as ``sum(S_phase * c_phase)`` over the
        present phases. If any present phase is missing compressibility, the
        system compressibility is unavailable and ``None`` is returned.
        """
        for phase in self.phases.values():
            if phase._comp is None:
                return None

        phases = self.phases
        saturations = self._broadcast_saturations()

        try:
            compressibilities = np.broadcast_arrays(
                *[
                    np.asarray(phase._comp, dtype=float)
                    for phase in phases.values()
                ]
            )
        except ValueError as exc:
            raise ValueError(
                "present phase compressibility arrays must be broadcast-compatible."
            ) from exc

        mixture = np.zeros_like(saturations[0], dtype=float)

        for saturation, compressibility in zip(saturations, compressibilities):
            mixture = mixture + saturation * compressibility

        return mixture

    @property
    def _pcow(self):
        """Oil-water capillary pressure in Pa, ``po - pw``."""
        if self.oil is None or self.water is None:
            return None

        return self._pressure_difference(
            self.oil,
            self.water,
            minuend_name="oil",
            subtrahend_name="water",
        )

    @property
    def pcow(self):
        """Oil-water capillary pressure in psi, ``po - pw``."""
        return None if self._pcow is None else self._pcow / uc.PSI_TO_PA

    @property
    def _pcgo(self):
        """Gas-oil capillary pressure in Pa, ``pg - po``."""
        if self.gas is None or self.oil is None:
            return None

        return self._pressure_difference(
            self.gas,
            self.oil,
            minuend_name="gas",
            subtrahend_name="oil",
        )

    @property
    def pcgo(self):
        """Gas-oil capillary pressure in psi, ``pg - po``."""
        return None if self._pcgo is None else self._pcgo / uc.PSI_TO_PA

    @property
    def _pcgw(self):
        """Gas-water capillary pressure in Pa, ``pg - pw``."""
        if self.gas is None or self.water is None:
            return None

        return self._pressure_difference(
            self.gas,
            self.water,
            minuend_name="gas",
            subtrahend_name="water",
        )

    @property
    def pcgw(self):
        """Gas-water capillary pressure in psi, ``pg - pw``."""
        return None if self._pcgw is None else self._pcgw / uc.PSI_TO_PA

    def validate_saturations(self) -> None:
        """
        Validate present phase saturations.

        Single-phase systems must have saturation equal to 1. Two- and
        three-phase systems must not sum to more than 1. NaN saturation entries
        are treated as unknown values and are ignored by these checks.
        """
        total = self.total_saturation

        if len(self.phases) == 1:
            invalid = np.isfinite(total) & (
                np.abs(total - 1.0) > self.saturation_tolerance
            )

            if np.any(invalid):
                raise ValueError("single-phase saturation must be equal to 1.")

            return

        invalid = np.isfinite(total) & (total > 1.0 + self.saturation_tolerance)

        if np.any(invalid):
            max_total = float(np.nanmax(total))
            raise ValueError(
                "present phase saturations cannot sum to more than 1; "
                f"maximum total saturation is {max_total:g}."
            )

    @staticmethod
    def _validate_phase(value, *, name: str) -> Fluid | None:
        if value is None:
            return None

        if not isinstance(value, Fluid):
            raise TypeError(
                f"{name} must be a Fluid instance or None; got {type(value).__name__}."
            )

        return value

    def validate_phases(self) -> None:
        """Validate that the system contains at least one active phase."""
        if len(self.phases) < 1:
            raise ValueError("BlackOil requires at least one phase.")

    @property
    def phases(self):
        """Dictionary of present phase objects."""
        return {
            name: phase
            for name, phase in (
                ("oil", self.oil),
                ("gas", self.gas),
                ("water", self.water),
            )
            if phase is not None
        }

    def has_phase(self, phase: str) -> bool:
        """
        Return whether a phase is defined in the system.

        Parameters
        ----------
        phase : str
            Phase name. Must be one of ``"water"``, ``"oil"``, or ``"gas"``.
        """
        for name in ("water", "oil", "gas"):
            if phase == name:
                return getattr(self, name) is not None

        raise ValueError("phase must be one of 'water', 'oil', or 'gas'.")
    
    def get_phase(self, phase: str) -> Fluid | None:
        """
        Return the phase object if it is defined in the system.

        Parameters
        ----------
        phase : str
            Phase name. Must be one of ``"water"``, ``"oil"``, or ``"gas"``.
        """
        for name in ("water", "oil", "gas"):
            if phase == name:
                return getattr(self, name)

        raise ValueError("phase must be one of 'water', 'oil', or 'gas'.")

    def _replace_phase(self, name: str, value: Fluid | None) -> None:
        value = self._validate_phase(value, name=name)
        attribute = f"_{name}"
        previous = getattr(self, attribute)

        setattr(self, attribute, value)
        try:
            self.validate_phases()
            self.validate_saturations()
        except Exception:
            setattr(self, attribute, previous)
            raise

    def _broadcast_saturations(self):
        phases = self.phases

        try:
            return np.broadcast_arrays(
                *[
                    np.asarray(phase.satur, dtype=float)
                    for phase in phases.values()
                ]
            )
        except ValueError as exc:
            raise ValueError(
                "present phase saturation arrays must be broadcast-compatible."
            ) from exc

    @staticmethod
    def _pressure_difference(
        minuend: Fluid,
        subtrahend: Fluid,
        *,
        minuend_name: str,
        subtrahend_name: str,
    ):
        if minuend._press is None or subtrahend._press is None:
            return None

        try:
            return np.asarray(minuend._press, dtype=float) - np.asarray(
                subtrahend._press,
                dtype=float,
            )
        except ValueError as exc:
            raise ValueError(
                f"{minuend_name} and {subtrahend_name} pressure arrays must be "
                "broadcast-compatible."
            ) from exc
