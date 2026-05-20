import numpy as np
import pytest

from prodpy.porsim.prerun import Borehole, Constraint
from prodpy.resprops import BlackOil, Fluid
from prodpy.transient._base_solver import BaseSolver


class DummySolver(BaseSolver):
    def __call__(self, times, nodes):
        return super().__call__(times, nodes)

    def _evaluate(self, solution):
        return solution


def _oil(*, rperm=1.0, satur=0.8):
    return Fluid(
        visc=1.0,
        rho=62.4,
        comp=1e-5,
        satur=satur,
        rperm=rperm,
    )


def _water(*, rperm=0.0, satur=0.2):
    return Fluid(
        visc=1.0,
        rho=62.4,
        comp=3e-6,
        satur=satur,
        rperm=rperm,
    )


def _solver(fluid=None, constraints=None):
    solver = DummySolver(
        100.0,
        yperm=25.0,
        poro=0.2,
        comp=3e-6,
        area=10.0,
        height=20.0,
    )
    solver.fluid = fluid or BlackOil(oil=_oil(), water=_water())
    solver.pinit = 3000.0
    solver.tcomp = None
    solver.borehole = Borehole(
        radius=0.5,
        constraints=constraints or [Constraint(orate=1000.0)],
    )

    return solver


def test_base_solver_prepares_solution_for_single_mobile_oil_phase():
    solver = _solver()

    solution = solver([1.0, 2.0], [1.0, 10.0])

    assert solver.mobile_phase_name == "oil"
    assert solver.rate == pytest.approx(1000.0)
    assert np.all(np.asarray(solver._hdiff) > 0.0)
    assert solution.times.size == 2
    assert solution.nodes.size == 2


def test_base_solver_uses_radial_permeability_perpendicular_to_borehole_axis():
    solver = _solver()

    assert solver.borehole.axis == "z"
    assert solver.radial_permeability == pytest.approx(np.sqrt(100.0 * 25.0))


def test_base_solver_dimensionless_radius_roundtrip():
    solver = _solver()
    nodes = np.array([0.5, 10.0])

    assert np.allclose(solver.rD2nodes(solver.nodes2rD(nodes)), nodes)


def test_base_solver_rejects_non_oil_rate_constraint():
    solver = _solver(constraints=[Constraint(press=3000.0)])

    with pytest.raises(ValueError, match="oil-rate-controlled"):
        solver([1.0], [1.0])


def test_base_solver_rejects_multiple_borehole_constraints():
    solver = _solver(
        constraints=[
            Constraint(start=0.0, stop=10.0, orate=1000.0),
            Constraint(start=10.0, orate=800.0),
        ],
    )

    with pytest.raises(ValueError, match="exactly one borehole constraint"):
        solver([1.0], [1.0])


def test_base_solver_rejects_multiple_mobile_phases():
    solver = _solver(fluid=BlackOil(oil=_oil(), water=_water(rperm=1.0)))

    with pytest.raises(ValueError, match="exactly one mobile phase"):
        solver([1.0], [1.0])


def test_base_solver_rejects_non_oil_mobile_phase():
    solver = _solver(
        fluid=BlackOil(
            oil=_oil(rperm=0.0, satur=0.8),
            water=_water(rperm=1.0, satur=0.2),
        )
    )

    with pytest.raises(ValueError, match="must be 'oil'"):
        solver([1.0], [1.0])


def test_base_solver_manages_boundaries():
    solver = _solver()

    boundary = solver.add_boundary("xmin", press=2500.0)

    assert solver.boundaries == (boundary,)
    assert solver.active_boundaries(0.0) == (boundary,)

    solver.clear_boundaries()

    assert solver.boundaries == ()
