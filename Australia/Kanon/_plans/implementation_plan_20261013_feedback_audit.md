# Australian Kanon Survey — Post-Agent Feedback Audit & Implementation Plan (2026-10-13)

## 1. Complete Audit of Feedback Not Yet Taken Into Account

Below is the exhaustive inventory of every item raised by the 3 User Persona Testers (`Suburban Parent`, `Regional Tradie`, `Young Renter`) and the User that was **missed, only partially implemented, or left with VFT jargon**:

### A. Scale & Button Labels (`-5` to `+5`) — "Extractive", "Greater Good", etc. Feel Weird & Overloaded
* **What was complained about (User + Persona 1 + Persona 2):**
  1. **User:** *"‘extractive’ ‘greater good’, etc for the answers is weird"*
  2. **Persona 1 (Suburban Parent):**
     - *"Endpoint labels (`Extractive / Suppress` at `-5` and `Greater Good` at `+5`) don't always match the grammar of the question... The `-5`, `0`, and `+5` labels on `SCALE_A`, `SCALE_B`, `SCALE_C`, and `SCALE_D` force VFT axis jargon (`Extractive / Suppress`, `Selfish / Inaction`, `Greater Good`) onto buttons where simple behavioural/agreement anchors would be 10x faster to read."*
     - Recommended natural plain-English labels tailored to each row (`A` Should, `B` Would, `C` Circle, `D` Society).
  3. **Persona 2 (Regional Tradie):**
     - *"11 Buttons Per Row × 4 Rows = 44 Buttons Per Card... Nobody at the pub can tell the difference between `+3 Should Uphold`, `+4 Proactive Build`, and `+5 Greater Good`, or between `-3 Should Not Do` and `-4 Reject / Prevent`. Having 11 labelled buttons per row creates massive visual clutter and choice paralysis."*
     - *"Keep the `-5` to `+5` numbers (so the math and Keyring Plot stay 100% intact), but only put text labels on the 3 or 5 anchor points (`-5`, `-3`, `0`, `+3`, `+5`) instead of all 11 buttons, OR group the bar visually with clear endpoint headers above the buttons."*
* **What we missed:** We kept `Extractive / Suppress`, `Proactive Build`, `Greater Good`, `Extractive / Harm`, etc. on the buttons (`SCALE_A`–`SCALE_D`) and left micro-labels on all 11 buttons per row!

---

### B. Tier 3 Individual Vector Prompts (354 Nodes) — Robotic "Noun-Stuffed" Mad-Libs & Weird Phrasing
* **What was complained about (Persona 2 + Persona 3):**
  1. **Persona 2 (Regional Tradie):**
     - *"Tier 3 Vector Prompts Are Robotic 'Noun-Stuffed' Mad-Libs: In Tier 3, almost every positive/lesser-good vector just stuffs `v.cleanName` into a generic sentence: `In the heat of everyday life, I actually practise and stand up for The Drought / The Flood / The Marsupial / Gondwana / The Sprawl`... Mate, how do I 'practise and stand up for The Drought'? Turn all my taps on and pray for no rain? Tell someone in Lismore that Australian institutions should 'deliver and protect The Flood'!"*
     - *"`3.6.7 The Wealth` (`v = +0.3, ψ = -0.4`): `qA`: 'We should champion and uphold The Wealth (Result): the immense geological wealth leads to a philosophical poverty... It creates a complacency in the national soul.' Why on earth is `qA` asking me to champion and uphold philosophical poverty and national complacency?!"*
     - *"`3.6.6 The Impact` (ancient asteroid craters): 'In practice, I actually adapt my habits and preparation to respect The Impact. My local community takes The Impact seriously and prepares practically for it.' (Are we prepping for a meteor strike in Dubbo?)"*
     - **Shadow Vector `qA` math leaks:** *"Every Shadow `qA` dumps internal VFT coordinate shorthand straight into the question sentence: `3.2.1: ...see through the distortion of The Squatter (Claim — Land seizure (+ψ) for private wealth (-υ). Bunyip aristocracy)`... Strip raw `(+ψ)` and `(-υ)` math codes out of `qA` sentences."*
  2. **Persona 3 (Young Renter):**
     - *"Double Role / `this establishes` Clunkiness in `qA`: `We should champion and uphold The Whistleblower (The Whistleblower): this establishes The Whistleblower as the Safety Valve...`"*
     - *"Historical Noun / Artifact Vectors in `qB`/`qC`/`qD`: Asking 'In the heat of everyday life, I actually practise and stand up for The Stump Jump Plough / The Wifi / The Boomerang / The Home Owner through my own actions' doesn't parse naturally."*
     - *"`A vs. B` Tension Vectors in Sense `7.4` (`7.4.1`–`7.4.7`): `7.4.2 (Sustainability vs. Extraction)` and `7.4.5 (Reconciliation vs. Denial)` ask 'We should champion and uphold Sustainability vs. Extraction'. If I rate `+5`, am I voting for Sustainability, Extraction, or the debate?"*
