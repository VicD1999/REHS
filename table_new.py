from CONSTANTES import BATTERY_LIFETIME, TURBINE_LIFETIME, BOAT_LIFETIME, AIRSHIP_LIFETIME, DRONE_LIFETIME, BATTERY_PRICE, TURBINE_PRICE, BOAT_VELOCITY, AIRSHIP_VELOCITY_L, DRONE_VELOCITY, AIRSHIP_PRICE, DRONE_PRICE
from transportation_CAPEX import boat_CAPEX
from transportation_optimal_cost import boat_opti_mass
from scenario_1 import losses_boat
from scenario_2 import losses_airship, losses_drone

import json

results = json.load(open("results/results_sc1.json", "r"))

distances = [30, 150, 400, 2000] # km

ms = [results[f"sc_1_{d}_0.1"]["size_m"] for d in distances]

dico = {**{"Battery pack": (BATTERY_LIFETIME, f"{round(BATTERY_PRICE/1000)} \$/kWh", -1, -1),
           "UFWT": (TURBINE_LIFETIME, f"{round(TURBINE_PRICE)} \$/MW", -1, -1)},
        **{f"Boat ({m:.0f} tons)": (BOAT_LIFETIME, f"{round(boat_CAPEX(m))} \$/ton", BOAT_VELOCITY, losses_boat(1000, m)) 
           for m in ms},
        "Airship": (AIRSHIP_LIFETIME, f"{round(AIRSHIP_PRICE / 4400)} \$/ton" , AIRSHIP_VELOCITY_L, losses_airship(1000, 4400)),
        "Drone (30 tons)": (DRONE_LIFETIME, f"{round(DRONE_PRICE / 30)} \$/ton", DRONE_VELOCITY, losses_drone(1, 30))}

latex_table = ""
# Ajout de chaque ligne de données à partir du dictionnaire
for component, values in dico.items():
    lifetime = values[0]
    capex = values[1]
    velocity = values[2] if values[2] != -1 else "/"  # Si la valeur est "_", on met "/"
    losses = f"{round(values[3])} \%/1000km " if values[3] != -1 else "/"   # Idem pour les pertes d'énergie
    if component.startswith("Drone"):
        losses = f"{round(values[3])} \%/km " if values[3] != -1 else "/"

    latex_table += f"    {component} & ${lifetime}$ & {capex} & {velocity} & {losses} \\\\\n"


# Affichage du tableau LaTeX généré
print(latex_table)

