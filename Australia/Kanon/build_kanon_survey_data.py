"""
Builds kanon_survey_data.js for the Australian Kanon Alignment & Identity Survey (Kanon_Survey.html).
Combines all 7 Planes (Tier 1), 49 Senses (Tier 2), and 353/354 Vectors (Tier 3) with ABCD questions
(A: Sense, B: Use, C: Need, D: Blocker), coordinates, quotes, narratives, and audited politician verdicts.
"""

import json
import glob
import os
import re

COMPACT_DIR = r"E:\Vector Field Theory\VFT Docs\_VFT MD\WWSUTRU\Australia\Aus_Kanon\compact JSON"
KANON_HTML_DIR = r"E:\china russia\git\WWSUTRUTheWebOfLiesRevealed\Australia\Kanon"
HANSON_HTML_DIR = r"E:\china russia\git\WWSUTRUTheWebOfLiesRevealed\Australia\Hanson_Audit"
ALBO_MD_DIR = r"E:\Vector Field Theory\VFT Docs\_VFT MD\WWSUTRU\Australia\Aus_Kanon\Audits\Albo_Audit"
OUT_JS = os.path.join(KANON_HTML_DIR, "kanon_survey_data.js")

S_ORDER = ["Who", "What", "Where", "Why", "How", "Cause", "Effect"]
S_SUBTITLES = {
    "Who": "Authenticity & Character",
    "What": "Roles & Definitions",
    "Where": "Place & Setting",
    "Why": "Drive & Motivation",
    "How": "Method & Practice",
    "Cause": "Roots & History",
    "Effect": "Legacy & Outcome",
}

PLANE_META = [
    {
        "n": 1,
        "id": "P1",
        "code": "Who",
        "name": "Identity",
        "fullTitle": "Values of Australian Identity",
        "pillar": "The Egalitarian",
        "pillarBadge": "Radical Horizontality",
        "domain": "Metaphysical",
        "tau": 3.0,
        "hue": "#CA8A04",
        "blurb": "Character over rank, horizontal loyalty, skepticism toward pretension, and deep-time belonging",
        "pillarSummary": "The Egalitarian does not believe in the destruction of hierarchy for chaos's sake, but for dignity's sake. They possess an innate inability to be impressed by status or titles: when the Prime Minister walks into the public bar, the Egalitarian does not bow or sneer—they simply nod and ask, 'What are you having?'",
        "shadowTitle": "Tall Poppy → Humble Excellence",
        "shadowText": "Transmutes envy into Humble Excellence. You are allowed to achieve greatness in Australia, but the price of admission is humility—never acting superior or pulling rank on your peers.",
        "practicalText": "Insisting on paying your round at the pub regardless of income; the CEO who eats in the staff canteen; the surgeon who introduces themselves by first name; treating the cleaner's view with the same baseline respect as the economist's.",
        "qA": "A person's worth in Australia should come from their character, resilience, and loyalty to the people beside them—never from wealth, title, or social rank.",
        "qB": "In the heat of everyday life, I actually treat everyone on a level playing field and stand by my mates rather than pulling rank or looking down on others.",
        "qC": "The people in my everyday circle believe we should treat everyone as equals and actually back one another without pretension.",
        "qD": "Across Australia today, our society and institutions actually practise genuine peer-to-peer equality rather than rewarding class hierarchy.",
        "tags": ["identity", "mateship", "egalitarianism", "belonging", "indigenous", "culture"],
    },
    {
        "n": 2,
        "id": "P2",
        "code": "What",
        "name": "Definition",
        "fullTitle": "Values of Australian Definition",
        "pillar": "The Constituent",
        "pillarBadge": "Skeptical Civil Duty",
        "domain": "Possible",
        "tau": 14.0,
        "hue": "#D97706",
        "blurb": "The civic contract, accountable public utilities, democratic voice, and equal standing under law",
        "pillarSummary": "The Constituent serves as the immune system of the body politic. Rather than worshipping the state as a sacred parent, Australians treat government as a pragmatic public utility bound by contract—and when Faceless Men or insiders try to bypass the public will, the Constituent stands up to hold them to account.",
        "shadowTitle": "Apathy ('She'll Be Right') → Vigilance",
        "shadowText": "Transmutes passive 'She'll be right' complacency into active civic vigilance—recognising that the Quiet Life is only protected through noisy democratic accountability.",
        "practicalText": "Reading the fine print on a council development application and showing up at Town Hall; the union delegate who knows the enterprise agreement by heart; voting carefully and defending independent public institutions.",
        "qA": "Public institutions, laws, and political leaders should exist strictly as practical utilities to serve empowered citizens—never as masters ruling over passive subjects.",
        "qB": "In practice, I actively exercise my democratic voice, hold authorities to a fair standard, and refuse to act like a passive subject.",
        "qC": "People in my community expect government to serve ordinary citizens and actively push back against political arrogance.",
        "qD": "In reality today, Australian parliaments, courts, and agencies actually operate as fair, transparent servants of the public rather than serving insiders.",
        "tags": ["democracy", "fair-go", "law", "governance", "voting", "rights"],
    },
    {
        "n": 3,
        "id": "P3",
        "code": "Where",
        "name": "Land",
        "fullTitle": "Values of Australian Land",
        "pillar": "The Steward",
        "pillarBadge": "Ecological Humility",
        "domain": "Physical",
        "tau": 3.0,
        "hue": "#16A34A",
        "blurb": "Continental stewardship, climate adaptation, housing security, and shared public commons",
        "pillarSummary": "The Steward has ceased fighting the continent. Adopting the deep-time perspective of First Nations Elders, the Steward understands we do not merely own the land as an extractive quarry—we hold and care for a fragile, ancient Country of drought, flood, bush, and open coast.",
        "shadowTitle": "The Terror of the Void → Respect & Custodianship",
        "shadowText": "Transmutes colonial fear and quarry-style extraction into ecological humility—connecting with the Red Heart, bush, and suburban commons rather than plundering or pricing people out of shelter.",
        "practicalText": "Checking the water tank and respecting river flows; backing Indigenous cultural burning in bushfire management; keeping beaches and public parks open to all; defending secure housing as a human foundation rather than a speculative casino.",
        "qA": "Living on this continent should mean humble stewardship of its fragile land and water cycles, alongside secure shelter and open public commons for every resident.",
        "qB": "In my own choices and daily habits, I actively care for my local environment, respect natural limits, and back fair access to housing and public space.",
        "qC": "My local community values and practises genuine stewardship of land, water, and neighbourhood housing security.",
        "qD": "Across Australia, our policies and markets actually deliver secure housing, healthy rivers and bushland, and fair regional infrastructure rather than speculative extraction.",
        "tags": ["land", "housing", "environment", "bush", "coast", "infrastructure", "climate"],
    },
    {
        "n": 4,
        "id": "P4",
        "code": "Why",
        "name": "Drive",
        "fullTitle": "Values of Australian Drive",
        "pillar": "The Volunteer",
        "pillarBadge": "Silent Agency",
        "domain": "Lyrical",
        "tau": 1.5,
        "hue": "#0D9488",
        "blurb": "Reward for honest effort, volunteer solidarity in crisis, protected rest, and the good life",
        "pillarSummary": "The Volunteer acts without waiting to be ordered. When bushfires or floodwaters rise, they launch the tinny and hold the hose—completing the historical shift from the Convict (forced labour) to the Volunteer (free service), while insisting that hard yakka earns a dignified living wage and protected rest.",
        "shadowTitle": "Bludging & Burnout → Service & Fair Reciprocity",
        "shadowText": "Transmutes both 'Bludging' (free-riding on mates) and extractive workaholic burnout into honourable service—where everyone pitches in when needed and everyone is guaranteed the Weekend and a fair living standard.",
        "practicalText": "Joining the RFS, SES, or Surf Life Saving; launching a tinny when neighbours are flooded; working honestly without performative hustle culture; defending penalty rates, the eight-hour day, and family time.",
        "qA": "Every person who puts in an honest effort should receive a living wage, protected rest and family time, and the community backing to have a fair crack at the good life.",
        "qB": "In practice, I pitch in when others need help, respect fair reciprocity, and protect a healthy balance between honest work and rest.",
        "qC": "People around me genuinely volunteer, pitch in during hard times, and respect fair wages and downtime.",
        "qD": "In practice today, Australia's economy actually rewards honest work with a living wage and protected rest rather than burnout and extractive profiteering.",
        "tags": ["work", "wages", "rest", "volunteering", "sport", "lifestyle", "burnout"],
    },
    {
        "n": 5,
        "id": "P5",
        "code": "How",
        "name": "Method",
        "fullTitle": "Values of Australian Method",
        "pillar": "The Improviser",
        "pillarBadge": "Pragmatic Genius",
        "domain": "Logical",
        "tau": 5.0,
        "hue": "#2563EB",
        "blurb": "Practical ingenuity, plain-spoken honesty, independent umpires, and humane workplace rules",
        "pillarSummary": "The Improviser is the spiritual descendant of the Bush Mechanic and CSIRO inventor—judging every method by whether it actually works in reality. Sceptical of grand bureaucratic spin, they combine stringybark ingenuity with the Pub Test and an independent Umpire to keep rules fair and humane.",
        "shadowTitle": "The Dodgy Shortcut → Pragmatic Innovation",
        "shadowText": "Transmutes corner-cutting and bureaucratic box-ticking into genuine innovation—cutting red tape and spin ruthlessly while respecting real-world safety and fair arbitration.",
        "practicalText": "Fixing problems on the spot with practical common sense; speaking plainly so anyone at the pub can verify the claim; backing public science (CSIRO, WiFi, bionic ear, solar) and fair workplace umpires.",
        "qA": "Problems in work and public life should be solved through plain-spoken honesty, practical ingenuity, and independent umpires—never spin, dodgy shortcuts, or robotic box-ticking.",
        "qB": "When a problem hits, I actually use practical common sense, speak plainly, and play by fair rules rather than hiding behind spin or red tape.",
        "qC": "In my workplace and local circle, people value practical competence, honest talk, and fair play over bureaucratic games.",
        "qD": "Across Australia today, our workplaces and institutions actually empower practical problem-solving and independent umpires rather than punitive bureaucracy.",
        "tags": ["method", "innovation", "workplace", "unions", "pub-test", "bureaucracy", "science"],
    },
    {
        "n": 6,
        "id": "P6",
        "code": "Cause",
        "name": "Foundation",
        "fullTitle": "Values of Australian Foundation",
        "pillar": "The Reconciler",
        "pillarBadge": "Historical Courage",
        "domain": "Historical",
        "tau": 30.0,
        "hue": "#4F46E5",
        "blurb": "Honest historical reckoning, 65,000 years of continuity, bottom-up democracy, and hard-won rights",
        "pillarSummary": "The Reconciler faces the full truth of Australian history—not with paralysing guilt or denial, but with active responsibility. They weave the three foundational stories of the nation—the 65,000-year Ancient Raft of First Nations law, the Convict and Eureka rebellion for bottom-up rights, and the postwar Migrant wave—into one honest Commonwealth.",
        "shadowTitle": "The Great Australian Silence → Truth-Telling",
        "shadowText": "Transmutes historical amnesia and Terra Nullius denial into courageous Truth-Telling—choosing honest reckoning and Mabo justice over the comfort of whitewashing.",
        "practicalText": "Holding both truths that 1788 was both Settlement and Invasion; respecting local Elders and native title; defending the hard-won democratic legacy of Eureka, women's suffrage, and the eight-hour day.",
        "qA": "A mature Australia should face the whole truth of its past—honouring 65,000 years of First Nations continuity alongside convict survival, democratic struggle, and migrant contribution without whitewashing injustice.",
        "qB": "In practice, I actively listen to and respect the full truth of Australian history and defend the hard-won rights inherited from past generations.",
        "qC": "People in my circle believe we should face our full history honestly and actually treat Indigenous, settler, and migrant heritage with respect.",
        "qD": "Across Australia today, our civic culture, schools, and laws actually reckon honestly with our past and uphold our foundational democratic settlements.",
        "tags": ["history", "reconciliation", "indigenous", "eureka", "mabo", "heritage", "truth"],
    },
    {
        "n": 7,
        "id": "P7",
        "code": "Effect",
        "name": "Result",
        "fullTitle": "Values of Australian Result",
        "pillar": "The Good Neighbour",
        "pillarBadge": "Regional & Civic Dividend",
        "domain": "Emotive",
        "tau": 7.0,
        "hue": "#9333EA",
        "blurb": "Universal care, shared national wealth, intergenerational fairness, and sovereign regional partnership",
        "pillarSummary": "The Good Neighbour measures the Australian experiment by its real human harvest: whether ordinary citizens enjoy universal healthcare (Medicare), dignified retirement (Superannuation), shared resource wealth, and whether Australia stands as a confident, generous partner in the Indo-Pacific rather than an anxious colonial outpost.",
        "shadowTitle": "Isolation & Extraction → Shared Commonwealth",
        "shadowText": "Transmutes island paranoia and private resource plundering into universal civic security at home and constructive neighbourly partnership across the Pacific.",
        "practicalText": "Protecting universal Medicare, PBS, HECS, and Superannuation so no citizen falls through the floor; ensuring mineral wealth benefits future generations; showing up for Pacific neighbours in crisis as family, not charity.",
        "qA": "The Australian project should deliver a generous, sovereign commonwealth—universal healthcare, shared resource wealth, intergenerational fairness, and constructive partnership in our region.",
        "qB": "In my own civic choices and voting, I actively back universal care, intergenerational fairness, and Australia acting as a good neighbour.",
        "qC": "My circle believes Australia should share its wealth fairly across generations and actually looks out for neighbours in practice.",
        "qD": "All things considered, the Australia we live in today actually delivers universal care, shared commonwealth prosperity, and a fair deal for the next generation.",
        "tags": ["health", "medicare", "housing", "superannuation", "foreign-policy", "sovereignty", "future"],
    },
]

