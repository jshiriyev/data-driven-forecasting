import numpy

class IPR():

    def __init__(self,**kwargs):
        """oil field units"""

        for key,value in kwargs.items():
            setattr(self,key,value)

    def pi_transient(self,time=1):
        """time in days"""

        upper = (self.perm*self.height)

        term = self.perm/(self.poro*self.muo*self.ct*self.rw**2)
        
        lower = 162.6*self.Bo*self.muo*(numpy.log10(term*time*24)-3.23+0.87*self.skin)

        return upper/lower

    def pi_steady(self):

        upper = (self.perm*self.height)

        lower = 141.2*self.Bo*self.muo*(numpy.log(self.re/self.rw)+self.skin)

        return upper/lower

    def pi_pseudo(self):

        upper = (self.perm*self.height)

        lower = 141.2*self.Bo*self.muo*(numpy.log(self.re/self.rw)-0.75+self.skin)

        return upper/lower

    def undersaturated(self,pres,rate=None,pwf=None,state="steady",**kwargs):
        
        productivity = getattr(self,f"pi_{state}")(**kwargs)

        if rate is None:
            return productivity*(pres-pwf)
        
        return pres-rate/productivity

    def vogel(self,pres,rate=None,pwf=None,state="steady",**kwargs):

        qmax = getattr(self,f"pi_{state}")(**kwargs)*pres/1.8

        if rate is None:
            return qmax*(1-0.2*(pwf/pres)-0.8*(pwf/pres)**2)

        values = 81-80*(rate/qmax)
        
        values[values<0] = numpy.nan
        
        return 0.125*pres*(numpy.sqrt(values)-1)

    def fetkovich(self,pres,rate=None,pwf=None,n=None,state="steady",**kwargs):

        qmax = getattr(self,f"pi_{state}")(**kwargs)*pres/1.8

        if rate is None:
            return qmax*(1-(pwf/pres)**2)**n

        values = 1-(rate/qmax)**(1/n)

        values[values<0] = numpy.nan

        return pres*numpy.sqrt(values)

    def saturated(self,pres,pwf=None,state="steady",**kwargs): #vogel

        rate = numpy.zeros(pwf.shape)

        rate[pwf<0] = numpy.nan

        PI = getattr(self,f"pi_{state}")(**kwargs)

        rate[pwf>self.pb] = PI*(pres-pwf[pwf>self.pb])

        TP = (1-0.2*(pwf[pwf<=self.pb]/self.pb)-0.8*(pwf[pwf<=self.pb]/self.pb)**2)

        rate[pwf<=self.pb] = PI*(pres-self.pb)+PI*self.pb/1.8*TP

        return rate

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    
    poro = 0.19
    perm = 8.2      # mD
    height = 53     # ft
    Pres = 5651     # psi
    Pb = 3000    # psi
    Bo = 1.1
    muo = 1.7       # cp
    ct = 1.29e-5    # 1/psi
    darea = 640     # acres
    rw = 0.328      # ft
    skin = 0

    re = numpy.sqrt((43560*darea)/numpy.pi)

    inflow = IPR(
        poro = poro,
        perm = perm,
        height = height,
        pb = Pb,
        Bo = Bo,
        muo = muo,
        ct = ct,
        re = re,
        rw = rw,
        skin = skin
        )
    
    qrange = numpy.linspace(0,1200)
    prange = numpy.linspace(0,5651)
    # prange = numpy.array((5651,5000,4500,4000,3500,3000,2500,2000,1500,1000,500,0))
    # prange = numpy.array((0,565,1130,1695,2260,2826,3000,5651))

    p_transt = inflow.undersaturated(Pres,rate=qrange,state="transient",time=30)
    p_steady = inflow.undersaturated(Pres,rate=qrange,state="steady")
    p_pseudo = inflow.undersaturated(Pres,rate=qrange,state="pseudo")

    q_transt = inflow.undersaturated(Pres,pwf=prange,state="transient",time=30)
    q_steady = inflow.undersaturated(Pres,pwf=prange,state="steady")
    q_pseudo = inflow.undersaturated(Pres,pwf=prange,state="pseudo")
    
    # p_vogel = inflow.vogel(Pres,rate=qrange,state="transient",time=30)
    # p_vogel = inflow.vogel(Pres,rate=qrange,state="steady")
    p_vogel = inflow.vogel(Pres,rate=qrange,state="pseudo")

    # q_vogel = inflow.vogel(Pres,pwf=prange,state="transient",time=30)
    # q_vogel = inflow.vogel(Pres,pwf=prange,state="steady")
    q_vogel1 = inflow.vogel(Pres,pwf=prange,state="pseudo")

    q_fetkovich = inflow.fetkovich(Pres,pwf=prange,state="pseudo",n=2)

    q_vogel2 = inflow.saturated(Pres,pwf=prange,state="pseudo")

    # plt.plot(qrange,pwf_transt,label='Transient')
    # plt.plot(qrange,pwf_steady,label='Steady-State')
    # plt.plot(qrange,pwf_pseudo,label='Pseudo-Steady-State')

    # plt.plot(q_pseudo,prange,label='Pseudo')
    plt.plot(q_vogel1,prange,label='Vogel')
    plt.plot(q_vogel2,prange,label='3000')
    # plt.plot(q_fetkovich,prange,label='Fetkovich')

    plt.legend()

    plt.xlim(xmin=0)
    plt.ylim(ymin=0)

    plt.show()
