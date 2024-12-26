import numpy as np
from CONSTANTES import DRONE_VELOCITY, g, DRONE_MASS, AIR_DENSITY, C_d, A_propeller, A_p, n_propeller, MU, AIRSHIP_LENGTH, AIRSHIP_VELOCITY_H, AIRSHIP_VELOCITY_L, HE_DENSITY, elec_efficiency, diesel_efficiency


def boat_consumption(m):# in MWh/ton-km
        return (0.023 + 1400/m) * (diesel_efficiency)/(elec_efficiency*3600)

def drone_consumption(m): # in MWh/ton-km
    m *= 1000 # mass in kg
    elec_efficiency = 0.9 
    return (((DRONE_MASS*1000)+m) * (DRONE_VELOCITY/3.6)**2/(m*2000) + (AIR_DENSITY*C_d*A_p*(DRONE_VELOCITY/3.6)**2)/m  + 2 * ((DRONE_MASS*1000) + m)**(3/2)/(m*(DRONE_VELOCITY/3.6)) * np.sqrt(g**3/(2*AIR_DENSITY*A_propeller*n_propeller)))/(2*elec_efficiency*3600)
    return 


""" Airship consumption between the HHS and the seaport """

def airship_consumption_L(m): # in MWh/ton-km 
    return 3/(4*elec_efficiency) *  (C_d*AIR_DENSITY *(AIRSHIP_VELOCITY_L/3.6)**2)/(AIRSHIP_LENGTH*(AIR_DENSITY-HE_DENSITY))/3600


""" Airship consumption within the HHS """

def airship_consumption_H(m): # in MWh/ton-km 
    return 3/(4*elec_efficiency) *  (C_d*AIR_DENSITY *(AIRSHIP_VELOCITY_H/3.6)**2)/(AIRSHIP_LENGTH*(AIR_DENSITY-HE_DENSITY))/3600


