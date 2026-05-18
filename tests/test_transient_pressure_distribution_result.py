import importlib.util
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose


def _load_pressure_distribution_module():
    module_path = (
        Path(__file__).parents[1]
        / "prodpy"
        / "transient"
        / "_pressure_distribution.py"
    )
    spec = importlib.util.spec_from_file_location("pressure_distribution", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pm = _load_pressure_distribution_module()
PressureDistribution = pm.PressureDistribution


def test_constructor_stores_axes_in_si_units_with_time_major_shape():
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0, 30.0]))

    assert result._times.shape == (2, 1)
    assert result._nodes.shape == (1, 3)
    assert result._press.shape == (2, 3)

    assert_allclose(result._times, [[86400.0], [172800.0]])
    assert_allclose(result._nodes, [[3.048, 6.096, 9.144]])

    assert_allclose(result.times, [[1.0], [2.0]])
    assert_allclose(result.nodes, [[10.0, 20.0, 30.0]])


@pytest.mark.parametrize(
    ("times", "nodes", "message"),
    [
        (1.0, np.array([10.0]), "times must be array-like"),
        (np.array([1.0]), 10.0, "nodes must be array-like"),
        (np.array([]), np.array([10.0]), "times cannot be empty"),
        (np.array([1.0]), np.array([]), "nodes cannot be empty"),
    ],
)
def test_constructor_rejects_invalid_axes(times, nodes, message):
    with pytest.raises((TypeError, ValueError), match=message):
        PressureDistribution(times, nodes)


def test_internal_arrays_are_read_only_and_cannot_be_replaced():
    result = PressureDistribution(np.array([1.0]), np.array([10.0, 20.0]))

    assert not result._times.flags.writeable
    assert not result._nodes.flags.writeable
    assert not result._press.flags.writeable

    with pytest.raises(ValueError, match="read-only"):
        result._press[0, 0] = 1.0

    with pytest.raises(AttributeError, match="_press is immutable"):
        result._press = np.zeros((1, 2))

    with pytest.raises(AttributeError, match="_times is immutable"):
        result._times = np.zeros((1, 1))

    with pytest.raises(AttributeError, match="_nodes is immutable"):
        result._nodes = np.zeros((1, 2))


def test_set_pressure_at_time_defaults_to_psi_and_updates_one_row():
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0, 30.0]))

    result.set_pressure_at_time(1.0, np.array([1000.0, 900.0, 800.0]))

    assert_allclose(result._press[0], np.array([1000.0, 900.0, 800.0]) * result.PSI_TO_PA)
    assert_allclose(result.press[0], [1000.0, 900.0, 800.0])


def test_set_pressure_at_time_accepts_si_pressure_values_when_requested():
    result = PressureDistribution(np.array([1.0]), np.array([10.0, 20.0, 30.0]))
    pressures_pa = np.array([[7_000_000.0], [6_000_000.0], [5_000_000.0]])

    result.set_pressure_at_time(1.0, pressures_pa, si_unit_flag=True)

    assert_allclose(result._press[0], pressures_pa.ravel())
    assert_allclose(result.press[0], pressures_pa.ravel() / result.PSI_TO_PA)


def test_set_pressure_at_time_uses_tolerance_when_matching_time():
    result = PressureDistribution(np.array([1.0]), np.array([10.0, 20.0]))

    result.set_pressure_at_time(1.0 + 1e-12, np.array([1000.0, 900.0]))

    assert_allclose(result.press[0], [1000.0, 900.0])


@pytest.mark.parametrize(
    ("time", "values", "message"),
    [
        (3.0, np.array([1000.0, 900.0]), "time 3.0 days is not present"),
        (np.nan, np.array([1000.0, 900.0]), "time must be a finite value"),
        (1.0, np.array([1000.0]), "expected 2, got 1"),
        (1.0, np.array([]), "values cannot be empty"),
    ],
)
def test_set_pressure_at_time_rejects_invalid_inputs(time, values, message):
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0]))

    with pytest.raises(ValueError, match=message):
        result.set_pressure_at_time(time, values)


