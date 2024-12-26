import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import BOAT_VELOCITY, r, MU, BATTERY_PRICE, BOAT_LIFETIME, BATTERY_LIFETIME, TURBINE_LIFETIME, TURBINE_PRICE, crane_efficiency, DC_AC_efficiency, charge_efficiency, prop_efficiency, CF, m_pack, UFWT_INSTALLED_POWER
from transportation_consumption import boat_consumption
from transportation_CAPEX import boat_CAPEX
from transportation_optimal_cost import boat_opti_mass




def cost_transportation_boat(d, m): # in $/MWh
    
    t = 2*d/BOAT_VELOCITY + 4*r*m # h
    rt_efficiency = 1 - 2*d* boat_consumption(m) / MU
    E = m*MU*rt_efficiency  # MWh (energy per boat of load capacity m at arrival)
    J = E/(m*t) * crane_efficiency*DC_AC_efficiency*charge_efficiency # MWh / t-h (normalized energy supplied to the grid)
    I = 3 * (BATTERY_PRICE*MU)/(BATTERY_LIFETIME * 365 * 24) + boat_CAPEX(m)/(BOAT_LIFETIME * 365 * 24) # $/t-h (3 times the battery price + empty boat price)
    return  I/J

def cost_production(d, m): # in $/MWh
    
    t = 2*d/BOAT_VELOCITY + 4*r*m # h
    rt_efficiency = 1 - 2*d * boat_consumption(m) / MU
    E = m*MU*rt_efficiency  # MWh (energy per boat of load capacity m at arrival)
    J = E/(m*t) * crane_efficiency*DC_AC_efficiency*charge_efficiency # MWh / t-h (normalized energy supplied to the grid)
    P_install = (m*MU)/(crane_efficiency*prop_efficiency*charge_efficiency*t*CF) # MW (wind farm total power)
    I = (TURBINE_PRICE*P_install)/(m*TURBINE_LIFETIME*365*24) # $/t-h
    return  I/J

def overall_costs(d, m):
    return cost_transportation_boat(d, m) + cost_production(d, m)

def overall_efficiency(d, m):
    rt_efficiency = 1 - 2*d* boat_consumption(m) / MU
    return charge_efficiency * prop_efficiency * crane_efficiency * rt_efficiency * crane_efficiency * charge_efficiency * DC_AC_efficiency

def losses_boat(x, m): #portion of battery pack energy consumed by boats for motion 
    return (x*boat_consumption(m)/MU)*100
    

def pack_per_UFWT_S1(d, m):
    t = 2*d/BOAT_VELOCITY + 4*r*m # h
    return (UFWT_INSTALLED_POWER * t * charge_efficiency * prop_efficiency * CF)/(m_pack * MU)

def print_tab_results(distances):
    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\eta_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = boat_opti_mass(d)
        efficiency = overall_efficiency(d, m)
        costs = overall_costs(d, m)
        print(f"{d} & {round(m)} & $ {round(efficiency, 2)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")

if __name__ == '__main__':
    
    # d = 150
    # m = boat_opti_mass(d)
    # print("Case1 (d =", d, "km, m =", round(m),"tons):")
    # print(" Overall costs = ", overall_costs(d, m), "$/MWh")
    # print(" Overall energy efficiency =", overall_efficiency(d, m))
    # print(" n_w = ", pack_per_UFWT_S1(d, m))
    
    # print("\n")
    
    # d = 400
    # m = boat_opti_mass(d)
    # print("Case2 (d =", d, "km, m =", round(m),"tons):")
    # print(" Overall costs = ", overall_costs(d, m), "$/MWh")
    # print(" Overall energy efficiency =", overall_efficiency(d, m))
    # print(" n_w = ", pack_per_UFWT_S1(d, m))
    
    # print("\n")
    
    # d = 2000
    # m = boat_opti_mass(d)
    # print("Case3 (d =", d, "km, m =", round(m),"tons):")
    # print(" Overall costs = ", overall_costs(d, m), "$/MWh")
    # print(" Overall energy efficiency =", overall_efficiency(d, m))
    # print(" n_w = ", pack_per_UFWT_S1(d, m))

    distances = [150, 400, 2000]
    print_tab_results(distances)
    
    
    
    
    