* **What we missed:** While we rewrote the 49 Senses (`SENSE_QUESTIONS`), we left the Tier 3 vector generator (`build_vector_questions` in `build_kanon_survey_data.py`) using the raw noun-stuffing template!

---

### C. Sense Titles, Plane Subtitles, and Duplicated / Mad-Libbed Card Boxes
* **What was complained about (Persona 1 + Persona 3):**
  1. **Cryptic Sense Titles (`The Who of the Who`):**
     - Persona 1: *"‘The Who of the Who’, ‘The What of the Who’, ‘The Where of the What’ sound like a riddle or an inside joke from a philosophy PhD seminar... Demote Matrix Coordinates in Sense Titles so a human-readable title leads (e.g. `1.1 · Australian Character & Mateship` with `Who.Who · Authenticity & Soul` as the small subtitle)."*
  2. **Awkward Plane Subtitle (`Values of Australian Definition`):**
     - Persona 1: *"‘Values of Australian Definition’ as a heading sounds weird to a normal Aussie (nobody says ‘Australian Definition’ at a BBQ—we'd say ‘Democracy, Law & Civic Voice’)."*
  3. **Duplicated `totality` paragraph inside `.7` Sense Narratives (`1.7`, `2.7`, `5.7`):**
     - Persona 1: *"Both `1.7` (`Who.Effect`) and `2.7` (`What.Effect`) append the entire Plane `totality` paragraph onto the end of their `narrative` field, which the user already read at the top of the page."*
  4. **Confusing Mad-Libbed Green/Red (`+1..+5 GREATER GOOD` / `−1..−5 EXTRACTIVE`) Boxes Inside Every Tier 2 Sense Card:**
     - Persona 1: *"Every single Sense card in Tier 2 has a green and red box above the questions that says: 'You strongly endorse the Australian ethos of Who.What (The What of the Who (Roles/Titles)), spanning The Fair Go, Tall Poppy Syndrome...' Because it lists negative things like 'Tall Poppy Syndrome' or 'The Faceless Men' (`2.5`) as things you 'strongly endorse', it actually confuses you right before you answer! Remove the redundant green/red boxes inside each Tier 2 Sense card."*
  5. **Repeated 3-Card Tier Selector Grid on Every `#/plane/*` Page:**
     - Persona 1 & Persona 3: *"When you click `Start at Plane 1` or `Next: Plane 6`, `renderPlane` renders the 3 huge Tier Selector cards at the very top of the page again, even though the tier switcher is already in the sticky header! Removing the Tier Selector Grid from `#/plane/*` saves ~220px of vertical scrolling immediately."*
  6. **Redundant Question Prefixes & Always-Expanded Blocker Chips:**
     - Persona 1: *"Put the question in the `probe-kind` pill (`A · PERSONAL SHOULD — WHAT WE SHOULD UPHOLD`, `B · PERSONAL WOULD — WHAT I ACTUALLY DO`, `C · COMMUNITY CIRCLE — WHAT MY CIRCLE DOES`, `D · AUSTRALIAN SOCIETY — WHAT AUSTRALIA DELIVERS`) so every prompt isn't cluttered, and make the 8 Blocker chips compact or collapsible until `D <= 1` (or clicked)."*
  7. **Glossary Tooltip Definitions Still Have `[Who.Where.Effect · υ=+0.2, ψ=-0.2]` & "This establishes...":**
     - Persona 1: *"Rewrite the remaining glossary tooltip definitions into plain-English historical context without `This establishes X as the Y... [Who.Where.Effect · υ=+0.2, ψ=-0.2]` suffix codes."*

---

### D. Results Page & PNG Export Remaining Items
* **What was complained about (Persona 3):**
  1. **Keyring Left Teeth vs Right Teeth Explanation:**
     - Persona 3: *"Explain clearly why there are 3 ticks on the right (`B: You · C: Circle · D: Society`) vs `Should (A)` on the left."*
  2. **Hegemony Canvas Inverted X-Axis Explanation (`+υ` on Left, `-υ` on Right):**
     - Persona 3: *"In the questionnaire, `-5` is on the LEFT and `+5` is on the RIGHT, whereas on the Hegemony canvas `+υ` (Greater Good) is on the LEFT and `-υ` (Self/Extractive) is on the RIGHT! Add a clear 1-line note right below the canvas header explaining the Kanon map convention so users don't feel spatially disoriented."*
  3. **Shareable PNG Visual Polish:**
     - Persona 3: *"Include `arch.desc` (wrapped) and a mini `(υ, ψ)` quadrant plot or 7-point star badge on the exported PNG card so it pops when shared in group chats."*

