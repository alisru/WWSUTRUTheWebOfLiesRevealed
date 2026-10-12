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
        "pillar": "The Egalitarian",
        "domain": "Metaphysical",
        "tau": 3.0,
        "hue": "#B98B22",
        "blurb": "Character over rank, horizontal loyalty, skepticism toward pretension, and deep-time belonging",
        "qA": "What should we uphold? A person's worth in Australia should come from their character, resilience, and loyalty to the people beside them—never from wealth, title, or social rank.",
        "qB": "What would you actually do? In the heat of everyday life, I actually treat everyone on a level playing field and stand by my mates rather than pulling rank or looking down on others.",
        "qC": "What does your community circle believe and do? The people in my everyday circle believe we should treat everyone as equals and actually back one another without pretension.",
        "qD": "What does wider Australian society actually do? Across Australia today, our society and institutions actually practise genuine peer-to-peer equality rather than rewarding class hierarchy.",
        "tags": ["identity", "mateship", "egalitarianism", "belonging", "indigenous", "culture"],
    },
    {
        "n": 2,
        "id": "P2",
        "code": "What",
        "name": "Definition",
        "pillar": "The Constituent",
        "domain": "Possible",
        "tau": 14.0,
        "hue": "#D97706",
        "blurb": "The civic contract, accountable public utilities, democratic voice, and equal standing under law",
        "qA": "What should we uphold? Public institutions, laws, and political leaders should exist strictly as practical utilities to serve empowered citizens—never as masters ruling over passive subjects.",
        "qB": "What would you actually do? In practice, I actively exercise my democratic voice, hold authorities to a fair standard, and refuse to act like a passive subject.",
        "qC": "What does your community circle believe and do? People in my community expect government to serve ordinary citizens and actively push back against political arrogance.",
        "qD": "What does wider Australian society actually do? In reality today, Australian parliaments, courts, and agencies actually operate as fair, transparent servants of the public rather than serving insiders.",
        "tags": ["democracy", "fair-go", "law", "governance", "voting", "rights"],
    },
    {
        "n": 3,
        "id": "P3",
        "code": "Where",
        "name": "Land",
        "pillar": "The Steward",
        "domain": "Physical",
        "tau": 3.0,
        "hue": "#1F7A6B",
        "blurb": "Continental stewardship, climate adaptation, housing security, and shared public commons",
        "qA": "What should we uphold? Living on this continent should mean humble stewardship of its fragile land and water cycles, alongside secure shelter and open public commons for every resident.",
        "qB": "What would you actually do? In my own choices and daily habits, I actively care for my local environment, respect natural limits, and back fair access to housing and public space.",
        "qC": "What does your community circle believe and do? My local community values and practises genuine stewardship of land, water, and neighbourhood housing security.",
        "qD": "What does wider Australian society actually do? Across Australia, our policies and markets actually deliver secure housing, healthy rivers and bushland, and fair regional infrastructure rather than speculative extraction.",
        "tags": ["land", "housing", "environment", "bush", "coast", "infrastructure", "climate"],
    },
    {
        "n": 4,
        "id": "P4",
        "code": "Why",
        "name": "Drive",
        "pillar": "The Volunteer",
        "domain": "Lyrical",
        "tau": 1.5,
        "hue": "#0D9488",
        "blurb": "Reward for honest effort, volunteer solidarity in crisis, protected rest, and the good life",
        "qA": "What should we uphold? Every person who puts in an honest effort should receive a living wage, protected rest and family time, and the community backing to have a fair crack at the good life.",
        "qB": "What would you actually do? In practice, I pitch in when others need help, respect fair reciprocity, and protect a healthy balance between honest work and rest.",
        "qC": "What does your community circle believe and do? People around me genuinely volunteer, pitch in during hard times, and respect fair wages and downtime.",
        "qD": "What does wider Australian society actually do? In practice today, Australia's economy actually rewards honest work with a living wage and protected rest rather than burnout and extractive profiteering.",
        "tags": ["work", "wages", "rest", "volunteering", "sport", "lifestyle", "burnout"],
    },
    {
        "n": 5,
        "id": "P5",
        "code": "How",
        "name": "Method",
        "pillar": "The Improviser",
        "domain": "Logical",
        "tau": 5.0,
        "hue": "#2E5B8A",
        "blurb": "Practical ingenuity, plain-spoken honesty, independent umpires, and humane workplace rules",
        "qA": "What should we uphold? Problems in work and public life should be solved through plain-spoken honesty, practical ingenuity, and independent umpires—never spin, dodgy shortcuts, or robotic box-ticking.",
        "qB": "What would you actually do? When a problem hits, I actually use practical common sense, speak plainly, and play by fair rules rather than hiding behind spin or red tape.",
        "qC": "What does your community circle believe and do? In my workplace and local circle, people value practical competence, honest talk, and fair play over bureaucratic games.",
        "qD": "What does wider Australian society actually do? Across Australia today, our workplaces and institutions actually empower practical problem-solving and independent umpires rather than punitive bureaucracy.",
        "tags": ["method", "innovation", "workplace", "unions", "pub-test", "bureaucracy", "science"],
    },
    {
        "n": 6,
        "id": "P6",
        "code": "Cause",
        "name": "Foundation",
        "pillar": "The Reconciler",
        "domain": "Historical",
        "tau": 30.0,
        "hue": "#4F46E5",
        "blurb": "Honest historical reckoning, 65,000 years of continuity, bottom-up democracy, and hard-won rights",
        "qA": "What should we uphold? A mature Australia should face the whole truth of its past—honouring 65,000 years of First Nations continuity alongside convict survival, democratic struggle, and migrant contribution without whitewashing injustice.",
        "qB": "What would you actually do? In practice, I actively listen to and respect the full truth of Australian history and defend the hard-won rights inherited from past generations.",
        "qC": "What does your community circle believe and do? People in my circle believe we should face our full history honestly and actually treat Indigenous, settler, and migrant heritage with respect.",
        "qD": "What does wider Australian society actually do? Across Australia today, our civic culture, schools, and laws actually reckon honestly with our past and uphold our foundational democratic settlements.",
        "tags": ["history", "reconciliation", "indigenous", "eureka", "mabo", "heritage", "truth"],
    },
    {
        "n": 7,
        "id": "P7",
        "code": "Effect",
        "name": "Result",
        "pillar": "The Good Neighbour",
        "domain": "Emotive",
        "tau": 7.0,
        "hue": "#7C3AED",
        "blurb": "Universal care, shared national wealth, intergenerational fairness, and sovereign regional partnership",
        "qA": "What should we uphold? The Australian project should deliver a generous, sovereign commonwealth—universal healthcare, shared resource wealth, intergenerational fairness, and constructive partnership in our region.",
        "qB": "What would you actually do? In my own civic choices and voting, I actively back universal care, intergenerational fairness, and Australia acting as a good neighbour.",
        "qC": "What does your community circle believe and do? My circle believes Australia should share its wealth fairly across generations and actually looks out for neighbours in practice.",
        "qD": "What does wider Australian society actually do? All things considered, the Australia we live in today actually delivers universal care, shared commonwealth prosperity, and a fair deal for the next generation.",
        "tags": ["health", "medicare", "housing", "superannuation", "foreign-policy", "sovereignty", "future"],
    },
]

