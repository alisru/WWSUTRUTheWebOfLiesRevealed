import json
import re

DATA_PATH = r"e:/china russia/git/WWSUTRUTheWebOfLiesRevealed/Australia/Kanon/kanon_survey_data.js"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("{")
end_idx = text.rfind("}")
data = json.loads(text[idx:end_idx+1])

planes = data.get("planes", [])
senses = data.get("senses", [])
vectors = data.get("vectors", [])

# Operator Definitions
OPERATORS = {
    "(0)": {"name": "Capacity / Receptivity", "trait": "Receptivity", "vector": "Ground state / Latent potential", "type": "Ground"},
    "(=)": {"name": "Truth / Equivalence", "trait": "Honesty", "vector": "Grounded transmission / Full alignment", "type": "Virtue"},
    "(+?)": {"name": "Will to Know", "trait": "Curiosity", "vector": "Active pursuit / Seeking expansion", "type": "Virtue"},
    "(<)": {"name": "Lie / Concealment", "trait": "Duplicity", "vector": "Inward vector / Subversion / Masking", "type": "Shadow"},
    "(~?)": {"name": "Indifference", "trait": "Apathy", "vector": "Null force / Inertia & non-response", "type": "Shadow"},
    "(>)": {"name": "Insult / Aggression", "trait": "Contempt", "vector": "Outward vector / Aggressive distortion", "type": "Shadow"},
    "(-?)": {"name": "Will Not to Know", "trait": "Denial", "vector": "Negative force / Active shielding / Blindness", "type": "Shadow"}
}

CATEGORIES = {
    "C1": "Civic Standing & Dignity (Recognition / Identity)",
    "C2": "Work, Skills & Opportunity (Purpose / Education)",
    "C3": "Housing, Rent & Utilities (Shelter / Infrastructure)",
    "C4": "Rest, Health & Community (Refreshment / Lifestyle)",
    "C5": "Household Budget & Power (Power / Agency / Voting)",
    "C6": "Fairness, Truth & Integrity (Moral / Law / History)",
    "C7": "Cost of Living, Food & Safety Net (Sustenance / Welfare)"
}

