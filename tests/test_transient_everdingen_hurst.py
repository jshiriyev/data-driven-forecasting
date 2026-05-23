import pytest

from prodpy.transient import EverdingenHurst
from prodpy.transient import _everdingen_hurst as eh


def _patch_inverse(monkeypatch):
    calls = []

    def fake_inverse(func, t, degree=12, **kwargs):
        call = {
            "func": func,
            "t": t,
            "degree": degree,
            "kwargs": kwargs,
        }
        calls.append(call)
        return call

    monkeypatch.setattr(eh, "_inverse_laplace_stehfest", fake_inverse)

    return calls


def test_pD_routes_infinite_boundary_to_constant_rate_pressure(monkeypatch):
    _patch_inverse(monkeypatch)

    result = EverdingenHurst.pD([1.0, 10.0], degree=10)

    assert result["func"] is eh._pbar_constant_rate_infinite
    assert result["t"] == [1.0, 10.0]
    assert result["degree"] == 10
    assert result["kwargs"] == {}


def test_pD_routes_closed_boundary_to_constant_rate_pressure(monkeypatch):
    _patch_inverse(monkeypatch)

    result = EverdingenHurst.pD([1.0], reD=25, boundary="closed")

    assert result["func"] is eh._pbar_constant_rate_closed
    assert result["kwargs"] == {"reD": 25.0}


def test_qD_routes_infinite_boundary_to_constant_pressure_rate(monkeypatch):
    _patch_inverse(monkeypatch)

    result = EverdingenHurst.qD([1.0], boundary="infinite")

    assert result["func"] is eh._qbar_constant_pressure_infinite
    assert result["kwargs"] == {}


def test_qD_preserves_closed_boundary_default(monkeypatch):
    _patch_inverse(monkeypatch)

    result = EverdingenHurst.qD([1.0], reD=25)

    assert result["func"] is eh._qbar_constant_pressure_closed
    assert result["kwargs"] == {"reD": 25.0}


@pytest.mark.parametrize("method", [EverdingenHurst.pD, EverdingenHurst.qD])
def test_closed_boundary_requires_reD(method):
    with pytest.raises(ValueError, match="reD is required"):
        method([1.0], boundary="closed")


@pytest.mark.parametrize("reD", [1.0, 0.5])
def test_closed_boundary_rejects_invalid_reD(reD):
    with pytest.raises(ValueError, match="greater than 1"):
        EverdingenHurst.qD([1.0], reD=reD)


def test_rejects_unknown_boundary():
    with pytest.raises(ValueError, match="boundary must be"):
        EverdingenHurst.pD([1.0], boundary="sealed")
