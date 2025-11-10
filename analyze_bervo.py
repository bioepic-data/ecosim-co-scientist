#!/usr/bin/env python
"""Analyze BERVO ontology and find plant-related terms."""

import csv
from collections import defaultdict

# Read BERVO terms
bervo_file = 'hackathon-case_study-experimental_warming_nitrogen/bervo/bervo-terms.tsv'

with open(bervo_file, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    bervo_terms = list(reader)

print(f"Total BERVO terms: {len(bervo_terms)}")
print()

# Analyze categories
categories = defaultdict(int)
for term in bervo_terms:
    cat = term.get('Category', 'Unknown')
    if cat:
        categories[cat] += 1

print(f"Categories ({len(categories)}):")
for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f"  {cat}: {count}")
print()

# Look for plant-related terms
plant_keywords = ['plant', 'leaf', 'root', 'photosynthesis', 'carbon', 'nitrogen',
                   'rubisco', 'chlorophyll', 'carboxylation', 'transpiration',
                   'uptake', 'vcmax', 'jmax']

plant_related = []
for term in bervo_terms:
    label = term.get('Label (description)', '').lower()
    definition = term.get('Definition', '').lower()
    ecosim_var = term.get('EcoSIM Variable Name', '').lower()

    if any(kw in label or kw in definition or kw in ecosim_var for kw in plant_keywords):
        plant_related.append(term)

print(f"Plant-related terms: {len(plant_related)}")
print()

# Show sample plant terms
print("Sample plant-related terms (first 20):")
for i, term in enumerate(plant_related[:20]):
    print(f"  {term['ID']}: {term['Label (description)']}")
    if term.get('has_units'):
        print(f"    Units: {term['has_units']}")
print()

# Look for terms with specific measurement contexts
measured_in_plant = []
for term in bervo_terms:
    measured_in = term.get('measured_ins', '')
    if 'Plant' in measured_in or 'Root' in measured_in or 'Leaf' in measured_in:
        measured_in_plant.append(term)

print(f"Terms measured in Plant/Root/Leaf: {len(measured_in_plant)}")
print()

# Show terms by file name to understand organization
file_names = defaultdict(list)
for term in bervo_terms:
    fname = term.get('File Name', '')
    if fname:
        file_names[fname].append(term['ID'])

print(f"Unique EcoSIM files referenced: {len(file_names)}")
for fname, terms in sorted(file_names.items()):
    print(f"  {fname}: {len(terms)} terms")
