import resprops


def test_prodpy_resprops_is_reservoir_properties_package():
    import prodpy
    from prodpy.resprops import BlackOil

    assert prodpy.resprops is resprops
    assert BlackOil is resprops.BlackOil
