import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import (
    MU, BATTERY_PRICE, AIRSHIP_LIFETIME, DRONE_LIFETIME, BATTERY_LIFETIME, TURBINE_LIFETIME, 
    TURBINE_PRICE, DC_AC_efficiency, charge_efficiency, prop_efficiency, CF, AIRSHIP_VELOCITY_H, 
    AIRSHIP_VELOCITY_L, d_prime, m_pack, UFWT_INSTALLED_POWER, DRONE_PRICE, AIRSHIP_PRICE
)
from transportation_consumption import airship_consumption_H, airship_consumption_L, drone_consumption
from scenario_1 import pack_per_UFWT_S1

def cost_transportation_airship(d, m):
    """Calculate the transportation cost using airships in $/MWh."""
    t = 2 * d / AIRSHIP_VELOCITY_L + m / (pack_per_UFWT_S2(d, m) * m_pack) * d_prime / (2 * AIRSHIP_VELOCITY_H)  # hours
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU  # Efficiency from HHS to seaport
    rtwa_efficiency = 1 - (m / (pack_per_UFWT_S2(d, m) * m_pack) * d_prime / 2) * airship_consumption_H(m) / MU  # Efficiency within HHS
    E = m * MU * rtla_efficiency * rtwa_efficiency  # Energy at arrival (MWh)
    J = E / (m * t) * DC_AC_efficiency * charge_efficiency  # Normalized energy to grid (MWh / t-h)
    I = 3 * (BATTERY_PRICE * MU) / (BATTERY_LIFETIME * 365 * 24) + AIRSHIP_PRICE / (m * AIRSHIP_LIFETIME * 365 * 24)  # $/t-h
    return I / J

def cost_transportation_drones(d, m):
    """Calculate the transportation cost using drones in $/MWh."""
    t = 2 * d / AIRSHIP_VELOCITY_L + m / (pack_per_UFWT_S2(d, m) * m_pack) * d_prime / (2 * AIRSHIP_VELOCITY_H)  # hours
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU  # Efficiency from HHS to seaport
    rtwa_efficiency = 1 - (m / (pack_per_UFWT_S2(d, m) * m_pack) * d_prime / 2) * airship_consumption_H(m) / MU  # Efficiency within HHS
    rtd_efficiency = 1 - 2 * 0.75 * drone_consumption(m_pack) / MU  # Drone efficiency (mean distance = 2 * 0.75 km)
    E = m * MU * rtla_efficiency * rtwa_efficiency  # Energy at arrival (MWh)
    J = E / (m * t) * DC_AC_efficiency * charge_efficiency  # Normalized energy to grid (MWh / t-h)
    I = 1 / (5 * rtd_efficiency) * DRONE_PRICE / (m_pack * DRONE_LIFETIME * 365 * 24)  # $/t-h
    return I / J

def cost_production(d, m):
    """Calculate the production cost of energy in $/MWh."""
    t = 2 * d / AIRSHIP_VELOCITY_L + m / (pack_per_UFWT_S2(d, m) * m_pack) * d_prime / (2 * AIRSHIP_VELOCITY_H)  # hours
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU  # Efficiency from HHS to seaport
    rtwa_efficiency = 1 - (m / (pack_per_UFWT_S2(d, m) * m_pack) * d_prime / 2) * airship_consumption_H(m) / MU  # Efficiency within HHS
    rtd_efficiency = 1 - 2 * 0.75 * drone_consumption(m_pack) / MU  # Drone efficiency (mean distance = 2 * 0.75 km)
    E = m * MU * rtla_efficiency * rtwa_efficiency  # Energy at arrival (MWh)
    J = E / (m * t) * DC_AC_efficiency * charge_efficiency  # Normalized energy to grid (MWh / t-h)
    P_install = (m * MU) / (rtd_efficiency * prop_efficiency * charge_efficiency * t * CF)  # Wind farm power (MW)
    I = (TURBINE_PRICE * P_install) / (m * TURBINE_LIFETIME * 365 * 24)  # $/t-h
    return I / J

def overall_costs(d, m):
    """Compute the total costs including transportation and production."""
    return cost_transportation_airship(d, m) + cost_transportation_drones(d, m) + cost_production(d, m)

def overall_efficiency(d, m, P):
    """Calculate the overall energy efficiency."""
    rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU
    rtwa_efficiency = 1 - (m / (battery_pack_per_UFWT(P, m) * m_pack) * d_prime / 2) * airship_consumption_H(m) / MU
    rtd_efficiency = 1 - 2 * 0.75 * drone_consumption(m_pack) / MU
    return charge_efficiency * prop_efficiency * rtd_efficiency * rtwa_efficiency * rtla_efficiency * charge_efficiency * DC_AC_efficiency

def pack_per_UFWT_S2(d, m):
    """Iteratively determine the number of battery packs per UFWT."""
    n_w = pack_per_UFWT_S1(d, m)
    n_w1, n_w2 = n_w, 10000

    for _ in range(10):
        if abs(n_w2 - n_w1) < 0.5:
            break
        n_w2 = n_w1
        t = 2 * d / AIRSHIP_VELOCITY_L + m / (n_w1 * m_pack) * d_prime / (2 * AIRSHIP_VELOCITY_H)  # hours
        n_w1 = (UFWT_INSTALLED_POWER * t * charge_efficiency * prop_efficiency * CF) / (m_pack * MU)

    return n_w1

def losses_drone(d, m):
    """Calculate the percentage of energy consumed by drones for motion."""
    return (d * drone_consumption(m) / MU) * 100

def losses_airship(d, m):
    """Calculate the percentage of energy consumed by airships for motion."""
    return (d * airship_consumption_L(m) / MU) * 100

