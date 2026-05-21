from dataclasses import dataclass
from typing import Optional, Dict

import numpy as np

from prodpy import UnitConversion as uc

from ._qconst_solver import BaseSolver
from ._pressure_distribution import PressureDistribution

@dataclass(frozen=True)
class Boundary:
    """Dietz drainage-area shape-factor record."""
    #shape factor, {C_A} value
    shape_factor: float
    # Use infinite system solution
    tDA_infinite_acting_end: Optional[float]
    # PSS is exact for higher values
    tDA_pss_start: Optional[float]

    note: str = ""

class PseudoSteadyState(BaseSolver):
    """Pseudo-steady-state constant-rate solutions.

    ``__call__`` evaluates the radial pressure distribution for a centered well
    in a closed cylindrical reservoir. ``well_pressure`` evaluates the flowing
    well pressure for any supported Dietz drainage-area shape factor.

    The solver is also applicable when there are two slightly compressible
    fluids where the second one is at irreducible saturation and immobile.
    
    Inherits from:
        BaseSolver: Handles base solver configurations and behaviors.

    """
    EULER_CONSTANT_EXP = float(np.exp(0.5772156649015329))

    SHAPE_FACTORS: Dict[str, Boundary] = {
        "circle_center":       Boundary(31.62,   0.10,  0.06, "Circle, centered well"),
        "hexagon_center":      Boundary(31.6,    0.10,  0.06, "Hexagon, centered well"),
        "triangle_center":     Boundary(27.6,    0.09,  0.07, "Triangle, centered well"),
        "parallelogram_center":Boundary(27.1,    0.09,  0.07, "Parallelogram/rhombus row"),
        "triangle_row":        Boundary(21.9,    0.08,  0.12, "Triangle row; verify well location"),
        "triangle_low_CA":     Boundary( 0.098,  0.015, 0.60, "Low-C_A triangular/boundary row"),
        "square_center":       Boundary(30.8828, 0.09,  0.05, "Square, centered well"),
        "square_quadrants":    Boundary(12.9851, 0.03,  0.25, "Square subdivided row"),
        "square_offcenter":    Boundary( 4.5132, 0.025, 0.30, "Square off-center row"),
        "square_grid":         Boundary( 3.3351, 0.01,  0.25, "Square grid row"),
        "rect_center":         Boundary(21.8369, 0.025, 0.15, "Rectangle centered row"),
        "rect_split_center":   Boundary(10.8374, 0.025, 0.15, "Rectangle split/center row"),
        "rect_offcenter":      Boundary( 4.5141, 0.06,  0.50, "Rectangle off-center row"),
        "rect_corner":         Boundary( 2.0769, 0.02,  0.50, "Rectangle/corner row"),
        "long_rect_center":    Boundary( 3.1573, 0.005, 0.15, "Long rectangle row"),
        "long_rect_edge":      Boundary( 0.5813, 0.02,  0.60, "Long rectangle edge row"),
        "very_long_rect_edge": Boundary( 0.1109, 0.005, 0.60, "Very long rectangle edge row"),
        "strip_center":        Boundary( 5.3790, 0.01,  0.30, "Strip/rectangle centered row"),
        "strip_split":         Boundary( 2.6896, 0.01,  0.30, "Strip split row"),
        "strip_offcenter":     Boundary( 0.2318, 0.03,  2.00, "Strip off-center row"),
        "strip_edge":          Boundary( 0.1155, 0.01,  2.00, "Strip edge row"),
    }

    def __init__(self,
        *args,
        shape_key: str = "circle_center",
        shape_factor: Optional[float] = None,
        tDA_infinite_acting_end: Optional[float] = None,
        tDA_pss_start: Optional[float] = None,
        note: str = "Circle, centered well",
        **kwargs
    ):
        """
        Initializes the Pseudo-State solver by invoking the initializers of 
        PorousMedia and BaseSolver.

        Args:
            size (float tuple): porous media size for PorousMedia.
            **kwargs: Keyword arguments for BaseSolver.

        """
        super().__init__(*args, **kwargs)

        if shape_factor is not None:
            self.shape_key = "custom"
            self.shape = Boundary(
                shape_factor = self._validate_positive("shape factor", shape_factor),
                tDA_infinite_acting_end = tDA_infinite_acting_end,
                tDA_pss_start = tDA_pss_start,
                note = note,
            )
        else:
            if shape_key not in self.SHAPE_FACTORS:
                raise KeyError(f"Unknown shape_key: {shape_key}")
            self.shape_key = shape_key
            self.shape = self.SHAPE_FACTORS[shape_key]

    def __repr__(self) -> str:

        args = []

        if self.shape_key == "custom":
            args.extend([
                f"shape_factor={self.shape.shape_factor!r}",
                f"tDA_infinite_acting_end={self.shape.tDA_infinite_acting_end!r}",
                f"tDA_pss_start={self.shape.tDA_pss_start!r}",
                f"note={self.shape.note!r}",
            ])
        else:
            args.append(f"shape_key={self.shape_key!r}")

        return f"{type(self).__name__}({', '.join(args)})"

    def __call__(self, times: np.typing.ArrayLike, nodes: np.typing.ArrayLike):
        """
        Evaluate the pseudo-steady-state pressure distribution in a cylinder.

        Parameters
        ----------
        times : array-like
            Evaluation times in days. Times earlier than ``tmin`` are retained
            in the result axes but their pressure rows are set to ``np.nan``.
        nodes : array-like
            Radial locations in ft. Nodes must be between the borehole radius
            and the circular drainage radius.

        Returns
        -------
        PressureDistribution
            Pressure distribution in oilfield units through public accessors.
        """
        return self.reservoir_pressure(times, nodes)
    
    def reservoir_pressure(
        self,
        times: np.typing.ArrayLike,
        nodes: np.typing.ArrayLike,
    ) -> PressureDistribution:
        """Return radial pressure distribution for a closed cylindrical reservoir."""
        return super().__call__(times, nodes)
    
    def well_pressure(self, times: np.typing.ArrayLike) -> PressureDistribution:
        """Return shape-factor flowing well pressure at the borehole radius."""
        self._require_ready()
        self._require_finite_area()
        self._require_scalar_analytical_state()

        borehole = self._require_borehole()
        solution = PressureDistribution(times, np.array([borehole.radius]))

        tDA = self.tDA(self._correct(solution.times))
        pwD = self.pwD(
            tDA,
            borehole._radius,
            self._area,
            self.shape_factor,
            skin=borehole.skin,
        )
        values = self._scalar_pinit() - self._scalar_pcons() * pwD

        solution.set_pressure(values, si_unit_flag=True)

        return solution
    
    @property
    def shape_factor(self) -> float:
        return self.shape.shape_factor
    
    @classmethod
    def available_shape_factors(cls) -> Dict[str, Boundary]:
        """Return available shape-factor records."""
        return cls.SHAPE_FACTORS.copy()

    @property
    def tmin(self):
        """Getter for the minimum time where PSS solution is applicable."""
        return self._tmin / uc.DAY_TO_SEC

    @property
    def _tmin(self):
        """Minimum pseudo-steady-state time in seconds."""
        if self.shape.tDA_pss_start is None:
            return 0.0

        return (
            self.shape.tDA_pss_start
            * self._require_finite_area()
            / self._scalar_hdiff()
        )

    def _evaluate(self, solution):
        """Populate radial cylindrical reservoir pressure values."""
        self._require_cylindrical_shape()
        self._require_finite_area()
        self._require_scalar_analytical_state()
        self._validate_nodes(solution.nodes)

        tD = self._dimensionless_radial_time(self._correct(solution.times))
        rD = self.nodes2rD(solution.nodes)
        reD = self._reservoir_radius_dimensionless()

        pD = self.prD(tD, rD, reD)
        pD = self._apply_skin_at_wellbore(pD, solution.nodes)

        values = self._scalar_pinit() - self._scalar_pcons() * pD

        solution.set_pressure(values, si_unit_flag=True)

        return solution

    def _correct(self, times: np.typing.ArrayLike):
        """
        Return times with values earlier than ``tmin`` replaced by ``np.nan``.
        """
        times = np.asarray(times, dtype=float)

        return np.where(times >= self.tmin, times, np.nan)
    
    def tDA(self, times: np.typing.ArrayLike):
        """Drainage-area dimensionless time, ``eta * t / A``."""
        times = np.asarray(times, dtype=float) * uc.DAY_TO_SEC

        return self._scalar_hdiff() * times / self._require_finite_area()
    
    def tDA2times(self, tDA: np.typing.ArrayLike):
        """Convert drainage-area dimensionless time to days."""
        tDA = np.asarray(tDA, dtype=float)

        return tDA * self._require_finite_area() / self._scalar_hdiff() / uc.DAY_TO_SEC
    
    def _dimensionless_radial_time(self, times: np.typing.ArrayLike):
        """Radial dimensionless time based on borehole radius."""
        borehole = self._require_borehole()
        times = np.asarray(times, dtype=float) * uc.DAY_TO_SEC

        return self._scalar_hdiff() * times / borehole._radius**2
    
    def _reservoir_radius_dimensionless(self) -> float:
        """Circular drainage radius divided by borehole radius."""
        borehole = self._require_borehole()

        return self._radius / borehole._radius
    
    def _require_cylindrical_shape(self) -> None:
        """Ensure the radial pressure-distribution formula is used only for cylinders."""
        if self.shape_key != "circle_center":
            raise ValueError(
                "Reservoir pressure distribution is only implemented for a "
                "centered well in a cylindrical reservoir. Use "
                "well_pressure(...) for shape-factor drainage geometries."
            )
    
    def _require_finite_area(self) -> float:
        """Return finite drainage area in square meters."""
        if not np.isfinite(self._area):
            raise ValueError("PseudoSteadyState requires a finite drainage area.")
        
        borehole = self._require_borehole()

        if self._radius <= borehole._radius:
            raise ValueError("drainage radius must be larger than borehole radius.")

        return self._area
    
    def _validate_nodes(self, nodes: np.typing.ArrayLike) -> None:
        """Validate radial nodes for the cylindrical PSS pressure distribution."""
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

        at_boundary = np.isclose(
            nodes,
            self.radius,
            rtol=1e-12,
            atol=1e-12,
        )
        outside_boundary = nodes > self.radius

        if np.any(outside_boundary & ~at_boundary):
            raise ValueError(
                "nodes must be smaller than or equal to the drainage radius."
            )
    
    def _apply_skin_at_wellbore(self, pD: np.ndarray, nodes: np.typing.ArrayLike):
        """Add skin only to pressure columns located at the borehole radius."""
        borehole = self._require_borehole()
        nodes = np.asarray(nodes, dtype=float)
        at_borehole = np.isclose(
            nodes,
            borehole.radius,
            rtol=1e-12,
            atol=1e-12,
        )

        if not np.any(at_borehole) or borehole.skin == 0.0:
            return pD

        pD = np.array(pD, copy=True)
        pD[:, at_borehole.ravel()] = pD[:, at_borehole.ravel()] + borehole.skin

        return pD
    
    def _require_scalar_analytical_state(self) -> None:
        """Validate scalar properties required by the analytical PSS equations."""
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
                f"PseudoSteadyState requires scalar analytical properties; "
                f"{name} has shape {arr.shape}."
            )

        return float(arr.item())
    
    @staticmethod
    def prD(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
        reD: float,
    ):
        """
        Dimensionless pressure for radial flow in a closed cylindrical reservoir.

        The spatial terms are referenced to average reservoir pressure, so
        their areal average is zero over the cylinder.
        """
        tD = np.asarray(tD, dtype=float)
        rD = np.asarray(rD, dtype=float)
        reD = float(reD)

        return (
            2.0 * tD / reD**2
            + np.log(reD / rD)
            - 0.75
            + rD**2 / (2.0 * reD**2)
        )
    
    @staticmethod
    def pwD(
        tDA: np.typing.ArrayLike,
        rw: float,
        A: float,
        C_A: float,
        *,
        skin: float = 0.0,
    ):
        """Dietz shape-factor dimensionless flowing well pressure."""
        tDA = np.asarray(tDA, dtype=float)

        term_shape = 0.5 * np.log(
            (4.0 * A)
            / (PseudoSteadyState.EULER_CONSTANT_EXP * C_A * rw**2)
        )

        return 2.0 * np.pi * tDA + term_shape + skin
