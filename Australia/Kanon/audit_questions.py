import json
import re

with open("Australia/Kanon/kanon_survey_data.js", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("{")
end_idx = text.rfind("}")
data = json.loads(text[idx:end_idx+1])

planes = data.get("planes", [])
senses = data.get("senses", [])
vectors = data.get("vectors", [])

print(f"Loaded: {len(planes)} Planes, {len(senses)} Senses, {len(vectors)} Vectors")

# Print all 7 Planes
print("\n" + "="*80)
print("TIER 1: 7 PLANES (CORE PILLARS)")
print("="*80)
for p in planes:
    print(f"P{p['n']} | Pillar: {p['pillar']} | Name: {p['name']} | Domain: {p.get('domain','')}")
    print(f"   qA: {p.get('qA')}")
    print(f"   qD: {p.get('qD')}")

# Print all 49 Senses
print("\n" + "="*80)
print("TIER 2: 49 SENSES (THEMES)")
print("="*80)
for s in senses:
    print(f"S{s['id']} | {s['title']} (Plane {s['plane']})")
    print(f"   qA: {s.get('qA')}")