def battery_pack_per_UFWT(P, m):
    """Determine the number of battery packs per UFWT."""
    round_trip_in_hours = 2 * d / AIRSHIP_VELOCITY_L
    E = P * round_trip_in_hours * CF * charge_efficiency * prop_efficiency  # Energy (MWh)
    n_ufwt = P / UFWT_INSTALLED_POWER
    ton_per_ufwt = m / n_ufwt
    n_w = ton_per_ufwt / m_pack
    return n_w

if __name__ == '__main__':
    distances = [30, 150, 400, 2000]
    P = 100  # Wind farm power (MW)
    # wacc = 0.10  # Weighted average cost of capital
    results = {}

    for wacc in [0.07]:
        for d in distances:
            round_trip_in_hours = 2 * d / AIRSHIP_VELOCITY_L
            E = P * round_trip_in_hours * CF * charge_efficiency * prop_efficiency
            E_max_per_year = P * 8760 * CF * charge_efficiency * prop_efficiency
            m = E / MU
            if m > 4400:
                print("Load capacity exceeds airship limit.")
                continue

            rtd_efficiency = 1 - 2 * 0.75 * drone_consumption(m_pack) / MU
            rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU
            rtwa_efficiency = 1 - (m / (battery_pack_per_UFWT(P, m) * m_pack) * d_prime / 2) * airship_consumption_H(m) / MU

            E_to_grid = E * rtd_efficiency * rtwa_efficiency * rtla_efficiency * charge_efficiency * DC_AC_efficiency
            # /!\ This is not the correct formula
            # loading_time = 4 * r * m
            time_to_cover_wind_farm = battery_pack_per_UFWT(P, m) * d_prime / (2 * AIRSHIP_VELOCITY_H)
            time_to_cover_wind_farm = m / (battery_pack_per_UFWT(P, m) * m_pack) * d_prime / (2 * AIRSHIP_VELOCITY_H)
            cycle_time = round_trip_in_hours + time_to_cover_wind_farm
            num_cycles = 8760 / cycle_time
            E_to_grid_per_year = E_to_grid * num_cycles

            price_batteries = BATTERY_PRICE * m * MU
            annuity_batteries = (price_batteries * wacc) / (1 - (1 + wacc) ** -BATTERY_LIFETIME)
            price_airships = AIRSHIP_PRICE * (m / 4400)
            annuity_airships = (price_airships * wacc) / (1 - (1 + wacc) ** -AIRSHIP_LIFETIME)
            num_drones = round(m / (5 * m_pack)) + 1
            # num_drones = m / (5 * m_pack)
            price_drones = DRONE_PRICE * num_drones
            annuity_drones = (price_drones * wacc) / (1 - (1 + wacc) ** -DRONE_LIFETIME)
            price_ufwt = TURBINE_PRICE * P
            annuity_ufwt = (price_ufwt * wacc) / (1 - (1 + wacc) ** -TURBINE_LIFETIME)

            total_annuity = 3 * annuity_batteries + annuity_drones + annuity_airships + annuity_ufwt
            price_per_MWh = total_annuity / E_to_grid_per_year
            efficiency = overall_efficiency(d, m, P)

            results[f"sc_2_{d}_{wacc}"] = {"distance":d, 
                                    "size_m": m, 
                                    "price_per_MWh": price_per_MWh,
                                    "efficiency": efficiency,
                                    "num_drones": num_drones,
                                    "annuity_drones": annuity_drones,
                                    "annuity_airships": annuity_airships,
                                    "annuity_batteries": annuity_batteries,
                                    "annuity_ufwt": annuity_ufwt,
                                    "total_annuity": total_annuity,
                                    "E_to_grid_per_year": E_to_grid_per_year,
                                    "E_max_per_year": E_max_per_year,
                                    "wacc": wacc
                                    }

    for key, value in results.items():
        print(key, value)

    import json
    with open('results/results_sc2.json', 'w') as f:
        json.dump(results, f)

    

    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\eta_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = results[f"sc_2_{d}_{wacc}"]["size_m"]
        efficiency = results[f"sc_2_{d}_{wacc}"]["efficiency"] * 100
        costs = results[f"sc_2_{d}_{wacc}"]["price_per_MWh"]
        print(f"{d} & {round(m)} & $ {round(efficiency, 1)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")

    for d in distances:
        # print share of costs
        print(f"Distance: {d} km")
        total_annuity = results[f"sc_2_{d}_{wacc}"]["total_annuity"]
        annuity_batteries = results[f"sc_2_{d}_{wacc}"]["annuity_batteries"]
        annuity_airships = results[f"sc_2_{d}_{wacc}"]["annuity_airships"]
        annuity_drones = results[f"sc_2_{d}_{wacc}"]["annuity_drones"]
        annuity_ufwt = results[f"sc_2_{d}_{wacc}"]["annuity_ufwt"]

        print(f"Total annuity: {total_annuity}")
        print(f"Share of batteries: {annuity_batteries / total_annuity * 100}")
        print(f"Share of airships: {annuity_airships / total_annuity * 100}")
        print(f"Share of drones: {annuity_drones / total_annuity * 100}")
        print(f"Share of UFWT: {annuity_ufwt / total_annuity * 100}")
        print()

        print(f"Distance: {d} km")
        # print total costs 
        print(f"Total annuity: {total_annuity}")
        print(f"Annuitiy of batteries: {annuity_batteries}")
        print(f"Annuitiy of airships: {annuity_airships}")
        print(f"Annuitiy of drones: {annuity_drones}")
        print(f"Annuitiy of UFWT: {annuity_ufwt}")
        print()


