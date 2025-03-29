from dataclasses import dataclass

import numpy

@dataclass
class Survey:
    """It is a well survey (direction or trajectory)."""

    MD      : numpy.ndarray = None
    TVD     : numpy.ndarray = None
    DX      : numpy.ndarray = None
    DY      : numpy.ndarray = None
    INC     : numpy.ndarray = None
    AZI     : numpy.ndarray = None

    def md2td(self,values):
        return numpy.interp(values,self.MD,self.TVD)
        
    def td2md(self,values):
        return numpy.interp(values,self.TVD,self.MD)

    @staticmethod
    def inc2td(INC:numpy.ndarray,MD:numpy.ndarray):

        TVD = MD.copy()

        offset = MD[1:]-MD[:-1]
        radian = INC[1:]/180*numpy.pi

        TVD[1:] = numpy.cumsum(offset*numpy.cos(radian))

        return TVD

    @staticmethod
    def off2td(DX:numpy.ndarray,DY:numpy.ndarray,MD:numpy.ndarray):

        TVD = MD.copy()

        offMD = MD[1:]-MD[:-1]
        offDX = DX[1:]-DX[:-1]
        offDY = DY[1:]-DY[:-1]
                         
        TVD[1:] = numpy.sqrt(offMD**2-offDX**2-offDY**2)

        return numpy.cumsum(TVD)

class Depth():
    """A class representing depth, which can be either Measured Depth (MD) or True Vertical Depth (TVD)."""

    def __init__(self,MD=None,TVD=None):

        if MD is None and TVD is None:
            raise ValueError("Either MD or TVD must be provided.")
        
        self.MD = MD
        self.TVD = TVD
    
    def __repr__(self):
        return f"Depth(MD={self.MD}, TVD={self.TVD})"
