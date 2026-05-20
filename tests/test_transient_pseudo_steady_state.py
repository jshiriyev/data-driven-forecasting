import numpy as np
import pytest

from prodpy import UnitConversion as uc
from prodpy.porsim.prerun import Borehole, Constraint
from prodpy.resprops import BlackOil, Fluid
from prodpy.transient import PseudoSteadyState


def _fluid_oil(*, rperm=1.0, satur=0.8, size=None):
    return Fluid(
        visc=1.0 if size is None else np.full(size, 1.0),
        rho=62.4 if size is None else np.full(size, 62.4),
        comp=1e-5 if size is None else np.full(size, 1e-5),
        satur=satur,
        rperm=rperm,
        size=size,
    )


def _fluid_water(*, rperm=0.0, satur=0.2, size=None):
    return Fluid(
        visc=1.0 if size is None else np.full(size, 1.0),
        rho=62.4 if size is None else np.full(size, 62.4),
        comp=3e-6 if size is None else np.full(size, 3e-6),
        satur=satur,
        rperm=rperm,
        size=size,
    )


def _solver(*, shape_key="circle_center", skin=0.0):
    solver = PseudoSteadyState(
        100.0,
        yperm=25.0,
        poro=0.2,
        comp=3e-6,
        area=640.0,
        height=20.0,
        shape_key=shape_key,
    )
    solver.fluid = BlackOil(
        oil=_fluid_oil(),
        water=_fluid_water(),
    )
    solver.pinit = 3000.0
    solver.tcomp = None
    solver.borehole = Borehole(
        radius=0.5,
        skin=skin,
        constraints=[Constraint(orate=1000.0)],
    )

    return solver


def _valid_time(solver):
    return max(2.0 * solver.tmin, 1e-9)


def test_pseudo_steady_state_solves_cylindrical_reservoir_pressure():
    solver = _solver(skin=2.0)
    time = _valid_time(solver)
    nodes = np.array([solver.borehole.radius, 10.0, solver.radius])

    solution = solver([time], nodes)

    tD = solver._dimensionless_radial_time(np.array([[time]]))
    rD = solver.nodes2rD(nodes)
    reD = solver._reservoir_radius_dimensionless()
    pD = PseudoSteadyState.prD(tD, rD, reD)
    pD[0, 0] += solver.borehole.skin
    expected = (solver._pinit - solver._pcons * pD) / uc.PSI_TO_PA

    assert solution.press.shape == (1, 3)
    assert np.allclose(solution.press, expected)
    assert solution.press[0, 0] < solution.press[0, -1]


def test_pseudo_steady_state_masks_times_before_shape_validity():
    solver = _solver()
    early = solver.tmin / 10.0
    valid = _valid_time(solver)

    solution = solver([early, valid], [solver.borehole.radius])

    assert np.isnan(solution.press[0, 0])
    assert np.isfinite(solution.press[1, 0])


def test_pseudo_steady_state_well_pressure_uses_shape_factor():
    solver = _solver(shape_key="square_center", skin=2.0)
    time = _valid_time(solver)

    solution = solver.well_pressure([time])

    tDA = solver.tDA(np.array([[time]]))
    pwD = PseudoSteadyState.pwD(
        tDA,
        solver.borehole._radius,
        solver._area,
        solver.shape_factor,
        skin=solver.borehole.skin,
    )
    expected = (solver._pinit - solver._pcons * pwD) / uc.PSI_TO_PA

    assert solution.nodes.item() == pytest.approx(solver.borehole.radius)
    assert solution.press.shape == (1, 1)
    assert solution.press[0, 0] == pytest.approx(expected.item())


def test_pseudo_steady_state_rejects_radial_distribution_for_shape_factor_geometry():
    solver = _solver(shape_key="square_center")

    with pytest.raises(ValueError, match="cylindrical reservoir"):
        solver([_valid_time(solver)], [solver.borehole.radius])


def test_pseudo_steady_state_rejects_array_effective_properties():
    solver = PseudoSteadyState(
        [100.0, 120.0],
        yperm=[25.0, 30.0],
        poro=[0.2, 0.25],
        comp=[3e-6, 4e-6],
        area=640.0,
        height=20.0,
    )
    solver.fluid = BlackOil(
        oil=_fluid_oil(
            rperm=[1.0, 1.0],
            satur=[0.8, 0.8],
            size=2,
        ),
        water=_fluid_water(
            rperm=[0.0, 0.0],
            satur=[0.2, 0.2],
            size=2,
        ),
    )
    solver.pinit = 3000.0
    solver.tcomp = None
    solver.borehole = Borehole(
        radius=0.5,
        constraints=[Constraint(orate=1000.0)],
    )

    with pytest.raises(ValueError, match="requires scalar analytical properties"):
        solver.well_pressure([1.0])
