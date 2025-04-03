import matplotlib.pyplot as plt
import numpy as np
from CONSTANTES import (
    MU, BATTERY_PRICE, AIRSHIP_LIFETIME, DRONE_LIFETIME, BATTERY_LIFETIME, TURBINE_LIFETIME, 
    TURBINE_PRICE, DC_AC_efficiency, charge_efficiency, prop_efficiency, CF, AIRSHIP_VELOCITY_H, 
    AIRSHIP_VELOCITY_L, d_prime, m_pack, UFWT_INSTALLED_POWER, DRONE_PRICE, AIRSHIP_PRICE, AIRSHIP_ALTITUDE
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
    distances = [150, 400, 2000]
    P = 100  # Wind farm power (MW)
    # wacc = 0.10  # Weighted average cost of capital
    results = {}

    for wacc in [0.07]:
        for d in distances:        
            round_trip_in_hours = 2 * d / AIRSHIP_VELOCITY_L
            
            E = P * round_trip_in_hours * CF # Total energy (MWh)
            E_max_per_year = P * 8760  # Maximum energy per year (MWh)
            n_ufwt = P / UFWT_INSTALLED_POWER
            
            L_prop = E * prop_efficiency
            L_charge = E * prop_efficiency * (1-charge_efficiency)
            E_in_batteries = E - L_prop - L_charge
            m = E_in_batteries / MU  # Optimal boat mass (tons)

            # if m > 4400:
            #     print("Load capacity exceeds airship limit.")
            #     continue
            
            L_rt = 2 * d * airship_consumption_L(m) * m
            L_rtwa = n_ufwt * d_prime * airship_consumption_H(m) * m
            L_rtd = 2 * AIRSHIP_ALTITUDE * drone_consumption(m_pack) * m

            # print(f"CONSOMMATION")
            # print(f"{L_rtd = }, {L_rtdr = }")


            # from CONSTANTES import g, Joule_to_MWh, elec_efficiency
            # h = 9000 # Airship altitude (m)
            # L_crane = ((m * g * h / 1000) * Joule_to_MWh) / elec_efficiency
            # print(f"{L_crane = } VS {L_rtd = }")  

            
            
            L_discharge = (1-charge_efficiency) * E_in_batteries
            L_DC_AC = (1-DC_AC_efficiency) * (E_in_batteries - L_discharge - L_rt - L_rtd - L_rtwa)
            
            # rtd_efficiency = 1 - 2 * 0.75 * drone_consumption(m_pack) / MU
            # rtla_efficiency = 1 - 2 * d * airship_consumption_L(m) / MU
            # rtwa_efficiency = 1 - (m / (battery_pack_per_UFWT(P, m) * m_pack) * d_prime / 2) * airship_consumption_H(m) / MU

            # E_to_grid = E * rtd_efficiency * rtwa_efficiency * rtla_efficiency * charge_efficiency * DC_AC_efficiency
            E_to_grid = E_in_batteries - L_rt - L_rtd - L_rtwa - L_discharge - L_DC_AC

            # time_to_cover_wind_farm = battery_pack_per_UFWT(P, m) * d_prime / (2 * AIRSHIP_VELOCITY_H)
            time_to_cover_wind_farm = (n_ufwt * d_prime) / (2 * AIRSHIP_VELOCITY_H)
            cycle_time = round_trip_in_hours + time_to_cover_wind_farm
            num_cycles = 8760 / cycle_time
            E_to_grid_per_year = E_to_grid * num_cycles

            print(f"{cycle_time = }")

            L_discard = P * time_to_cover_wind_farm * CF
            # print(f"{L_discard = }")

            n_batteries = m / m_pack
            n_batteries_per_UFWT = n_batteries / n_ufwt
            print(f"HEEEELLLLLLO")
            print(f"{d = }, {n_batteries = }, {n_batteries_per_UFWT = }")

            load_factor_ecosystem = E_to_grid_per_year / E_max_per_year

            price_batteries = BATTERY_PRICE * m * MU
            annuity_batteries = (price_batteries * wacc) / (1 - (1 + wacc) ** -BATTERY_LIFETIME)
            price_airships = AIRSHIP_PRICE * (m / 4400)
            annuity_airships = (price_airships * wacc) / (1 - (1 + wacc) ** -AIRSHIP_LIFETIME)
            num_drones = round(n_batteries_per_UFWT) if round(n_batteries_per_UFWT) > 1 else 1
            # num_drones = m / (5 * m_pack) 
            price_drones = DRONE_PRICE * num_drones
            annuity_drones = (price_drones * wacc) / (1 - (1 + wacc) ** -DRONE_LIFETIME)
            price_ufwt = TURBINE_PRICE * P
            annuity_ufwt = (price_ufwt * wacc) / (1 - (1 + wacc) ** -TURBINE_LIFETIME)

            total_annuity = 3 * annuity_batteries + annuity_drones + annuity_airships + annuity_ufwt
            print(f"{total_annuity = }")
            print(f"{annuity_airships = }, {annuity_drones = }, {annuity_batteries = }, {annuity_ufwt = }")
            price_per_MWh = total_annuity / E_to_grid_per_year
            efficiency = overall_efficiency(d, m, P)


            load_factor_ecosystem = E_to_grid_per_year / E_max_per_year


            loss_during_supply = L_discard + L_prop + L_charge + L_rt + L_rtd + L_rtwa + L_discharge + L_DC_AC
            E_cycle = P * cycle_time * CF
            balance = E_cycle - loss_during_supply - E_to_grid
            
            E_max_cycle = P * cycle_time

            # print(f"{balance = }")
            # print(f"{E_to_grid/E_cycle = }")
            # print(f"{E_to_grid/E_max_cycle = }")
            # print(f"{E_to_grid_per_year = }")


            results[f"sc_2_{d}_{wacc}"] = {"distance":d, 
                                    "size_m": m, 
                                    "price_per_MWh": price_per_MWh,
                                    "efficiency": efficiency,
                                    "load_factor_ecosystem": load_factor_ecosystem,
                                    "num_drones": num_drones,
                                    "annuity_drones": annuity_drones,
                                    "annuity_airships": annuity_airships,
                                    "annuity_batteries": annuity_batteries,
                                    "annuity_ufwt": annuity_ufwt,
                                    "total_annuity": total_annuity,
                                    "E_to_grid_per_year": E_to_grid_per_year,
                                    "E_max_per_year": E_max_per_year,
                                    "wacc": wacc,
                                    "L_discard": L_discard,
                                    "L_prop": L_prop,
                                    "L_charge": L_charge,
                                    "E_in_batteries": E_in_batteries,
                                    "m": m,
                                    "L_rt": L_rt,
                                    "L_rtwa": L_rtwa,
                                    "L_rtd": L_rtd,
                                    "L_discharge": L_discharge,
                                    "L_DC_AC": L_DC_AC,
                                    "E_cycle": E_cycle,
                                    "E_to_grid": E_to_grid,
                                    "time_to_cover_wind_farm": time_to_cover_wind_farm,
                                    "cycle_time": cycle_time,
                                    "num_cycles": num_cycles
                                    }


    import json
    with open('results/results_sc2.json', 'w') as f:
        json.dump(results, f)

    

    print(f"\\toprule")
    print(f"d [km] & m [ton] & $ \\pi_e $ [\\%] & $c_e $ [\\$/MWh]\\\\")
    print(f"\\midrule")
    for d in distances:
        m = results[f"sc_2_{d}_{wacc}"]["size_m"]
        efficiency = results[f"sc_2_{d}_{wacc}"]["efficiency"] * 100
        load_factor_ecosystem = results[f"sc_2_{d}_{wacc}"]["load_factor_ecosystem"] * 100
        costs = results[f"sc_2_{d}_{wacc}"]["price_per_MWh"]
        print(f"{d} & {round(m)} & $ {round(load_factor_ecosystem, 1)} $ & {round(costs)} \\\\")

    print(f"\\bottomrule")

    # Print Losses table
    print(f"\\toprule")
    print("d [km] & $L_{prop}$ & $L_{charge}$ & $L_{rt}$ [\\%] & $L_{rtwa}$ & $L_{rtd}$ & $L_{discharge}$ & $L_{DC-AC}$ \\\\")
    print(f"\\midrule")
    for d in distances:
        L_prop = results[f"sc_2_{d}_{wacc}"]["L_prop"]
        L_charge = results[f"sc_2_{d}_{wacc}"]["L_charge"]
        L_rt = results[f"sc_2_{d}_{wacc}"]["L_rt"]
        L_rtwa = results[f"sc_2_{d}_{wacc}"]["L_rtwa"]
        L_rtd = results[f"sc_2_{d}_{wacc}"]["L_rtd"]
        L_discharge = results[f"sc_2_{d}_{wacc}"]["L_discharge"]
        L_DC_AC = results[f"sc_2_{d}_{wacc}"]["L_DC_AC"]
        print(f"{d} & {round(L_prop, 1)} & {round(L_charge, 1)} & {round(L_rt, 1)} & {round(L_rtwa, 1)} & {round(L_rtd, 1)} & {round(L_discharge, 1)} & {round(L_DC_AC, 1)} \\\\")
    print(f"\\bottomrule")
    print(f"{L_rtwa = }")

    # Print Prices table
    print(f"\\toprule")
    print(f"d [km] & UFWT [\\%] & Batteries [\\%] & Drones [\\%] & Airship [\\%] \\\\")    
    print(f"\\midrule")
    for d in distances:
        annuity_batteries = results[f"sc_2_{d}_{wacc}"]["annuity_batteries"]
        annuity_airships = results[f"sc_2_{d}_{wacc}"]["annuity_airships"]
        annuity_drones = results[f"sc_2_{d}_{wacc}"]["annuity_drones"]
        annuity_ufwt = results[f"sc_2_{d}_{wacc}"]["annuity_ufwt"]
        total_annuity = results[f"sc_2_{d}_{wacc}"]["total_annuity"]
        # print(f"{d} & {round(annuity_batteries, 1)} & {round(annuity_airships, 1)} & {round(annuity_drones, 1)} & {round(annuity_ufwt, 1)} & {round(total_annuity, 1)} \\\\")
        # Print percentage of total annuity
        print(f"{d} & {round(annuity_ufwt/total_annuity * 100, 1)} & {round(3 * annuity_batteries/total_annuity * 100, 1)} & {round(annuity_drones/total_annuity * 100, 1)} & {round(annuity_airships/total_annuity * 100, 1)} \\\\")
    print(f"\\bottomrule")
    print(f"{L_rtwa = }")

    # Print Energy and Losses per cycle table
    print(f"\\toprule")
    print("d [km] & $E_{cycle}$ & $L_{+}$ & $L_{prop}$ & $L_{charge}$ & $L_{rtd}$ & $L_{rt}$ & $L_{rtwa}$ & $L_{-}$ & $L_{DC-AC}$ & $E_{grid}$ \\\\")
    print(f"\\midrule")
    for d in distances:
        E_cycle = results[f"sc_2_{d}_{wacc}"]["E_cycle"]
        L_discard = results[f"sc_2_{d}_{wacc}"]["L_discard"]
        L_prop = results[f"sc_2_{d}_{wacc}"]["L_prop"]
        L_charge = results[f"sc_2_{d}_{wacc}"]["L_charge"]
        L_rt = results[f"sc_2_{d}_{wacc}"]["L_rt"]
        L_rtwa = results[f"sc_2_{d}_{wacc}"]["L_rtwa"]
        L_rtd = results[f"sc_2_{d}_{wacc}"]["L_rtd"]
        L_discharge = results[f"sc_2_{d}_{wacc}"]["L_discharge"]
        L_DC_AC = results[f"sc_2_{d}_{wacc}"]["L_DC_AC"]
        E_to_grid = results[f"sc_2_{d}_{wacc}"]["E_to_grid"]
        print(f"{d} & {round(E_cycle, 1)} & {round(L_discard, 1)} & {round(L_prop, 1)} & {round(L_charge, 1)} & {round(L_rtd, 1)} & {round(L_rt, 1)} & {round(L_rtwa, 1)} & {round(L_discharge, 1)} & {round(L_DC_AC, 1)} & {round(E_to_grid, 1)} \\\\")
        # Print percentage of E_cycle
        # print(f"{d} & {round(E_cycle/E_cycle, 1)} & {round(L_discard/E_cycle, 1)} & {round(L_prop/E_cycle, 1)} & {round(L_charge/E_cycle, 1)} & {round(L_rt/E_cycle, 1)} & {round(L_rtwa/E_cycle, 1)} & {round(L_rtd/E_cycle, 1)} & {round(L_discharge/E_cycle, 1)} & {round(L_DC_AC/E_cycle, 1)} & {round(E_to_grid/E_cycle)} \\\\")
    print(f"\\bottomrule")