# 49 Senses baseline categories & operators mapping
SENSE_META = {
    # Pillar 1: Identity & Character
    "1.1": {"cats": ["C1"], "econ": 0.0, "auth": -0.6, "op_virtue": "(=)", "op_shadow": "(~?)", "stance": "Mateship & Loyalty"},
    "1.2": {"cats": ["C1", "C6"], "econ": -0.4, "auth": -0.5, "op_virtue": "(=)", "op_shadow": "(>)", "stance": "Level Playing Field"},
    "1.3": {"cats": ["C1", "C3"], "econ": 0.0, "auth": 0.0, "op_virtue": "(0)", "op_shadow": "(~?)", "stance": "Belonging to Country"},
    "1.4": {"cats": ["C1", "C2"], "econ": 0.0, "auth": -0.4, "op_virtue": "(+?)", "op_shadow": "(<)", "stance": "Homegrown Confidence"},
    "1.5": {"cats": ["C5", "C1"], "econ": 0.0, "auth": -0.7, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "The Pub Test (Anti-Spin)"},
    "1.6": {"cats": ["C1", "C6"], "econ": 0.0, "auth": -0.4, "op_virtue": "(=)", "op_shadow": "(-?)", "stance": "Three Streams of Identity"},
    "1.7": {"cats": ["C1", "C7"], "econ": -0.4, "auth": -0.5, "op_virtue": "(+?)", "op_shadow": "(~?)", "stance": "Neighbourly Solidarity"},

    # Pillar 2: Democracy & Law
    "2.1": {"cats": ["C5", "C1"], "econ": 0.0, "auth": -0.8, "op_virtue": "(=)", "op_shadow": "(>)", "stance": "Empowered Citizens (Anti-Nanny)"},
    "2.2": {"cats": ["C6"], "econ": 0.0, "auth": 0.0, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Equal Rule of Law"},
    "2.3": {"cats": ["C5", "C7"], "econ": -0.4, "auth": 0.0, "op_virtue": "(+?)", "op_shadow": "(~?)", "stance": "Regional Equity"},
    "2.4": {"cats": ["C2", "C7"], "econ": -0.7, "auth": 0.3, "op_virtue": "(=)", "op_shadow": "(~?)", "stance": "Workingman's Commonwealth"},
    "2.5": {"cats": ["C5"], "econ": 0.0, "auth": -0.6, "op_virtue": "(+?)", "op_shadow": "(<)", "stance": "Clean Elections & Secret Ballot"},
    "2.6": {"cats": ["C3", "C7", "C5"], "econ": -0.8, "auth": 0.4, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Public Utilities vs Privatisation"},
    "2.7": {"cats": ["C5"], "econ": 0.0, "auth": -0.7, "op_virtue": "(0)", "op_shadow": "(>)", "stance": "Common Sense vs Nanny State"},

    # Pillar 3: Land & Housing
    "3.1": {"cats": ["C3"], "econ": 0.0, "auth": 0.0, "op_virtue": "(0)", "op_shadow": "(-?)", "stance": "Respecting Continental Limits"},
    "3.2": {"cats": ["C3", "C6"], "econ": -0.7, "auth": 0.0, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Affordable Homes vs Speculation"},
    "3.3": {"cats": ["C3"], "econ": -0.5, "auth": 0.0, "op_virtue": "(+?)", "op_shadow": "(>)", "stance": "Protecting Rivers & Country"},
    "3.4": {"cats": ["C3"], "econ": -0.6, "auth": 0.2, "op_virtue": "(+?)", "op_shadow": "(~?)", "stance": "Water Lifelines & Clean Energy Grid"},
    "3.5": {"cats": ["C3", "C2"], "econ": -0.6, "auth": 0.1, "op_virtue": "(=)", "op_shadow": "(~?)", "stance": "Regional Roads & Transport"},
    "3.6": {"cats": ["C7", "C5"], "econ": -0.8, "auth": 0.2, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Mineral Royalties vs Corporate Quarry"},
    "3.7": {"cats": ["C3", "C4"], "econ": -0.4, "auth": -0.5, "op_virtue": "(0)", "op_shadow": "(<)", "stance": "Liveable Suburbs & Free Public Commons"},

    # Pillar 4: Work & Community
    "4.1": {"cats": ["C4", "C2"], "econ": -0.4, "auth": -0.5, "op_virtue": "(+?)", "op_shadow": "(~?)", "stance": "Volunteers & Honest Workers"},
    "4.2": {"cats": ["C2", "C7", "C4"], "econ": -0.9, "auth": 0.1, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Living Wage, 8-Hr Day & Weekend"},
    "4.3": {"cats": ["C4"], "econ": -0.4, "auth": -0.5, "op_virtue": "(0)", "op_shadow": "(~?)", "stance": "Accessible Gathering Places & Clubs"},
    "4.4": {"cats": ["C1", "C2"], "econ": 0.0, "auth": -0.4, "op_virtue": "(+?)", "op_shadow": "(>)", "stance": "Ambition Without Tall-Poppy Envy"},
    "4.5": {"cats": ["C5", "C7"], "econ": -0.5, "auth": -0.4, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Reciprocity & Anti-Pokies Defense"},
    "4.6": {"cats": ["C7"], "econ": -0.7, "auth": 0.0, "op_virtue": "(=)", "op_shadow": "(-?)", "stance": "Preventing Destitution (Depression Memory)"},
    "4.7": {"cats": ["C4", "C2"], "econ": -0.5, "auth": -0.5, "op_virtue": "(0)", "op_shadow": "(>)", "stance": "Work-Life Balance vs Corporate Burnout"},

    # Pillar 5: Practical Method & Agency
    "5.1": {"cats": ["C2", "C6"], "econ": -0.3, "auth": -0.6, "op_virtue": "(+?)", "op_shadow": "(<)", "stance": "Trades, Whistleblowers & Problem-Solvers"},
    "5.2": {"cats": ["C2"], "econ": -0.5, "auth": 0.1, "op_virtue": "(+?)", "op_shadow": "(~?)", "stance": "Local Science (CSIRO) & Living Awards"},
    "5.3": {"cats": ["C1", "C5"], "econ": -0.7, "auth": -0.5, "op_virtue": "(=)", "op_shadow": "(>)", "stance": "Public Schools, Courts & Free Ballots"},
    "5.4": {"cats": ["C2", "C1"], "econ": -0.6, "auth": -0.5, "op_virtue": "(=)", "op_shadow": "(>)", "stance": "Workplace Human Dignity vs Taylorism"},
    "5.5": {"cats": ["C4", "C2"], "econ": -0.7, "auth": -0.4, "op_virtue": "(0)", "op_shadow": "(<)", "stance": "Humane Rhythms (Smoko, Safe Sites)"},
    "5.6": {"cats": ["C6", "C3"], "econ": 0.0, "auth": 0.0, "op_virtue": "(+?)", "op_shadow": "(-?)", "stance": "Indigenous Ecological Fire & Science"},
    "5.7": {"cats": ["C5", "C3"], "econ": -0.4, "auth": -0.6, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Physical Infrastructure vs Bureaucratic Spin"},

    # Pillar 6: Foundation & History
    "6.1": {"cats": ["C6", "C1"], "econ": 0.0, "auth": -0.3, "op_virtue": "(=)", "op_shadow": "(-?)", "stance": "Honouring All Founders (65k Yrs to Migrants)"},
    "6.2": {"cats": ["C6", "C5"], "econ": -0.4, "auth": -0.4, "op_virtue": "(+?)", "op_shadow": "(<)", "stance": "Milestone Laws (Mabo, Secret Ballot)"},
    "6.3": {"cats": ["C6"], "econ": 0.0, "auth": 0.0, "op_virtue": "(0)", "op_shadow": "(>)", "stance": "Protecting Sacred Memory & Sites"},
    "6.4": {"cats": ["C1", "C6"], "econ": 0.0, "auth": -0.5, "op_virtue": "(=)", "op_shadow": "(-?)", "stance": "Mateship Solidarity vs Invasion Paranoia"},
    "6.5": {"cats": ["C5", "C6"], "econ": 0.0, "auth": 0.0, "op_virtue": "(=)", "op_shadow": "(>)", "stance": "Arbitration & Ballots Over Violence"},
    "6.6": {"cats": ["C6", "C3"], "econ": 0.0, "auth": 0.0, "op_virtue": "(0)", "op_shadow": "(~?)", "stance": "Deep Time & Continental Continuity"},
    "6.7": {"cats": ["C6", "C7"], "econ": -0.5, "auth": -0.3, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "Treaty, Truth-Telling & Safety Net"},

    # Pillar 7: Result & Sustenance
    "7.1": {"cats": ["C1", "C3"], "econ": -0.5, "auth": -0.4, "op_virtue": "(=)", "op_shadow": "(>)", "stance": "Civic Decency vs Housing Greed"},
    "7.2": {"cats": ["C7", "C4", "C3"], "econ": -0.9, "auth": 0.1, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "The Commonwealth Dividend (Medicare, Super)"},
    "7.3": {"cats": ["C5"], "econ": 0.0, "auth": 0.0, "op_virtue": "(0)", "op_shadow": "(~?)", "stance": "Independent Sovereign Middle Power"},
    "7.4": {"cats": ["C1", "C7"], "econ": -0.8, "auth": -0.4, "op_virtue": "(=)", "op_shadow": "(<)", "stance": "People Over Raw Market Duopolies"},
    "7.5": {"cats": ["C6", "C5"], "econ": -0.4, "auth": -0.5, "op_virtue": "(+?)", "op_shadow": "(<)", "stance": "Watchdogs of Truth (Royal Commissions, ABC)"},
    "7.6": {"cats": ["C3", "C7"], "econ": -0.6, "auth": 0.0, "op_virtue": "(+?)", "op_shadow": "(~?)", "stance": "Intergenerational Housing Fairness"},
    "7.7": {"cats": ["C1", "C7"], "econ": -0.8, "auth": -0.5, "op_virtue": "(=)", "op_shadow": "(~?)", "stance": "Land of the Second Chance & Fair Go"}
}

AUDITED_VECTORS = []

for v in vectors:
    s_id = v.get("senseId")
    p_num = v.get("plane")
    meta = SENSE_META.get(s_id, {"cats": [f"C{p_num}"], "econ": 0.0, "auth": 0.0, "op_virtue": "(=)", "op_shadow": "(~?)", "stance": ""})
    
    # Vector-specific refinement based on text
    text_corpus = (v.get("name","") + " " + v.get("role","") + " " + v.get("description","") + " " + v.get("qA","")).lower()
    
    cats = list(meta["cats"])
    if any(w in text_corpus for w in ["rent", "landlord", "tenant", "housing", "eviction", "mortgage", "suburb"]):
        if "C3" not in cats: cats.append("C3")
    if any(w in text_corpus for w in ["food", "grocer", "supermarket", "ration", "susso", "hunger", "meal", "pay packet", "cost of living"]):
        if "C7" not in cats: cats.append("C7")
    if any(w in text_corpus for w in ["strike", "union", "tafe", "apprentice", "wage", "award", "worker", "tradie"]):
        if "C2" not in cats: cats.append("C2")
    if any(w in text_corpus for w in ["doctor", "medicare", "hospital", "smoko", "rest", "weekend", "holiday", "sleep"]):
        if "C4" not in cats: cats.append("C4")
    if any(w in text_corpus for w in ["vote", "ballot", "election", "bureaucrat", "council", "parliament", "tax", "fee"]):
        if "C5" not in cats: cats.append("C5")
    if any(w in text_corpus for w in ["court", "corruption", "whistleblower", "treaty", "mabo", "truth", "justice"]):
        if "C6" not in cats: cats.append("C6")

    coords = v.get("coords", {})
    upsilon = coords.get("v", 0.0)
    psi = coords.get("psi", 0.0)
    
    # Positive virtue operator
    if psi > 0.3:
        op_virtue = "(+?)"
    elif upsilon > 0.4:
        op_virtue = "(=)"
    else:
        op_virtue = "(0)"
        
    # Shadow failure operator
    if upsilon < 0 and psi > 0:
        op_shadow = "(<)"
    elif upsilon < 0 and psi < 0:
        op_shadow = "(>)"
    elif psi < -0.2:
        op_shadow = "(~?)"
    else:
        op_shadow = "(-?)"

    AUDITED_VECTORS.append({
        "uid": v.get("uid"),
        "name": v.get("name"),
        "plane": p_num,
        "senseId": s_id,
        "categories": cats,
        "econ": meta["econ"],
        "auth": meta["auth"],
        "op_virtue": op_virtue,
        "op_shadow": op_shadow
    })

print(f"Total Audited Nodes:")
print(f"- Planes: {len(planes)}")
print(f"- Senses: {len(senses)}")
print(f"- Vectors: {len(AUDITED_VECTORS)}")
print(f"TOTAL: {len(planes) + len(senses) + len(AUDITED_VECTORS)} questions audited!")

vec_cat_counts = {k: 0 for k in CATEGORIES}
for av in AUDITED_VECTORS:
    for c in av["categories"]:
        vec_cat_counts[c] += 1

print("\n=== VECTOR-LEVEL CATEGORY DISTRIBUTION (354 Vectors) ===")
for c, cnt in vec_cat_counts.items():
    print(f"{c}: {cnt} vectors ({round(cnt/len(AUDITED_VECTORS)*100, 1)}%) -> {CATEGORIES[c]}")

op_v_counts = {}
op_s_counts = {}
for av in AUDITED_VECTORS:
    op_v_counts[av["op_virtue"]] = op_v_counts.get(av["op_virtue"], 0) + 1
    op_s_counts[av["op_shadow"]] = op_s_counts.get(av["op_shadow"], 0) + 1

print("\n=== VECTOR VIRTUE OPERATORS ===")
for op, cnt in op_v_counts.items():
    print(f"{op} {OPERATORS[op]['name']}: {cnt} vectors")

print("\n=== VECTOR SHADOW OPERATORS ===")
for op, cnt in op_s_counts.items():
    print(f"{op} {OPERATORS[op]['name']}: {cnt} vectors")