---

## 2. Step-by-Step Action Plan to Implement All Missed Feedback

### Phase 1: Replace Weird VFT Button Labels (`Extractive`, `Greater Good`, `Proactive Build`) with Natural Plain-English Scales & Declutter the 11 Buttons (`Kanon_Survey.html`)
1. **Redesign `SCALE_A`, `SCALE_B`, `SCALE_C`, `SCALE_D` (and Shadow scales) with Natural Plain-English Labels:**
   - **Row A (`Personal · Should` — What we should uphold):**
     - `-5`: `Strongly Oppose` | `-4`: `Oppose` | `-3`: `Should Not` | `-2`: `Lean Against` | `-1`: `Slight Against` | `0`: `Neutral / Unsure` | `+1`: `Slight Support` | `+2`: `Lean Support` | `+3`: `Should Uphold` | `+4`: `Strongly Support` | `+5`: `Core Principle`
   - **Row B (`Personal · Would` — What I actually do in practice):**
     - `-5`: `Do the Opposite` | `-4`: `Rarely Do` | `-3`: `Often Fall Short` | `-2`: `Give In to Pressure` | `-1`: `Sometimes Slip` | `0`: `50/50 / Passive` | `+1`: `Try When Easy` | `+2`: `Usually Do` | `+3`: `Practise Mostly` | `+4`: `Stand By It` | `+5`: `Always Live It`
   - **Row C (`Community · Circle` — What people around me do):**
     - `-5`: `Dead Against It` | `-4`: `Rejects It` | `-3`: `Mostly Ignores` | `-2`: `Talk Only` | `-1`: `Fading Fast` | `0`: `Mixed / Split` | `+1`: `Some Try` | `+2`: `Generally Backs` | `+3`: `Practises Mostly` | `+4`: `Strong Culture` | `+5`: `Lives It Fully`
   - **Row D (`Society · Australia` — What Australia & institutions actually deliver):**
     - `-5`: `Rigged / Broken` | `-4`: `Failing Badly` | `-3`: `Fails in Practice` | `-2`: `Lip Service Only` | `-1`: `Slipping Backward` | `0`: `Mixed / Patchy` | `+1`: `Muddlings Through` | `+2`: `Partial Delivery` | `+3`: `Works Mostly` | `+4`: `Works Well` | `+5`: `World-Class / Fair`
   - **Shadow / Flaw Scales (`SCALE_*_SHADOW`):**
     - `-5`: `Fully Endorse Flaw` / `Trapped in Flaw` .. `0`: `Neutral / Unsure` .. `+5`: `Totally Reject Flaw` / `Overcome Flaw`.
2. **Declutter the 11-Button Row for Instant Scanning (Persona 2 Fix):**
   - Only display sub-labels on the **5 key anchor buttons** (`-5`, `-3`, `0`, `+3`, `+5`) inside `.seg-btn` (keeping full hover tooltips on all 11 buttons), and make those 5 labels slightly larger and crisper (`0.64rem`) so the user can scan and click in half a second without reading 44 cramped micro-labels per card.

### Phase 2: Overhaul Tier 3 Vector Prompts, Sense Titles, Duplicated Narratives & Glossary in `build_kanon_survey_data.py`
1. **Human-First Sense Titles & Natural Plane Subtitles:**
   - Give every Sense (`1.1`–`7.7`) a clear, plain-English Australian title (e.g., `1.1 · Mateship, grit & the Outback spirit`, `2.2 · Constitutional checks & fair representation`, `3.2 · Fair land access, housing & Native Title`, `4.2 · The Fair Go, living wages & the Weekend`, `7.2 · Home ownership, Medicare & Superannuation`) while keeping `Who.Who (Authenticity)` as the compact badge.
   - Update awkward Plane `fullTitle` values (e.g. Plane 2: `Democracy, Law & the Civic Contract`; Plane 5: `Pragmatic Ingenuity, Plain Speaking & Fair Rules`; Plane 6: `Deep Time, Convict Roots & Federation`; Plane 7: `Shared Prosperity, Sovereignty & Reconciliation`).
