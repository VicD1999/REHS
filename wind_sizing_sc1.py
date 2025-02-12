import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import (
    BOAT_VELOCITY, r, MU, BATTERY_PRICE, BOAT_LIFETIME, BATTERY_LIFETIME, 
    TURBINE_LIFETIME, TURBINE_PRICE, crane_efficiency, DC_AC_efficiency, 
    charge_efficiency, prop_efficiency, CF, m_pack, UFWT_INSTALLED_POWER, d_prime, g, h, Joule_to_MWh
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
    distances = [150, 400, 2000]  # Example distances in km
    P = 100  # Wind farm power in MW
    results = {}
    wacc = 0.07  # Weighted average cost of capital
    

    for d in distances:
        round_trip_in_hours = round_trip_time(d)
        
        E = P * round_trip_in_hours * CF * charge_efficiency * prop_efficiency  # Total energy (MWh)
        E_max_per_year = P * 8760  # Maximum energy per year (MWh)

        m = E / MU  # Optimal boat mass (tons)

        rt_efficiency = 1 - 2 * d * boat_consumption(m) / MU  # Round-trip efficiency
        E_to_grid = (
            E * crane_efficiency * rt_efficiency * 
            crane_efficiency * charge_efficiency * DC_AC_efficiency
        )

        t_cycle = round_trip_in_hours + loading_time(m)
        num_cycles = 8760 / t_cycle # (round_trip_time(d) + loading_time(m) + time_to_pass_by_each_UFWT(d, P, m))  # Number of cycles per year
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

        load_factor_ecosystem = E_to_grid_per_year / E_max_per_year

        # Number of battery packs
        n_w = battery_pack_per_UFWT(P, m)
        # n_w_prev = pack_per_UFWT_S1(d, m)

        results[f"sc_1_{d}_{wacc}"] = {
            'distance': d,
            'size_m': m,
            'price_per_MWh': price_per_MWh,
            'load_factor_ecosystem': load_factor_ecosystem,
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

    print(f"{E_to_grid_per_year/E_max_per_year}")

    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\pi_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = results[f"sc_1_{d}_{wacc}"]["size_m"]
        load_factor_ecosystem = results[f"sc_1_{d}_{wacc}"]["load_factor_ecosystem"] * 100
        efficiency = results[f"sc_1_{d}_{wacc}"]["efficiency"] * 100
        costs = results[f"sc_1_{d}_{wacc}"]["price_per_MWh"]
        print(f"{d} & {round(m)} & $ {round(load_factor_ecosystem, 1)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")


    for d in distances:
        round_trip_in_hours = round_trip_time(d)
         # Losses computation TO BE IMPLEMENTED
        # L_boat = losses_boat(d, m)
        
        E = P * round_trip_in_hours * CF # Total energy (MWh)
        E_max_per_year = P * 8760  # Maximum energy per year (MWh)

        L_prop = E * prop_efficiency
        L_charge = E * prop_efficiency * (1-charge_efficiency)
        E_in_batteries = E - L_prop - L_charge
        m = E_in_batteries / MU  # Optimal boat mass (tons)

        L_crane = (m * g * h / 1000) * Joule_to_MWh
        L_rt = 2 * d * boat_consumption(m) * m
        
        L_discharge = (1-charge_efficiency) * E_in_batteries
        L_DC_AC = (1-DC_AC_efficiency) * (E_in_batteries - L_discharge - L_rt - L_crane)

        E_to_grid = E_in_batteries - L_crane - L_rt - L_crane - L_discharge - L_DC_AC
        t_cycle = round_trip_in_hours + loading_time(m)
        num_cycles = 8760 / t_cycle # (round_trip_time(d) + loading_time(m) + time_to_pass_by_each_UFWT(d, P, m))  # Number of cycles per year
        E_to_grid_per_year = E_to_grid * num_cycles  # Total energy delivered per year (MWh)
        
        E_cycle = P * t_cycle * CF
        L_discard = P * loading_time(m) * CF
        # print(f"{L_discard = }")
        E_to_grid = E - L_prop - L_charge - L_rt - L_discharge - L_DC_AC
        # Cost calculations
        price_batteries = BATTERY_PRICE * m * MU  # Battery CAPEX ($)
        annuity_batteries = (price_batteries * wacc) / (1 - (1 + wacc) ** -BATTERY_LIFETIME)  # $/year

        price_boats = boat_CAPEX(m)  # Boat CAPEX ($)
        annuity_boats = (price_boats * wacc) / (1 - (1 + wacc) ** -BOAT_LIFETIME)  # $/year

        price_ufwt = TURBINE_PRICE * P  # Wind farm CAPEX ($)
        annuity_ufwt = (price_ufwt * wacc) / (1 - (1 + wacc) ** -TURBINE_LIFETIME)  # $/year

        total_annuity = 3 * annuity_batteries + annuity_boats + annuity_ufwt  # Total cost ($/year)
        price_per_MWh = total_annuity / E_to_grid_per_year  # Cost per MWh ($/MWh)

        load_factor_ecosystem = E_to_grid_per_year / E_max_per_year

        # Number of battery packs
        n_w = battery_pack_per_UFWT(P, m)
        # n_w_prev = pack_per_UFWT_S1(d, m)
        
        # print(f"{L_prop/E_prod = }, {L_charge/E_prod = }, {L_crane/E_prod = }, {L_rt/E_prod = }, {L_discharge/E_prod = }, {L_DC_AC/E_prod = }")
        # print(f"{L_prop/E_prod = }, {L_charge/E_prod = }, {L_crane/E = }, {L_rt/E = }, {L_discharge/E = }, {L_DC_AC/E = }")
        # print(f"{L_prop = }, {L_charge = }, {L_crane = }, {L_rt = }, {L_discharge = }, {L_DC_AC = }")

        # # conso = 0.00113 # MWH/km 
        # # conso_d = 2 * d * conso # MWH/km
        # print(f"{E_prod = }, {E = }")
        # print(f"{d}, {L_rt}")
        # print(f"{conso_d}")
        # E_final = E - L_crane - L_rt - L_crane - L_discharge - L_DC_AC
        # print(f"{E_final = }, {E_to_grid = }")
        results[f"sc_1_{d}_{wacc}"] = {
            'distance': d,
            'size_m': m,
            'price_per_MWh': price_per_MWh,
            'load_factor_ecosystem': load_factor_ecosystem,
            'efficiency': efficiency,
            'n_w': n_w,
            'num_cycles': num_cycles,
            'annuity_batteries': annuity_batteries,
            'annuity_boats': annuity_boats,
            'annuity_ufwt': annuity_ufwt,
            'total_annuity': total_annuity,
            'wacc': wacc,
            'E_cycle': E_cycle,
            'L_discard': L_discard,
            'L_prop': L_prop,
            'L_charge': L_charge,
            'L_crane': L_crane,
            'L_rt': L_rt,
            'L_discharge': L_discharge,
            'L_DC_AC': L_DC_AC,
            'E_to_grid': E_to_grid
        }
    
    import json
    with open('results/results_sc1.json', 'w') as f:
        json.dump(results, f)

    # Print results
    for res in results:
        print(res)

    print(f"{E_to_grid_per_year/E_max_per_year}")

    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\pi_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = results[f"sc_1_{d}_{wacc}"]["size_m"]
        load_factor_ecosystem = results[f"sc_1_{d}_{wacc}"]["load_factor_ecosystem"] * 100
        efficiency = results[f"sc_1_{d}_{wacc}"]["efficiency"] * 100
        costs = results[f"sc_1_{d}_{wacc}"]["price_per_MWh"]
        print(f"{d} & {round(m)} & $ {round(load_factor_ecosystem, 1)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")

    print(f"\\toprule")
    print(f"d [km] & UFWT [\\%] & Batteries [\\%] & Boats [\\%] \\\\")
    print(f"\\midrule")
    for d in distances:
        annuity_batteries = results[f"sc_1_{d}_{wacc}"]["annuity_batteries"]
        annuity_boats = results[f"sc_1_{d}_{wacc}"]["annuity_boats"]
        annuity_ufwt = results[f"sc_1_{d}_{wacc}"]["annuity_ufwt"]
        total_annuity = results[f"sc_1_{d}_{wacc}"]["total_annuity"]
        # print(f"{d} & {3 * round(annuity_batteries)} & {round(annuity_boats)} & {round(annuity_ufwt)} & {round(total_annuity)} \\\\")
        print(f"{d} & {round(annuity_ufwt/total_annuity * 100, 1)} & {round(3 * annuity_batteries/total_annuity * 100, 1)} & {round(annuity_boats/total_annuity * 100, 1)} \\\\")
        load_factor_ecosystem = results[f"sc_1_{d}_{wacc}"]["load_factor_ecosystem"] * 100
        efficiency = results[f"sc_1_{d}_{wacc}"]["efficiency"] * 100
        costs = results[f"sc_1_{d}_{wacc}"]["price_per_MWh"]
        # print(f"{d} & {round(m)} & $ {round(load_factor_ecosystem, 1)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")

    # Print Losses table
    print(f"\\toprule")
    print("d [km] & $E_{cycle}$ & $L_{discard}$ & $L_{prop}$ & $L_{+}$ & $L_{crane}$ & $L_{rt}$ & $L_{-}$ & $L_{DC-AC}$ & $E_{grid}$\\\\")
    print(f"\\midrule")
    for d in distances:
        E_cycle = results[f"sc_1_{d}_{wacc}"]["E_cycle"]
        L_discard = results[f"sc_1_{d}_{wacc}"]["L_discard"]
        L_prop = results[f"sc_1_{d}_{wacc}"]["L_prop"]
        L_charge = results[f"sc_1_{d}_{wacc}"]["L_charge"]
        L_crane = results[f"sc_1_{d}_{wacc}"]["L_crane"]
        L_rt = results[f"sc_1_{d}_{wacc}"]["L_rt"]
        L_discharge = results[f"sc_1_{d}_{wacc}"]["L_discharge"]
        L_DC_AC = results[f"sc_1_{d}_{wacc}"]["L_DC_AC"]
        E_to_grid = results[f"sc_1_{d}_{wacc}"]["E_to_grid"]
        print(f"{d} & {round(E_cycle, 1)} & {round(L_discard, 1)} & {round(L_prop, 1)} & {round(L_charge, 1)} & {round(L_crane, 1)} & {round(L_rt, 1)} & {round(L_discharge, 1)} & {round(L_DC_AC, 1)} & {round(E_to_grid, 1)} \\\\")
        # print(f"{d} & {round(L_prop, 2)} & {round(L_charge, 2)} & {round(L_crane, 2)} & {round(L_rt, 2)} & {round(L_discharge, 2)} & {round(L_DC_AC, 2)} \\\\")
        # balance = E_cycle - L_discard - L_prop - L_charge - L_crane - L_rt - L_discharge - L_DC_AC
        # print(f"{balance = }")
    print(f"\\bottomrule")
    print(f"{L_crane}")

