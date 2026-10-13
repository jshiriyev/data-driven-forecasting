import sys

import resprops

from .utils import UnitConversion

from . import decline
# resprops now lives in the reservoir-properties package; keep
# `prodpy.resprops` importable for existing code.
sys.modules[__name__ + ".resprops"] = resprops
from . import transient
from .transient import type_curves as typex
from . import mbal
from . import porsim
from . import wellflow

from ._allocation import Allocation
from ._schedule import Schedule

from ._decline import DCA
# from ._pressure import PTA
# from ._rate import RTA

__all__ = [
    "UnitConversion",
    "decline",
    "resprops",
    "transient",
    "typex",
    "mbal",
    "porsim",
    "wellflow",
    "Allocation",
    "Schedule",
    "DCA",
    "PTA",
    "RTA",
]
