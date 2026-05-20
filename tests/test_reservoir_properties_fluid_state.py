import numpy as np
from numpy.testing import assert_allclose

import pytest

from scipy import constants

from prodpy.resprops import Fluid
from prodpy import UnitConversion as uc

def test_oilfield_units_and_si_storage():
    fluid = Fluid(
        visc=[2.0, 4.0],
        rho=[62.4, 70.0],
        comp=[1e-6, 2e-6],
        fvf=[1.2, 1.4],
        press=[3000.0, 3500.0],
        satur=[0.7, 0.8],
        rperm=[0.6, 0.4],
        size=2,
    )

    assert_allclose(fluid.visc, [2.0, 4.0])
    assert_allclose(fluid.rho, [62.4, 70.0])
    assert_allclose(fluid.comp, [1e-6, 2e-6])
    assert_allclose(fluid.fvf, [1.2, 1.4])
    assert_allclose(fluid.press, [3000.0, 3500.0])
    assert_allclose(fluid.satur, [0.7, 0.8])
    assert_allclose(fluid.rperm, [0.6, 0.4])

    assert_allclose(fluid._visc, np.array([2.0, 4.0]) * uc.CP_TO_PA_SEC)
    assert_allclose(fluid._rho, np.array([62.4, 70.0]) * uc.LBM_TO_KG / uc.FT_TO_M**3)
    assert_allclose(fluid._comp, np.array([1e-6, 2e-6]) / uc.PSI_TO_PA)
    assert_allclose(fluid._press, np.array([3000.0, 3500.0]) * uc.PSI_TO_PA)


def test_default_properties():
    fluid = Fluid()

    assert fluid.visc is None
    assert fluid._visc is None
    assert fluid.rho is None
    assert fluid._rho is None
    assert fluid.comp is None
    assert fluid._comp is None
    assert fluid.grad is None
    assert fluid._grad is None
    assert fluid.mobil is None
    assert fluid._mobil is None
    assert_allclose(fluid.fvf, [1.0])
    assert fluid.press is None
    assert_allclose(fluid.satur, [1.0])
    assert_allclose(fluid.rperm, [1.0])


def test_viscosity_is_keyword_only():
    with pytest.raises(TypeError):
        Fluid(2.0)


def test_viscosity_can_be_cleared_after_assignment():
    fluid = Fluid(visc=2.0)

    assert_allclose(fluid.visc, [2.0])
    assert_allclose(fluid.mobil, [0.5])

    fluid.visc = None

    assert fluid.visc is None
    assert fluid._visc is None
    assert fluid.mobil is None
    assert fluid._mobil is None


def test_gradient_and_mobility_are_computed_from_current_state():
    fluid = Fluid(visc=2.0, rho=62.4, fvf=1.0, rperm=1.0)

    assert_allclose(fluid._grad, fluid._rho * constants.g)
    assert_allclose(fluid.grad, fluid._grad * uc.FT_TO_M / uc.PSI_TO_PA)
    assert_allclose(fluid._mobil, fluid._rperm / (fluid._visc * fluid._fvf))
    assert_allclose(fluid.mobil, [0.5])

    fluid.rho = 70.0
    fluid.visc = 4.0
    fluid.fvf = 2.0
    fluid.rperm = 0.5

    assert_allclose(fluid.grad, fluid._grad * uc.FT_TO_M / uc.PSI_TO_PA)
    assert_allclose(fluid.mobil, [0.0625])


def test_array_mobility_broadcasts_scalar_default_properties():
    fluid = Fluid(visc=[1.0, 2.0, 4.0])

    assert fluid.rho is None
    assert_allclose(fluid.mobil, [1.0, 0.5, 0.25])


def test_size_validates_array_lengths_without_expanding_scalars():
    fluid = Fluid(visc=[1.0, 2.0, 3.0], rho=60.0, size=3)

    assert_allclose(fluid.visc, [1.0, 2.0, 3.0])
    assert_allclose(fluid.rho, [60.0])

    with pytest.raises(ValueError, match="rho must be scalar or have length 3"):
        Fluid(visc=[1.0, 2.0, 3.0], rho=[60.0, 70.0], size=3)


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: Fluid(visc=0.0), "visc cannot be smaller than or equal to 0"),
        (lambda: Fluid(visc=-1.0), "visc cannot be smaller than or equal to 0"),
        (lambda: Fluid(visc=1.0, rho=0.0), "rho cannot be smaller than or equal to 0"),
        (lambda: Fluid(visc=1.0, rho=-1.0), "rho cannot be smaller than or equal to 0"),
        (lambda: Fluid(visc=1.0, fvf=0.0), "fvf cannot be smaller than or equal to 0"),
        (lambda: Fluid(visc=1.0, fvf=-1.0), "fvf cannot be smaller than or equal to 0"),
        (lambda: Fluid(visc=1.0, comp=-1e-6), "comp cannot be smaller than 0"),
        (lambda: Fluid(visc=1.0, press=-100.0), "press cannot be smaller than 0"),
        (lambda: Fluid(visc=1.0, satur=-0.1), "satur cannot be smaller than 0"),
        (lambda: Fluid(visc=1.0, satur=1.1), "satur cannot be larger than 1"),
        (lambda: Fluid(visc=1.0, rperm=-0.1), "rperm cannot be smaller than 0"),
        (lambda: Fluid(visc=1.0, rperm=1.1), "rperm cannot be larger than 1"),
    ],
)
def test_invalid_physical_ranges_are_rejected(factory, message):
    with pytest.raises(ValueError, match=message):
        factory()


