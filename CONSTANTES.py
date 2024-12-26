
""" Technical data """
elec_efficiency = 0.9
diesel_efficiency = 0.35
crane_efficiency = 0.9999
DC_AC_efficiency = 0.97
prop_efficiency = 0.5
charge_efficiency = 0.959
r = 2.3896e-4 # h/t
g = 9.81 # m/s^2
AIR_DENSITY = 1.225 # kg/m^3
HE_DENSITY = 0.1784 #kg/m^3


""" Velocity """
BOAT_VELOCITY = 24 # km/h
DRONE_VELOCITY = 30 # km/h
AIRSHIP_VELOCITY_L = 80 # km/h between the HHS and the sea port
AIRSHIP_VELOCITY_H = 10 # km/h within the HHS


""" Lifetime """
BATTERY_LIFETIME = 30 # yr
TURBINE_LIFETIME = 30 # yr
BOAT_LIFETIME = 20 # yr
AIRSHIP_LIFETIME = 20 # yr
DRONE_LIFETIME = 20 #yr


""" UFWT data"""
CF = 0.65
TURBINE_PRICE = 2.5e6 # $/MW
d_prime = 0.8 # km distance between 2 UFWT's
UFWT_INSTALLED_POWER = 10 #MW


""" Battery pack data """
m_cells = 28 # ton
m_pack = 30 #ton
MU = 0.467 # MWh/t_pack
BATTERY_PRICE = 71500 # $/MWh (pack)


""" Drone & airship data """
DRONE_MASS = 10 # tons
DRONE_PRICE = 20e6 # $/(30tons)
A_p = 67 # m^2 drone
C_d = 0.04
n_propeller = 3
A_propeller = 20 # m^2
AIRSHIP_LENGTH = 600 # m
AIRSHIP_PRICE = 600e6 # $/ (4400 tons)



#A = 2.485e-3 # kWh/t-km
#B = 151.23 # kWh/km
