import numpy as np
import pytest

from prodpy.porsim.prerun import Borehole, Constraint
from prodpy.resprops import BlackOil, Fluid
from prodpy.transient._infinite_acting import InfiniteActing


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


def _solver(*, skin=0.0):
    solver = InfiniteActing(
        100.0,
        yperm=25.0,
        poro=0.2,
        comp=3e-6,
        area=640.0,
        height=20.0,
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
    assert solver.tmin < solver.tmax
    return float(np.sqrt(solver.tmin * solver.tmax))


def test_infinite_acting_is_instantiable_and_solves_valid_times():
    solver = _solver()

    solution = solver([_valid_time(solver)], [0.5, 10.0])

    assert solution.press.shape == (1, 2)
    assert np.all(np.isfinite(solution.press))


def test_infinite_acting_masks_times_outside_validity_window_to_nan():
    solver = _solver()
    early = solver.tmin / 10.0
    valid = _valid_time(solver)
    late = solver.tmax * 2.0

    solution = solver([early, valid, late], [0.5, 10.0])

    assert np.all(np.isnan(solution.press[0, :]))
    assert np.all(np.isfinite(solution.press[1, :]))
    assert np.all(np.isnan(solution.press[2, :]))


@pytest.mark.parametrize("nodes", [[0.0], [-1.0], [0.25]])
def test_infinite_acting_rejects_nonphysical_nodes(nodes):
    solver = _solver()

    with pytest.raises(ValueError, match="nodes"):
        solver([_valid_time(solver)], nodes)


def test_infinite_acting_applies_skin_only_at_wellbore_radius():
    no_skin = _solver(skin=0.0)
    with_skin = _solver(skin=2.0)
    time = _valid_time(no_skin)
    nodes = [0.5, 10.0]

    base_press = no_skin([time], nodes).press
    skin_press = with_skin([time], nodes).press
    expected_wellbore_drop = float(np.asarray(with_skin.pcons).item()) * 2.0

    assert skin_press[0, 0] == pytest.approx(base_press[0, 0] - expected_wellbore_drop)
    assert skin_press[0, 1] == pytest.approx(base_press[0, 1])


def test_infinite_acting_rejects_array_effective_properties():
    solver = InfiniteActing(
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
        solver([1.0], [1.0])
