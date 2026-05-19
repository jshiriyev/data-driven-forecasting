import logging

import numpy as np
from scipy import special

from ._base_solver import BaseSolver
from ._pressure_distribution import PressureDistribution

class InfiniteReservoir(BaseSolver):
    """
    Infinite acting reservoir solution of the diffusivity equation in radial coordinates
    assuming a line source solution for the well; The solver is based on the exponential integral.

    Inherits from:
        BaseSolver: Handles base solver configurations and behaviors.

    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def tmin(self):
        """Getter for the minimum time limit for the transient solution because of the finite wellbore size."""
        return self._tmin/self.DAY_TO_SEC
    
    @property
    def _tmin(self):
        """Setter for the mimimum time limit for the transient solution because of the finite wellbore size."""
        return 100 * self.borehole._radius**2 / self._hdiff

    @property
    def tmax(self):
        """Getter for the maximum time limit for the transient solution because of the finite reservoir size."""
        return self._tmax / self.DAY_TO_SEC

    @property
    def _tmax(self):
        """Setter for the maximum time limit for the transient solution because of the finite reservoir size."""
        return 0.25 * self._radius_equivalent**2 / self._hdiff

    def _evaluate(self, solution):
        """
        Compute pressure distribution for this specific analytical solution.

        """
        tD = self.tD(self._correct(solution.times))
        rD = self.rD(solution.nodes)

        theta = self.theta(
            self.beta(tD, rD)
        )

        if self._pinit is None:
            raise ValueError("pinit must be set before evaluating InfiniteReservoir.")

        values = self._pinit - self._pcons * theta # how to add skin factor: self.borehole.skin

        solution.set_pressure(values, si_unit_flag=True)

        return solution

    def _correct(self, times:np.ndarray):
        """
        It sets the time values to np.nan if it is outside of the solver limit.
        
        """
        bound_internal = times>=self.tmin
        bound_external = times<=self.tmax

        if np.any(~bound_internal):
            logging.warning("Not all times satisfy the early time limits!")

        if np.any(~bound_external):
            logging.warning("Not all times satisfy the late time limits!")

        valids = np.logical_and(bound_internal,bound_external)

        return np.where(valids, times, np.nan)
    
    @staticmethod
    def beta(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        return rD ** 2 / (4 * tD)
    
    @staticmethod
    def theta(
        beta: np.typing.ArrayLike
    ) -> np.typing.NDArray:
        return -1/2*special.expi(-beta)
    
    @staticmethod
    def get_beta(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        tD = PressureDistribution._set_times(tD)
        rD = PressureDistribution._set_nodes(rD)
        return InfiniteReservoir.beta(tD, rD)
    
    @staticmethod
    def get_theta_from_beta(
        beta: np.typing.ArrayLike
    ) -> np.typing.NDArray:
        beta = np.asarray(beta, dtype=float)

        return InfiniteReservoir.theta(beta)
    
    @staticmethod
    def get_theta(
        tD: np.typing.ArrayLike,
        rD: np.typing.ArrayLike,
    ) -> np.typing.NDArray:
        tD = PressureDistribution._set_times(tD)
        rD = PressureDistribution._set_nodes(rD)

        beta = InfiniteReservoir.beta(tD, rD)
        return InfiniteReservoir.theta(beta)