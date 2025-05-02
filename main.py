# Authors: Anthony Maïo, Pierre Counotte, Victor Dachet

import numpy as np
import json
from CONSTANTES import (
    BOAT_VELOCITY, r, MU, BATTERY_PRICE, BOAT_LIFETIME, BATTERY_LIFETIME,
    TURBINE_LIFETIME, TURBINE_PRICE, crane_efficiency, DC_AC_efficiency,
    charge_efficiency, prop_efficiency, CF, m_pack, UFWT_INSTALLED_POWER, d_prime, g, h, Joule_to_MWh, diesel_efficiency, elec_efficiency
)


def boat_CAPEX(m):
    """Calculate the CAPEX for the boat in $/ton."""
    return (4000 - 0.005 * m) * 1.1

def boat_consumption(m):
    """Calculate the boat consumption in MWh/ton-km."""
    return (0.023 + 1400 / m) * (diesel_efficiency) / (elec_efficiency * 3600)

def round_trip_time(d):
    """Calculate the round-trip time in hours."""
    return 2 * d / BOAT_VELOCITY

def loading_time(m):
    """Calculate the loading/unloading time in hours."""
    return 4 * r * m

def time_to_pass_by_each_UFWT(d, P, m):
    """Calculate the time to pass by each UFWT."""
    n = P / UFWT_INSTALLED_POWER
    d_w = d_prime
    return n * d_w / BOAT_VELOCITY

def time_ratio(d, P, m):
    """Calculate the time ratio."""
    numerator = time_to_pass_by_each_UFWT(d, P, m)
    denominator = round_trip_time(d) + loading_time(m)
    return numerator / denominator

def battery_pack_per_UFWT(d, P, m):
    """Calculate the number of battery packs per UFWT."""
    round_trip_in_hours = round_trip_time(d)
    E = P * round_trip_in_hours * CF * charge_efficiency * prop_efficiency * crane_efficiency
    n_ufwt = P / UFWT_INSTALLED_POWER
    ton_per_ufwt = m / n_ufwt
    return ton_per_ufwt / m_pack

def calculate_costs_and_efficiencies(d, P, wacc):
    """Calculate costs and efficiencies for given parameters."""
    round_trip_in_hours = round_trip_time(d)
    E = P * round_trip_in_hours * CF
    E_max_per_year = P * 8760

    L_prop = E * prop_efficiency
    L_charge = E * (1 - prop_efficiency) * (1 - charge_efficiency)
    E_in_batteries = E - L_prop - L_charge
    m = E_in_batteries / MU

    L_crane = 4 * (m * g * h / 1000) * Joule_to_MWh
    L_rt = 2 * d * boat_consumption(m) * m
    L_discharge = (1 - charge_efficiency) * E_in_batteries
    L_DC_AC = (1 - DC_AC_efficiency) * (E_in_batteries - L_discharge - L_rt - L_crane)

    E_to_grid = E_in_batteries - L_crane - L_rt - L_discharge - L_DC_AC
    t_cycle = round_trip_in_hours + loading_time(m)
    num_cycles = 8760 / t_cycle
    E_to_grid_per_year = E_to_grid * num_cycles

    price_batteries = BATTERY_PRICE * m * MU
    annuity_batteries = (price_batteries * wacc) / (1 - (1 + wacc) ** -BATTERY_LIFETIME)

    price_boats = boat_CAPEX(m)
    annuity_boats = (price_boats * wacc) / (1 - (1 + wacc) ** -BOAT_LIFETIME)

    price_ufwt = TURBINE_PRICE * P
    annuity_ufwt = (price_ufwt * wacc) / (1 - (1 + wacc) ** -TURBINE_LIFETIME)

    total_annuity = 3 * annuity_batteries + annuity_boats + annuity_ufwt
    price_per_MWh = total_annuity / E_to_grid_per_year

    load_factor_ecosystem = E_to_grid_per_year / E_max_per_year
    n_w = battery_pack_per_UFWT(d, P, m)
    zeta = time_ratio(d, P, m)

    return {
        'distance': d,
        'size_m': m,
        'price_per_MWh': price_per_MWh,
        'load_factor_ecosystem': load_factor_ecosystem,
        'n_w': n_w,
        'num_cycles': num_cycles,
        'annuity_batteries': annuity_batteries,
        'annuity_boats': annuity_boats,
        'annuity_ufwt': annuity_ufwt,
        'total_annuity': total_annuity,
        'wacc': wacc,
        'E_cycle': E,
        'L_discard': 0,  # Placeholder, calculate if needed
        'L_prop': L_prop,
        'L_charge': L_charge,
        'L_crane': L_crane,
        'L_rt': L_rt,
        'L_discharge': L_discharge,
        'L_DC_AC': L_DC_AC,
        'E_to_grid': E_to_grid,
        'loading_time_ratio': zeta
    }

def main():
    distances = [150, 400, 2000]
    P = 100
    results = {}
    wacc = 0.07

    for d in distances:
        results[f"sc_1_{d}_{wacc}"] = calculate_costs_and_efficiencies(d, P, wacc)

    with open('results/results_sc1.json', 'w') as f:
        json.dump(results, f)

    print_results(results, distances, wacc)

def print_results(results, distances, wacc):
    """Print the results in a formatted manner."""
    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\pi_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        res = results[f"sc_1_{d}_{wacc}"]
        m = res['size_m']
        load_factor_ecosystem = res['load_factor_ecosystem'] * 100
        costs = res['price_per_MWh']
        print(f"{d} & {round(m)} & $ {round(load_factor_ecosystem, 1)} $ & {round(costs)} \\\\")
    print(f"\\bottomrule")

    print(f"\\toprule")
    print(f"d [km] & UFWT [\\%] & Batteries [\\%] & Boats [\\%] \\\\")
    print(f"\\midrule")
    for d in distances:
        res = results[f"sc_1_{d}_{wacc}"]
        annuity_batteries = res['annuity_batteries']
        annuity_boats = res['annuity_boats']
        annuity_ufwt = res['annuity_ufwt']
        total_annuity = res['total_annuity']
        print(f"{d} & {round(annuity_ufwt / total_annuity * 100, 1)} & "
              f"{round(3 * annuity_batteries / total_annuity * 100, 1)} & "
              f"{round(annuity_boats / total_annuity * 100, 1)} \\\\")
    print(f"\\bottomrule")

    print(f"\\toprule")
    print("d [km] & $E_{cycle}$ & $L_{discard}$ & $L_{prop}$ & $L_{+}$ & $L_{crane}$ & $L_{rt}$ & $L_{-}$ & $L_{DC-AC}$ & $E_{grid}$\\\\")
    print(f"\\midrule")
    for d in distances:
        res = results[f"sc_1_{d}_{wacc}"]
        print(f"{d} & {round(res['E_cycle'], 1)} & {round(res['L_discard'], 1)} & "
              f"{round(res['L_prop'], 1)} & {round(res['L_charge'], 1)} & "
              f"{round(res['L_crane'], 1)} & {round(res['L_rt'], 1)} & "
              f"{round(res['L_discharge'], 1)} & {round(res['L_DC_AC'], 1)} & "
              f"{round(res['E_to_grid'], 1)} \\\\")
    print(f"\\bottomrule")

if __name__ == '__main__':
    main()
