from dataclasses import dataclass
from typing import Optional, Dict
import logging

import numpy as np

from ._base_solver import BaseSolver
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
    """Pseudo Steady State solution based on shape factors.

    The solver is also applicable when there are two slightly compressible fluids
    where the second one is at irreducible saturation, not mobile.
    
    Inherits from:
        PorousMedia: Provides radial porous media properties.
        BaseSolver: Handles base solver configurations and behaviors.

    """
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

    def __call__(self,well,shape:str="circle",pinit:float=None):
        """
        Prepares the Pseudo-State solver instance for execution by configuring 
        the well and optional shape and initial pressure.

        Args:
            well  : An object representing the well to be simulated.
            shape : The shape of the reservoir.
            pinit (float, optional): Initial reservoir pressure. Defaults to None.

        Returns:
            PseudoSteadyState: Returns self to allow for method chaining or deferred execution.
        
        """
        self.tmin  = None
        self.term  = None

        self.pinit = pinit
        
        return self
    
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
        return self._tmin/(24*60*60)

    @tmin.setter
    def tmin(self,value):
        """Setter for the minimum time where PSS solution is applicable."""
        self._tmin = self.dim2t(self.bound.time_pss_accurate)*(24*60*60)

    def solve(self,times,nodes):
        """Solves for the pressure values at pseudo-steady state."""
        result = PressureDistribution(self.correct(times),nodes)

        inner = (4*self._surface)/(self.GAMMA*self.bound.factor*self.well._radius**2)
        drop1 = self._term*(1/2*np.log(inner)+self.well._skin)
        drop2 = (self.well._cond*self.fluid._fvf)/(self._vpore*self._tcomp)*result._times

        result._press = self._pinit-drop1-drop2

        return result

    def correct(self,values):
        """It sets the time values to np.nan if it is outside of the solver limit."""
        boundary = values>=self.tmin

        if np.any(~boundary):
            logging.warning("Not all times satisfy the early time limits!")

        return np.where(boundary,values,np.nan)
    
    def pseudosteady(self,times):
        """
        Sets the radius of outer circular boundary, ft and calculates
        pseudo steady state solution correcting pressure for boundary effects.
        
        If area is not None, the radius is calculated from area [acre].
        """

        term_well = -0.012648*(self.diffuse*times)/self.wcond.radius**2

        term_edge = -np.log(self.rrock.radius/self.wcond.radius)

        return self.pzero-self.pcons*(term_well+term_edge+3/4-self.wcond.skin)