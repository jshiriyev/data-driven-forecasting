import numpy as np
import pytest
from numpy.testing import assert_allclose

from prodpy import UnitConversion as uc
from prodpy.resprops import BlackOil, Fluid


def _fluid(visc=1.0, *, press=None, satur=0.0, comp=None, size=None):
    return Fluid(visc=visc, press=press, satur=satur, comp=comp, size=size)


def test_black_oil_is_exported_from_resprops():
    from prodpy import resprops

    assert resprops.BlackOil is BlackOil


def test_black_oil_requires_fluid_phase_objects():
    oil = _fluid(satur=0.6)
    gas = _fluid(satur=0.1)
    water = _fluid(satur=0.2)

    with pytest.raises(TypeError, match="oil must be a Fluid instance"):
        BlackOil(object(), gas, water)

    with pytest.raises(TypeError, match="gas must be a Fluid instance"):
        BlackOil(oil, object(), water)

    with pytest.raises(TypeError, match="water must be a Fluid instance"):
        BlackOil(oil, gas, object())


def test_saturations_are_exposed_and_sum_may_be_less_than_or_equal_to_one():
    oil = _fluid(satur=[0.6, 0.5], size=2)
    gas = _fluid(satur=[0.1, 0.2], size=2)
    water = _fluid(satur=[0.2, 0.3], size=2)

    system = BlackOil(oil, gas, water)

    assert system.oil is oil
    assert system.gas is gas
    assert system.water is water

    assert_allclose(system.so, [0.6, 0.5])
    assert_allclose(system.sg, [0.1, 0.2])
    assert_allclose(system.sw, [0.2, 0.3])
    assert_allclose(system.total_saturation, [0.9, 1.0])

    assert system.satur == {
        "oil": oil.satur,
        "gas": gas.satur,
        "water": water.satur,
    }


def test_black_oil_supports_oil_water_two_phase_system():
    oil = _fluid(press=3000.0, satur=0.7)
    water = _fluid(press=2800.0, satur=0.2)

    system = BlackOil(oil=oil, water=water)

    assert system.oil is oil
    assert system.gas is None
    assert system.water is water
    assert_allclose(system.total_saturation, [0.9])
    assert_allclose(system.pcow, [200.0])
    assert system.pcgo is None
    assert system.pcgw is None
    assert system.sg is None
    assert system.satur["gas"] is None
    assert system.phases == {"oil": oil, "water": water}


def test_black_oil_supports_gas_water_two_phase_system():
    gas = _fluid(press=3200.0, satur=0.3)
    water = _fluid(press=2800.0, satur=0.6)

    system = BlackOil(gas=gas, water=water)

    assert system.oil is None
    assert system.gas is gas
    assert system.water is water
    assert_allclose(system.total_saturation, [0.9])
    assert system.pcow is None
    assert system.pcgo is None
    assert_allclose(system.pcgw, [400.0])
    assert system.so is None
    assert system.satur["oil"] is None
    assert system.phases == {"gas": gas, "water": water}


def test_black_oil_supports_gas_oil_two_phase_system():
    oil = _fluid(press=3000.0, satur=0.6)
    gas = _fluid(press=3200.0, satur=0.3)

    system = BlackOil(oil=oil, gas=gas)

    assert system.oil is oil
    assert system.gas is gas
    assert system.water is None
    assert_allclose(system.total_saturation, [0.9])
    assert system.pcow is None
    assert_allclose(system.pcgo, [200.0])
    assert system.pcgw is None
    assert system.sw is None
    assert system.satur["water"] is None
    assert system.phases == {"oil": oil, "gas": gas}


def test_has_phase_reports_defined_and_missing_phases():
    oil = _fluid(press=3000.0, satur=0.6)
    gas = _fluid(press=3200.0, satur=0.3)

    system = BlackOil(oil=oil, gas=gas)

    assert system.has_phase("oil") is True
    assert system.has_phase("gas") is True
    assert system.has_phase("water") is False

    system.water = _fluid(press=2800.0, satur=0.1)

    assert system.has_phase("water") is True


def test_has_phase_rejects_unknown_phase_name():
    oil = _fluid(press=3000.0, satur=1.0)
    system = BlackOil(oil=oil)

    with pytest.raises(ValueError, match="phase must be one of"):
        system.has_phase("condensate")


