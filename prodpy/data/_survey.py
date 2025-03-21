from dataclasses import dataclass

import numpy

@dataclass
class Survey:
    """It is a well survey (direction or trajectory)."""

    MD      : numpy.ndarray = None
    TD      : numpy.ndarray = None
    DX      : numpy.ndarray = None
    DY      : numpy.ndarray = None
    INC     : numpy.ndarray = None
    AZI     : numpy.ndarray = None

    def md2td(self,values):
        return numpy.interp(values,self.MD,self.TD)
        
    def td2md(self,values):
        return numpy.interp(values,self.TD,self.MD)

    @staticmethod
    def inc2td(INC:numpy.ndarray,MD:numpy.ndarray):

        TD = MD.copy()

        offset = MD[1:]-MD[:-1]
        radian = INC[1:]/180*numpy.pi

        TD[1:] = numpy.cumsum(offset*numpy.cos(radian))

        return TD

    @staticmethod
    def off2td(DX:numpy.ndarray,DY:numpy.ndarray,MD:numpy.ndarray):

        TD = MD.copy()

        offMD = MD[1:]-MD[:-1]
        offDX = DX[1:]-DX[:-1]
        offDY = DY[1:]-DY[:-1]
                         
        TD[1:] = numpy.sqrt(offMD**2-offDX**2-offDY**2)

        return numpy.cumsum(TD)

class Depth():
    """A class representing depth, which can be either Measured Depth (MD) or True Vertical Depth (TD)."""

    def __init__(self,MD=None,TD=None):

        if MD is None and TD is None:
            raise ValueError("Either MD or TD must be provided.")
        
        self.MD = MD
        self.TD = TD
    
    def __repr__(self):
        return f"Depth(MD={self.MD}, TD={self.TD})"
