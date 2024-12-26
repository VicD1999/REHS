import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import BOAT_VELOCITY, r, m_pack, d_prime
from transportation_optimal_cost import boat_opti_mass
from scenario_1 import pack_per_UFWT_S1




def time_ratio(d):
    m = boat_opti_mass(d)
    t = 2*d/BOAT_VELOCITY + 4*r*m # h
    n = m/(pack_per_UFWT_S1(d,m)*m_pack) # number of wind turbines
    t_sup = d_prime*n/BOAT_VELOCITY #h
    
    return t_sup/t


if __name__ == '__main__':
    distances = [150, 400, 2000]
    for d in distances:
        print(f"Time ratio at {d}: {time_ratio(d):.3f}")
        
    
    
    
    
    """ Time ratio as a function of d """
    d = np.linspace(20,200,200)
    tr = np.zeros_like(d)
    for i in range(len(d)):
        tr[i] = time_ratio(d[i])
    plt.figure()
    plt.plot(d, tr)
    plt.xlabel("Wind park distance [km]")
    plt.ylabel("Time ratio")
    
        
    