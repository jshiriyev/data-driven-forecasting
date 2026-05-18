import importlib.util
import math
from pathlib import Path

import pytest
from numpy.testing import assert_allclose


def _load_reservoir_domain_module():
    module_path = Path(__file__).parents[1] / "prodpy" / "transient" / "_reservoir_domain.py"
    spec = importlib.util.spec_from_file_location("reservoir_domain", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pm = _load_reservoir_domain_module()
ReservoirDomain = pm.ReservoirDomain
Boundary = pm.Boundary


def test_area_height_radius_and_volume_conversions():
    res = ReservoirDomain(1.0, 1.0)

    assert_allclose(res.area, 1.0)
    assert_allclose(res.height, 1.0)
    assert_allclose(res.radius_equivalent, math.sqrt(43560.0 / math.pi))
    assert_allclose(res.volume, 43560.0)


def test_radius_and_volume_recompute_after_area_or_height_change():
    res = ReservoirDomain(1.0, 1.0)

    res.area = 4.0
    assert_allclose(res.area, 4.0)
    assert_allclose(res.radius_equivalent, math.sqrt(4.0 * 43560.0 / math.pi))
    assert_allclose(res.volume, 4.0 * 43560.0)

    res.height = 2.0
    assert_allclose(res.height, 2.0)
    assert_allclose(res.volume, 4.0 * 43560.0 * 2.0)


@pytest.mark.parametrize("name", ["circle_center", "square_center", "strip_edge"])
def test_shape_key_uses_registered_boundary(name):
    res = ReservoirDomain(1.0, shape_key=name)

    assert res.shape_key == name
    assert res.shape == ReservoirDomain.SHAPE_FACTORS[name]
    assert res.shape_factor == ReservoirDomain.SHAPE_FACTORS[name].shape_factor


def test_available_shape_factors_returns_copy():
    shapes = ReservoirDomain.available_shape_factors()

    assert shapes == ReservoirDomain.SHAPE_FACTORS
    assert shapes is not ReservoirDomain.SHAPE_FACTORS
    assert isinstance(shapes["circle_center"], Boundary)


def test_custom_shape_factor():
    res = ReservoirDomain(
        1.0,
        shape_factor=12.3,
        tDA_infinite_acting_end=0.2,
        tDA_pss_start=0.4,
        note="custom boundary",
    )

    assert res.shape_key == "custom"
    assert_allclose(res.shape_factor, 12.3)
    assert res.shape.tDA_infinite_acting_end == 0.2
    assert res.shape.tDA_pss_start == 0.4
    assert res.shape.note == "custom boundary"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("area", 0),
        ("area", -1),
        ("area", float("nan")),
        ("area", float("inf")),
        ("area", "not-a-number"),
        ("height", 0),
        ("height", -1),
        ("height", float("nan")),
        ("height", float("inf")),
        ("height", "not-a-number"),
    ],
)
def test_area_and_height_reject_invalid_values(field, value):
    kwargs = {"area": 1.0, "height": 1.0}
    kwargs[field] = value

    with pytest.raises(ValueError, match=f"{field} must be a positive finite value"):
        ReservoirDomain(kwargs["area"], kwargs["height"])


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), "not-a-number"])
def test_custom_shape_factor_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="shape factor must be a positive finite value"):
        ReservoirDomain(1.0, shape_factor=value)


def test_numeric_strings_are_normalized_to_floats():
    res = ReservoirDomain("2", "3", shape_factor="4")

    assert_allclose(res.area, 2.0)
    assert_allclose(res.height, 3.0)
    assert_allclose(res.shape_factor, 4.0)


def test_repr_for_registered_shape_uses_public_units_and_shape_key():
    res = ReservoirDomain(2.0, 3.0, shape_key="square_center")

    assert repr(res) == "ReservoirDomain(reservoir_area=2.0 acres, payzone_height=3.0 ft, shape_key='square_center')"


def test_repr_for_custom_shape_includes_boundary_metadata():
    res = ReservoirDomain(
        2.0,
        3.0,
        shape_factor=12.3,
        tDA_infinite_acting_end=0.2,
        tDA_pss_start=0.4,
        note="custom boundary",
    )

    assert repr(res) == (
        "ReservoirDomain(reservoir_area=2.0 acres, payzone_height=3.0 ft, shape_factor=12.3, "
        "tDA_infinite_acting_end=0.2, tDA_pss_start=0.4, "
        "note='custom boundary')"
    )


def test_unknown_shape_key_raises_key_error():
    with pytest.raises(KeyError, match="Unknown shape_key"):
        ReservoirDomain(1.0, shape_key="unknown")


def test_setting_invalid_area_or_height_after_init_raises():
    res = ReservoirDomain(1.0, 1.0)

    with pytest.raises(ValueError, match="area must be a positive finite value"):
        res.area = -1

    with pytest.raises(ValueError, match="height must be a positive finite value"):
        res.height = 0