def test_zero_comp_press_satur_and_rperm_bounds_are_accepted():
    fluid = Fluid(visc=1.0, comp=0.0, press=0.0, satur=0.0, rperm=0.0)

    assert_allclose(fluid.comp, [0.0])
    assert_allclose(fluid.press, [0.0])
    assert_allclose(fluid.satur, [0.0])
    assert_allclose(fluid.rperm, [0.0])

    fluid.satur = 1.0
    fluid.rperm = 1.0

    assert_allclose(fluid.satur, [1.0])
    assert_allclose(fluid.rperm, [1.0])


def test_density_and_compressibility_can_be_cleared_after_assignment():
    fluid = Fluid(visc=1.0, rho=62.4, comp=1e-6)

    assert_allclose(fluid.rho, [62.4])
    assert_allclose(fluid.comp, [1e-6])
    assert fluid.grad is not None

    fluid.rho = None
    fluid.comp = None

    assert fluid.rho is None
    assert fluid._rho is None
    assert fluid.grad is None
    assert fluid._grad is None
    assert fluid.comp is None
    assert fluid._comp is None


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Fluid(visc=[]),
        lambda: Fluid(visc=1.0, rho=[]),
        lambda: Fluid(visc=1.0, comp=[]),
        lambda: Fluid(visc=1.0, fvf=[]),
        lambda: Fluid(visc=1.0, press=[]),
        lambda: Fluid(visc=1.0, satur=[]),
        lambda: Fluid(visc=1.0, rperm=[]),
    ],
)
def test_empty_values_are_rejected(factory):
    with pytest.raises(ValueError, match="cannot be empty"):
        factory()


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Fluid(visc=float("inf")),
        lambda: Fluid(visc=float("-inf")),
        lambda: Fluid(visc=1.0, rho=float("inf")),
        lambda: Fluid(visc=1.0, comp=float("-inf")),
        lambda: Fluid(visc=1.0, fvf=float("inf")),
        lambda: Fluid(visc=1.0, press=float("-inf")),
        lambda: Fluid(visc=1.0, satur=float("inf")),
        lambda: Fluid(visc=1.0, rperm=float("-inf")),
    ],
)
def test_infinite_values_are_rejected(factory):
    with pytest.raises(ValueError, match="must not contain positive or negative infinity"):
        factory()


def test_nan_values_are_accepted():
    fluid = Fluid(
        visc=[1.0, np.nan],
        rho=[60.0, np.nan],
        comp=[1e-6, np.nan],
        fvf=[1.0, np.nan],
        press=[3000.0, np.nan],
        satur=[0.5, np.nan],
        rperm=[0.25, np.nan],
        size=2,
    )

    assert_allclose(fluid.visc, [1.0, np.nan], equal_nan=True)
    assert_allclose(fluid.rho, [60.0, np.nan], equal_nan=True)
    assert_allclose(fluid.comp, [1e-6, np.nan], equal_nan=True)
    assert_allclose(fluid.fvf, [1.0, np.nan], equal_nan=True)
    assert_allclose(fluid.press, [3000.0, np.nan], equal_nan=True)
    assert_allclose(fluid.satur, [0.5, np.nan], equal_nan=True)
    assert_allclose(fluid.rperm, [0.25, np.nan], equal_nan=True)
    assert_allclose(fluid.grad, [fluid.grad[0], np.nan], equal_nan=True)
    assert_allclose(fluid.mobil, [0.25, np.nan], equal_nan=True)


def test_invalid_size_is_rejected():
    with pytest.raises(ValueError, match="size must be a positive integer"):
        Fluid(visc=1.0, size=0)


def test_non_numeric_values_are_rejected():
    with pytest.raises(TypeError, match="visc must be convertible to a float array"):
        Fluid(visc="heavy")
