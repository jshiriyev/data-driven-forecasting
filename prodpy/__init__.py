import sys

import resprops
import wellflow

from .utils import UnitConversion

from . import decline
# resprops and wellflow now live in the reservoir-properties and
# wellbore-flow packages; keep `prodpy.resprops` and `prodpy.wellflow`
# importable for existing code.
sys.modules[__name__ + ".resprops"] = resprops
sys.modules[__name__ + ".wellflow"] = wellflow
from . import transient
from .transient import type_curves as typex
from . import mbal
from . import porsim

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
