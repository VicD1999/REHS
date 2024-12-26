import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import (
    BOAT_VELOCITY, r, MU, BATTERY_PRICE, BOAT_LIFETIME, BATTERY_LIFETIME, 
    TURBINE_LIFETIME, TURBINE_PRICE, crane_efficiency, DC_AC_efficiency, 
    charge_efficiency, prop_efficiency, CF, m_pack, UFWT_INSTALLED_POWER, d_prime
)
from transportation_consumption import boat_consumption
from transportation_CAPEX import boat_CAPEX
from transportation_optimal_cost import boat_opti_mass

# Calculate transportation cost for boats in $/MWh
def cost_transportation_boat(d, m):
    t = 2 * d / BOAT_VELOCITY + 4 * r * m  # Total trip time (hours)
    rt_efficiency = 1 - 2 * d * boat_consumption(m) / MU  # Round-trip efficiency
    E = m * MU * rt_efficiency  # Energy delivered at arrival (MWh)
    J = E / (m * t) * crane_efficiency * DC_AC_efficiency * charge_efficiency  # Normalized energy to grid (MWh/t-h)
    I = 3 * (BATTERY_PRICE * MU) / (BATTERY_LIFETIME * 365 * 24) + boat_CAPEX(m) / (BOAT_LIFETIME * 365 * 24)  # $/t-h
    return I / J

# Calculate production cost in $/MWh
def cost_production(d, m):
    t = 2 * d / BOAT_VELOCITY + 4 * r * m  # Total trip time (hours)
    rt_efficiency = 1 - 2 * d * boat_consumption(m) / MU  # Round-trip efficiency
    E = m * MU * rt_efficiency  # Energy delivered at arrival (MWh)
    J = E / (m * t) * crane_efficiency * DC_AC_efficiency * charge_efficiency  # Normalized energy to grid (MWh/t-h)
    P_install = (m * MU) / (crane_efficiency * prop_efficiency * charge_efficiency * t * CF)  # Wind farm power (MW)
    I = (TURBINE_PRICE * P_install) / (m * TURBINE_LIFETIME * 365 * 24)  # $/t-h
    return I / J

# Calculate overall costs in $/MWh
def overall_costs(d, m):
    return cost_transportation_boat(d, m) + cost_production(d, m)

# Calculate overall efficiency
def overall_efficiency(d, m):
    rt_efficiency = 1 - 2 * d * boat_consumption(m) / MU  # Round-trip efficiency
    return (
        charge_efficiency * prop_efficiency * crane_efficiency * rt_efficiency * 
        crane_efficiency * charge_efficiency * DC_AC_efficiency
    )

# Calculate energy losses for boats as a percentage
def losses_boat(x, m):
    return (x * boat_consumption(m) / MU) * 100

# Calculate number of battery packs per UFWT for Scenario 1
def pack_per_UFWT_S1(d, m):
    t = 2 * d / BOAT_VELOCITY + 4 * r * m  # Total trip time (hours)
    return (UFWT_INSTALLED_POWER * t * charge_efficiency * prop_efficiency * CF) / (m_pack * MU)

# Print results table in LaTeX format
def print_tab_results(distances):
    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\eta_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = boat_opti_mass(d)
        efficiency = overall_efficiency(d, m)
        costs = overall_costs(d, m)
        # print(f"{d} & {round(m)} & $ {round(efficiency, 2)} $ & {round(costs)} \\\")
        # print(f"{d} & {round(m)} & $ {round(efficiency, 2)} $ & {round(costs)} \\\")
    print(f"\\bottomrule")

# Calculate round-trip time in hours
def round_trip_time(d):
    return 2 * d / BOAT_VELOCITY  # Time for round trip (hours)

# Calculate loading/unloading time in hours
def loading_time(m):
    return 4 * r * m

def time_to_pass_by_each_UFWT(d, P, m):
    n = P/UFWT_INSTALLED_POWER
    d_w = d_prime
    return n * d_w / BOAT_VELOCITY

