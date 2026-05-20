import numpy as np

from prodpy.resprops import BlackOil, Fluid
from prodpy.transient import ReservoirDomain


def test_reservoir_domain_repr_includes_layer_properties_and_geometry():
    reservoir = ReservoirDomain(
        100.0,
        yperm=25.0,
        zperm=10.0,
        poro=0.2,
        comp=3e-6,
        area=np.inf,
        height=20.0,
    )

    assert repr(reservoir) == (
        "ReservoirDomain(xperm=100.0, yperm=25.0, zperm=10.0, "
        "poro=0.2, comp=3e-06, press=None, area=np.inf acres, "
        "height=20.0 ft)"
    )


def test_reservoir_domain_repr_includes_initialized_state_compactly():
    reservoir = ReservoirDomain(
        100.0,
        poro=0.2,
        comp=3e-6,
        area=10.0,
        height=20.0,
    )
    reservoir.fluid = BlackOil(oil=Fluid(visc=1.0, comp=1e-5))
    reservoir.pinit = 3000.0
    reservoir.tcomp = 1e-5

    assert repr(reservoir) == (
        "ReservoirDomain(perm=100.0, is_isotropic=True, poro=0.2, "
        "comp=3e-06, press=None, area=10.0 acres, height=20.0 ft, "
        "fluid=BlackOil(phases=('oil',)), pinit=3000.0 psi, "
        "tcomp=1e-05 1/psi)"
    )