# Unified Essence Questions for all 49 Senses (1.1 through 7.7)
# Each question distils the functional intersection of Plane Q x Sense q without listing the 7 sub-vectors.
SENSE_QUESTIONS = {
    # PLANE 1: IDENTITY (WHO)
    "1.1": (
        "When pressure hits, true Australian character shows up as quiet grit, resourceful improvisation, humor against arrogance, and unconditional loyalty to the person beside you.",
        "The people in my daily circle genuinely back one another under pressure and judge people by their character rather than their status.",
        "Should we strengthen this ethos of unconditional mutual loyalty and humble grit (+1 to +5), or move away from it (-1 to -5)?",
        "How much is blocking authentic mutual loyalty and solidarity in your daily circle?",
    ),
    "1.2": (
        "The highest unwritten law of Australian social life is a level playing field: everyone gets a fair go, nobody is born better than anyone else, and self-important pretence should be punctured.",
        "The workplaces and communities I move in actually operate on a level playing field where nobody pulls rank or demands deference.",
        "Should we enforce a stricter level playing field and fair go (+1 to +5), or accept wider social hierarchy and class privilege (-1 to -5)?",
        "How much is blocking peer-to-peer equality and the fair go in your daily environment?",
    ),
    "1.3": (
        "Our identity is inseparable from the physical continent—its ancient bush, open coast, red interior, and suburbs—and requires respecting the land as a living home rather than an empty void.",
        "I am able to live with a strong, grounded connection to my local landscape and community without being isolated or priced out.",
        "Should we deepen our cultural connection and access to bush, coast, and Country (+1 to +5), or treat land purely as a commodity (-1 to -5)?",
        "How much is blocking your connection to land, coast, and local community place?",
    ),
    "1.4": (
        "Australians should back their own homegrown talent and have the courage to try bold things, free from the insecurity that something only matters if it is approved overseas.",
        "People around me have the confidence and support to back local ideas and take a fair crack without being held back by cultural inferiority or lazy complacency.",
        "Should we push harder to back homegrown capability and ambition (+1 to +5), or rely on overseas models and passive resource luck (-1 to -5)?",
        "How much is blocking Australians from backing homegrown capability and creative ambition?",
    ),
    "1.5": (
        "Power in Australia must always answer to plain-spoken common sense, collective workplace solidarity, and independent public inquiries that expose corruption.",
        "In practice, our institutions and workplaces respect plain-English common sense, protect workers who band together, and act on public inquiries.",
        "Should we strengthen grassroots accountability and collective voice (+1 to +5), or curtail them in favour of managerial authority (-1 to -5)?",
        "How much is blocking everyday accountability and fair workplace voice?",
    ),
    "1.6": (
        "Modern Australian identity is woven from three living streams—65,000 years of First Nations custodial law, the hard-won egalitarianism of settlers and convicts, and the energy of migrants from every corner of the world.",
        "In my community, people of Indigenous, settler, and migrant heritage are respected as equal co-authors of who we are.",
        "Should we actively weave our Indigenous, settler, and multicultural roots closer together (+1 to +5), or pull back into a narrower monoculture (-1 to -5)?",
        "How much is blocking honest unity across Australia's foundational cultural streams?",
    ),
    "1.7": (
        "At our best, our national character produces a country that looks after the sick and vulnerable at home while acting as a generous, independent bridge-builder in our region.",
        "I can see compassionate care at home and constructive, independent Australian leadership in the world operating in practice today.",
        "Should we expand universal care at home and independent regional bridge-building (+1 to +5), or retreat from them (-1 to -5)?",
        "How much is blocking Australia from living up to its compassionate and independent character?",
    ),

    # PLANE 2: DEFINITION (WHAT — CIVIC CONTRACT)
    "2.1": (
        "In a true commonwealth, the citizen is the sovereign partner and employer of the state—never a passive subject to be managed, patronised, or ruled over.",
        "When I interact with public servants, councils, or parliaments, I am treated as an empowered citizen rather than a compliance problem.",
        "Should we strengthen citizen sovereignty over public agencies (+1 to +5), or accept more top-down administrative authority (-1 to -5)?",
        "How much is blocking citizens from being respected as the true owners of government?",
    ),
    "2.2": (
        "Our constitutional order should guarantee peace, order, and good government through an independent judiciary and strict rules that prevent any leader from seizing unchecked power.",
        "Our constitutional checks and courts actually protect ordinary citizens from executive overreach and political stitch-ups.",
        "Should we reinforce constitutional checks and judicial independence (+1 to +5), or loosen them for executive convenience (-1 to -5)?",
        "How much is blocking fair, transparent constitutional governance in Australia?",
    ),
    "2.3": (
        "A fair federation requires sharing national revenue so that every state, regional town, and outer suburb enjoys the same baseline of hospitals, schools, and infrastructure as the wealthiest capital city.",
        "My region or suburb receives a genuinely fair share of national funding, hospitals, transport, and public services.",
        "Should we strengthen horizontal revenue-sharing for regions and outer suburbs (+1 to +5), or let wealthy postcodes pull further ahead (-1 to -5)?",
        "How much is blocking fair regional and postcode-to-postcode resource sharing?",
    ),
    "2.4": (
        "The founding promise of the Australian Commonwealth is a secular, practical society where working people can enjoy fair wages, free internal movement, and a peaceful life free from sectarian fanatics.",
        "Working households today can still rely on the Commonwealth promise of fair wages, civic peace, and a secure standard of living.",
        "Should we renew this founding social contract for working households (+1 to +5), or dismantle it in favour of raw market competition (-1 to -5)?",
        "How much is blocking working Australians from a secure, peaceful standard of living?",
    ),
    "2.5": (
        "Democratic legitimacy depends on clean, independent elections where every citizen votes on equal terms—not backroom factional warlords, donor lobbies, or party-room coups.",
        "Our electoral system and party politics actually deliver representatives and policies chosen by voters rather than factional insiders and donors.",
        "Should we clean up party machines and donor capture (+1 to +5), or leave political parties and donors to operate as they do now (-1 to -5)?",
        "How much is blocking genuine voter choice and clean democratic representation?",
    ),
    "2.6": (
        "Australian democracy was built from the ground up by ordinary people demanding representation and building public utilities to serve the common good rather than private monopolies.",
        "Essential services and public infrastructure today are run for the public good rather than privatised price-gouging.",
        "Should we restore public-interest ownership and democratic control over essential utilities (+1 to +5), or privatise more public assets (-1 to -5)?",
        "How much is blocking essential services and utilities from serving the public good?",
    ),
    "2.7": (
        "A mature civic order protects public safety and hears First Nations voices without suffocating everyday life in petty fines, over-policing, and nanny-state prohibitions.",
        "Our laws strike a healthy balance—keeping people safe and included without burying everyday freedom in petty rules and revenue-raising fines.",
        "Should we wind back petty nanny-state over-regulation while advancing genuine civic inclusion (+1 to +5), or increase paternalistic regulation (-1 to -5)?",
        "How much is blocking a mature, self-confident, and un-micromanaged civic life?",
    ),

    # PLANE 3: LAND (WHERE — CONTINENT & HOME)
    "3.1": (
        "The sheer scale and volatility of the Australian continent—its bushfires, droughts, and ancient spirit of place—demand humility and preparation rather than human arrogance.",
        "My community is well-prepared for bushfire, flood, and heat extremes and builds in harmony with the landscape's natural limits.",
        "Should we invest much more in climate resilience and landscape-aware planning (+1 to +5), or ignore environmental limits (-1 to -5)?",
        "How much is blocking proper adaptation to Australia's harsh landscape and climate?",
    ),
    "3.2": (
        "Land in Australia must be shared fairly for families to live and farm on, while respecting First Nations native title—never locked up by land-banking monopolies or oligarchs.",
        "Ordinary Australians can still secure a fair piece of land or a family home without being locked out by speculative property hoarding.",
        "Should we break up land banking and housing monopolies (+1 to +5), or protect speculative property hoarding (-1 to -5)?",
        "How much is blocking fair access to housing, land tenure, and Country?",
    ),
    "3.3": (
        "Australia's ancient soils, rivers, and unique native wildlife are irreplaceable treasures that must be protected from over-clearing, water theft, and ecological collapse.",
        "Our local rivers, soils, bushland, and native species are actively protected and healthy rather than degraded or drained.",
        "Should we enforce stronger protection for rivers, soils, and native wildlife (+1 to +5), or relax environmental protections for short-term extraction (-1 to -5)?",
        "How much is blocking the restoration and protection of Australia's rivers, soils, and native species?",
    ),
    "3.4": (
        "On the driest inhabited continent, water and abundant solar/wind energy are shared national lifelines that must be managed for long-term survival rather than private cartel profit.",
        "Water and clean energy are managed reliably and affordably for households and communities rather than hoarded or price-gouged.",
        "Should we manage water and clean renewable energy as public lifelines (+1 to +5), or leave them to private trading and fossil/energy cartels (-1 to -5)?",
        "How much is blocking fair water security and cheap, reliable clean power?",
    ),
    "3.5": (
        "Because distance is Australia's great physical challenge, reliable transport, telecommunications, postal, and emergency medical networks must reach every town and suburb regardless of postcode.",
        "My area has dependable public transport, roads, digital connectivity, and emergency medical access.",
        "Should we expand public transport, regional health, and digital lifelines across the continent (+1 to +5), or cut back regional and outer-suburban services (-1 to -5)?",
        "How much is blocking reliable transport, communications, and medical connectivity where you live?",
    ),
    "3.6": (
        "The mineral and energy wealth dug from beneath Australian soil belongs to all Australians and must fund lasting public prosperity without destroying sacred heritage or local environments.",
        "Resource wealth extracted in Australia actually flows into public schools, hospitals, and sovereign funds rather than vanishing offshore untaxed.",
        "Should we capture a much fairer public share of mineral and gas wealth (+1 to +5), or keep taxes and royalties low for multinational miners (-1 to -5)?",
        "How much is blocking Australians from capturing a fair sovereign dividend from our resource wealth?",
    ),
    "3.7": (
        "Every Australian town and suburb should offer the physical foundations of a good life: secure homes, green backyards or parks, free public beaches, and welcoming places for neighbours to gather.",
        "My suburb or town offers affordable housing, green public space, and walkable community life rather than isolating sprawl or locked-out enclaves.",
        "Should we redesign and fund our suburbs and towns for affordability and community life (+1 to +5), or leave urban development to speculative sprawl (-1 to -5)?",
        "How much is blocking a liveable, affordable suburban or regional home environment?",
    ),

    # PLANE 4: DRIVE (WHY — MOTIVATION & THE GOOD LIFE)
    "4.1": (
        "We should honour the everyday people who pitch in—the volunteer on the fireline, the carer, and the honest worker—while calling out those who extract wealth without contributing.",
        "In my workplace and community, people who pitch in and do the heavy lifting are genuinely supported rather than taken for granted or exploited.",
        "Should we do more to reward everyday contributors and volunteers over rent-seekers (+1 to +5), or reward passive wealth extraction (-1 to -5)?",
        "How much is blocking fair recognition and backing for volunteers and honest workers?",
    ),
    "4.2": (
        "The whole point of a productive economy is a decent human life: a pay packet that covers a family's needs, a secure home, a protected two-day weekend, annual holidays, and a dignified retirement.",
        "My household actually enjoys a pay packet with breathing room, a protected weekend, holiday rest, and confidence in retirement.",
        "Should we defend and restore the living wage, the weekend, and retirement security (+1 to +5), or let work demands and living costs erode them (-1 to -5)?",
        "How much is blocking your household from a secure pay packet, home, and protected rest?",
    ),
    "4.3": (
        "Healthy communities need accessible 'third places' outside work and home—local pubs, surf and sports clubs, community sheds, parks, and beaches—where people can recharge and belong without paying a fortune.",
        "I have welcoming, affordable local places where I can relax, play sport, and connect with neighbours.",
        "Should we protect and fund non-commercial community third places and local clubs (+1 to +5), or let them be priced out and commercialised (-1 to -5)?",
        "How much is blocking access to affordable community third places and recreational spaces?",
    ),
    "4.4": (
        "Healthy ambition means striving for excellence while staying grounded—avoiding both tall-poppy envy that tears achievers down and status-obsessed panic that turns neighbours into rivals.",
        "I feel free to pursue my goals and enjoy life at a humane pace without being driven by financial panic or cut down by resentment.",
        "Should we foster a healthier balance of ambitious drive and grounded humility (+1 to +5), or embrace cut-throat status competition (-1 to -5)?",
        "How much is blocking a confident, unhurried pursuit of the good life?",
    ),
    "4.5": (
        "Everyday Australian trust is built on small rituals of reciprocity—taking turns fairly, shouting your round, pitching in, and refusing to let predatory gambling or price-gouging strip-mine our communities.",
        "People around me still practice everyday generosity and fairness, and my community is protected from predatory pokies and betting apps.",
        "Should we curb predatory gambling and rebuild everyday civic reciprocity (+1 to +5), or leave gambling and extractive industries unchecked (-1 to -5)?",
        "How much is blocking everyday social reciprocity and protection from predatory gambling?",
    ),
    "4.6": (
        "The memory of past hardships—dispossession, convict chains, wartime sacrifice, and economic depressions—should make us determined never to let any neighbour fall into destitution.",
        "When people in my community hit hard times, our social safety net and community solidarity catch them with dignity rather than punishment.",
        "Should we build stronger, more compassionate safety nets against hard times (+1 to +5), or make welfare harsher and more punitive (-1 to -5)?",
        "How much is blocking compassionate protection for people hit by economic or personal crisis?",
    ),
    "4.7": (
        "When a nation's drive is healthy, the result is a confident, self-reliant citizenry and broad middle-class stability—not widespread exhaustion and political cynicism.",
        "Around me, I see genuine economic security and civic confidence rather than a hollowed-out middle class sliding into cynicism.",
        "Should we act decisively to rebuild broad middle-class security and civic trust (+1 to +5), or accept growing inequality and disillusionment (-1 to -5)?",
        "How much is blocking shared prosperity and civic confidence today?",
    ),

    # PLANE 5: METHOD (HOW — PRACTICAL MECHANICS)
    "5.1": (
        "Systems stay honest only when we empower practical problem-solvers—skilled tradespeople, scientists, frank public servants, union reps, independent umpires, and whistleblowers who call out wrongdoing.",
        "In my experience, independent umpires, scientists, and whistleblowers are protected and listened to rather than silenced or punished.",
        "Should we strengthen legal protections for whistleblowers, scientists, and independent umpires (+1 to +5), or give executives more power to silence them (-1 to -5)?",
        "How much is blocking honest umpires, whistleblowers, and practical experts from doing their job?",
    ),
    "5.2": (
        "Australia should be a country that invents, builds, and arbitrates fairly—investing in local science, practical engineering, and living-wage awards rather than offshoring our brains and undercutting workers.",
        "We actually invest in homegrown research, local manufacturing, and fair wage-setting rather than letting our best inventions and jobs go offshore.",
        "Should we boost local R&D, sovereign manufacturing, and fair wage arbitration (+1 to +5), or rely on imported technology and deregulated labour (-1 to -5)?",
        "How much is blocking Australian invention, local making, and fair wage setting?",
    ),
    "5.3": (
        "The everyday arenas of Australian democracy—the local public school, the Saturday polling booth, the courtroom, the workplace, and the volunteer surf club—must remain open and equal for every class.",
        "Our local public schools, courts, workplaces, and community clubs are well-resourced and bring people from all backgrounds together as equals.",
        "Should we reinvest in universal public schools, equal legal access, and civic spaces (+1 to +5), or let two-tier private segregation widen (-1 to -5)?",
        "How much is blocking equal quality across public schools, courts, and community institutions?",
    ),
    "5.4": (
        "Every workplace and public system must balance practical efficiency with human fairness—efficiency that crushes people's dignity is a failure, not a success.",
        "The systems I deal with at work and in public services are both practically competent and genuinely fair to the human beings inside them.",
        "Should we require workplaces and agencies to put human fairness alongside efficiency (+1 to +5), or prioritise ruthless cost-cutting (-1 to -5)?",
        "How much is blocking workplaces and public systems from being both competent and humane?",
    ),
    "5.5": (
        "Good work requires humane rhythms—proper rest breaks, predictable rosters, sick leave when needed, and doing the job properly rather than taking dangerous shortcuts or burying problems in another report.",
        "My work and daily schedule respect humane breaks and safety, and real problems get fixed instead of being buried in box-ticking reports.",
        "Should we enforce humane work rhythms and real quality standards (+1 to +5), or allow more gig-style insecurity and corner-cutting (-1 to -5)?",
        "How much is blocking humane work rosters, rest breaks, and honest quality standards?",
    ),
    "5.6": (
        "Solving continental challenges requires combining modern engineering and science with 65,000 years of First Nations ecological knowledge and relational care for Country.",
        "Our land, fire, and water management actively integrates Indigenous ecological methods alongside modern science.",
        "Should we scale up the integration of First Nations ecological methods and modern science (+1 to +5), or keep them separate (-1 to -5)?",
        "How much is blocking the synthesis of Indigenous ecological wisdom and modern governance?",
    ),
    "5.7": (
        "The bottom-line test of any government or corporate system is whether it delivers fair outcomes and working infrastructure in the real world—not automated robo-debt cruelty or bureaucratic maze-running.",
        "Government and workplace rules actually help people solve problems in my life rather than trapping them in automated bureaucratic cruelty.",
        "Should we strip out punitive bureaucracy and enforce human-centred service delivery (+1 to +5), or expand automated compliance enforcement (-1 to -5)?",
        "How much is blocking bureaucracy from serving people instead of punishing them?",
    ),

    # PLANE 6: FOUNDATION (CAUSE — HISTORY & DEEP TIME)
    "6.1": (
        "To understand Australia, we must acknowledge every figure at our foundation—the 65,000-year First Nations Elder, the chained convict, the free settler, the gold digger, and the migrant—while honestly naming colonial dispossession.",
        "Our national culture honours all of our founding peoples honestly without erasing Indigenous survival or whitewashing colonial land grabs.",
        "Should we champion an honest, inclusive account of all who shaped Australia (+1 to +5), or revert to a one-sided myth (-1 to -5)?",
        "How much is blocking an honest, unifying reckoning with Australia's founding figures?",
    ),
    "6.2": (
        "Australia's greatest legal achievements are the milestones that expanded justice—Federation by popular vote, the living wage, compulsory voting, and the overturning of Terra Nullius and White Australia.",
        "The legal guarantees of a living wage, equal voting power, and native title are actively upheld and carried forward today.",
        "Should we defend and complete these foundational legal settlements (+1 to +5), or wind them back (-1 to -5)?",
        "How much is blocking the full realization of wage justice, voting equality, and native title?",
    ),
    "6.3": (
        "Australia has a sacred geography of memory—from ancient Indigenous songlines and Uluru to sites of convict pain, Eureka rebellion, wartime sacrifice, and democratic self-government—that must be protected from desecration.",
        "Our sacred Indigenous Country and historic civic heritage sites are protected with dignity rather than blown up or commercialised.",
        "Should we strengthen legal protection for sacred Country and historic heritage (+1 to +5), or allow commercial development to override them (-1 to -5)?",
        "How much is blocking respect and protection for Australia's sacred and historic places?",
    ),
    "6.4": (
        "Australia's history has always been a contest between two drives: generous solidarity and redemption on one side, versus invasion paranoia and lazy reliance on resource luck on the other.",
        "Our national choices today are guided by courage, solidarity, and long-term vision rather than fear-mongering or complacent luck.",
        "Should we steer national policy toward courage and solidarity over fear and complacency (+1 to +5), or lean into border fear and resource complacency (-1 to -5)?",
        "How much is blocking Australia from overcoming fear-driven politics and resource complacency?",
    ),
    "6.5": (
        "Unlike nations forged in civil war, Australia built its best institutions through bush survival skills, organised labour, the secret ballot, industrial arbitration, and constitutional conventions.",
        "Big national disagreements today are still resolved through fair arbitration, democratic reform, and peaceful consensus rather than division.",
        "Should we revitalise fair arbitration and bottom-up democratic reform (+1 to +5), or let adversarial conflict and union-busting dominate (-1 to -5)?",
        "How much is blocking fair arbitration and constructive democratic reform today?",
    ),
    "6.6": (
        "Our history does not begin in 1788; it is anchored in Deep Time—ancient Gondwanan ecosystems, the Great Barrier Reef, and 65,000 years of Indigenous fire-stick farming across an arid continent.",
        "We actively apply the lessons of Deep Time—protecting the Reef, expanding cultural burning, and living within our arid continent's limits.",
        "Should we ground our national policies in Deep Time ecological stewardship (+1 to +5), or treat the environment as a short-term quarry (-1 to -5)?",
        "How much is blocking deep-time ecological care for the Reef and the continent?",
    ),
    "6.7": (
        "Our historical inheritance leaves us with both proud achievements—the welfare safety net and civic consensus—and urgent unfinished business in First Nations justice, treaty, and truth-telling.",
        "Australia is actively repairing its social safety net while making real, good-faith progress on the unfinished business of Indigenous reconciliation.",
        "Should we finish the unfinished business of reconciliation and welfare repair (+1 to +5), or abandon them (-1 to -5)?",
        "How much is blocking the repair of our welfare safety net and historical reconciliation?",
    ),

    # PLANE 7: RESULT (EFFECT — SHARED COMMONWEALTH & FUTURE)
    "7.1": (
        "A healthy Australia produces citizens who combine quiet civic decency, multicultural openness, and neighbourly care—rejecting the 'I've got mine' selfishness that turns housing and wealth into a zero-sum game.",
        "In my community, people across different backgrounds and generations still look out for one another rather than splintering into selfish competition.",
        "Should we foster generous, cohesive citizenship over 'I've got mine' individualism (+1 to +5), or encourage pure self-interest (-1 to -5)?",
        "How much is blocking social cohesion and neighbourly care in modern Australia?",
    ),
    "7.2": (
        "The tangible dividend of the Australian Commonwealth should be universal and rock-solid: bulk-billed Medicare, secure housing, accessible education, dignified superannuation, clean energy, and thriving biodiversity.",
        "I actually experience these core dividends in my life today—affordable housing, free healthcare at the point of need, accessible education, and retirement security.",
        "Should we guarantee and rebuild universal Medicare, housing, education, and Super (+1 to +5), or shift more costs onto individuals (-1 to -5)?",
        "How much is blocking these core pillars of Australian security from working for you?",
    ),
    "7.3": (
        "In the wider world, Australia should stand on its own two feet as an independent middle power, a respected Pacific family member, and a value-adding economy—not a passive quarry or uncritical client state.",
        "Australia today acts with genuine diplomatic independence, adds value to our resources onshore, and engages as a trusted equal in the Pacific and Asia.",
        "Should we build sovereign economic complexity and an independent foreign policy (+1 to +5), or remain a raw-materials quarry and compliant deputy (-1 to -5)?",
        "How much is blocking Australia from standing as an independent, value-adding nation in our region?",
    ),
    "7.4": (
        "When forced to choose between competing national directions, Australia must put the Fair Go over raw market rule, sustainability over extraction, regional equity alongside cities, and reconciliation over division.",
        "Current Australian economic and social policies are actually tilted toward the Fair Go, sustainability, regional balance, and unity.",
        "Should we rebalance national policy toward the Fair Go, sustainability, and unity (+1 to +5), or tilt further toward market extraction and division (-1 to -5)?",
        "How much is blocking Australia from choosing the Fair Go and sustainability over market extraction?",
    ),
    "7.5": (
        "A self-governing people needs trustworthy instruments of truth—an independent electoral commission, honest public broadcasting and diverse media, royal commissions with teeth, and transparent economic reporting.",
        "Our media landscape and public accountability bodies give citizens the unvarnished truth rather than billionaire propaganda and partisan spin.",
        "Should we break up media concentration and strengthen truth and integrity bodies (+1 to +5), or leave media monopolies and political spin unchecked (-1 to -5)?",
        "How much is blocking honest media reporting and institutional accountability in Australia?",
    ),
    "7.6": (
        "The ultimate duty of every generation of Australians is to hand on a better commonwealth to the next—completing the clean energy transition, restoring housing fairness, and achieving full constitutional maturity.",
        "Young Australians today are inheriting a fairer housing market, a safer climate, and a more sovereign, reconciled nation than the generation before.",
        "Should we take bold action for intergenerational fairness, clean energy, and constitutional maturity (+1 to +5), or protect incumbent wealth at the expense of the young (-1 to -5)?",
        "How much is blocking a fair deal and a proud future for the next generation of Australians?",
    ),
    "7.7": (
        "Stripped to its essence, the meaning of Australia is the Land of the Second Chance and the Fair Go—transforming a place of exile and dispossession into a reconciled, egalitarian home where nobody is left behind.",
        "All things considered, the Australia I live in today truly honours the Second Chance and the Fair Go for everyone who calls this continent home.",
        "Should we recommit whole-heartedly to the Australian promise of the Fair Go and the Second Chance (+1 to +5), or abandon it (-1 to -5)?",
        "How much is blocking Australia from fulfilling its highest promise as the Land of the Fair Go?",
    ),
}