2. **Fix Duplicated `totality` Text in `.7` Senses (`1.7`, `2.7`, `5.7`):**
   - Strip the appended `The Totality of Australian ...` paragraph from Sense `.7` narratives in `build_kanon_survey_data.py`.
3. **Rewrite Tier 3 Vector Question Generator (`build_vector_questions`) So Every Vector Passes the Pub Test:**
   - Strip raw VFT coordinate math `(+ψ)`, `(-υ)` from `rationale` and `coreMeaning` before generating text.
   - Fix duplicate role names like `The Whistleblower (The Whistleblower)` when `role.lower() in clean_name.lower()`.
   - Handle **5 distinct vector categories** cleanly instead of blind noun-stuffing:
     1. **Shadow / Flaw Vectors (`v < 0`, e.g., `The Bludger`, `The Squatter`, `Terra Nullius`, `The Opencut`):** Frame around calling out, rejecting, and reforming the flaw (with zero `(+ψ)`/`(-υ)` jargon).
     2. **Cautionary / Complacency Vectors (`3.6.7 The Wealth`, `3.7.2 The Sprawl`, `1.2.4 'She'll be right'`):** Frame around the Kanon lesson (e.g., turning resource wealth into real capability rather than complacency; balancing suburban comfort with community connection).
     3. **Continental Forces, Disasters & Deep-Time Facts (`The Drought`, `The Flood`, `The Red Steer`, `The Sun`, `The Marsupial`, `Gondwana`, `The Impact`, `Megafauna Extinction`):** Never ask *"Do you stand up for and protect The Flood / The Drought / The Impact?"* Instead, ask about **respecting Australia's continental reality, adapting our towns/water/fire preparation, and pitching in together when natural extremes hit**.
     4. **"A vs. B" Tension Vectors (`7.4.1`–`7.4.7`, e.g., `Sustainability vs. Extraction`, `Reconciliation vs. Denial`, `Republic vs. Monarchy`):** Frame explicitly around resolving the national tension toward the constructive Kanon pole (e.g., choosing long-term sustainability over short-term extraction; honest reconciliation over historical denial).
     5. **Positive / Constructive Kanon Principles & Institutions (`Mateship`, `The Fair Go`, `Medicare`, `The Whistleblower`, `The Stump Jump Plough`):** Frame around upholding the underlying Australian principle (`establishes` / `coreMeaning` cleaned into natural English) in personal life (`B`), local community (`C`), and national institutions (`D`).
4. **Clean Up Glossary Tooltip Definitions:**
   - Remove `This establishes X as the Y.` and `[Who.Where.Effect · υ=..., ψ=...]` from all 52 glossary definitions so hovering a dotted term gives a clean, natural plain-English explanation.

### Phase 3: Clean Up Questionnaire Visual Density & Results Page Explanations (`Kanon_Survey.html`)
1. **Remove Repeated 3-Card Tier Selector from `#/plane/*` Pages:**
   - Keep the 3-card Tier Selector on `#/hub` and use the compact header switcher (`Tier 2: 49 Senses ▾`) on `#/plane/*` pages, saving ~220px at the top of every Plane.
2. **Remove Confusing Mad-Libbed Green/Red Boxes Inside Tier 2 Sense Cards:**
   - Remove the redundant `+1..+5 GREATER GOOD` / `−1..−5 EXTRACTIVE` boxes from `.node-lore` on Tier 2 cards so each card shows only the clean Sense Narrative + Vector badges above the 4 ABCD rows.
3. **Clearer Row Headers & Collapsible Blocker Chips:**
   - Make the 4 row pills self-explanatory:
     - `A · PERSONAL SHOULD (What we should uphold)`
     - `B · PERSONAL WOULD (What I actually do)`
     - `C · COMMUNITY CIRCLE (What people around me do)`
     - `D · AUSTRALIAN SOCIETY (What Australia actually delivers)`
   - Auto-show the Blocker chips when `D <= 1` or when blockers are already selected, or via a compact `+ Tag what's blocking this` toggle button when `D > 1` or unanswered.
4. **Results Page (`#/results`) & Shareable PNG Upgrades:**
   - Add a 1-line orientation callout under the Psochic Hegemony canvas header explaining why `+υ (Greater Good / All)` is on the Left and `−υ (Self-Only / Extractive)` is on the Right.
   - Clarify the Keyring tutorial text regarding the 1 Left (`Should A`) vs 3 Right (`Would: B You, C Circle, D Society`) teeth in Tiers 1–2.
   - Upgrade `downloadShareCardPNG()` to include wrapped `arch.desc` text and a mini `(υ, ψ)` 4-quadrant visual badge so the exported PNG looks like a complete 12Axes shareable card.
