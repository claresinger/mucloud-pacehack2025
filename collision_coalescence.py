import numpy as np
import metpy
from metpy.units import units
import metpy.calc as metcalc
from metpy.constants import *

# Collision-Coalenscence Process Rates in terms of re/ve
def CC_growth_rates_retrieval(re_ret, ve_ret, tau_ret, CTT=270, CTP=680, Cw=0.0020, fad=0.7, Qext=2.0):
    # Units 
    re_ret = re_ret *units.um
    CTT = CTT *units.degC
    CTP = CTP *units.hPa
    Cw = Cw *units('g/m^4')
    
    # Constants
    rho_0 = 1.225 *units('kg/m^3')         # kg/m^3
    kcc = 4.44*10**9 *units('m^3/(kg^2*s)')      # m^3/(kg^2*s) Pinsky collision efficiencies
    rstar = 40 *units.um     # drop size cutoff for cloud and precip
    xstar = 2.68*10**-10 *units.kg  # mass kg drop mass cutoff for cloud and precip kg
    fadcw = fad*Cw
    rhol = density_water
    Qext = 2
    
    mixing_ratio = metcalc.saturation_mixing_ratio(CTP, CTT, phase='liquid').to('g/kg')
    rho = metcalc.density(CTP, CTT, mixing_ratio) #@modify to metpy
    dens_corr = rho_0/rho # change in air resistance with altitude/density
    
    Nrate_AU = kcc*(1/xstar)*(4/9)*((fadcw*rhol**2)/Qext)*(((1+ve_ret)*(ve_ret-1)**2)/(2*ve_ret-1))*(re_ret)**4*tau_ret
    Nrate_SC = -kcc*(20/9)*((fadcw*rhol)/Qext)*((ve_ret-1)/(2*ve_ret-1))*(re_ret)*tau_ret-Nrate_AU

    return(Nrate_AU.to('1/cm^3*1/s'), Nrate_SC.to('1/cm^3*1/s'))