import html

# Unified Essence Questions for all 49 Senses (1.1 through 7.7)
# Each entry is an explicit 4-tuple:
#   (qA: Personal Should, qB: Personal Would, qC: Community Circle, qD: Wider Australian Society)
SENSE_QUESTIONS = {
    # PLANE 1: IDENTITY (WHO)
    "1.1": (
        "When pressure hits, true Australian character should show up as quiet grit, practical improvisation, dry humour against arrogance, and unconditional loyalty to the person beside you.",
        "When things get tough in my own life or work, I actually pitch in, improvise practically, and stand by the people beside me rather than looking out only for myself.",
        "The people in my everyday circle genuinely back one another under pressure and judge people by their character rather than their title or bank balance.",
        "Across Australia today, our wider culture and institutions actually reward quiet grit and mutual loyalty rather than self-promotion and status.",
    ),
    "1.2": (
        "The highest unwritten law of Australian social life should be a level playing field: everyone gets a fair go, nobody is born better than anyone else, and self-important pretence gets punctured.",
        "In my own daily interactions, I actually treat everyone from the cleaner to the boss as an equal peer and refuse to pull rank or flatter power.",
        "The workplaces and local circles I move in actually operate on a level playing field where people speak plainly as equals without demanding deference.",
        "Across Australia today, our social and economic systems actually keep the playing field level rather than cementing class privilege and elitism.",
    ),
    "1.3": (
        "Our identity is inseparable from the physical continent—its ancient bush, open coast, red interior, and suburbs—and we should respect the land as a living home rather than a commodity.",
        "In my own lifestyle and habits, I actively spend time in, care for, and respect my local bush, coast, and neighbourhood commons.",
        "People in my local community feel a grounded connection to our landscape and look after shared public spaces, parks, and beaches.",
        "Across Australia today, urban planning, housing markets, and public policy actually keep people connected to the coast, bush, and liveable communities rather than locking them out.",
    ),
    "1.4": (
        "Australians should back our own homegrown talent, ideas, and makers with confidence, free from the 'Cultural Cringe' that assumes something only matters if approved overseas.",
        "In my own choices, I actively support Australian creators, local businesses, and ambitious homegrown ideas rather than cutting down tall poppies or defaulting to overseas brands.",
        "People in my everyday circle encourage local ambition and give people having a genuine crack fair support rather than cynical tall-poppy knocking.",
        "Across Australia today, our institutions, media, and investors actually back homegrown capability and creative ambition rather than coasting on passive resource luck.",
    ),
    "1.5": (
        "Power in Australia should always answer to plain-spoken common sense (the Pub Test), collective workplace solidarity, and independent public inquiries that expose corruption.",
        "When I see spin, unfairness, or bullying at work or in public life, I actually speak up plainly and back collective fairness rather than staying quiet.",
        "In my workplace and community circle, people apply the Pub Test to authority and back coworkers who stand up for fair treatment.",
        "Across Australia today, governments, corporations, and courts actually answer to plain-English accountability, worker solidarity, and public inquiries.",
    ),
    "1.6": (
        "Modern Australian identity should weave together three living streams—65,000 years of First Nations custodial law, the hard-won egalitarianism of settlers and convicts, and the energy of migrants from every corner of the world.",
        "In my own daily life, I actively welcome and respect Indigenous, settler, and multicultural neighbours as equal co-authors of modern Australia.",
        "In my community circle, people of First Nations, settler, and migrant heritage actually get along and treat each other with everyday respect and inclusion.",
        "Across Australia today, our national politics and media actually foster honest unity across our Indigenous, British, and multicultural roots rather than stoking division.",
    ),
    "1.7": (
        "At our best, Australian character should produce a nation that looks after the sick and vulnerable at home while acting as a generous, independent bridge-builder in our region.",
        "In my own civic and personal choices, I support universal care for vulnerable Australians and constructive engagement with our regional neighbours.",
        "People in my community circle genuinely care about looking after the vulnerable at home and being a good neighbour in the Asia-Pacific.",
        "Across Australia today, our national policies actually deliver compassionate care at home and confident, independent bridge-building in the world.",
    ),

    # PLANE 2: DEFINITION (WHAT — CIVIC CONTRACT)
    "2.1": (
        "In a true commonwealth, the citizen should be the sovereign partner and employer of the state—never a passive subject to be managed, patronised, or ruled over.",
        "When dealing with government agencies, councils, or rules, I actively insist on fair citizen rights and fulfill my civic duties rather than acting like a passive subject.",
        "People in my community circle understand their rights as citizens and expect public officials to act as public servants, not bosses.",
        "Across Australia today, public agencies, councils, and parliaments actually treat ordinary Australians as respected citizens rather than compliance problems.",
    ),
    "2.2": (
        "Our constitutional order should guarantee peace, order, and good government through an independent judiciary and strict rules that prevent any leader from seizing unchecked power.",
        "In my own voting and civic stance, I support constitutional checks, the rule of law, and judicial independence even when my preferred party is in power.",
        "People in my everyday circle value lawful, accountable governance and reject leaders who try to rig the rules or stack the courts.",
        "Across Australia today, our constitutional checks, courts, and parliamentary rules actually protect citizens from executive overreach and political stitch-ups.",
    ),
    "2.3": (
        "A fair federation should share national revenue so every state, regional town, and outer suburb enjoys the same baseline of hospitals, schools, and roads as the wealthiest capital city.",
        "I personally support fair national tax-and-revenue sharing for outer suburbs and regional towns, even when the funding goes beyond my own postcode.",
        "People in my local area believe every town and suburb deserves fair public services and support sharing national funding equitably.",
        "Across Australia today, federal and state funding actually delivers a fair share of hospitals, schools, and transport to regional towns and outer suburbs.",
    ),
    "2.4": (
        "The founding promise of the Australian Commonwealth should guarantee a secular, practical society where working people enjoy fair wages, free internal movement, and peace free from sectarian fanaticism.",
        "In my own work and civic life, I uphold secular tolerance and back fair living wages and working conditions for ordinary households.",
        "In my community circle, people keep religion and politics respectful and support a fair living wage for working families.",
        "Across Australia today, working households can actually rely on the Commonwealth promise of fair wages, civic peace, and a secure standard of living.",
    ),
    "2.5": (
        "Democratic legitimacy should rest on clean, independent elections where every citizen votes on equal terms—not backroom factional warlords, donor lobbies, or party-room coups.",
        "When I vote, I take my ballot seriously—looking past partisan spin and punishing backroom factional games and corporate donor capture.",
        "People in my everyday circle take democratic voting seriously and are fed up with factional powerbrokers and corporate lobbying.",
        "Across Australia today, our electoral system and political parties actually deliver leaders and policies chosen by voters rather than factional insiders and big donors.",
    ),
    "2.6": (
        "Essential services and core infrastructure—water, power, roads, banking access, and communications—should be built and run as public utilities for the common good rather than private price-gouging monopolies.",
        "In my own civic choices and voting, I back public-interest ownership and strict accountability for essential utilities over privatisation.",
        "People in my community circle believe essential utilities belong in public hands or under strict public-interest rules rather than toll-road and energy monopolies.",
        "Across Australia today, essential services and infrastructure are actually run affordably for the public good rather than privatised price-gouging.",
    ),
    "2.7": (
        "A mature civic order should protect public safety and include First Nations voices without suffocating everyday life in petty fines, over-policing, and nanny-state prohibitions.",
        "In my own life, I act responsibly toward others' safety while supporting common-sense personal freedom over petty nanny-state micromanagement.",
        "People in my local community look out for safety with common sense without acting like wowsers or calling for petty rules on everything.",
        "Across Australia today, our laws and councils actually strike a healthy balance—keeping people safe and included without burying daily life in revenue-raising fines and red tape.",
    ),

    # PLANE 3: LAND (WHERE — CONTINENT & HOME)
    "3.1": (
        "The sheer scale and volatility of the Australian continent—its bushfires, droughts, and ancient spirit of place—demand humility, respect, and preparation rather than human arrogance.",
        "In my own home and habits, I actively prepare for heat, fire, storm, and water limits rather than assuming 'she'll be right' or ignoring the landscape.",
        "My local community respects the bush and climate extremes, prepares practically for fire and flood seasons, and backs local emergency volunteers.",
        "Across Australia today, national planning, building codes, and disaster systems actually adapt to the continent's harsh climate and natural limits.",
    ),
    "3.2": (
        "Land in Australia should be shared fairly for families to live and farm on, while respecting First Nations native title—never locked up by land-banking monopolies or oligarchs.",
        "In my own financial and voting choices, I treat housing as a human home first rather than backing speculative property hoarding that locks out young families.",
        "People in my everyday circle believe every working person and family should be able to afford a secure home and respect native title.",
        "Across Australia today, our housing and land laws actually enable ordinary Australians to secure a fair home without being locked out by speculative property monopolies.",
    ),
    "3.3": (
        "Australia's ancient soils, rivers, and unique native wildlife are irreplaceable treasures that must be protected from over-clearing, water theft, and ecological collapse.",
        "In my own daily choices, I actively reduce waste, respect local waterways and native bushland, and support conservation of native species.",
        "People in my local area care for our rivers, parks, soils, and native wildlife rather than treating the environment as a dumping ground.",
        "Across Australia today, governments and industries actually protect and restore our rivers, soils, bushland, and native species rather than letting them degrade.",
    ),
    "3.4": (
        "On the driest inhabited continent, water and abundant solar and wind energy should be managed as shared national lifelines for long-term survival rather than private cartel profit.",
        "In my own household, I use water and energy responsibly and back practical transitions to clean, affordable power and water security.",
        "People in my community circle conserve water when needed and support affordable, reliable clean power for local households.",
        "Across Australia today, water basins and energy grids are actually managed reliably and affordably for households and farmers rather than hoarded or price-gouged.",
    ),
    "3.5": (
        "Because distance is Australia's great physical challenge, reliable transport, telecommunications, postal, and emergency medical networks must reach every town and suburb regardless of postcode.",
        "I support investing public funds into regional roads, rail, digital connectivity, and emergency services like the Flying Doctor so no town is left stranded.",
        "People in my local area look out for isolated neighbours and rely on connected local transport, communications, and medical lifelines.",
        "Across Australia today, every regional town and outer suburb actually receives dependable roads, public transport, digital coverage, and emergency medical care.",
    ),
    "3.6": (
        "The mineral and energy wealth dug from beneath Australian soil belongs to all Australians and must fund lasting public prosperity without destroying sacred heritage or local environments.",
        "In my own voting and civic stance, I back taxing multinational resource extraction fairly to fund public schools, hospitals, and sovereign wealth while protecting sacred sites.",
        "People in my everyday circle agree that Australia's mining and gas booms should leave lasting wealth for everyday Australians rather than vanishing offshore untaxed.",
        "Across Australia today, our tax and royalty laws actually capture a fair sovereign dividend from our mineral and gas wealth for the public good.",
    ),
    "3.7": (
        "Every Australian town and suburb should offer the physical foundations of a good life: secure homes, green backyards or parks, free public beaches, and welcoming places for neighbours to gather.",
        "In my own neighbourhood, I help keep local streets, parks, and beaches welcoming and support liveable, affordable town planning.",
        "My suburb or town has a genuine neighbourhood spirit where people share beaches, parks, and local streets respectfully.",
        "Across Australia today, urban and regional planning actually delivers affordable homes, green public space, and walkable community life rather than car-dependent sprawl.",
    ),

    # PLANE 4: DRIVE (WHY — MOTIVATION & THE GOOD LIFE)
    "4.1": (
        "We should honour the everyday people who pitch in—the volunteer on the fireline, the carer, and the honest worker—while calling out those who extract wealth without contributing.",
        "In my own life, I put in an honest share of effort at work and in the community rather than bludging on my mates or cutting down people who try.",
        "In my workplace and local community, people who pitch in, volunteer, and do the heavy lifting are genuinely backed and appreciated.",
        "Across Australia today, our economy and tax system actually reward honest workers, carers, and volunteers over corporate rent-seekers and speculators.",
    ),
    "4.2": (
        "The whole point of a productive economy should be a decent human life: a pay packet that covers a family's needs, a secure home, a protected two-day weekend, annual holidays, and a dignified retirement.",
        "In my own work and family life, I actively protect proper rest, weekends, and fair pay standards rather than letting hustle culture or unpaid overtime take over.",
        "People in my workplace and social circle respect the weekend, family time, and a fair living wage rather than glorifying burnout.",
        "Across Australia today, working households actually enjoy a pay packet with breathing room, a secure home, a protected weekend, and confidence in retirement.",
    ),
    "4.3": (
        "Healthy communities need accessible 'third places' outside work and home—local pubs, surf and sports clubs, community sheds, parks, and beaches—where people can recharge and belong without paying a fortune.",
        "I actively participate in or support local community spaces, clubs, parks, or beaches to stay connected with people outside work.",
        "My local community keeps its sports clubs, sheds, parks, and gathering spots welcoming and active for locals of all ages.",
        "Across Australia today, affordable community third places and grassroots clubs are actually protected and accessible rather than priced out or commercialised.",
    ),
    "4.4": (
        "Healthy ambition means striving for excellence while staying grounded—avoiding both tall-poppy envy that tears achievers down and status-obsessed panic that turns neighbours into rivals.",
        "In my own goals, I strive to do good work while staying humble and grounded, without letting financial anxiety or status comparison rule my life.",
        "People in my circle celebrate genuine skill and achievement while keeping each other grounded and realistic.",
        "Across Australia today, people can actually pursue their goals and enjoy life at a humane pace without being driven by housing and cost-of-living panic.",
    ),
    "4.5": (
        "Everyday Australian trust is built on small rituals of reciprocity—taking turns fairly, shouting your round, pitching in, and refusing to let predatory gambling or price-gouging strip-mine our communities.",
        "In my own habits, I always pay my fair share, return favours to mates, and refuse to let gambling or rip-off merchants take over social life.",
        "People around me still practise everyday generosity—shouting their round, helping a neighbour move—without keeping petty score.",
        "Across Australia today, our communities are actually protected from predatory pokies, relentless betting ads, and corporate price-gouging.",
    ),
    "4.6": (
        "The memory of past hardships—dispossession, convict chains, wartime sacrifice, and economic depressions—should make us determined never to let any neighbour fall into destitution.",
        "When someone around me hits hard times, illness, or job loss, I actually check in and lend a hand rather than judging or looking away.",
        "When people in my local community hit crisis or hardship, neighbours and local networks rally around them with practical support.",
        "Across Australia today, our welfare safety net and public services actually catch people in hard times with dignity rather than punitive cruelty.",
    ),
    "4.7": (
        "When a nation's drive is healthy, the result should be a confident, self-reliant citizenry and broad middle-class stability—not widespread exhaustion and political cynicism.",
        "Despite pressures, I work to stay constructive and engaged in my community rather than giving in to total cynicism or apathy.",
        "Among my friends, coworkers, and neighbours, there is still a shared belief that we can build a decent, stable life together.",
        "Across Australia today, our economic and political settings actually produce broad middle-class security and civic confidence rather than burnout and disillusionment.",
    ),

    # PLANE 5: METHOD (HOW — PRACTICAL MECHANICS)
    "5.1": (
        "Systems stay honest only when we empower practical problem-solvers—skilled tradespeople, scientists, frank public servants, union reps, independent umpires, and whistleblowers who call out wrongdoing.",
        "In my own work and life, I respect genuine expertise, play by the umpire's fair rules, and back whistleblowers who tell uncomfortable truths.",
        "In my workplace and circle, people respect skilled hands-on competence, honest union/worker reps, and independent umpires.",
        "Across Australia today, our institutions and laws actually protect whistleblowers, independent scientists, and honest umpires so they can do their job without retaliation.",
    ),
    "5.2": (
        "Australia should be a country that invents, builds, and arbitrates fairly—investing in local science, practical engineering, and living-wage awards rather than offshoring our brains and undercutting workers.",
        "In my own work and spending, I value quality Australian engineering, practical innovation, and fair award wages over cheap corner-cutting.",
        "People in my industry and circle take pride in solving problems ingeniously and support fair wage arbitration.",
        "Across Australia today, government and industry actually invest in homegrown R&D (like CSIRO), sovereign manufacturing, and fair wage-setting.",
    ),
    "5.3": (
        "The everyday arenas of Australian democracy—the local public school, the Saturday polling booth, the courtroom, the workplace, and the volunteer surf club—must remain open and equal for every class.",
        "I actively use, respect, and support shared public institutions—from the local public school and polling booth to community clubs.",
        "In my local area, public schools, community clubs, and Saturday sausage-sizzle polling booths bring people from all backgrounds together as equals.",
        "Across Australia today, our public schools, legal system, and civic spaces are actually funded to give every child and citizen an equal chance regardless of wealth.",
    ),
    "5.4": (
        "Every workplace and public system must balance practical efficiency with human fairness—efficiency that crushes people's dignity is a failure, not a success.",
        "When managing tasks or working with others, I look for practical efficiency while always treating coworkers and customers as human beings first.",
        "In my workplace and local services, people balance getting the job done efficiently with giving people a fair, humane hearing.",
        "Across Australia today, corporate and government systems actually balance competence and efficiency with genuine human fairness.",
    ),
    "5.5": (
        "Good work requires humane rhythms—proper rest breaks (smoko), predictable rosters, sick leave when needed, and doing the job properly rather than taking dangerous shortcuts or burying problems in another report.",
        "In my own work, I take pride in doing the job properly and safely, and I respect proper rest breaks and sick leave for myself and others.",
        "In my workplace and circle, people respect smoko breaks, safe rosters, and fixing real problems rather than cutting dodgy corners.",
        "Across Australia today, workplace rules and management practices actually enforce humane rosters, safe standards, and real action over box-ticking reports.",
    ),
    "5.6": (
        "Solving continental challenges requires combining modern engineering and science with 65,000 years of First Nations ecological knowledge and relational care for Country.",
        "I am open to learning from both modern science and traditional Indigenous knowledge (such as cultural burning and land care) to solve practical problems.",
        "People in my community circle respect combining practical modern science with First Nations land and fire management.",
        "Across Australia today, our environmental, fire, and water agencies actually integrate First Nations ecological wisdom alongside modern engineering.",
    ),
    "5.7": (
        "The bottom-line test of any government or corporate system is whether it delivers fair outcomes and working infrastructure in the real world—not automated robo-debt cruelty or bureaucratic maze-running.",
        "When dealing with rules or forms, I focus on real-world fairness and help others navigate bureaucratic mazes when they get stuck.",
        "People in my circle judge policies by whether they actually help real people on the ground rather than how good they look in a press release.",
        "Across Australia today, government services and corporate systems actually serve people humanely and effectively instead of trapping them in automated bureaucracy.",
    ),

    # PLANE 6: FOUNDATION (CAUSE — HISTORY & DEEP TIME)
    "6.1": (
        "To understand Australia, we must acknowledge every figure at our foundation—the 65,000-year First Nations Elder, the chained convict, the free settler, the gold digger, and the migrant—while honestly naming colonial dispossession.",
        "I personally take the time to understand and respect all streams of Australia's past—Indigenous, convict, settler, and migrant—without whitewashing the hard parts.",
        "People in my everyday circle can talk honestly about Australia's history—respecting both pioneer resilience and the truth of Indigenous dispossession.",
        "Across Australia today, our schools, memorials, and national culture actually honour all of our founding peoples honestly without erasure or culture-war spin.",
    ),
    "6.2": (
        "Australia's greatest legal achievements are the milestones that expanded justice—Federation by popular vote, the living wage, compulsory voting, and the overturning of Terra Nullius and White Australia.",
        "In my own civic stance, I actively defend Australia's landmark democratic achievements—equal voting, living wages, anti-discrimination, and native title.",
        "People in my circle are proud of Australia's democratic reforms like the secret ballot, compulsory voting, the living wage, and Mabo.",
        "Across Australia today, our parliaments and courts actively uphold and build upon wage justice, voting equality, multicultural inclusion, and native title.",
    ),
    "6.3": (
        "Australia has a sacred geography of memory—from ancient Indigenous songlines and Uluru to sites of convict pain, Eureka rebellion, wartime sacrifice, and democratic self-government—that must be protected from desecration.",
        "When I visit or vote on historic and Indigenous heritage places, I treat them with genuine respect rather than as mere tourist backdrops or real estate.",
        "People in my community respect sacred Indigenous sites, local war memorials, and historic civic landmarks.",
        "Across Australia today, our heritage laws and mining/development approvals actually protect sacred Indigenous Country and historic sites from destruction.",
    ),
    "6.4": (
        "Australia's history has always been a contest between two drives: generous solidarity and redemption on one side, versus invasion paranoia and lazy reliance on resource luck on the other.",
        "In my own political and social views, I choose solidarity and long-term building over fear-mongering, scapegoating, or lazy 'she'll be right' complacency.",
        "People in my everyday circle respond to national challenges with level-headed solidarity rather than panic or blaming minorities.",
        "Across Australia today, our national leadership and media actually appeal to courage, solidarity, and long-term vision rather than fear-driven politics and resource complacency.",
    ),
    "6.5": (
        "Unlike nations forged in civil war, Australia built its best institutions through bush survival skills, organised labour, the secret ballot, industrial arbitration, and constitutional conventions.",
        "When disagreements arise in my workplace or community, I back fair negotiation, democratic voting, and practical compromise over intimidation.",
        "People in my workplace and local community resolve disputes through fair talk, representation, and agreed rules.",
        "Across Australia today, major industrial and social disagreements are actually resolved through fair arbitration and democratic reform rather than union-busting or division.",
    ),
    "6.6": (
        "Our history does not begin in 1788; it is anchored in Deep Time—ancient Gondwanan ecosystems, the Great Barrier Reef, and 65,000 years of Indigenous fire-stick farming across an arid continent.",
        "I personally view Australia through a long-term lens—supporting the protection of ancient ecosystems like the Reef and learning from 65,000 years of human adaptation here.",
        "People in my circle appreciate the ancient depth of Australia's natural wonders and 65,000-year Indigenous history.",
        "Across Australia today, our climate, land, and Reef policies actually honour our deep-time ecological inheritance rather than sacrificing it for short-term extraction.",
    ),
    "6.7": (
        "Our historical inheritance leaves us with both proud achievements—the welfare safety net and civic consensus—and urgent unfinished business in First Nations justice, treaty, and truth-telling.",
        "I personally support finishing Australia's unfinished historical business—backing practical Indigenous justice, truth-telling, and a strong social safety net.",
        "People in my circle believe we should keep strengthening our social safety net and work in good faith toward lasting First Nations reconciliation.",
        "Across Australia today, our nation is actually repairing its social safety net and making real, good-faith progress on the unfinished business of reconciliation.",
    ),

    # PLANE 7: RESULT (EFFECT — SHARED COMMONWEALTH & FUTURE)
    "7.1": (
        "A healthy Australia should produce citizens who combine quiet civic decency, multicultural openness, and neighbourly care—rejecting the 'I've got mine' selfishness that turns housing and wealth into a zero-sum game.",
        "In my own life, I try to live as a generous neighbour and citizen—rejecting 'I've got mine' greed even when the system rewards selfishness.",
        "In my local community, people across different cultural backgrounds and generations still look out for one another as good neighbours.",
        "Across Australia today, our tax, housing, and social settings actually foster neighbourly cohesion rather than splintering us into 'I've got mine' competition.",
    ),
    "7.2": (
        "The tangible dividend of the Australian Commonwealth should be universal and rock-solid: bulk-billed Medicare, secure housing, accessible education, dignified superannuation, clean energy, and thriving biodiversity.",
        "In my own voting and civic choices, I consistently defend universal Medicare, public education, housing affordability, and fair superannuation for all.",
        "In my everyday circle, people rely on and strongly support universal Medicare, affordable education, secure housing, and dignified retirement.",
        "Across Australia today, our society and institutions actually deliver these core pillars—bulk-billed healthcare, affordable housing, accessible education, and clean energy—in practice.",
    ),
    "7.3": (
        "In the wider world, Australia should stand on its own two feet as an independent middle power, a respected Pacific family member, and a value-adding economy—not a passive quarry or uncritical client state.",
        "I personally support Australia building sovereign manufacturing capability, acting independently in foreign policy, and treating Pacific neighbours as family.",
        "People in my circle believe Australia should process more of what we dig up onshore and make our own independent decisions in the world.",
        "Across Australia today, our foreign and economic policies actually make us an independent, value-adding middle power and trusted Pacific partner.",
    ),
    "7.4": (
        "When forced to choose between competing national directions, Australia must put the Fair Go over raw market rule, sustainability over extraction, regional equity alongside cities, and reconciliation over division.",
        "When weighing up political choices, I put the Fair Go, environmental sustainability, regional fairness, and reconciliation ahead of short-term private self-interest.",
        "People in my everyday circle favour a fair balance between economy and human dignity, cities and regions, and unity over division.",
        "Across Australia today, our national policies actually choose the Fair Go, sustainability, regional equity, and reconciliation over market extraction and division.",
    ),
    "7.5": (
        "A self-governing people needs trustworthy instruments of truth—an independent electoral commission, honest public broadcasting and diverse media, royal commissions with teeth, and transparent economic reporting.",
        "In my own media habits, I seek out verifiable facts and independent reporting rather than echoing partisan spin or rage-bait.",
        "People in my circle value honest journalism, independent public broadcasters, and corruption watchdogs with real teeth.",
        "Across Australia today, our media landscape and integrity watchdogs actually give citizens the unvarnished truth rather than billionaire spin and cover-ups.",
    ),
    "7.6": (
        "The ultimate duty of every generation of Australians is to hand on a better commonwealth to the next—completing the clean energy transition, restoring housing fairness, and achieving full constitutional maturity.",
        "In my own decisions and vote, I prioritise giving young Australians and the next generation a fairer housing market, a safe climate, and a more mature nation.",
        "People in my circle care deeply about whether the next generation of Australians can afford a home and inherit a liveable climate.",
        "Across Australia today, our policies actually ensure young Australians inherit a fairer housing market, a clean energy economy, and a more united nation.",
    ),
    "7.7": (
        "Stripped to its essence, the meaning of Australia is the Land of the Second Chance and the Fair Go—transforming a place of exile and dispossession into a reconciled, egalitarian home where nobody is left behind.",
        "In how I treat others every day, I try to live out the ethic of the Second Chance and the Fair Go so nobody around me is written off.",
        "In my community circle, the spirit of the Second Chance and the Fair Go is still alive and practised between neighbours.",
        "All things considered, the Australia we live in today actually fulfills its highest promise as the Land of the Second Chance and the Fair Go.",
    ),
}