def test_black_oil_supports_oil_only_single_phase_system_when_saturation_is_one():
    oil = _fluid(press=3000.0, satur=1.0)

    system = BlackOil(oil=oil)

    assert system.oil is oil
    assert system.gas is None
    assert system.water is None
    assert_allclose(system.total_saturation, [1.0])
    assert system.pcow is None
    assert system.pcgo is None
    assert system.pcgw is None
    assert system.phases == {"oil": oil}


def test_black_oil_supports_gas_only_single_phase_system_when_saturation_is_one():
    gas = _fluid(press=3200.0, satur=1.0)

    system = BlackOil(gas=gas)

    assert system.oil is None
    assert system.gas is gas
    assert system.water is None
    assert_allclose(system.total_saturation, [1.0])
    assert system.pcow is None
    assert system.pcgo is None
    assert system.pcgw is None
    assert system.phases == {"gas": gas}


def test_black_oil_supports_water_only_single_phase_system_when_saturation_is_one():
    water = _fluid(press=2800.0, satur=1.0)

    system = BlackOil(water=water)

    assert system.oil is None
    assert system.gas is None
    assert system.water is water
    assert_allclose(system.total_saturation, [1.0])
    assert system.pcow is None
    assert system.pcgo is None
    assert system.pcgw is None
    assert system.phases == {"water": water}


def test_single_phase_system_requires_saturation_equal_to_one():
    oil = _fluid(satur=0.6)

    with pytest.raises(ValueError, match="single-phase saturation must be equal to 1"):
        BlackOil(oil=oil)


def test_black_oil_requires_at_least_one_phase():
    with pytest.raises(ValueError, match="requires at least one phase"):
        BlackOil()


def test_saturation_validation_rejects_total_above_one():
    oil = _fluid(satur=0.7)
    gas = _fluid(satur=0.2)
    water = _fluid(satur=0.2)

    with pytest.raises(ValueError, match="cannot sum to more than 1"):
        BlackOil(oil, gas, water)


def test_saturation_validation_allows_nan_unknowns():
    oil = _fluid(satur=[0.6, np.nan], size=2)
    gas = _fluid(satur=[0.1, 0.2], size=2)
    water = _fluid(satur=[0.2, 0.3], size=2)

    system = BlackOil(oil, gas, water)

    assert_allclose(system.total_saturation, [0.9, np.nan], equal_nan=True)


def test_saturation_validation_rejects_incompatible_shapes():
    oil = _fluid(satur=[0.6, 0.5])
    gas = _fluid(satur=[0.1, 0.2, 0.3])
    water = _fluid(satur=0.1)

    with pytest.raises(ValueError, match="saturation arrays must be broadcast-compatible"):
        BlackOil(oil, gas, water)


def test_replacing_phase_validates_saturation_sum_and_rolls_back_on_failure():
    oil = _fluid(satur=0.6)
    gas = _fluid(satur=0.1)
    water = _fluid(satur=0.2)
    system = BlackOil(oil, gas, water)

    replacement = _fluid(satur=0.5)

    with pytest.raises(ValueError, match="cannot sum to more than 1"):
        system.water = replacement

    assert system.water is water
    assert_allclose(system.total_saturation, [0.9])


def test_replacing_phase_allows_valid_transition_to_single_phase_state():
    oil = _fluid(satur=0.6)
    gas = _fluid(satur=0.1)
    water = _fluid(satur=0.2)
    system = BlackOil(oil, gas, water)

    system.gas = None

    assert system.gas is None
    assert system.phases == {"oil": oil, "water": water}
    assert_allclose(system.total_saturation, [0.8])

    oil.satur = 1.0
    system.water = None

    assert system.water is None
    assert system.phases == {"oil": oil}
    assert_allclose(system.total_saturation, [1.0])


def test_replacing_phase_rolls_back_when_single_phase_saturation_is_not_one():
    oil = _fluid(satur=0.6)
    water = _fluid(satur=0.2)
    system = BlackOil(oil=oil, water=water)

    with pytest.raises(ValueError, match="single-phase saturation must be equal to 1"):
        system.water = None

    assert system.water is water
    assert system.phases == {"oil": oil, "water": water}