def test_set_pressure_at_time_rejects_ambiguous_duplicate_time_matches():
    result = PressureDistribution(np.array([1.0, 1.0 + 1e-12]), np.array([10.0, 20.0]))

    with pytest.raises(ValueError, match="matches multiple stored times"):
        result.set_pressure_at_time(1.0, np.array([1000.0, 900.0]))


def test_set_pressure_defaults_to_psi_and_updates_full_matrix_in_place():
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0, 30.0]))
    pressures = np.array([
        [1000.0, 900.0, 800.0],
        [950.0, 850.0, 750.0],
    ])
    press_id = id(result._press)

    result.set_pressure(pressures)

    assert id(result._press) == press_id
    assert not result._press.flags.writeable
    assert_allclose(result.press, pressures)
    assert_allclose(result._press, pressures * result.PSI_TO_PA)


def test_set_pressure_accepts_si_pressure_matrix_when_requested():
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0]))
    pressures_pa = np.array([
        [7_000_000.0, 6_000_000.0],
        [5_000_000.0, 4_000_000.0],
    ])

    result.set_pressure(pressures_pa, si_unit_flag=True)

    assert_allclose(result._press, pressures_pa)
    assert_allclose(result.press, pressures_pa / result.PSI_TO_PA)


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (np.array([1000.0, 900.0, 800.0]), "two-dimensional"),
        (
            np.array([[[1000.0, 900.0, 800.0]]]),
            "two-dimensional",
        ),
        (
            np.array([[1000.0, 900.0], [950.0, 850.0]]),
            r"values shape must match pressure shape \(2, 3\); got \(2, 2\)",
        ),
    ],
)
def test_set_pressure_rejects_non_2d_or_wrong_shape_values(values, message):
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0, 30.0]))

    with pytest.raises(ValueError, match=message):
        result.set_pressure(values)


def test_repr_uses_public_units_and_summarizes_pressure_shape():
    result = PressureDistribution(np.array([1.0, 2.0]), np.array([10.0, 20.0, 30.0]))

    assert repr(result) == (
        "PressureDistribution(times=np.array([1., 2.]) days, "
        "nodes=np.array([10., 20., 30.]) ft, press_shape=(2, 3))"
    )


def test_plot_time_indices_include_all_times_when_not_exceeding_limit():
    result = PressureDistribution(np.arange(5.0), np.array([10.0, 20.0]))

    assert_allclose(result._plot_time_indices(max_lines=10), np.arange(5))


def test_plot_time_indices_uniformly_select_at_most_limit_and_include_edges():
    result = PressureDistribution(np.arange(25.0), np.array([10.0, 20.0]))

    indices = result._plot_time_indices(max_lines=10)

    assert indices.size == 10
    assert indices[0] == 0
    assert indices[-1] == 24
    assert_allclose(indices, [0, 3, 5, 8, 11, 13, 16, 19, 21, 24])


def test_plot_rejects_invalid_max_lines():
    result = PressureDistribution(np.arange(5.0), np.array([10.0, 20.0]))

    with pytest.raises(ValueError, match="max_lines must be at least 2"):
        result.plot(max_lines=1)


def test_plot_draws_selected_pressure_rows_with_oilfield_unit_labels():
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    result = PressureDistribution(np.arange(12.0), np.array([10.0, 20.0, 30.0]))

    for time in result.times.ravel():
        result.set_pressure_at_time(time, np.array([1000.0, 900.0, 800.0]) - time)

    fig, ax = plt.subplots()
    try:
        returned_ax = result.plot(ax=ax)

        assert returned_ax is ax
        assert len(ax.lines) == 10
        assert ax.get_xlabel() == "Node position, ft"
        assert ax.get_ylabel() == "Pressure, psi"

        labels = [text.get_text() for text in ax.get_legend().get_texts()]
        assert labels[0] == "t = 0 days"
        assert labels[-1] == "t = 11 days"
    finally:
        plt.close(fig)