def clean_html(raw):
    text = re.sub(r"<[^>]+>", "", raw or "")
    text = html.unescape(text)
    # Strip Markdown bold/italic asterisks (**text** and *text*)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    return re.sub(r"\s+", " ", text).strip()


def extract_role_and_meaning(establishes, name):
    m = re.search(r"This establishes [^.*]*\*\*([^*]+)\*\*\.\s*(.*)", establishes, re.S)
    if m:
        role = clean_html(m.group(1))
        rest = clean_html(m.group(2))
    else:
        m2 = re.search(r"\*\*([^*]+)\*\*", establishes)
        role = clean_html(m2.group(1)) if m2 else clean_html(name)
        rest = clean_html(establishes)
    # Remove leading "This establishes X as the Y." if still present in rest
    rest = re.sub(r"^This establishes [^.]+?\.\s*", "", rest, flags=re.I)
    sents = re.split(r"(?<=[.!?])\s+", rest)
    core = sents[0].strip() if sents and sents[0] else rest[:220]
    if len(sents) > 1 and len(core) < 95:
        core = (core + " " + sents[1].strip()).strip()
    return role, core


def infer_tags(name, desc, estab, plane_num):
    blob = (name + " " + desc + " " + estab).lower()
    tags = []
    mapping = [
        ("mateship", ["mateship", "mate", "solidarity", "brotherhood", "shouting"]),
        ("fair-go", ["fair go", "egalitarian", "harvester", "equal", "living wage", "award"]),
        ("indigenous", ["indigenous", "aboriginal", "first nations", "dreaming", "songlines", "mabo", "uluru", "custodian", "terra nullius", "treaty", "apology", "voice", "stanner"]),
        ("housing", ["suburb", "home", "housing", "quarter-acre", "rent", "squatter", "property", "selector", "sprawl"]),
        ("work-wages", ["wage", "union", "strike", "worker", "workingman", "battler", "smoko", "sickie", "roster", "yakka", "bludger"]),
        ("democracy", ["vote", "voting", "ballot", "constitution", "parliament", "referendum", "senate", "federation", "republic", "royal commission", "spill", "faceless"]),
        ("land-climate", ["bush", "drought", "flood", "fire", "red centre", "river", "water", "sun", "wind", "reef", "gondwana", "arid", "soil", "marsupial", "el niño"]),
        ("economy-mining", ["gold", "miner", "mining", "quarry", "commodity", "uranium", "opencut", "superannuation", "treasury", "boom", "slump", "depression", "lucky country"]),
        ("health-welfare", ["medicare", "pension", "welfare", "hospital", "flying doctor", "care", "nanny state"]),
        ("culture-sport", ["sport", "cricket", "bradman", "ashes", "beach", "surf", "pub", "bbq", "larrikin", "tall poppy", "cringe", "anzac", "digger", "gallipoli"]),
        ("innovation", ["stringybark", "improvis", "wifi", "csiro", "black box", "plough", "bricoleur", "science", "scientist"]),
        ("world-region", ["pacific", "asia", "asian", "alliance", "expat", "immigrant", "multicultural", "white australia", "distance"]),
    ]
    for tag, kws in mapping:
        if any(k in blob for k in kws):
            tags.append(tag)
    if not tags:
        tags.append(PLANE_META[plane_num - 1]["tags"][0])
    return tags[:4]


