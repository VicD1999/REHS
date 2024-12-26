import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import  MU, BATTERY_PRICE, AIRSHIP_LIFETIME, DRONE_LIFETIME, BATTERY_LIFETIME, TURBINE_LIFETIME, TURBINE_PRICE, DC_AC_efficiency, charge_efficiency, prop_efficiency, CF, AIRSHIP_VELOCITY_H, AIRSHIP_VELOCITY_L, d_prime, m_pack, UFWT_INSTALLED_POWER, DRONE_PRICE, AIRSHIP_PRICE
from transportation_consumption import airship_consumption_H, airship_consumption_L, drone_consumption
from scenario_1 import pack_per_UFWT_S1



def cost_transportation_airship(d, m): # in $/MWh
    
    t = 2*d/AIRSHIP_VELOCITY_L + m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/(2*AIRSHIP_VELOCITY_H)  # h
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU # airship efficiency between the HHS and seaport
    rtwa_efficiency = 1 - (m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/2) * airship_consumption_H(m)/MU # airship efficiency within the HHS
    E = m*MU*rtla_efficiency*rtwa_efficiency  # MWh (energy per airship of load capacity m at arrival)
    J = E/(m*t) *DC_AC_efficiency*charge_efficiency # MWh / t-h (normalized energy supplied to the grid)
    I = 3 * (BATTERY_PRICE*MU)/(BATTERY_LIFETIME * 365 * 24) + AIRSHIP_PRICE/(m*AIRSHIP_LIFETIME * 365 * 24) # $/t-h (3 times the battery price + empty airship price)
    return  I/J


def cost_transportation_drones(d, m): # in $/MWh (We consider one drone can handle 5 battery packs)
    
    t = 2*d/AIRSHIP_VELOCITY_L + m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/(2*AIRSHIP_VELOCITY_H)  # h
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU # airship efficiency between the HHS and seaport
    rtwa_efficiency = 1 - (m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/2) * airship_consumption_H(m)/MU # airship efficiency within the HHS
    rtd_efficiency = 1 - 2*0.75 * drone_consumption(m_pack)/MU # drone efficiency (mean distance covered = 2*0.75 km)
    E = m*MU*rtla_efficiency*rtwa_efficiency  # MWh (energy per airship of load capacity m at arrival)
    J = E/(m*t) *DC_AC_efficiency*charge_efficiency # MWh / t-h (normalized energy supplied to the grid)
    I = 1/(5*rtd_efficiency) * DRONE_PRICE/(m_pack*DRONE_LIFETIME * 365 * 24) # $/t-h (lot's of simplifications)

    return  I/J

def cost_production(d, m): # in $/MWh
    
    t = 2*d/AIRSHIP_VELOCITY_L + m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/(2*AIRSHIP_VELOCITY_H)  # h
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU # airship efficiency between the HHS and seaport
    rtwa_efficiency = 1 - (m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/2) * airship_consumption_H(m)/MU # airship efficiency within the HHS
    rtd_efficiency = 1 - 2*0.75 * drone_consumption(m_pack)/MU # drone efficiency (mean distance covered = 2*0.75 km)
    E = m*MU*rtla_efficiency*rtwa_efficiency  # MWh (energy per airship of load capacity m at arrival)
    J = E/(m*t) *DC_AC_efficiency*charge_efficiency # MWh / t-h (normalized energy supplied to the grid)
    P_install = (m*MU)/(rtd_efficiency * prop_efficiency*charge_efficiency*t*CF) # MW (wind farm total power)
    I = (TURBINE_PRICE*P_install)/(m*TURBINE_LIFETIME*365*24) # $/t-h
    return  I/J


def overall_costs(d, m):
    return cost_transportation_airship(d, m) + cost_transportation_drones(d, m) + cost_production(d, m)

def overall_efficiency(d, m):
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU # airship efficiency between the HHS and seaport
    rtwa_efficiency = 1 - (m/(pack_per_UFWT_S2(d, m)*m_pack) * d_prime/2) * airship_consumption_H(m)/MU # airship efficiency within the HHS
    rtd_efficiency = 1 - 2*0.75 * drone_consumption(m_pack)/MU # drone efficiency (mean distance covered = 2*0.75 km)
    return charge_efficiency * prop_efficiency * rtd_efficiency * rtwa_efficiency * rtla_efficiency * charge_efficiency * DC_AC_efficiency
    

def pack_per_UFWT_S2(d, m): # iterative method to find n_w
    n_w = pack_per_UFWT_S1(d, m)
    n_w1 = n_w
    n_w2 = 10000
    
    for i in range(10):
        if(abs(n_w2-n_w1) < 0.5):
            n_w = n_w1
            break
        
        n_w2 = n_w1
        t = 2*d/AIRSHIP_VELOCITY_L + m/(n_w1*m_pack) * d_prime/(2*AIRSHIP_VELOCITY_H)  # h
        n_w1 = (UFWT_INSTALLED_POWER * t * charge_efficiency * prop_efficiency * CF)/(m_pack * MU)
    
    return n_w

def losses_drone(d, m): #portion of battery pack energy consumed by drones for motion
    return (d* drone_consumption(m)/MU)*100


def losses_airship(d, m): #portion of battery pack energy consumed by airship for motion
    return (d* airship_consumption_L(m) /MU)*100

    


if __name__ == '__main__':
    
    
    d = 150
    m = 4400
    print("Case1 (d =", d, "  km, m =", round(m)," tons):")
    print(" Overall costs = ", overall_costs(d, m), "$/MWh")
    print(" Overall energy efficiency =", overall_efficiency(d, m))
    print(" n_w = ", pack_per_UFWT_S2(d, m))
    
    print("\n")
    
    d = 400
    m = 4400
    print("Case2 (d =", d, "  km, m =", round(m)," tons):")
    print(" Overall costs = ", overall_costs(d, m), "$/MWh")
    print(" Overall energy efficiency =", overall_efficiency(d, m))
    print(" n_w = ", pack_per_UFWT_S2(d, m))
    
    print("\n")
    
    d = 2000
    m = 4400
    print("Case3 (d =", d, "  km, m =", round(m)," tons):")
    print(" Overall costs = ", overall_costs(d, m), "$/MWh")
    print(" Overall energy efficiency =", overall_efficiency(d, m))
    print(" n_w = ", pack_per_UFWT_S2(d, m))
    
    print("\n")

    
    print(100-losses_drone(2, 30))