def test_capillary_pressure_equations_use_public_psi_units():
    oil = _fluid(press=[3000.0, 2900.0], satur=[0.6, 0.5], size=2)
    gas = _fluid(press=[3200.0, 3000.0], satur=[0.1, 0.2], size=2)
    water = _fluid(press=[2800.0, 2700.0], satur=[0.2, 0.3], size=2)

    system = BlackOil(oil, gas, water)

    assert_allclose(system.pcow, [200.0, 200.0])
    assert_allclose(system.pcgo, [200.0, 100.0])
    assert_allclose(system.pcgw, [400.0, 300.0])

    assert_allclose(system._pcow, np.array([200.0, 200.0]) * uc.PSI_TO_PA)
    assert_allclose(system._pcgo, np.array([200.0, 100.0]) * uc.PSI_TO_PA)
    assert_allclose(system._pcgw, np.array([400.0, 300.0]) * uc.PSI_TO_PA)


def test_capillary_pressure_returns_none_when_required_phase_pressure_is_missing():
    oil = _fluid(press=3000.0, satur=0.6)
    gas = _fluid(press=3200.0, satur=0.1)
    water = _fluid(press=None, satur=0.2)

    system = BlackOil(oil, gas, water)

    assert system.pcow is None
    assert system._pcow is None
    assert_allclose(system.pcgo, [200.0])
    assert system.pcgw is None
    assert system._pcgw is None


def test_capillary_pressure_rejects_incompatible_pressure_shapes():
    oil = _fluid(press=[3000.0, 2900.0], satur=0.6)
    gas = _fluid(press=3200.0, satur=0.1)
    water = _fluid(press=[2800.0, 2700.0, 2600.0], satur=0.2)

    system = BlackOil(oil, gas, water)

    with pytest.raises(ValueError, match="oil and water pressure arrays must be broadcast-compatible"):
        _ = system.pcow


def test_single_phase_compressibility_is_phase_saturation_weighted_value():
    oil = _fluid(satur=1.0, comp=1e-6)

    system = BlackOil(oil=oil)

    assert_allclose(system.comp, [1e-6])
    assert_allclose(system._comp, np.array([1e-6]) / uc.PSI_TO_PA)


def test_two_phase_compressibility_is_saturation_weighted_sum():
    oil = _fluid(satur=0.7, comp=1e-6)
    water = _fluid(satur=0.2, comp=3e-6)

    system = BlackOil(oil=oil, water=water)

    expected = 0.7 * 1e-6 + 0.2 * 3e-6

    assert_allclose(system.comp, [expected])
    assert_allclose(system._comp, np.array([expected]) / uc.PSI_TO_PA)


def test_three_phase_compressibility_supports_array_saturations_and_compressibilities():
    oil = _fluid(satur=[0.6, 0.5], comp=[1e-6, 2e-6], size=2)
    gas = _fluid(satur=[0.1, 0.2], comp=[10e-6, 20e-6], size=2)
    water = _fluid(satur=[0.2, 0.3], comp=[3e-6, 4e-6], size=2)

    system = BlackOil(oil, gas, water)

    expected = (
        np.array([0.6, 0.5]) * np.array([1e-6, 2e-6])
        + np.array([0.1, 0.2]) * np.array([10e-6, 20e-6])
        + np.array([0.2, 0.3]) * np.array([3e-6, 4e-6])
    )

    assert_allclose(system.comp, expected)
    assert_allclose(system._comp, expected / uc.PSI_TO_PA)


def test_compressibility_returns_none_when_present_phase_compressibility_is_missing():
    oil = _fluid(satur=0.7, comp=1e-6)
    water = _fluid(satur=0.2, comp=None)

    system = BlackOil(oil=oil, water=water)

    assert system.comp is None
    assert system._comp is None


def test_compressibility_rejects_incompatible_phase_compressibility_shapes():
    oil = _fluid(satur=0.6, comp=[1e-6, 2e-6])
    water = _fluid(satur=0.2, comp=[3e-6, 4e-6, 5e-6])

    system = BlackOil(oil=oil, water=water)

    with pytest.raises(ValueError, match="compressibility arrays must be broadcast-compatible"):
        _ = system.comp


def test_saturation_tolerance_must_be_non_negative_and_finite():
    oil = _fluid(satur=0.6)
    gas = _fluid(satur=0.1)
    water = _fluid(satur=0.2)

    with pytest.raises(ValueError, match="non-negative finite"):
        BlackOil(oil, gas, water, saturation_tolerance=-1.0)

    with pytest.raises(ValueError, match="non-negative finite"):
        BlackOil(oil, gas, water, saturation_tolerance=np.inf)