def _role_tag(clean_name, role):
    """Return ' (Role)' only if role is meaningfully distinct from clean_name."""
    cn_norm = re.sub(r"^the\s+", "", clean_name.lower()).strip()
    rl_norm = re.sub(r"^the\s+", "", role.lower()).strip()
    if not rl_norm or rl_norm == cn_norm or rl_norm in cn_norm:
        return ""
    return f" ({role})"


def _clean_rationale(rationale):
    """Strip raw (+ψ)/(-υ) math shorthand from rationale for plain-English reading."""
    txt = clean_html(rationale)
    txt = re.sub(r"\s*\([+-][υψv]\)", "", txt)
    return txt.rstrip(".")


# Nodes whose title is an environmental condition, historical object, or complacency trap
# where "practise and stand up for [Name]" sounds robotic unless framed around its lesson:
PRINCIPLE_OVERRIDES = {
    "The Drought": "stoic endurance, water conservation, and mutual support through dry seasons",
    "The Flood": "respecting floodplains and pitching in to rescue neighbours when floodwaters surge",
    "The Sunburnt Country": "resilient love and respect for Australia's harsh, volatile landscape",
    "The Weird Melancholy": "quiet reflection and solidarity amidst the ancient stillness of the bush",
    "The Never-Never": "humility and respect toward the vast, remote interior of the continent",
    "The Saltbush": "hardy adaptation and living within the arid limits of the land",
    "The Marsupial": "adaptive efficiency—doing more with less in a fragile, unique ecosystem",
    "Gondwana": "protecting Australia's irreplaceable Gondwanan wildlife and ancient evolutionary heritage",
    "The Thirst": "careful water stewardship and engineering on the driest inhabited continent",
    "The Windmill": "practical bush engineering that sustains life in dry country",
    "The Sprawl": "making suburban growth liveable, connected, and affordable rather than car-dependent sprawl",
    "The Wealth": "turning Australia's natural resource wealth into lasting public capability rather than lazy complacency",
    "The Impact": "respecting the deep geological age and ancient scars of the Australian continent",
    "The Stump Jump Plough": "inventing practical local tools that work with the Australian landscape",
    "The Boomerang": "respecting Indigenous aerodynamic genius and sustainable resource design",
    "The Black Box": "backing world-leading Australian safety engineering and scientific invention",
    "The Wifi": "funding public research (like CSIRO) and keeping sovereign inventions for the public good",
    "The Home Owner": "ensuring secure, affordable home ownership is achievable for ordinary working families",
}


