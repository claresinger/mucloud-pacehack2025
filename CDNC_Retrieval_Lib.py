
import numpy as np
from metpy.units import units
import metpy.calc as mpcalc
from metpy.constants import *

def LWC_Lapse_Rate(P,T):
    mr = mpcalc.saturation_mixing_ratio(P,T)
    rho_air = mpcalc.density(P,T,mr)
    cp = dry_air_spec_heat_press
    Lv = water_heat_vaporization
    Gamma_dry = dry_adiabatic_lapse_rate
    Tp = mpcalc.moist_lapse([P.to('hPa').magnitude,P.to('hPa').magnitude-30]*units('hPa'),T)
    dh = mpcalc.thickness_hydrostatic([P.to('hPa').magnitude,P.to('hPa').magnitude-30]*units('hPa'),Tp)
    dTdz = np.abs(Tp[0]-Tp[1])/dh
    cw = rho_air * cp/Lv * (Gamma_dry-dTdz)
    return cw.to('g/m^4').magnitude

class Cw_LUT(object):
    def __init__(self):
        self.P = np.linspace(600,1200,20) * units('hPa')
        self.T = np.linspace(-30,30,40) * units('degreeC')
        TT,PP = np.meshgrid(self.T,self.P)
        self.cw = np.zeros_like(TT)
        for i in range(self.P.size):
            for j in range(self.T.size):
                dTdh = LWC_Lapse_Rate(self.P[i],self.T[j])
                self.cw[i,j] = dTdh
    #return P,T,cw

def Nd_from_tau_re(tau,re,Cw=0.0020, fad=0.7, k=0.8,Qe = 2.0):
    """
    tau: cloud optical thickness [unitless]
    re: cloud effective radius [um]
    fad : adiabaticity of cloud [unitless]
    Cw:   lapse rate of water content [g/m^4]
    k:    disperson const rv^3 = k * re^3
    Qe:  extinction efficiency [unitless]

    """
    C = np.sqrt(5)/(2.0*np.pi*k)
    re_m = re*1e-6 # change unit of re from um to m
    rho  = 1e6 # density of water [g/m^3]
    CDNC = C * np.sqrt(fad*Cw*tau/Qe/rho/(re_m**5)) *1e-6
    return CDNC
