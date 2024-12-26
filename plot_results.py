import matplotlib.pyplot as plt
import numpy as np
import json

# Load results from JSON file
results = json.load(open("results/results_sc2.json", "r"))

# Organize data for plotting
distances = sorted(set(value["distance"] for value in results.values()))
components = ["annuity_ufwt", "annuity_batteries", "annuity_airships", "annuity_drones"]  # Components
colors = ['#d62728', '#2ca02c', '#ff7f0e', '#1f77b4']  # Colors for components
component_labels = ['UFWT', 'Batteries', 'Airships', 'Drones']  # Matching labels

# Prepare data for plotting
cost_per_component = {d: {comp: 0 for comp in components} for d in distances}

for key, value in results.items():
    distance = value["distance"]
    for comp in components:
        cost_per_component[distance][comp] += value[comp]

# Create data arrays
x_positions = np.arange(len(distances))  # Positions for distances
bar_width = 0.2  # Width of each bar

fig, ax = plt.subplots(figsize=(12, 6))

# Plot bars for each component
for i, comp in enumerate(components):
    heights = [cost_per_component[d][comp] for d in distances]
    ax.bar(x_positions + i * bar_width, heights, bar_width, label=component_labels[i], color=colors[i])

# Customize the plot
ax.set_xticks(x_positions + (len(components) - 1) * bar_width / 2)
ax.set_xticklabels([f"{d} km" for d in distances])
ax.set_xlabel("Distance (d)")
ax.set_ylabel("Cost per Component (€)")
ax.set_title("Cost per Component by Distance")
ax.legend(title="Cost Components", loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()

plt.savefig("results/cost_per_component.png", dpi = 1000)

# Show plot
plt.show()

import matplotlib.pyplot as plt
import numpy as np
import json

# Load results from JSON file
results = json.load(open("results/results_sc2.json", "r"))

# Organize data for plotting
distances = sorted(set(value["distance"] for value in results.values()))
components = ["annuity_ufwt", "annuity_batteries", "annuity_airships", "annuity_drones"]  # Components
colors = ['#d62728', '#2ca02c', '#ff7f0e', '#1f77b4']  # Colors for components
component_labels = ['UFWT', 'Batteries', 'Airships', 'Drones']  # Matching labels

# Prepare data for plotting
cost_per_component = {d: {comp: 0 for comp in components} for d in distances}

for key, value in results.items():
    distance = value["distance"]
    for comp in components:
        cost_per_component[distance][comp] += value[comp]

# Prepare data for the stacked bar plot
x_positions = np.arange(len(distances))
width = 0.6

fig, ax = plt.subplots(figsize=(12, 6))

# Plot each component's contribution in a stacked bar
bottoms = np.zeros(len(distances))  # Initialize bottom for stacking
for i, comp in enumerate(components):
    heights = [cost_per_component[d][comp] for d in distances]
    ax.bar(x_positions, heights, width, bottom=bottoms, label=component_labels[i], color=colors[i])
    bottoms += heights  # Update bottoms for the next component

# Customize the plot
ax.set_xticks(x_positions)
ax.set_xticklabels([f"{d} km" for d in distances])
ax.set_xlabel("Distance (d)")
ax.set_ylabel("Total Cost (€)")
ax.set_title("Stacked Cost per Component by Distance")
ax.legend(title="Cost Components", loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()

plt.savefig("results/stacked_cost_per_component.png", dpi = 1000)

# Show plot
plt.show()

import matplotlib.pyplot as plt
import numpy as np
import json

# Load results from JSON file
results = json.load(open("results/results_sc2.json", "r"))

# Organize data for plotting
distances = sorted(set(value["distance"] for value in results.values()))
components = ["annuity_ufwt", "annuity_batteries", "annuity_airships", "annuity_drones"]  # Components
colors = ['#d62728', '#2ca02c', '#ff7f0e', '#1f77b4']  # Colors for components
component_labels = ['UFWT', 'Batteries', 'Airships', 'Drones']  # Matching labels

# Prepare data for plotting
cost_per_MWh = {d: {comp: 0 for comp in components} for d in distances}

for key, value in results.items():
    distance = value["distance"]
    energy_delivered = value["E_to_grid_per_year"]
    for comp in components:
        cost_per_MWh[distance][comp] += value[comp] / energy_delivered  # Calculate cost per MWh

# Prepare data for the stacked bar plot
x_positions = np.arange(len(distances))
width = 0.6

fig, ax = plt.subplots(figsize=(12, 6))

# Plot each component's contribution in a stacked bar
bottoms = np.zeros(len(distances))  # Initialize bottom for stacking
for i, comp in enumerate(components):
    heights = [cost_per_MWh[d][comp] for d in distances]
    ax.bar(x_positions, heights, width, bottom=bottoms, label=component_labels[i], color=colors[i])
    bottoms += heights  # Update bottoms for the next component

# Customize the plot
ax.set_xticks(x_positions)
ax.set_xticklabels([f"{d} km" for d in distances])
ax.set_xlabel("Distance (d)")
ax.set_ylabel("Cost ($/MWh)")
ax.set_title("Stacked Cost per Component by Distance (Cost in $/MWh)")
ax.legend(title="Cost Components", loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()

plt.savefig("results/stacked_cost_per_component_per_mwh.png", dpi = 1000)
# Show plot
plt.show()