def build_vector_questions(name, clean_name, role, core_meaning, v, psi, zone, is_fn, rationale, plane_num=1):
    cm = core_meaning.rstrip(".")
    cm_low = cm[0].lower() + cm[1:] if len(cm) > 1 else cm
    rtag = _role_tag(clean_name, role)
    rat_clean = _clean_rationale(rationale)

    if is_fn:
        if v < 0:
            qA = f"We should recognise the historical wound of {clean_name}{rtag}—{cm_low}—and actively work to heal and overcome it."
            qB = f"In my own choices and speech, I actively reject and refuse to excuse {clean_name}."
            qC = f"People in my everyday circle agree we should heal {clean_name} and treat First Nations people with fairness and respect."
            qD = f"Across Australia today, our society and institutions actually address and dismantle {clean_name} rather than denying or entrenching it."
        else:
            qA = f"We should honour the First Nations principle of {clean_name}{rtag}: {cm_low}."
            qB = f"In my own daily life and civic choices, I actively respect and support {clean_name} rather than treating it as tokenism."
            qC = f"People in my everyday circle believe we should respect {clean_name} and actually honour it in practice."
            qD = f"Across Australia today, our wider society and institutions actually uphold and integrate {clean_name} in practice."
        return qA, qB, qC, qD

    # Handle "A vs. B" tension vectors (e.g. "Sustainability vs. Extraction", "The Fair Go vs. The Market")
    if " vs. " in clean_name:
        left_side, right_side = [s.strip() for s in clean_name.split(" vs. ", 1)]
        qA = f"When navigating the tension of {clean_name}{rtag}, Australia should prioritise {left_side} over raw {right_side}: {cm_low}."
        qB = f"In my own daily choices and voting, I actually back {left_side} when it conflicts with {right_side}."
        qC = f"People in my everyday circle believe we should put {left_side} ahead of {right_side} and act accordingly."
        qD = f"Across Australia today, our economic and political institutions actually put {left_side} ahead of {right_side} in practice."
        return qA, qB, qC, qD

    if v > 0:
        principle_phrase = PRINCIPLE_OVERRIDES.get(clean_name)
        if principle_phrase:
            qA = f"We should uphold the Australian lesson of {clean_name}{rtag}—{principle_phrase} ({cm_low})."
            qB = f"In my own choices and civic stance, I actively support {principle_phrase}."
            qC = f"People in my everyday circle value and practise {principle_phrase}."
            qD = f"Across Australia today, our society and institutions actually deliver {principle_phrase} in practice."
        else:
            qA = f"We should uphold the Australian principle of {clean_name}{rtag}: {cm_low}."
            qB = f"In my own everyday life and civic choices, I actually stand by and practise the ethic of {clean_name}."
            qC = f"The people in my everyday circle believe in the ethic of {clean_name} and actually live it out."
            qD = f"Across Australia today, our society and institutions actually uphold and deliver {clean_name} in practice."
    elif v < 0:
        # Negative / Shadow Kanon Vector (Greatest Lie, Greater Evil, Lesser Evil)
        qA = f"We should see through and reject the national flaw of {clean_name}{rtag} ({cm_low})."
        qB = f"In my own everyday actions, I refuse to practise or excuse {clean_name} even when it would be convenient."
        qC = f"People in my everyday circle see through {clean_name} and refuse to practise or excuse it."
        qD = f"Across Australia today, our wider society and institutions actually resist and overcome {clean_name} rather than being captured by it."
    else:
        # Neutral / Constraint / Continental Reality (v == 0)
        qA = f"We should respect and adapt wisely to the continental reality of {clean_name}{rtag}: {cm_low}."
        qB = f"In my own outlook and habits, I respect the reality of {clean_name} rather than ignoring it."
        qC = f"People in my local community understand the reality of {clean_name} and adapt practically to it."
        qD = f"Across Australia today, our infrastructure, planning, and institutions actually adapt wisely to {clean_name}."

    return qA, qB, qC, qD


def format_sense_should_would(sense_tuple, sense_title):
    qA, qB, qC, qD = sense_tuple
    return qA, qB, qC, qD



