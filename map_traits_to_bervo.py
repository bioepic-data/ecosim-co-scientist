#!/usr/bin/env python
"""Map plant_traits.json variables to BERVO ontology terms."""

import json
import csv
from difflib import SequenceMatcher

# Load plant traits
with open('hackathon-case_study-experimental_warming_nitrogen/plant_traits.json') as f:
    traits = json.load(f)

# Load BERVO terms
with open('hackathon-case_study-experimental_warming_nitrogen/bervo/bervo-terms.tsv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    bervo_terms = list(reader)

# Filter for plant trait terms
plant_trait_bervo = [t for t in bervo_terms if t.get('Category') == 'Plant trait data type']

print(f"Plant trait JSON has {len(traits)} entries")
print(f"BERVO has {len(plant_trait_bervo)} Plant trait data type terms")
print()

# Extract unique variables from plant_traits.json
trait_variables = {}
for trait in traits:
    var = trait['variable']
    if var not in trait_variables:
        trait_variables[var] = {
            'unit': trait['unit'],
            'plant_types': []
        }
    trait_variables[var]['plant_types'].append(trait['plant_type'])

print(f"Unique variables in plant_traits.json: {len(trait_variables)}")
print()

# Try to map each variable to BERVO terms
def similarity(a, b):
    """Calculate string similarity."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

print("Mapping plant trait variables to BERVO:")
print("=" * 80)

mappings = []
for var_name, var_info in sorted(trait_variables.items()):
    print(f"\nVariable: {var_name}")
    print(f"  Unit: {var_info['unit']}")

    # Find best BERVO matches
    matches = []
    for bervo_term in plant_trait_bervo:
        label = bervo_term.get('Label (description)', '')
        ecosim_name = bervo_term.get('EcoSIM Variable Name', '')

        # Calculate similarity scores
        label_sim = similarity(var_name, label)
        ecosim_sim = similarity(var_name, ecosim_name) if ecosim_name else 0

        max_sim = max(label_sim, ecosim_sim)
        if max_sim > 0.3:  # Threshold for considering a match
            matches.append({
                'bervo_id': bervo_term['ID'],
                'label': label,
                'ecosim_var': ecosim_name,
                'unit': bervo_term.get('has_units', ''),
                'similarity': max_sim,
                'match_type': 'label' if label_sim > ecosim_sim else 'ecosim_var'
            })

    matches.sort(key=lambda x: x['similarity'], reverse=True)

    if matches:
        print(f"  Potential BERVO matches:")
        for match in matches[:3]:  # Show top 3
            print(f"    {match['bervo_id']}: {match['label']}")
            print(f"      Similarity: {match['similarity']:.2f} (via {match['match_type']})")
            if match['unit']:
                print(f"      Unit: {match['unit']}")
    else:
        print(f"  No strong BERVO matches found")

    mappings.append({
        'variable': var_name,
        'unit': var_info['unit'],
        'best_match': matches[0] if matches else None
    })

# Summary statistics
mapped = sum(1 for m in mappings if m['best_match'] and m['best_match']['similarity'] > 0.5)
print()
print("=" * 80)
print(f"\nSummary:")
print(f"  Total variables: {len(mappings)}")
print(f"  Strong matches (>0.5 similarity): {mapped}")
print(f"  Weak/no matches: {len(mappings) - mapped}")
