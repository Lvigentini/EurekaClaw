# Paper Types

EurekaLab produces 5 types of academic paper. Each type runs a different pipeline with different agents and produces a different paper structure.

## Survey Paper

**Best for:** Mapping a research field, comparing methods, identifying trends.

**What you get:**
- Hierarchical taxonomy of approaches
- Comparison tables across key dimensions
- Trend analysis (what's growing, what's declining)
- Open problems and future directions

**Default for:** `explore`, `from-bib`, `from-zotero`

**Example:**
```bash
eurekalab explore "reinforcement learning for robotics" --paper-type survey
```

---

## Proof Paper

**Best for:** Mathematical research, theorem proving, formal results.

**What you get:**
- Formal theorem statements
- Lemma-by-lemma proofs
- Optional numerical experiments validating bounds
- LaTeX with theorem environments

**Default for:** `prove`

**Example:**
```bash
eurekalab prove "The regret bound is O(sqrt(dT))" --domain "bandit theory"
```

---

## Systematic Review

**Best for:** Evidence-based reviews following PRISMA methodology.

**What you get:**
- Explicit search protocol with inclusion/exclusion criteria
- PRISMA flow diagram (described in text)
- Quality assessment of included studies
- Thematic synthesis with summary tables

**Example:**
```bash
eurekalab explore "effects of mindfulness on anxiety" --paper-type review
```

---

## Experimental Study

**Best for:** Testable hypotheses that need empirical validation.

**What you get:**
- Formal hypothesis with variables defined
- Experimental methodology and design
- Results with statistical significance tests
- Discussion of findings and limitations

**Example:**
```bash
eurekalab explore "does model size improve reasoning ability" --paper-type experimental
```

---

## Discussion Paper

**Best for:** Advancing a position, challenging assumptions, or synthesizing perspectives.

**What you get:**
- Clear thesis statement with supporting claims
- Evidence for and against the thesis
- Steel-manned counterarguments with rebuttals
- Implications and recommendations

**Example:**
```bash
eurekalab explore "AI alignment is fundamentally unsolvable" --paper-type discussion
```
