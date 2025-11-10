#!/usr/bin/env python
"""Analyze plant_traits.json structure and content."""

import json
from collections import defaultdict

# Load the plant traits JSON
with open('hackathon-case_study-experimental_warming_nitrogen/plant_traits.json') as f:
    traits = json.load(f)

print(f"Total trait entries: {len(traits)}")
print()

# Analyze structure
plant_types = set()
variables = set()
units = set()

for trait in traits:
    plant_types.add(trait.get('plant_type', 'Unknown'))
    variables.add(trait.get('variable', 'Unknown'))
    units.add(trait.get('unit', 'Unknown'))

print(f"Unique plant types: {len(plant_types)}")
print("Plant types:")
for pt in sorted(plant_types):
    print(f"  - {pt}")
print()

print(f"Unique variables: {len(variables)}")
print("Variables:")
for var in sorted(variables):
    print(f"  - {var}")
print()

print(f"Unique units: {len(units)}")
print()

# Group by plant type
by_plant = defaultdict(list)
for trait in traits:
    by_plant[trait.get('plant_type', 'Unknown')].append(trait)

print("Trait counts by plant type:")
for pt, traits_list in sorted(by_plant.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {pt}: {len(traits_list)} traits")
print()

# Show example trait structure
print("Example trait entry (first one):")
print(json.dumps(traits[0], indent=2))
