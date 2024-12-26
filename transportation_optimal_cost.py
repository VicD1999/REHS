import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import BOAT_VELOCITY, AIRSHIP_VELOCITY_L, r,  MU, BATTERY_PRICE, BOAT_LIFETIME, BATTERY_LIFETIME, crane_efficiency, DC_AC_efficiency, charge_efficiency, m_cells, m_pack, AIRSHIP_LIFETIME, prop_efficiency, CF, TURBINE_LIFETIME, TURBINE_PRICE
from transportation_consumption import boat_consumption, drone_consumption, airship_consumption_L
from transportation_CAPEX import boat_CAPEX



def boat_LCOE(m, x, consumption, capex, transportation_lifetime, velocity): 
    """
    m: masse de batteries par bateau
    x: distance en km du hub à la cote
    consumption: consommation du bateau par MWh/t-km A RETIRER consumption(m) 
    capex: $/ton pareil capex(m) 
    transportation_lifetime: years
    velocity: km/h 
    """
    t = (2*x)/(velocity) + 4*r*m #h
    rt_efficiency = 1 - 2*x * consumption(m) / MU
    E = m*MU*rt_efficiency  # MWh (energy per boat of load capacity m at arrival)
    J = E/(m*t) * crane_efficiency*DC_AC_efficiency*charge_efficiency # MWh / t-h (normalized energy supplied to the grid)
    P_install = (m*MU)/(crane_efficiency*prop_efficiency*charge_efficiency*t*CF) # MW (wind farm total power)
    I = 3 * (BATTERY_PRICE*MU)/(BATTERY_LIFETIME * 365 * 24) + capex(m)/(transportation_lifetime * 365 * 24) + (TURBINE_PRICE*P_install)/(m*TURBINE_LIFETIME*365*24) # $/t-h
    
    return  I/J


def boat_opti_mass(x):
    A = 2.485e-6 # MWh/t-km
    B = 151.23e-3 # MWh/km
    m = np.linspace(B*(MU/(2*x)-A)**-1 + 50, 40000, 40000)
    return m[np.argmin(boat_LCOE(m, x, boat_consumption, boat_CAPEX, BOAT_LIFETIME, BOAT_VELOCITY))]


    
"""def airship_opti_mass(x):
    m = np.linspace(50, 40000, 40000) 
    return m[np.argmin(transportation_LCOE(m, x, airship_consumption_L, airship_CAPEX, AIRSHIP_LIFETIME, AIRSHIP_VELOCITY_L))]
"""

"""if __name__ == '__main__':
    
    
    
    x = np.linspace(1,5000)
    y = np.zeros_like(x)
    print(opti_mass(2000))
   
    for i in range(len(x)):
        y[i] = opti_mass(x[i])


    plt.figure()
    plt.plot(x, y)
    plt.xlabel("Distance of the wind farm to shore [km]")
    plt.ylabel("Optimal mass [t]")
    
    print(boat_consumption(opti_mass(2000))*1000/MU)"""
    
