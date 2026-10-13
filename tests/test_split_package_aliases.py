import resprops


def test_prodpy_resprops_is_reservoir_properties_package():
    import prodpy
    from prodpy.resprops import BlackOil

    assert prodpy.resprops is resprops
    assert BlackOil is resprops.BlackOil


def test_prodpy_wellflow_is_wellbore_flow_package():
    import prodpy
    import wellflow
    from prodpy.wellflow import CircularConduit

    assert prodpy.wellflow is wellflow
    assert CircularConduit is wellflow.CircularConduit