def main():
    # 1. Load Hanson verdicts
    hanson_verdicts = {}
    hanson_files = sorted(glob.glob(os.path.join(HANSON_HTML_DIR, "Plane_*_*.html")))
    for hf in hanson_files:
        htxt = open(hf, encoding="utf-8").read()
        matches = re.findall(
            r'<span class="text-xs font-mono text-gray-500 block mb-1">([^<]+)</span>\s*<h4[^>]*>([^<]+)</h4>.*?<span[^>]*>\s*(HIT|FAIL)\s*</span>',
            htxt,
            re.S,
        )
        for addr, nm, verd in matches:
            hanson_verdicts[(addr.strip(), clean_html(nm))] = verd.strip()

    # 2. Load Albo verdicts (Planes 1-3)
    albo_verdicts = {}
    albo_files = sorted(glob.glob(os.path.join(ALBO_MD_DIR, "Plane_*_*.md")))
    for af in albo_files:
        atxt = open(af, encoding="utf-8").read()
        matches = re.findall(
            r"\*\*\(([A-Za-z]+\.[A-Za-z]+\.[A-Za-z]+)\)\s+([^(]+?)\s*\([^)]+\):\s*(HIT|FAIL)",
            atxt,
        )
        for addr, nm, verd in matches:
            albo_verdicts[(addr.strip(), nm.strip())] = verd.strip()

    # 3. Parse Plane HTMLs and Compact JSONs
    planes_out = []
    senses_out = []
    vectors_out = []

    json_files = sorted(glob.glob(os.path.join(COMPACT_DIR, "Plane_*_compact.json")))
    html_files = sorted(glob.glob(os.path.join(KANON_HTML_DIR, "Plane_*_*.html")))

    for idx in range(7):
        pmeta = dict(PLANE_META[idx])
        pnum = pmeta["n"]
        jdata = json.load(open(json_files[idx], encoding="utf-8"))
        htxt = open(html_files[idx], encoding="utf-8").read()

        # Extract Plane quote, attribution, totality
        q_m = re.search(r"<blockquote[^>]*>(.*?)</blockquote>", htxt, re.S)
        c_m = re.search(r"<cite[^>]*>(.*?)</cite>", htxt, re.S)
        tot_m = re.search(
            r'<div class="prose prose-lg max-w-none text-gray-600 leading-relaxed">\s*(.*?)\s*</div>',
            htxt,
            re.S,
        )
        pmeta["quote"] = clean_html(q_m.group(1)).strip('"') if q_m else ""
        pmeta["attribution"] = clean_html(c_m.group(1)).lstrip("—").strip() if c_m else ""
        pmeta["totality"] = clean_html(tot_m.group(1)) if tot_m else ""

        # Extract Sense titles & narratives from HTML
        s_titles = re.findall(
            r'<h3 class="text-2xl font-bold tracking-tight font-serif">\s*([^<]+?)\s*</h3>',
            htxt,
        )
        s_narrs = re.findall(
            r'<div class="prose prose-lg max-w-none text-gray-700 leading-relaxed font-serif">\s*(.*?)\s*</div>',
            htxt,
            re.S,
        )

        # Group vectors by sense
        by_sense = {sk: [] for sk in S_ORDER}
        for v_item in jdata:
            s_code = v_item["address"].split(".")[1]
            by_sense[s_code].append(v_item)

        p_u_vals = []
        p_psi_vals = []

        for s_idx, s_code in enumerate(S_ORDER, 1):
            sense_id = f"{pnum}.{s_idx}"
            sense_addr = f"{pmeta['code']}.{s_code}"
            raw_title = s_titles[s_idx - 1].strip() if s_idx <= len(s_titles) else f"The {s_code} of the {pmeta['code']}"
            raw_narr = clean_html(s_narrs[s_idx - 1]) if s_idx <= len(s_narrs) else ""
            # Remove leading "The Narrative of ...:" prefix if present
            raw_narr = re.sub(r"^The Narrative of [^:]+:\s*", "", raw_narr)
            # Strip any trailing "The Totality of Australian ..." that leaked from Plane footer
            raw_narr = re.sub(r"\s*The Totality of Australian .*$", "", raw_narr, flags=re.S).strip()

            s_vecs = by_sense[s_code]
            s_u = round(sum(x["coordinates"]["v"] for x in s_vecs) / max(1, len(s_vecs)), 2)
            s_psi = round(sum(x["coordinates"]["psi"] for x in s_vecs) / max(1, len(s_vecs)), 2)
            p_u_vals.extend(x["coordinates"]["v"] for x in s_vecs)
            p_psi_vals.extend(x["coordinates"]["psi"] for x in s_vecs)

            qA, qB, qC, qD = format_sense_should_would(SENSE_QUESTIONS[sense_id], raw_title)

            # Collect sense tags from constituent vectors
            sense_tags = []
            vec_uids = []
            sense_vec_objs = []

            for v_pos, v_item in enumerate(s_vecs, 1):
                addr = v_item["address"]
                raw_name = v_item["name"]
                is_fn = "[First Nations Perspective]" in raw_name
                clean_nm = raw_name.replace("[First Nations Perspective]", "").strip()
                uid = f"{sense_id}.{v_pos}"

                est_raw = v_item.get("establishes", "")
                # Fix upstream data bug on 3.2.3 Custodianship [First Nations Perspective]
                if uid == "3.2.3" and is_fn:
                    est_raw = (
                        "This establishes **Custodianship** as the **Law**. "
                        "The land cannot be 'empty' because it is a living entity with which the people are in constant dialogue. "
                        "Where colonial law saw a vacuum to be filled, Indigenous law saw a fullness to be maintained—shifting the legal framework from 'Rights of Possession' to 'Duties of Care.'"
                    )
                # Clarify 6.1.7 "The Immigrant" (which is the -0.6 White Australia Exclusion vector)
                if uid == "6.1.7" and clean_nm == "The Immigrant":
                    clean_nm = "The Immigrant (White Australia Exclusion)"
                    raw_name = "The Immigrant (White Australia Exclusion)"

                role, core_meaning = extract_role_and_meaning(est_raw, clean_nm)
                v_coord = v_item["coordinates"]["v"]
                psi_coord = v_item["coordinates"]["psi"]
                zone = v_item.get("zone", "Good")
                rationale = v_item.get("judgment_rationale", "")

                vqA, vqB, vqC, vqD = build_vector_questions(
                    raw_name, clean_nm, role, core_meaning, v_coord, psi_coord, zone, is_fn, rationale, pnum
                )

                # Match Hanson verdict
                hv = hanson_verdicts.get((addr, v_item["name"]))
                if not hv:
                    for (ha, hn), hval in hanson_verdicts.items():
                        if ha == addr and (clean_nm.lower() in hn.lower() or hn.lower() in clean_nm.lower()):
                            hv = hval
                            break
                in_hanson_353 = hv is not None

                # Match Albo verdict
                av = albo_verdicts.get((addr, v_item["name"]))
                if not av:
                    for (aa, an), aval in albo_verdicts.items():
                        if aa == addr and (clean_nm.lower() in an.lower() or an.lower() in clean_nm.lower()):
                            av = aval
                            break

                v_tags = infer_tags(clean_nm, v_item.get("description", ""), est_raw, pnum)
                for tg in v_tags:
                    if tg not in sense_tags:
                        sense_tags.append(tg)

                est_clean = clean_html(est_raw)
                role_label = role if role.lower().startswith("the ") else f"The {role}"
                if v_coord < 0:
                    help_obj = {
                        "highA": f"You see through and reject {clean_nm} ({role})—recognising how it distorts or betrays the Australian ethos ({core_meaning}).",
                        "lowA": f"You accept, excuse, or do not see a problem with {clean_nm}, allowing its extractive or divisive logic to stand.",
                        "highB": f"In your daily life and community, people are free from {clean_nm} and actively resist its pull.",
                        "lowB": f"Your community, workplace, or political reality is still trapped in or harmed by {clean_nm}.",
                        "note": f"⚠️ Corrective / Shadow Node (υ = {v_coord}, ψ = {psi_coord}): Because {clean_nm} is a negative shadow or failure mode in the Australian Kanon, the rating scale is framed in the restorative direction—rating +1 to +5 means rejecting and overcoming the shadow (Kanon HIT), while rating −1 to −5 means being captured by it (Kanon FAIL). {est_clean}",
                    }
                elif is_fn:
                    help_obj = {
                        "highA": f"You recognise and honour {clean_nm} ({role}) as a foundational First Nations pillar of Australia ({core_meaning}).",
                        "lowA": f"You dismiss or overlook {clean_nm} as part of Australia's living identity and law.",
                        "highB": f"In practice, {clean_nm} is respected, protected, and lived in your community and institutions.",
                        "lowB": f"In practice, {clean_nm} is ignored, tokenised, or blocked from real recognition.",
                        "note": f"🪃 First Nations Perspective Node (υ = +{v_coord}, ψ = {psi_coord}): This node anchors the 65,000-year Indigenous continuum alongside the post-1788 Commonwealth. {est_clean}",
                    }
                else:
                    help_obj = {
                        "highA": f"You strongly hold to {clean_nm} ({role}) as a core part of what Australia should be ({core_meaning}).",
                        "lowA": f"You do not see {clean_nm} as an important or desirable part of the Australian ethos.",
                        "highB": f"You and the people around you actually experience and practise {clean_nm} in everyday Australian life.",
                        "lowB": f"Even if people talk about {clean_nm}, it is missing, eroded, or blocked in daily reality.",
                        "note": f"Kanon Role — {role_label} (υ = {v_coord:+g}, ψ = {psi_coord:+g} · {zone}): {est_clean}",
                    }

                vec_obj = {
                    "uid": uid,
                    "addr": addr,
                    "plane": pnum,
                    "senseId": sense_id,
                    "name": raw_name,
                    "cleanName": clean_nm,
                    "role": role,
                    "fn": is_fn,
                    "quote": clean_html(v_item.get("canonical_quote", "")),
                    "attribution": clean_html(v_item.get("attribution", "")),
                    "source": clean_html(v_item.get("source", "")),
                    "description": clean_html(v_item.get("description", "")),
                    "establishes": est_clean,
                    "coreMeaning": core_meaning,
                    "coords": {"v": v_coord, "psi": psi_coord},
                    "zone": zone,
                    "rationale": clean_html(rationale),
                    "hansonVerdict": hv,
                    "alboVerdict": av,
                    "inHanson353": in_hanson_353,
                    "qA": vqA,
                    "qB": vqB,
                    "qC": vqC,
                    "qD": vqD,
                    "help": help_obj,
                    "tags": v_tags,
                }
                vectors_out.append(vec_obj)
                sense_vec_objs.append(vec_obj)
                vec_uids.append(uid)

            v_names_list = [v["name"].replace("[First Nations Perspective]", "[FN]").strip() for v in sense_vec_objs]
            # If the upstream HTML had a placeholder narrative ("The Narrative of the ..."), synthesise a real narrative
            if not raw_narr or raw_narr.lower().startswith("the narrative of ") or len(raw_narr) < 45:
                pos_highlights = [f"{v['cleanName']} ({v['role']})" for v in sense_vec_objs if v["coords"]["v"] >= 0][:4]
                shd_highlights = [f"{v['cleanName']} ({v['role']})" for v in sense_vec_objs if v["coords"]["v"] < 0]
                shd_clause = (
                    f", while confronting the shadow of {', '.join(shd_highlights)}"
                    if shd_highlights
                    else ""
                )
                raw_narr = (
                    f"In Plane {pnum} ({pmeta['name']}), {sense_addr} ({S_SUBTITLES[s_code]}) maps how Australian {pmeta['name'].lower()} is expressed through "
                    f"{', '.join(pos_highlights)}{shd_clause}. {qA}"
                )

            sense_help = {
                "highA": f"You strongly endorse the Australian ethos of {sense_addr} ({raw_title}), spanning {', '.join(v_names_list[:4])}, and more.",
                "lowA": f"You feel disconnected from or skeptical of the traditional Australian values grouped under {sense_addr} ({raw_title}).",
                "highB": f"In your everyday Australian life, the promise of {sense_addr} is genuinely lived, working, and accessible.",
                "lowB": f"In practice, {sense_addr} feels broken, priced out, or blocked by systemic friction where you live.",
                "note": f"Matrix Sense {sense_id} ({sense_addr}): Synthesises {len(s_vecs)} Kanon vectors ({', '.join(v_names_list)}). {raw_narr}",
            }

            sense_obj = {
                "id": sense_id,
                "addr": sense_addr,
                "plane": pnum,
                "senseIdx": s_idx,
                "senseCode": s_code,
                "title": raw_title,
                "shortTitle": f"{sense_addr} · {S_SUBTITLES[s_code]}",
                "narrative": raw_narr,
                "coords": {"v": s_u, "psi": s_psi},
                "vectorNames": v_names_list,
                "vectorUids": vec_uids,
                "qA": qA,
                "qB": qB,
                "qC": qC,
                "qD": qD,
                "help": sense_help,
                "tags": sense_tags[:5],
            }
            senses_out.append(sense_obj)

        pmeta["coords"] = {
            "v": round(sum(p_u_vals) / max(1, len(p_u_vals)), 2),
            "psi": round(sum(p_psi_vals) / max(1, len(p_psi_vals)), 2),
        }
        pmeta["help"] = {
            "highA": f"You strongly hold to Pillar {pnum} ({pmeta['pillar']} — {pmeta['name']}): {pmeta['blurb']}.",
            "lowA": f"You place lower personal weight on Pillar {pnum} ({pmeta['pillar']}) or disagree with how Australia defines {pmeta['name']}.",
            "highB": f"In your daily life and community, Pillar {pnum} ({pmeta['name']}) is thriving and experienced in practice.",
            "lowB": f"In daily reality, Pillar {pnum} ({pmeta['name']}) is eroded, blocked, or out of reach.",
            "note": f"Plane {pnum} ({pmeta['code']} · {pmeta['domain']} Domain): {pmeta['totality']}",
        }
        planes_out.append(pmeta)

    # 4. Archetypes & Historical/Audited Figures for 12axes-style matching
    archetypes = [
        {
            "id": "stoic_guardian",
            "name": "The Stoic Guardian",
            "subtitle": "The Ideal Australian Synthesis",
            "coords": {"v": 0.85, "psi": 0.70},
            "zone": "Greater Good",
            "quote": "The world is hard, so we must be soft with each other.",
            "badge": "The Kanon Ideal",
            "color": "#1F7A6B",
            "desc": "You embody the full tensile strength of the Australian Kanon: enduring the harshness of the continent without losing the horizontal bond of Mateship. You view society peer-to-peer, pick up a hose when crisis hits, respect 65,000 years of Custodianship, and judge ideas by the Pub Test and the Fair Go.",
            "pillars": [0.95, 0.90, 0.90, 0.92, 0.90, 0.92, 0.90],
        },
        {
            "id": "betrayed_battler",
            "name": "The Trapped Idealist (Betrayed Battler)",
            "subtitle": "High Kanon Ethos · Blocked Lived Reality",
            "coords": {"v": 0.65, "psi": -0.25},
            "zone": "Lesser Good (Under Strain)",
            "quote": "We fight it down, and we live it down, or we bear it bravely well.",
            "badge": "The Betrayed Promise",
            "color": "#B98B22",
            "desc": "You hold the Australian promise deeply in your heart (high Sense)—you believe in the Fair Go, Mateship, honest yakka, and a decent home—but systemic blockers like cost of living, housing lockouts, or institutional capture stop you from living it (low Use). You are the living proof of why the Kanon matters: you feel the betrayal because you still keep the faith.",
            "pillars": [0.80, 0.65, 0.60, 0.75, 0.70, 0.70, 0.55],
        },
        {
            "id": "larrikin_skeptic",
            "name": "The Larrikin Skeptic",
            "subtitle": "Anti-Authoritarian Bullshit Detector",
            "coords": {"v": 0.55, "psi": 0.60},
            "zone": "Greater Good",
            "quote": "Jack is as good as his master, if not a good deal better.",
            "badge": "The Court Jester & Leveler",
            "color": "#D97706",
            "desc": "You are the immune system of Australian democracy. Allergic to wowsers, corporate spin, Faceless Men, and petty Nanny State rules, you use dry wit and empirical common sense to cut down hubris while fiercely defending the underdog and horizontal equality.",
            "pillars": [0.88, 0.72, 0.65, 0.80, 0.85, 0.68, 0.70],
        },
        {
            "id": "bush_mechanic",
            "name": "The Stringybark Improviser",
            "subtitle": "Pragmatic Genius & Builder",
            "coords": {"v": 0.60, "psi": 0.75},
            "zone": "Greater Good",
            "quote": "Stringy-bark and Green-hide are the mainstay of Australia.",
            "badge": "The Bricoleur",
            "color": "#2E5B8A",
            "desc": "You judge everything by whether it actually works. Descending from the Bush Mechanic, the Stump Jump Plough, and CSIRO inventors, you cut through red tape to build practical solutions, value generalist capability over titled specialists, and volunteer quietly when the job needs doing.",
            "pillars": [0.78, 0.75, 0.75, 0.88, 0.94, 0.65, 0.78],
        },
        {
            "id": "indigenous_steward",
            "name": "The Deep-Time Steward & Reconciler",
            "subtitle": "Country, Truth-Telling & Custodianship",
            "coords": {"v": 0.90, "psi": 0.55},
            "zone": "Greater Good",
            "quote": "We ask for justice, not for charity. Always Was, Always Will Be.",
            "badge": "The Custodian",
            "color": "#4F46E5",
            "desc": "You anchor Australian identity in the 65,000-year continuum of Country and historical truth. You know that the land owns us rather than the reverse, and that Australia can only become whole by healing the wound of Terra Nullius and uniting the Ancient Raft with the Commonwealth.",
            "pillars": [0.85, 0.82, 0.95, 0.80, 0.80, 0.96, 0.88],
        },
        {
            "id": "quiet_australian",
            "name": "The Quiet Suburban Anchor",
            "subtitle": "Suburban Stability & The Fair Baseline",
            "coords": {"v": 0.45, "psi": -0.35},
            "zone": "Lesser Good",
            "quote": "The home is the foundation of sanity and sobriety.",
            "badge": "The Anchor",
            "color": "#64748B",
            "desc": "You are the stabilising ballast of the Commonwealth—focused on family, home, fair rules, and a peaceful life on the verandah or at the beach. You distrust extremes on both sides, keep the community running day-to-day, and expect government to maintain order and the Fair Go without drama.",
            "pillars": [0.65, 0.70, 0.62, 0.65, 0.65, 0.55, 0.68],
        },
        {
            "id": "siege_sentinel",
            "name": "The Siege Sentinel",
            "subtitle": "Inward-Pointed Guardian",
            "coords": {"v": -0.15, "psi": 0.35},
            "zone": "Greatest Lie / Contested Ground",
            "quote": "The Fair Go is real—it's just fenced off for the ingroup.",
            "badge": "The Fortress Guard",
            "color": "#E11D48",
            "desc": "You strongly invoke traditional Australian symbols—the Battler, the Anzac, the Pub Test, and sovereign borders—but draw the circle of Mateship tightly around an ingroup, viewing multiculturalism, First Nations treaties, or global change as threats to be walled out.",
            "pillars": [0.42, 0.48, 0.45, 0.55, 0.42, 0.30, 0.35],
        },
        {
            "id": "quarry_extractor",
            "name": "The Lucky Country Quarryman",
            "subtitle": "Speculative & Transactional Operator",
            "coords": {"v": -0.45, "psi": 0.45},
            "zone": "Greatest Lie",
            "quote": "Dig it up, flip the property, she'll be right.",
            "badge": "The Speculator",
            "color": "#991B1B",
            "desc": "You treat Australia primarily as an economic quarry and speculative asset class—prioritising private accumulation, property leverage, and resource extraction over horizontal solidarity, ecological limits, or the Commonwealth social contract.",
            "pillars": [0.25, 0.30, 0.22, 0.35, 0.30, 0.20, 0.28],
        },
    ]

    figures = [
        {
            "id": "monash",
            "name": "General Sir John Monash",
            "role": "The Civic Builder & Commander (1865–1931)",
            "coords": {"v": 0.85, "psi": 0.85},
            "alignment": 92,
            "pillars": [0.92, 0.90, 0.86, 0.94, 0.98, 0.88, 0.92],
            "desc": "Engineered both victory through meticulous preparation and peace-time public utilities (SEC Victoria), embodying egalitarian merit and pragmatic genius.",
        },
        {
            "id": "higgins",
            "name": "Justice H.B. Higgins",
            "role": "Architect of the Fair Go (Harvester Judgement, 1907)",
            "coords": {"v": 0.90, "psi": 0.65},
            "alignment": 91,
            "pillars": [0.90, 0.98, 0.80, 0.94, 0.92, 0.92, 0.90],
            "desc": "Codified the Living Wage into law—establishing that markets must serve human dignity in a civilised community.",
        },
        {
            "id": "cooper",
            "name": "William Cooper",
            "role": "Yorta Yorta Elder & Civil Rights Pioneer (1860–1941)",
            "coords": {"v": 0.92, "psi": 0.60},
            "alignment": 90,
            "pillars": [0.92, 0.88, 0.96, 0.88, 0.84, 0.98, 0.94],
            "desc": "Demanded 'justice, not charity'—bridging 65,000 years of Custodianship with active democratic citizenship.",
        },
        {
            "id": "lawson",
            "name": "Henry Lawson",
            "role": "Poet of Mateship & The Battler (1867–1922)",
            "coords": {"v": 0.68, "psi": 0.25},
            "alignment": 82,
            "pillars": [0.95, 0.74, 0.84, 0.86, 0.80, 0.78, 0.75],
            "desc": "Gave voice to horizontal solidarity, the struggling bush worker, and fierce suspicion of class pretension.",
        },
        {
            "id": "keating",
            "name": "Paul Keating",
            "role": "Architect of Redfern, Superannuation & The Asian Century",
            "coords": {"v": 0.55, "psi": 0.78},
            "alignment": 76,
            "pillars": [0.76, 0.82, 0.70, 0.72, 0.78, 0.84, 0.86],
            "desc": "Named the lie of Terra Nullius at Redfern, oriented Australia toward Asia and the Republic, while advancing market deregulation.",
        },
        {
            "id": "horne",
            "name": "Donald Horne",
            "role": "Diagnostic Critic of 'The Lucky Country' (1964)",
            "coords": {"v": 0.65, "psi": 0.40},
            "alignment": 79,
            "pillars": [0.84, 0.80, 0.74, 0.78, 0.82, 0.76, 0.80],
            "desc": "Warned that Australia's grassroots decency was being squandered by second-rate elites coasting on resource luck.",
        },
        {
            "id": "kelly",
            "name": "Ned Kelly",
            "role": "The Larrikin Outlaw & Rebel (Jerilderie Letter, 1879)",
            "coords": {"v": 0.35, "psi": 0.75},
            "alignment": 64,
            "pillars": [0.82, 0.42, 0.72, 0.74, 0.76, 0.68, 0.45],
            "desc": "Fierce anti-authoritarian defiance against corrupt traps and squatter tyranny, pushed to armed rebellion.",
        },
        {
            "id": "menzies",
            "name": "Robert Menzies",
            "role": "Champion of 'The Forgotten People' & Suburban Stability",
            "coords": {"v": 0.35, "psi": -0.20},
            "alignment": 58,
            "pillars": [0.55, 0.68, 0.52, 0.66, 0.60, 0.48, 0.62],
            "desc": "Anchored post-war suburban home ownership and university expansion, while maintaining British imperial deference.",
        },
        {
            "id": "albanese",
            "name": "Anthony Albanese (Audited Record)",
            "role": "Institutional Labor Manager (Partial Kanon Audit)",
            "coords": {"v": 0.18, "psi": -0.12},
            "alignment": 54,
            "pillars": [0.58, 0.60, 0.48, 0.54, 0.52, 0.56, 0.52],
            "desc": "Strong rhetorical alignment on Medicare, Voice, and wages, tempered by cautious incrementalism and institutional risk-aversion in actuality.",
        },
        {
            "id": "hanson",
            "name": "Pauline Hanson (Full 353-Vector Audit)",
            "role": "The Siege Matriarch (16.1% Net Alignment · 205H / 148F)",
            "coords": {"v": -0.05, "psi": -0.01},
            "alignment": 16,
            "pillars": [0.44, 0.48, 0.42, 0.52, 0.40, 0.28, 0.32],
            "desc": "Audited across all 353 vectors: hits populist Battler/Pub Test vectors rhetorically, but fails universal Mateship, First Nations, and multicultural Commonwealth vectors.",
        },
    ]

    # 5. Curated Australian Kanon Glossary for inline 12axes-style tooltips
    glossary = [
        {"id": "mateship", "term": "Mateship", "definition": "The horizontal bond of unconditional loyalty, mutual aid, and equality between peers—treating a stranger or co-worker as a partner in survival rather than a superior or inferior.", "match": ["Mateship", "mateship"]},
        {"id": "larrikin", "term": "The Larrikin", "definition": "The irreverent, anti-authoritarian Australian jester who uses dry humour and skepticism to puncture pretension, wowsers, and self-important authority.", "match": ["Larrikin", "larrikin", "Larrikinism"]},
        {"id": "battler", "term": "The Battler", "definition": "The ordinary working Australian who keeps going with quiet dignity despite economic hardship, rigged odds, or a harsh environment.", "match": ["Battler", "Battler's", "battler"]},
        {"id": "fair_go", "term": "The Fair Go", "definition": "Australia's core moral rule ('the Rule of 1'): every person deserves a level playing field, a living wage, and a fair chance without privilege rigging the game.", "match": ["Fair Go", "fair suck of the sauce bottle"]},
        {"id": "harvester", "term": "Harvester Judgement (1907)", "definition": "Landmark 1907 ruling by Justice H.B. Higgins that established the world's first statutory Living Wage—declaring wages must meet 'the normal needs of the average employee regarded as a human being living in a civilized community.'", "match": ["Harvester Judgement", "Harvester", "Living Wage Case", "Living Wage"]},
        {"id": "tall_poppy", "term": "Tall Poppy Syndrome", "definition": "The egalitarian habit of cutting down people who act superior, boastful, or forget they are 'a man for a' that'—originally aimed at arrogance and inherited rank rather than genuine excellence.", "match": ["Tall Poppy Syndrome", "Tall Poppy"]},
        {"id": "terra_nullius", "term": "Terra Nullius", "definition": "Latin for 'land belonging to no one'—the colonial legal fiction used by Britain in 1788 to erase 65,000 years of Aboriginal and Torres Strait Islander law and sovereignty, finally overturned by the High Court's 1992 Mabo decision.", "match": ["Terra Nullius", "terra nullius"]},
        {"id": "mabo", "term": "Mabo Decision (1992)", "definition": "The historic 1992 High Court ruling led by Meriam man Eddie Koiki Mabo that abolished the lie of Terra Nullius and recognised Native Title in Australian common law.", "match": ["Mabo Decision", "Mabo"]},
        {"id": "songlines", "term": "Songlines", "definition": "Ancient First Nations dreaming tracks and oral memory maps sung across the continent for tens of thousands of years—encoding law, waterholes, navigation, and ecological kinship into Country.", "match": ["Songlines", "songlines"]},
        {"id": "country", "term": "Country (First Nations)", "definition": "In Aboriginal and Torres Strait Islander cosmology, Country is not mere real estate—it is a living ancestral matrix of land, water, sky, law, and kin that owns and sustains human beings.", "match": ["Indigenous Country", "stewardship of Country", "connection to Country", "sacred Country"]},
        {"id": "stringybark", "term": "Stringybark and Greenhide", "definition": "19th-century bush shorthand for Australian bush improvisation—fixing anything with eucalyptus bark and untanned cattle hide when no specialist tools or spare parts exist.", "match": ["Stringybark and Greenhide", "Stringy-bark and Green-hide", "Stringybark"]},
        {"id": "bricoleur", "term": "Bricoleur / Bush Mechanic", "definition": "Someone who invents practical working solutions on the spot using whatever scraps and tools are at hand.", "match": ["Bricoleur", "Bush Mechanic"]},
        {"id": "washminster", "term": "Washminster Hybrid", "definition": "Australia's 1901 constitutional blend of British Westminster responsible cabinet government (House of Representatives) with an American-style federal Senate representing the states.", "match": ["Washminster", "Washminster hybrid"]},
        {"id": "faceless_men", "term": "Faceless Men", "definition": "Unaccountable party machine bosses, factional warlords, and backroom powerbrokers who install or knife prime ministers behind closed doors.", "match": ["Faceless Men"]},
        {"id": "leadership_spill", "term": "Leadership Spill", "definition": "A sudden party-room coup where MPs depose a sitting Prime Minister or party leader between elections.", "match": ["leadership spills", "Leadership Spill", "The Spill"]},
        {"id": "the_dismissal", "term": "The Dismissal (1975)", "definition": "The 11 November 1975 constitutional crisis when Governor-General Sir John Kerr sacked elected Prime Minister Gough Whitlam—exposing the tension between Vice-Regal reserve powers and democratic sovereignty.", "match": ["The Dismissal"]},
        {"id": "nanny_state", "term": "The Nanny State", "definition": "Australia's tendency to trade personal liberty for safety through dense layers of fines, permits, compliance signage, and paternalistic rules.", "match": ["Nanny State"]},
        {"id": "wowser", "term": "The Wowser", "definition": "Coinage popularised by C.J. Dennis and John Norton for a joyless, moralising puritan or busybody who wants to ban or police everyone else's harmless fun.", "match": ["Wowser", "wowsers"]},
        {"id": "pub_test", "term": "The Pub Test", "definition": "The vernacular standard of common sense: does a policy or excuse sound fair and believable to ordinary people having a quiet beer at the local pub?", "match": ["Pub Test"]},
        {"id": "cultural_cringe", "term": "The Cultural Cringe", "definition": "Term coined by A.A. Phillips (1950) for the colonial inferiority complex that assumes anything made or thought in Australia is second-rate until validated by London or New York.", "match": ["Cultural Cringe"]},
        {"id": "convict_stain", "term": "The Convict Stain", "definition": "19th-century shame over Australia's penal origins, which inverted over time into healthy skepticism of police, courts, and inherited authority.", "match": ["Convict Stain"]},
        {"id": "squatter", "term": "The Squatter", "definition": "Colonial oligarchs ('the Squattocracy') who seized vast tracts of Crown and Indigenous land for sheep stations, locking out small farmers and ordinary families—mirrored today by property hoarding and land-banking.", "match": ["Squatters", "Squatter", "squatter"]},
        {"id": "selector", "term": "The Selector", "definition": "Small family farmers under the 1860s Selection Acts who battled debt, drought, and Squatter monopolies to stake out an independent living on the land.", "match": ["The Selector", "Selector"]},
        {"id": "goyders_line", "term": "Goyder's Line", "definition": "The 1865 rainfall boundary mapped across South Australia by Surveyor-General George Goyder separating land suitable for crops from arid saltbush country—a permanent lesson that nature sets limits human hubris cannot ignore.", "match": ["Goyder's Line"]},
        {"id": "barassi_line", "term": "The Barassi Line", "definition": "The cultural meridian dividing Australian Rules Football country (South/West: VIC, SA, WA, TAS) from Rugby League/Union country (North/East: NSW, QLD).", "match": ["Barassi Line"]},
        {"id": "never_never", "term": "The Never-Never", "definition": "The remote, timeless outback beyond the settled horizon—a place of existential vastness, silence, and spiritual testing.", "match": ["Never-Never"]},
        {"id": "weird_melancholy", "term": "Weird Melancholy", "definition": "Marcus Clarke's 1876 phrase for the haunting, ancient, and uncanny atmosphere of the Australian bush.", "match": ["Weird Melancholy"]},
        {"id": "red_steer", "term": "The Red Steer", "definition": "Old bush idiom for an uncontrolled bushfire charging across dry country.", "match": ["The Red Steer", "Red Steer"]},
        {"id": "lucky_country", "term": "The Lucky Country", "definition": "Donald Horne's ironic 1964 diagnosis: 'Australia is a lucky country run mainly by second-rate people who share its luck'—warning that resource wealth was masking lazy leadership.", "match": ["Lucky Country"]},
        {"id": "populate_or_perish", "term": "Populate or Perish", "definition": "Post-WWII national slogan coined by Arthur Calwell driving mass European migration and industrial nation-building out of fear of continental isolation.", "match": ["Populate or Perish"]},
        {"id": "white_australia", "term": "White Australia Policy", "definition": "The racially exclusionary immigration regime enacted at Federation (Immigration Restriction Act 1901) and dismantled between 1966 and 1973.", "match": ["White Australia Policy", "White Australia", "The White Walls"]},
        {"id": "great_silence", "term": "The Great Silence", "definition": "Anthropologist W.E.H. Stanner's 1968 term for the deliberate erasure of Aboriginal history and frontier conflict from mainstream Australian memory.", "match": ["Great Silence"]},
        {"id": "uluru_statement", "term": "Uluru Statement from the Heart", "definition": "The 2017 First Nations consensus declaration calling for Voice, Treaty, and Truth (Makarrata) so Indigenous Australians can take their 'rightful place' in their own country.", "match": ["Uluru Statement", "Voice, Treaty, Truth"]},
        {"id": "eureka", "term": "Eureka Stockade (1854)", "definition": "The armed rebellion of Ballarat gold miners under the Southern Cross flag against unfair licensing taxes without parliamentary representation—the birthplace of Australian vernacular democracy.", "match": ["Eureka Stockade", "Eureka"]},
        {"id": "corowa_plan", "term": "The Corowa Plan (1893)", "definition": "Dr John Quick's breakthrough proposal that the Australian Constitution be drafted by an elected convention and ratified by popular vote of the people rather than colonial parliaments alone.", "match": ["Corowa Plan"]},
        {"id": "secret_ballot", "term": "The Secret Ballot (Australian Ballot)", "definition": "Pioneered in Victoria and South Australia in 1856: government-printed ballot papers marked in private booths so bosses and landlords could no longer intimidate voters—adopted worldwide as the 'Australian Ballot'.", "match": ["Secret Ballot"]},
        {"id": "preferential_voting", "term": "Preferential Voting", "definition": "Australia's voting system where citizens rank candidates (1, 2, 3...) so winners must command a broad majority of preferences, rewarding consensus over extremes.", "match": ["Preferential Voting", "The Calculus of preferences"]},
        {"id": "compulsory_voting", "term": "Compulsory Voting", "definition": "Introduced federally in 1924: treats voting not just as a private right but a shared civic duty, ensuring elections reflect the whole working public rather than only fired-up partisans.", "match": ["Compulsory Voting", "Compelled Voting"]},
        {"id": "fiscal_equalization", "term": "Fiscal Equalization", "definition": "The Commonwealth principle of distributing GST and federal revenue so every state and territory can provide comparable schools, hospitals, and roads regardless of its tax base.", "match": ["Fiscal Equalization"]},
        {"id": "smoko", "term": "Smoko", "definition": "The sacred mid-morning or afternoon rest pause on Australian worksites—a protected breather for tea, food, yarn, and human dignity during hard work.", "match": ["Smoko"]},
        {"id": "sickie", "term": "The Sickie", "definition": "Taking a day off work to recover one's sanity, health, or life balance—an informal safety valve against burnout.", "match": ["Sickie"]},
        {"id": "hard_yakka", "term": "Hard Yakka", "definition": "Adapted from the Jagera (Yagara) Indigenous language word 'yaga' (work): strenuous, honest physical labour.", "match": ["Hard Yakka", "yakka"]},
        {"id": "bludger", "term": "The Bludger", "definition": "Someone who leans on the effort of their mates without pitching in—violation of the Australian reciprocity contract (often weaponised by politicians against the vulnerable while ignoring corporate tax bludgers).", "match": ["Bludger", "bludger"]},
        {"id": "knocker", "term": "The Knocker", "definition": "A cynic who sits on the sidelines tearing down anyone who tries to build or improve something.", "match": ["Knocker"]},
        {"id": "shouting", "term": "Shouting a Round", "definition": "The unwritten pub law where each mate takes their turn buying a round of drinks for the group without keeping petty score.", "match": ["shouting your round", "shouting"]},
        {"id": "pokies", "term": "Pokies (Poker Machines)", "definition": "Electronic gaming machines concentrated in Australian pubs and clubs that extract billions from working communities.", "match": ["pokies", "Pokies"]},
        {"id": "stump_jump", "term": "Stump Jump Plough", "definition": "Invented in South Australia in 1876 by Richard and Clarence Smith: a hinged plough share that hopped over mallee roots instead of snapping, opening the continent to farming.", "match": ["Stump Jump Plough"]},
        {"id": "fire_stick", "term": "Fire-Stick Farming", "definition": "Term coined by archaeologist Rhys Jones for the sophisticated First Nations practice of cool, mosaic cultural burning to regenerate pastures and prevent catastrophic megafires.", "match": ["Fire-Stick Farming", "cultural burning"]},
        {"id": "rfds", "term": "Royal Flying Doctor Service (RFDS)", "definition": "Founded by Rev. John Flynn in 1928 using pedal radios and bush planes to cast a 'mantle of safety' over the furthest outback stations and communities.", "match": ["Royal Flying Doctor Service", "RFDS"]},
        {"id": "forgotten_people", "term": "The Forgotten People", "definition": "Robert Menzies' 1942 radio address defining the salaried middle class, small shopkeepers, and suburban home-builders not rich enough to be idle nor unionised in mass industry.", "match": ["Forgotten People"]},
        {"id": "pogg", "term": "Peace, Order, and Good Government", "definition": "The founding phrase in Section 51 of the Australian Constitution—contrasting with America's 'Life, Liberty and the Pursuit of Happiness' by prizing collective stability, fairness, and functional public order.", "match": ["Peace, Order, and Good Government"]},
        {"id": "psochic_hegemony", "term": "Psochic Hegemony (υ, ψ)", "definition": "The two-axis moral/will coordinate map: υ (Morality, horizontal) measures WHO benefits (+υ = everyone / greater good, -υ = self/ingroup extraction); ψ (Will, vertical) measures WHAT the energy does (+ψ = active creation/reform, -ψ = passive suppression or entropy).", "match": ["Psochic Hegemony", "Hegemony Coordinate"]},
    ]

    # 6. Classic Australian Reading & Primary Sources for Results Screen
    books = [
        {
            "id": "lucky_country",
            "title": "The Lucky Country",
            "author": "Donald Horne",
            "year": "1964",
            "planes": [1, 4, 7],
            "desc": "The foundational diagnostic critique of modern Australia—praising the egalitarian decency of ordinary Australians while warning that second-rate elites were coasting on resource luck.",
        },
        {
            "id": "new_province",
            "title": "A New Province for Law and Order ( & The Harvester Judgement)",
            "author": "Justice H.B. Higgins",
            "year": "1907 / 1922",
            "planes": [2, 4, 5],
            "desc": "Higgins' account of how Australian industrial arbitration and the Living Wage replaced raw industrial warfare with the rule of the Fair Go.",
        },
        {
            "id": "biggest_estate",
            "title": "The Biggest Estate on Earth: How Aborigines Made Australia",
            "author": "Bill Gammage",
            "year": "2011",
            "planes": [3, 5, 6],
            "desc": "Reveals how First Nations people managed the entire Australian continent for 65,000 years through precise Fire-Stick Farming and ecological law.",
        },
        {
            "id": "while_billy_boils",
            "title": "While the Billy Boils",
            "author": "Henry Lawson",
            "year": "1896",
            "planes": [1, 3, 4],
            "desc": "The classic stories that forged the creed of bush Mateship, the stoic Battler, and dry solidarity against a harsh continent.",
        },
        {
            "id": "australian_legend",
            "title": "The Australian Legend",
            "author": "Russel Ward",
            "year": "1958",
            "planes": [1, 5, 6],
            "desc": "Traces how the convict, bushman, shearer, and gold digger created Australia's egalitarian, anti-authoritarian, and practical national ethos.",
        },
        {
            "id": "redfern_speech",
            "title": "The Redfern Park Speech & Uluru Statement from the Heart",
            "author": "Paul Keating (1992) & First Nations Constitutional Convention (2017)",
            "year": "1992 / 2017",
            "planes": [2, 6, 7],
            "desc": "The twin moral anchors of modern Australian truth-telling, naming the fracture of dispossession and charting the path to Voice, Treaty, and Reconciliation.",
        },
    ]

    payload = {
        "planes": planes_out,
        "senses": senses_out,
        "vectors": vectors_out,
        "archetypes": archetypes,
        "figures": figures,
        "glossary": glossary,
        "books": books,
        "blockerTags": [
            "Cost of Living / Priced Out",
            "Red Tape / Nanny State",
            "Corporate / Political Capture",
            "No Time / Burnout",
            "Tall Poppy / Social Pushback",
            "Tyranny of Distance / Isolation",
            "Pride / Stoic Silence",
            "Broken Trust / Burned Before",
        ],
    }

    with open(OUT_JS, "w", encoding="utf-8") as f:
        f.write("// Auto-generated Australian Kanon Survey Dataset (7 Planes, 49 Senses, 354 Vectors)\n")
        f.write("window.KANON_SURVEY_DATA = ")
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(
        f"Wrote {OUT_JS} -> Planes: {len(planes_out)}, Senses: {len(senses_out)}, Vectors: {len(vectors_out)}, Glossary: {len(glossary)}, Books: {len(books)}"
    )


if __name__ == "__main__":
    main()