def clean_html(raw):
    text = re.sub(r"<[^>]+>", "", raw)
    text = (
        text.replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&amp;", "&")
        .replace("&mdash;", "—")
        .replace("&ndash;", "–")
    )
    return re.sub(r"\s+", " ", text).strip()


def extract_role_and_meaning(establishes, name):
    m = re.search(r"This establishes [^.*]*\*\*([^*]+)\*\*\.\s*(.*)", establishes, re.S)
    if m:
        role = m.group(1).strip()
        rest = m.group(2).strip()
    else:
        m2 = re.search(r"\*\*([^*]+)\*\*", establishes)
        role = m2.group(1).strip() if m2 else name
        rest = establishes
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


def build_vector_questions(name, clean_name, role, core_meaning, v, psi, zone, is_fn, rationale):
    # Ensure core_meaning doesn't trail with awkward punctuation
    cm = core_meaning.rstrip(".")
    cm_low = cm[0].lower() + cm[1:] if len(cm) > 1 else cm
    if is_fn:
        if v < 0:
            # Shadow FN node like Dispossession or Exclusion or Guilt
            qA = f"What should we do? We should recognise the reality of {clean_name} ({role} — {cm_low}) and actively work to heal and overcome it."
            qB = f"What would you actually do? In practice, I actively call out and refuse to perpetuate {clean_name} in my own choices and speech."
            qC = f"What does your community circle believe and do? People in my everyday circle agree we should heal {clean_name} and actually treat First Nations people with fairness and respect."
            qD = f"What does wider Australian society actually do? Across Australia today, our society and institutions actually address and dismantle {clean_name} rather than denying or entrenching it."
        else:
            qA = f"What should we uphold? We should honour the First Nations principle of {clean_name} ({role}): {cm_low}."
            qB = f"What would you actually do? In my own daily life and decisions, I actively respect and practise {clean_name} rather than treating it as tokenism."
            qC = f"What does your community circle believe and do? My immediate circle believes we should respect {clean_name} and actually honours it in practice."
            qD = f"What does wider Australian society actually do? Across Australia today, our wider society and institutions actually uphold and integrate {clean_name} in practice."
        return qA, qB, qC, qD

    if v > 0:
        # Positive Kanon Vector (Greater Good, Good, Lesser Good, Tension Point with +v)
        qA = f"What should we uphold? We should champion and uphold {clean_name} ({role}): {cm_low}."
        qB = f"What would you actually do? In the heat of everyday life, I actually practise and stand up for {clean_name} through my own actions."
        qC = f"What does your community circle believe and do? The people in my everyday circle believe we should uphold {clean_name} and actually live it out."
        qD = f"What does wider Australian society actually do? Across Australia today, our society and institutions actually deliver and protect {clean_name} in practice."
    elif v < 0:
        # Negative / Shadow Kanon Vector (Greatest Lie, Greater Evil, Lesser Evil)
        qA = f"What should we do? We should see through the distortion of {clean_name} ({role} — {rationale.rstrip('.')}) and reject its extractive or divisive grip."
        qB = f"What would you actually do? In the heat of the moment, I actually refuse to go along with {clean_name} even when it is convenient."
        qC = f"What does your community circle believe and do? People in my everyday circle see through {clean_name} and refuse to practice or excuse it."
        qD = f"What does wider Australian society actually do? Across Australia today, our wider society and institutions actually resist and dismantle {clean_name} rather than being captured by it."
    else:
        # Neutral / Constraint / Tension Axis (v == 0)
        if "Tension" in zone or "vs." in clean_name:
            qA = f"What should we do? We should balance the tension of {clean_name} ({role}) in favour of the common good: {cm_low}."
            qB = f"What would you actually do? In my own daily choices, I actually act to balance {clean_name} fairly for everyone."
            qC = f"What does your community circle believe and do? People in my local circle believe in and practise a fair, practical balance on {clean_name}."
            qD = f"What does wider Australian society actually do? Across Australia today, our society and economy actually strike a fair, constructive balance on {clean_name}."
        else:
            qA = f"What should we do? We should respect and prepare for the continental reality of {clean_name} ({role}): {cm_low}."
            qB = f"What would you actually do? In practice, I actually adapt my habits and preparation to respect {clean_name}."
            qC = f"What does your community circle believe and do? My local community takes {clean_name} seriously and prepares practically for it."
            qD = f"What does wider Australian society actually do? Across Australia today, our infrastructure, planning, and institutions actually adapt to and endure {clean_name}."

    return qA, qB, qC, qD


