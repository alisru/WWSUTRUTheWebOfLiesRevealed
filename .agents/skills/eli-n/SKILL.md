---
name: eli-n
description: >-
  Use this skill when you need to write or translate complex academic, technical,
  or economic text into multi-tiered reading levels (ELI5, ELI18, and Core Points),
  ensuring all core scientific and empirical anchor points are preserved and explained.
---

# Writing Multi-Tiered Reading Level Explanations (ELI-N)

This skill provides a systematic runbook for translating rigorous academic, economic, or physics-based analyses into multiple reading levels: **ELI5**, **ELI18**, **Expert**, and **Core Points (Highlights)**. 

The primary challenge is translating the narrative complexity while adhering to the **"No Point Loss"** rule—ensuring that simplified levels do not omit mathematical variables, datasets, models, or empirical statistics, but instead explain them in context.

---

## The Four Reading Levels

### 1. ELI5 (Explain Like I'm 5)
* **Goal**: Maximize readability using everyday analogies, simple metaphors (e.g., water pipes, fridges, engines, board games), and elementary vocabulary.
* **Anchor Handling**: Do not omit technical terms or variables (e.g., MPC, SFC, Kalecki profit identity, NDIS, EBIT margins). Instead, introduce them conversational-style, explain what they mean in simple terms, and weave them directly into the analogy.
* **Formatting**: 
  * Do **NOT** use italicized text wrappers (e.g., *this is an ELI5 text*). Keep it normal text.
  * Do **NOT** add introductory prefixes like `"ELI5 explanation:"` or `"Simplified:"`.
  * Keep sentences short and clear.

### 2. ELI18 (Explain Like I'm 18)
* **Goal**: Clear, undergraduate-level explanation.
* **Anchor Handling**: Use standard academic terms (e.g., Marginal Propensity to Consume, Stock-Flow Consistent models, New Keynesian policies) but define and contextualize them simply as they are introduced.
* **Formatting**: 
  * Do **NOT** use introductory prefixes.
  * Keep the tone analytical but highly readable.

### 3. Expert Mode
* **Goal**: Untangled, clear, authoritative academic prose.
* **Guidelines**: Refer to the [`untangle-academic-prose`](file:///e:/china%20russia/git/WWSUTRUTheWebOfLiesRevealed/.agents/skills/untangle-academic-prose/SKILL.md) skill to simplify syntax without losing expert rigor.

### 4. Core Points / Highlights
* **Goal**: Provide a structured, high-impact bulleted summary of the exact key academic, mathematical, and empirical anchors of the section.
* **Content**: List the exact models, datasets, physical variables (e.g., \(Def\), \(S_w\), \(P\), \(\rho\), \(\vec{J}\)), and empirical statistics.

---

## Best Practices and Rules

### 1. The "No Point Loss" Rule
Never simplify a paragraph by dropping its underlying data or scientific framework. 
* If the Expert text mentions a dataset (e.g., *HILDA Survey*) and specific statistics (e.g., *MPC of 0.04 to 0.06 vs. 1.0*), the ELI5 and ELI18 versions **must** include those specific numbers and the survey name, explaining them in simple terms.
* E.g. in ELI5: *"Studies like the HILDA Survey show that poor families have an MPC (fancy name for spending rate) close to 1.0 (they spend all of it), while rich families save almost all of it (MPC of 0.04 to 0.06)."*

### 2. Consistent Mathematical Relationships
Ensure that accounting and logical relationships are preserved accurately across all levels. For example, in Stock-Flow Consistent models, the government deficit ($Def$) directly creates the private sector surplus. Keep this double-entry consistency clear even in ELI5 (e.g., *"the government's deficit is, to the penny, the private sector's savings"*).

### 3. Structural Alignment
Always keep matching level paragraphs inside their respective HTML toggles (`content-eli5`, `content-eli18`, `content-expert`, `content-core`) to allow clean paragraph-by-paragraph switching without layout displacement.

---

## Examples

### Example 1: Section 1 (Synthesis)
* **Expert**:
  > *"We propose a structural reframe: the welfare apparatus functions as an active, high-velocity 'indirect moral micro-subsidy' directed toward the corporate sector. The state injects fiat currency at the base of the economy, utilizing the citizen as a biological conduit. Because biological survival requires food, shelter, and care, this liquidity is immediately captured by private monopolies."*
* **ELI18**:
  > *"Rather than being a passive debt burden, the welfare state is a high-velocity indirect subsidy for businesses. By analyzing cash movements using Stock-Flow Consistent (SFC) models and the physics-based models of econophysics, we see that government spending on pensions, rent help, and disability care is not a loss. The state gives money to low-income households (acting as biological conduits). Because they must spend this money immediately to survive, it flows directly into the cash registers of grocery duopolies, landlords, and care companies."*
* **ELI5**:
  > *"Traditional economics says welfare is just a money drain. But when we look closely, it is like a water pump. The government pumps money to families who need it to survive (acting as biological pipelines). Because they must buy food, pay rent, and get care, they spend the money instantly. This money flows straight to giant supermarkets, landlords, and private care companies."*
* **Core Points**:
  > * **Macroeconomic Paradigm**: Neoclassical view models welfare as a unilateral fiscal liability. Heterodox analysis reframes it as an active "indirect moral micro-subsidy".
  > * **Capture Mechanism**: Treasury disbursements are captured by private monopolies in food (grocery duopolies), housing (private rental market), and care (privatized care networks) via the biological survival needs of citizens.
  > * **Methodology**: Applied Stock-Flow Consistent (SFC) models, the Kalecki-Levy profit equation, and thermodynamic principles of econophysics.
