import json

with open("Australia/Kanon/kanon_survey_data.js", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("{")
end_idx = text.rfind("}")
data = json.loads(text[idx:end_idx+1])

planes = data.get("planes", [])
senses = data.get("senses", [])
vectors = data.get("vectors", [])

# Taxonomy of Categories
CATEGORIES = {
    "C1": "Civic Standing & Dignity (Recognition / Identity)",
    "C2": "Work, Skills & Opportunity (Purpose / Education)",
    "C3": "Housing, Rent & Utilities (Shelter / Infrastructure)",
    "C4": "Rest, Health & Community (Refreshment / Lifestyle)",
    "C5": "Household Budget & Power (Power / Agency / Voting)",
    "C6": "Fairness, Truth & Integrity (Moral / Law / History)",
    "C7": "Cost of Living, Food & Safety Net (Sustenance / Welfare)"
}

# Mapping all 7 Planes
PLANE_MAP = {
    1: {"cats": ["C1"], "scale": "Total", "econ": "Left-Center", "civic": "Libertarian"},
    2: {"cats": ["C5", "C6"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian"},
    3: {"cats": ["C3"], "scale": "Macro", "econ": "Left-Center", "civic": "Neutral"},
    4: {"cats": ["C4", "C2"], "scale": "Meso", "econ": "Left", "civic": "Libertarian"},
    5: {"cats": ["C5", "C2"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian"},
    6: {"cats": ["C6", "C1"], "scale": "Total", "econ": "Center", "civic": "Libertarian"},
    7: {"cats": ["C7", "C3"], "scale": "Macro", "econ": "Left", "civic": "Neutral"}
}

# Explicit mapping of all 49 Senses based on their actual questions and themes
SENSE_MAP = {
    # Pillar 1: Identity & Character
    "1.1": {"cats": ["C1"], "scale": "Micro/Meso", "econ": "Neutral", "civic": "Libertarian", "utility": "Cultural/Solidarity"},
    "1.2": {"cats": ["C1", "C6"], "scale": "Meso/Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Fair Go baseline)"},
    "1.3": {"cats": ["C1", "C3"], "scale": "Total", "econ": "Neutral", "civic": "Neutral", "utility": "Cultural (Belonging)"},
    "1.4": {"cats": ["C1", "C2"], "scale": "Macro", "econ": "Center", "civic": "Libertarian", "utility": "Medium (Homegrown capability)"},
    "1.5": {"cats": ["C5", "C1"], "scale": "Meso", "econ": "Neutral", "civic": "Libertarian", "utility": "High (Anti-spin/Pub test)"},
    "1.6": {"cats": ["C1", "C6"], "scale": "Total", "econ": "Neutral", "civic": "Libertarian", "utility": "High (Reconciliation)"},
    "1.7": {"cats": ["C1", "C7"], "scale": "Meso", "econ": "Left-Center", "civic": "Libertarian", "utility": "Medium (Neighbourly care)"},

    # Pillar 2: Democracy & Law
    "2.1": {"cats": ["C5", "C1"], "scale": "Macro", "econ": "Neutral", "civic": "Libertarian", "utility": "High (Anti-authoritarian)"},
    "2.2": {"cats": ["C6"], "scale": "Macro", "econ": "Neutral", "civic": "Neutral", "utility": "High (Rule of Law)"},
    "2.3": {"cats": ["C5", "C7"], "scale": "Macro", "econ": "Left-Center", "civic": "Neutral", "utility": "High (Regional equity)"},
    "2.4": {"cats": ["C2", "C7"], "scale": "Macro", "econ": "Left", "civic": "Authoritarian-Left", "utility": "High (Welfare state)"},
    "2.5": {"cats": ["C5"], "scale": "Macro", "econ": "Neutral", "civic": "Libertarian", "utility": "High (Secret ballot / Voting)"},
    "2.6": {"cats": ["C3", "C7", "C5"], "scale": "Macro", "econ": "Left", "civic": "Authoritarian-Left", "utility": "High (Public assets vs Privatisation)"},
    "2.7": {"cats": ["C5"], "scale": "Macro", "econ": "Neutral", "civic": "Libertarian", "utility": "High (Anti-Nanny State)"},

    # Pillar 3: Land & Housing
    "3.1": {"cats": ["C3"], "scale": "Total", "econ": "Neutral", "civic": "Neutral", "utility": "Medium (Climate/Disaster)"},
    "3.2": {"cats": ["C3", "C6"], "scale": "Macro", "econ": "Left", "civic": "Neutral", "utility": "High (Affordable Housing & Native Title)"},
    "3.3": {"cats": ["C3"], "scale": "Total", "econ": "Left-Center", "civic": "Neutral", "utility": "High (River & Soil protection)"},
    "3.4": {"cats": ["C3"], "scale": "Macro/Total", "econ": "Left", "civic": "Neutral", "utility": "High (Clean energy & Water)"},
    "3.5": {"cats": ["C3", "C2"], "scale": "Macro", "econ": "Left", "civic": "Neutral", "utility": "High (Regional roads & Transport)"},
    "3.6": {"cats": ["C7", "C5"], "scale": "Macro", "econ": "Left", "civic": "Neutral", "utility": "High (Mining royalties vs Corporate plunder)"},
    "3.7": {"cats": ["C3", "C4"], "scale": "Meso", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Liveable suburbs & Free beaches)"},

    # Pillar 4: Work & Community
    "4.1": {"cats": ["C4", "C2"], "scale": "Meso", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Volunteers & Worker respect)"},
    "4.2": {"cats": ["C2", "C7", "C4"], "scale": "Macro/Meso", "econ": "Left", "civic": "Neutral", "utility": "Critical (Living wage, 8hr day, Weekend)"},
    "4.3": {"cats": ["C4"], "scale": "Meso", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Pubs, clubs, third places)"},
    "4.4": {"cats": ["C1", "C2"], "scale": "Micro", "econ": "Neutral", "civic": "Libertarian", "utility": "Cultural (Tall poppy vs Ambition)"},
    "4.5": {"cats": ["C5", "C7"], "scale": "Meso", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Anti-gambling gouging)"},
    "4.6": {"cats": ["C7"], "scale": "Macro/Meso", "econ": "Left", "civic": "Neutral", "utility": "High (Depression memory / Safety net)"},
    "4.7": {"cats": ["C4", "C2"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Work-life balance / Anti-burnout)"},

    # Pillar 5: Practical Method & Agency
    "5.1": {"cats": ["C2", "C6"], "scale": "Meso/Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Tradies, Whistleblowers, Umpires)"},
    "5.2": {"cats": ["C2"], "scale": "Macro", "econ": "Left-Center", "civic": "Neutral", "utility": "High (Local science & Living awards)"},
    "5.3": {"cats": ["C1", "C5"], "scale": "Macro", "econ": "Left", "civic": "Libertarian", "utility": "High (Public schools, Courts, Ballots)"},
    "5.4": {"cats": ["C2", "C1"], "scale": "Meso", "econ": "Left", "civic": "Libertarian", "utility": "High (Human dignity over Taylorism)"},
    "5.5": {"cats": ["C4", "C2"], "scale": "Micro/Meso", "econ": "Left", "civic": "Libertarian", "utility": "High (Smoko, Safe sites, Sick leave)"},
    "5.6": {"cats": ["C6", "C3"], "scale": "Total", "econ": "Neutral", "civic": "Neutral", "utility": "High (Indigenous firestick & Science)"},
    "5.7": {"cats": ["C5", "C3"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Anti-Robodebt / Real infrastructure)"},

    # Pillar 6: Foundation & History
    "6.1": {"cats": ["C6", "C1"], "scale": "Total", "econ": "Neutral", "civic": "Libertarian", "utility": "High (First Nations & Convict history)"},
    "6.2": {"cats": ["C6", "C5"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Franchise, Mabo, Native Title)"},
    "6.3": {"cats": ["C6"], "scale": "Total", "econ": "Neutral", "civic": "Neutral", "utility": "Medium (Preserving sacred & historic memory)"},
    "6.4": {"cats": ["C1", "C6"], "scale": "Total", "econ": "Neutral", "civic": "Libertarian", "utility": "Cultural (Solidarity vs Fear)"},
    "6.5": {"cats": ["C5", "C6"], "scale": "Macro", "econ": "Neutral", "civic": "Neutral", "utility": "High (Arbitration & Ballot over violence)"},
    "6.6": {"cats": ["C6", "C3"], "scale": "Total", "econ": "Neutral", "civic": "Neutral", "utility": "High (Deep time & 65,000yrs)"},
    "6.7": {"cats": ["C6", "C7"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Treaty, Truth & Safety net)"},

    # Pillar 7: Outcomes & Sustenance
    "7.1": {"cats": ["C1", "C3"], "scale": "Meso/Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Decency vs 'I've Got Mine')"},
    "7.2": {"cats": ["C7", "C4", "C3"], "scale": "Macro", "econ": "Left", "civic": "Neutral", "utility": "Critical (Medicare, Super, Housing)"},
    "7.3": {"cats": ["C5"], "scale": "Total", "econ": "Center", "civic": "Neutral", "utility": "High (Independent foreign policy/Sovereignty)"},
    "7.4": {"cats": ["C1", "C7"], "scale": "Macro", "econ": "Left", "civic": "Libertarian", "utility": "High (Fair go over raw market greed)"},
    "7.5": {"cats": ["C6", "C5"], "scale": "Macro", "econ": "Left-Center", "civic": "Libertarian", "utility": "High (Royal Commissions, ABC, Truth)"},
    "7.6": {"cats": ["C3", "C7"], "scale": "Total", "econ": "Left-Center", "civic": "Neutral", "utility": "High (Clean energy & Housing fairness)"},
    "7.7": {"cats": ["C1", "C7"], "scale": "Total", "econ": "Left", "civic": "Libertarian", "utility": "High (Land of second chance / Fair go)"}
}

# Aggregate stats
cat_counts = {k: 0 for k in CATEGORIES}
econ_counts = {"Left": 0, "Left-Center": 0, "Center": 0, "Neutral": 0, "Right": 0}
civic_counts = {"Libertarian": 0, "Neutral": 0, "Authoritarian-Left": 0, "Authoritarian": 0}

for s_id, meta in SENSE_MAP.items():
    for c in meta["cats"]:
        cat_counts[c] += 1
    econ_counts[meta["econ"]] = econ_counts.get(meta["econ"], 0) + 1
    civic_counts[meta["civic"]] = civic_counts.get(meta["civic"], 0) + 1

print("\n=== SENSE AUDIT CATEGORY DISTRIBUTION (49 Senses) ===")
for c, count in cat_counts.items():
    print(f"{c}: {count} senses hit -> {CATEGORIES[c]}")

print("\n=== POLITICAL COMPASS DISTRIBUTION (49 Senses) ===")
print("Economic:", econ_counts)
print("Civic:", civic_counts)