def format_sense_should_would(sense_tuple, sense_title):
    raw_a, raw_b, raw_c, raw_d = sense_tuple
    # Clean raw_d topic tail ("How much is blocking X?" -> "X")
    topic_tail = re.sub(r"^How much is blocking\s+", "", raw_d).rstrip("?")
    qA = f"What should we uphold? {raw_a}"
    qB = f"What would you actually do? In the heat of everyday life, I personally stand by and practise this standard rather than taking the easy or selfish way out."
    qC = f"What does your community circle believe and do? {raw_b}"
    qD = f"What does wider Australian society actually do? Across Australia today, our society and institutions actually deliver {topic_tail} in practice."
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

            s_vecs = by_sense[s_code]
            s_u = round(sum(x["coordinates"]["v"] for x in s_vecs) / max(1, len(s_vecs)), 2)
            s_psi = round(sum(x["coordinates"]["psi"] for x in s_vecs) / max(1, len(s_vecs)), 2)
            p_u_vals.extend(x["coordinates"]["v"] for x in s_vecs)
            p_psi_vals.extend(x["coordinates"]["psi"] for x in s_vecs)

            qA, qB, qC, qD = format_sense_should_would(SENSE_QUESTIONS[sense_id], raw_title)

            # Collect sense tags from constituent vectors
            sense_tags = []
            vec_uids = []

            for v_pos, v_item in enumerate(s_vecs, 1):
                addr = v_item["address"]
                raw_name = v_item["name"]
                is_fn = "[First Nations Perspective]" in raw_name
                clean_nm = raw_name.replace("[First Nations Perspective]", "").strip()
                uid = f"{sense_id}.{v_pos}"

                role, core_meaning = extract_role_and_meaning(v_item.get("establishes", ""), clean_nm)
                v_coord = v_item["coordinates"]["v"]
                psi_coord = v_item["coordinates"]["psi"]
                zone = v_item.get("zone", "Good")
                rationale = v_item.get("judgment_rationale", "")

                vqA, vqB, vqC, vqD = build_vector_questions(
                    raw_name, clean_nm, role, core_meaning, v_coord, psi_coord, zone, is_fn, rationale
                )

                # Match Hanson verdict
                hv = hanson_verdicts.get((addr, raw_name))
                if not hv:
                    # Try matching without [First Nations Perspective] or partial
                    for (ha, hn), hval in hanson_verdicts.items():
                        if ha == addr and (clean_nm.lower() in hn.lower() or hn.lower() in clean_nm.lower()):
                            hv = hval
                            break
                in_hanson_353 = hv is not None

                # Match Albo verdict
                av = albo_verdicts.get((addr, raw_name))
                if not av:
                    for (aa, an), aval in albo_verdicts.items():
                        if aa == addr and (clean_nm.lower() in an.lower() or an.lower() in clean_nm.lower()):
                            av = aval
                            break

                v_tags = infer_tags(clean_nm, v_item.get("description", ""), v_item.get("establishes", ""), pnum)
                for tg in v_tags:
                    if tg not in sense_tags:
                        sense_tags.append(tg)

                est_clean = clean_html(v_item.get("establishes", ""))
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
                        "note": f"Kanon Role — The {role} (υ = {v_coord:+g}, ψ = {psi_coord:+g} · {zone}): {est_clean}",
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
                    "quote": v_item.get("canonical_quote", ""),
                    "attribution": v_item.get("attribution", ""),
                    "source": v_item.get("source", ""),
                    "description": v_item.get("description", ""),
                    "establishes": est_clean,
                    "coreMeaning": core_meaning,
                    "coords": {"v": v_coord, "psi": psi_coord},
                    "zone": zone,
                    "rationale": rationale,
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
                vec_uids.append(uid)

            v_names_list = [x["name"].replace("[First Nations Perspective]", "[FN]").strip() for x in s_vecs]
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
            "note": f"Plane {pnum} ({pmeta['code']} · {pmeta['domain']} Domain · Decay constant τ = {pmeta['tau']} days): {pmeta['totality']}",
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
        {"id": "tau_constant", "term": "τ (Decay Constant)", "definition": "The number of days a Plane can be neglected or starved before acute systemic breakdown sets in (e.g., τ = 3 days for Physical Land/Shelter and Identity).", "match": ["τ = 3d", "τ = 14d", "τ = 2d", "τ = 90d", "τ = 7d", "τ = 365d", "τ = 30d"]},
    ]

    # Also auto-register any Kanon vector cleanName >= 5 chars not already matched
    existing_matches = {m.lower() for g in glossary for m in g["match"]}
    for v in vectors_out:
        cn = v["cleanName"]
        if len(cn) >= 5 and cn.lower() not in existing_matches:
            existing_matches.add(cn.lower())
            glossary.append({
                "id": f"vec_{v['uid']}",
                "term": f"{cn} ({v['role']})",
                "definition": f"{v['coreMeaning']} [{v['addr']} · υ={v['coords']['v']:+g}, ψ={v['coords']['psi']:+g}]",
                "match": [cn],
            })

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
