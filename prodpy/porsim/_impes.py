import numpy as np

from ._solver import BaseSolver
from respy.solver._time import Time

from ._block import Block
from ._builder import Builder
from ._vector import Vector
from ._matrix import Matrix

class IMPES(BaseSolver):
    """
    The class solves for single phase reservoir flow in Rectangular Cuboids;

    """
    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

    def set_build(self):

        self.build = Builder(self.grid)

    def __call__(self,press=None,tcurr=0,tstep=None):

        env = super().__call__(press,tcurr,tstep)

        vec = self.block(*env)

        mat = self.build(vec)

        return mat

    def solve(self,**kwargs):
        """Solves the linear system of equation"""

        Pn = np.copy(self._press[:,0])
        
        for index,tcurr,tstep in self.time:

            if index==0 or not self.tstat:
                mat = self(Pn,tcurr,tstep)

            if not self.tstat:
                mat = self.iterate(mat,**kwargs)

            Pn = mat.imppress(Pn)

            print(f"{index:10}",Pn.flatten())
            
            self._press[:,index+1] = Pn

            Pn = Pn.reshape((-1,1))

    def iterate(self,mat:Matrix,jacobian=None,maxiter=100,tol=1e-6):

        Pn = np.copy(mat._P)

        Pk = np.copy(Pn)

        for k in range(maxiter):

            Rv = mat.impresid(Pn)

            if jacobian is None:
                Pk = mat.imppress(Pn)
            elif jacobian is True:
                Jm = self.jacobian(Pk,tcurr,tstep,Pn)
                Pk = Pk+np.linalg.solve(Jm,-Rv)
            else:
                Jm = jacobian(Pk,tstep,tcomp)
                Pk = Pk+np.linalg.solve(Jm,-Rv)
                
            error = np.linalg.norm(Rv,2)

            print(f"{k:2}",f"{error:.5e}",Pk.flatten())

            if np.linalg.norm(Rv,2)<tol:
                break

            mat = self(Pk,tcurr,tstep)

        else:

            print(f"It could not converge after {maxiter} iterations.")

        return mat

    def jacobian(self,press,tcurr,tstep,pprev,delta=10):

        mat0 = self(press,tcurr,tstep)

        resid0 = mat.impresid(pprev)

        press1 = np.zeros(press.shape)
        press2 = np.zeros(press.shape)

        press1[0::2] = press[0::2]+delta
        press2[1::2] = press[1::2]+delta

        mat1 = self(press1,tcurr,tstep)
        mat2 = self(press2,tcurr,tstep)

        resid1 = mat1.impresid(pprev)
        resid2 = mat2.impresid(pprev)

        vector = np.zeros(press.shape)

        vector[0::2] = (resid1-resid0)/delta
        vector[1::2] = (resid2-resid0)/delta

        return self.build.get_diag(vector)

    