def time_ratio(d, P, m):
    numerator = time_to_pass_by_each_UFWT(d, P, m)
    denominator = round_trip_time(d) + loading_time(m)
    return numerator / denominator # loading_time(m) / (round_trip_time(d) + loading_time(m))

# Calculate number of battery packs per UFWT
# Note: `d` should be passed to this function but is missing in the arguments
def battery_pack_per_UFWT(P, m):
    round_trip_in_hours = round_trip_time(d)  # `d` needs to be defined
    E = P * round_trip_in_hours * CF * charge_efficiency * prop_efficiency * crane_efficiency  # MWh
    n_ufwt = P / UFWT_INSTALLED_POWER
    ton_per_ufwt = m / n_ufwt
    return ton_per_ufwt / m_pack

# Main execution block
if __name__ == '__main__':
    distances = [30, 150, 400, 2000]  # Example distances in km
    P = 100  # Wind farm power in MW
    results = {}
    wacc = 0.07  # Weighted average cost of capital
    

    for d in distances:
        round_trip_in_hours = round_trip_time(d)
        
        E = P * round_trip_in_hours * CF * charge_efficiency * prop_efficiency  # Total energy (MWh)

        m = E / MU  # Optimal boat mass (tons)

        rt_efficiency = 1 - 2 * d * boat_consumption(m) / MU  # Round-trip efficiency
        E_to_grid = (
            E * crane_efficiency * rt_efficiency * rt_efficiency * 
            crane_efficiency * charge_efficiency * DC_AC_efficiency
        )

        num_cycles = 8760 / (round_trip_in_hours + loading_time(m) ) # (round_trip_time(d) + loading_time(m) + time_to_pass_by_each_UFWT(d, P, m))  # Number of cycles per year
        E_to_grid_per_year = E_to_grid * num_cycles  # Total energy delivered per year (MWh)

        # Cost calculations
        price_batteries = BATTERY_PRICE * m * MU  # Battery CAPEX ($)
        annuity_batteries = (price_batteries * wacc) / (1 - (1 + wacc) ** -BATTERY_LIFETIME)  # $/year

        price_boats = boat_CAPEX(m)  # Boat CAPEX ($)
        annuity_boats = (price_boats * wacc) / (1 - (1 + wacc) ** -BOAT_LIFETIME)  # $/year

        price_ufwt = TURBINE_PRICE * P  # Wind farm CAPEX ($)
        annuity_ufwt = (price_ufwt * wacc) / (1 - (1 + wacc) ** -TURBINE_LIFETIME)  # $/year

        total_annuity = 3 * annuity_batteries + annuity_boats + annuity_ufwt  # Total cost ($/year)
        price_per_MWh = total_annuity / E_to_grid_per_year  # Cost per MWh ($/MWh)

        zeta = time_ratio(d, P, m)  # Loading time ratio
        efficiency = overall_efficiency(d, m)  # Overall efficiency

        # Number of battery packs
        n_w = battery_pack_per_UFWT(P, m)
        # n_w_prev = pack_per_UFWT_S1(d, m)

        # results.append((d, m, price_per_MWh, efficiency, zeta, n_w))

        results[f"sc_1_{d}_{wacc}"] = {
            'distance': d,
            'size_m': m,
            'price_per_MWh': price_per_MWh,
            'efficiency': efficiency,
            'loading_time_ratio': zeta,
            'n_w': n_w,
            'num_cycles': num_cycles,
            'annuity_batteries': annuity_batteries,
            'annuity_boats': annuity_boats,
            'annuity_ufwt': annuity_ufwt,
            'total_annuity': total_annuity,
            'wacc': wacc
        }
    
    import json
    with open('results/results_sc1.json', 'w') as f:
        json.dump(results, f)

    # Print results
    for res in results:
        print(res)

    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\eta_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = results[f"sc_1_{d}_{wacc}"]["size_m"]
        efficiency = results[f"sc_1_{d}_{wacc}"]["efficiency"] * 100
        costs = results[f"sc_1_{d}_{wacc}"]["price_per_MWh"]
        print(f"{d} & {round(m)} & $ {round(efficiency, 1)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")