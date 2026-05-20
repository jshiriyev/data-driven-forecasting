import numpy as np
from numpy.testing import assert_allclose

import prodpy
from prodpy.utils import UnitConversion


def test_unit_conversion_is_exported_from_utils_and_top_level_package():
    assert prodpy.UnitConversion is UnitConversion


def test_mass_amount_force_and_time_constants():
    assert_allclose(UnitConversion.LBM_TO_KG, 0.45359237)
    assert_allclose(UnitConversion.LBMOL_TO_MOL, 453.59237)
    assert_allclose(UnitConversion.LBF_TO_N, 4.4482216152605)
    assert_allclose(UnitConversion.DAY_TO_SEC, 86400.0)


def test_pressure_viscosity_and_permeability_constants():
    assert_allclose(UnitConversion.CP_TO_PA_SEC, 0.001)
    assert_allclose(UnitConversion.PSI_TO_PA, 6894.757293168)
    assert_allclose(UnitConversion.MD_TO_FT2, 1.062314e-14)
    assert_allclose(UnitConversion.MD_TO_M2, 9.869233e-16)


def test_length_area_and_volume_constants():
    assert_allclose(UnitConversion.FT_TO_M, 0.3048)
    assert_allclose(UnitConversion.ACRE_TO_FT2, 43560.0)
    assert_allclose(UnitConversion.ACRE_TO_M2, 4046.8564224)
    assert_allclose(UnitConversion.BBL_TO_FT3, 5.614583333)
    assert_allclose(UnitConversion.BBL_TO_M3, 0.158987294928)


def test_fahrenheit_celsius_conversions_are_inverse_for_scalars():
    assert_allclose(UnitConversion.f_to_c(32.0), 0.0)
    assert_allclose(UnitConversion.f_to_c(212.0), 100.0)
    assert_allclose(UnitConversion.c_to_f(0.0), 32.0)
    assert_allclose(UnitConversion.c_to_f(100.0), 212.0)

    temperatures_f = np.array([-40.0, 32.0, 212.0])
    assert_allclose(UnitConversion.c_to_f(UnitConversion.f_to_c(temperatures_f)), temperatures_f)


def test_rankine_kelvin_conversions_are_inverse_for_scalars():
    assert_allclose(UnitConversion.r_to_k(491.67), 273.15)
    assert_allclose(UnitConversion.k_to_r(273.15), 491.67)

    temperatures_r = np.array([0.0, 491.67, 671.67])
    assert_allclose(UnitConversion.k_to_r(UnitConversion.r_to_k(temperatures_r)), temperatures_r)


def test_celsius_kelvin_conversions_are_inverse_for_scalars():
    assert_allclose(UnitConversion.c_to_k(0.0), 273.15)
    assert_allclose(UnitConversion.k_to_c(273.15), 0.0)
    assert_allclose(UnitConversion.c_to_k(100.0), 373.15)

    temperatures_c = np.array([-273.15, 0.0, 100.0])
    assert_allclose(UnitConversion.k_to_c(UnitConversion.c_to_k(temperatures_c)), temperatures_c)


def test_fahrenheit_rankine_conversions_are_inverse_for_scalars():
    assert_allclose(UnitConversion.f_to_r(32.0), 491.67)
    assert_allclose(UnitConversion.r_to_f(491.67), 32.0)
    assert_allclose(UnitConversion.f_to_r(212.0), 671.67)

    temperatures_f = np.array([-459.67, 32.0, 212.0])
    assert_allclose(UnitConversion.r_to_f(UnitConversion.f_to_r(temperatures_f)), temperatures_f)


def test_temperature_conversion_paths_are_consistent():
    temperatures_f = np.array([32.0, 122.0, 212.0])

    kelvin_from_fahrenheit = UnitConversion.c_to_k(UnitConversion.f_to_c(temperatures_f))
    kelvin_from_rankine = UnitConversion.r_to_k(UnitConversion.f_to_r(temperatures_f))

    assert_allclose(kelvin_from_fahrenheit, kelvin_from_rankine)
