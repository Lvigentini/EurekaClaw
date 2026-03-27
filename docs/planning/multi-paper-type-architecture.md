# Multi-Paper-Type Architecture — Design Plan

**Status:** Plan
**Date:** 2026-03-28
**Version:** Post-0.5.0

---

## 1. The Problem

EurekaLab is **hardcoded for mathematical proof papers** at every level:

- The pipeline forces: survey → ideation (hypotheses) → **theory** (prove lemmas) → experiment (validate bounds) → writer (theorem+proof LaTeX)
- The ideation agent always generates "mathematical conjectures to prove"
- The writer requires `TheoryState` or fails
- The writer's system prompt mandates: Abstract, Introduction, Preliminaries, **Main Results**, Experiments, Related Work, Conclusion
- Proof style rules are unconditionally enforced
- `explore` funnels into the same proof pipeline — there's no way to produce a survey, review, or discussion paper

**This means:** A user running `eurekalab explore "impact of LLMs on scientific reproducibility"` will get a paper that tries to prove a theorem about LLMs rather than a structured discussion or literature review.

---

## 2. The Solution: Paper Type as a First-Class Concept

### 2.1 Paper Types

| Type | What It Produces | Who Needs It |
|------|-----------------|--------------|
| **Proof** (current) | Mathematical paper with theorems, lemmas, proofs | Theorists, mathematicians |
| **Systematic Review** | PRISMA-style systematic literature review with inclusion/exclusion criteria, synthesis | Researchers doing meta-analysis |
| **Survey** | Narrative survey with taxonomy, comparison tables, trend analysis, open problems | Researchers mapping a field |
| **Experimental** | Paper with hypothesis, methodology, experiments, statistical analysis, results | Empirical researchers |
| **Discussion** | Position/opinion paper with thesis, evidence, counterarguments, synthesis | Researchers advancing an argument |

### 2.2 Architectural Principle

**The input source (`mode`) and the output type (`paper_type`) are orthogonal.**

- `mode` = where data comes from (from-bib, from-zotero, from-draft, explore, prove)
- `paper_type` = what kind of paper to produce (proof, survey, review, experimental, discussion)

Any combination is valid:
- `from-bib` + `survey` = "Here are my papers, write a survey of this area"
- `explore` + `discussion` = "Explore this topic and write a position paper"
- `from-draft` + `proof` = "Here's my draft, help me prove the theorems"
- `from-zotero` + `review` = "Systematically review my Zotero collection"

### 2.3 Pipeline Per Paper Type

Each paper type gets its own pipeline YAML. They share `survey` and `writer` stages but differ in the middle:

```
PROOF (current):
  survey → ideation → direction_gate → theory → theory_review → experiment → writer

SURVEY (narrative):
  survey → taxonomy → deep_analysis → comparison → gap_identification → writer

SYSTEMATIC REVIEW:
  protocol_design → systematic_search → screening → quality_assessment →
  data_extraction → synthesis → writer

EXPERIMENTAL:
  survey → hypothesis → experiment_design → implementation → execution →
  analysis → writer

DISCUSSION:
  survey → thesis_formulation → evidence_gathering → counterargument →
  synthesis → writer
```

---

## 3. Data Model Changes

### 3.1 InputSpec — Add `paper_type`

```python
# eurekalab/types/tasks.py
class InputSpec(BaseModel):
    mode: Literal["detailed", "reference", "exploration", "from_bib", "from_draft", "from_zotero"]
    paper_type: Literal["proof", "survey", "review", "experimental", "discussion"] = "proof"
    # ... existing fields ...
```

### 3.2 ResearchBrief — Add `paper_type`

```python
# eurekalab/types/artifacts.py
class ResearchBrief(BaseModel):
    # ... existing fields ...
    paper_type: Literal["proof", "survey", "review", "experimental", "discussion"] = "proof"
```

### 3.3 New Artifact Types

For non-proof pipelines, we need new artifacts on the KnowledgeBus (analogous to TheoryState):

```python
# eurekalab/types/artifacts.py

class Taxonomy(BaseModel):
    """For survey papers — hierarchical categorization of papers."""
    session_id: str
    categories: list[TaxonomyCategory] = Field(default_factory=list)
    uncategorized: list[str] = Field(default_factory=list)  # paper_ids

class TaxonomyCategory(BaseModel):
    name: str
    description: str = ""
    paper_ids: list[str] = Field(default_factory=list)
    subcategories: list[TaxonomyCategory] = Field(default_factory=list)

class SynthesisState(BaseModel):
    """For review/survey papers — synthesis of findings."""
    session_id: str
    themes: list[Theme] = Field(default_factory=list)
    comparison_tables: list[ComparisonTable] = Field(default_factory=list)
    open_problems: list[str] = Field(default_factory=list)
    trend_analysis: str = ""
    status: str = "pending"

class Theme(BaseModel):
    name: str
    description: str
    evidence: list[str] = Field(default_factory=list)  # paper_ids
    key_findings: list[str] = Field(default_factory=list)

class ComparisonTable(BaseModel):
    title: str
    dimensions: list[str] = Field(default_factory=list)  # column headers
    rows: list[dict[str, str]] = Field(default_factory=list)  # paper_id → values

class ScreeningLog(BaseModel):
    """For systematic reviews — PRISMA screening record."""
    session_id: str
    total_identified: int = 0
    after_dedup: int = 0
    after_title_screen: int = 0
    after_fulltext_screen: int = 0
    included: list[str] = Field(default_factory=list)  # paper_ids
    excluded: list[ExclusionRecord] = Field(default_factory=list)

class ExclusionRecord(BaseModel):
    paper_id: str
    stage: str  # "title_screen", "fulltext_screen", "quality"
    reason: str

class ThesisState(BaseModel):
    """For discussion papers — argument structure."""
    session_id: str
    thesis: str = ""
    sub_claims: list[str] = Field(default_factory=list)
    supporting_evidence: list[EvidenceItem] = Field(default_factory=list)
    counterarguments: list[CounterargumentItem] = Field(default_factory=list)
    synthesis: str = ""
    recommendations: list[str] = Field(default_factory=list)
    status: str = "pending"

class EvidenceItem(BaseModel):
    claim: str
    source_paper_id: str = ""
    strength: str = "moderate"  # weak, moderate, strong
    excerpt: str = ""

class CounterargumentItem(BaseModel):
    objection: str
    source: str = ""
    strength: str = "moderate"
    rebuttal: str = ""

class HypothesisSpec(BaseModel):
    """For experimental papers — testable hypotheses."""
    session_id: str
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    variables: dict[str, str] = Field(default_factory=dict)  # name → description
    methodology: str = ""
    status: str = "pending"

class Hypothesis(BaseModel):
    statement: str
    null_hypothesis: str = ""
    variables: list[str] = Field(default_factory=list)
    expected_effect: str = ""
    test_method: str = ""  # "t-test", "anova", "regression", etc.
```

---

## 4. Pipeline YAML Specs

### 4.1 Proof Pipeline (existing, renamed)

```yaml
# eurekalab/orchestrator/pipelines/proof_pipeline.yaml
# (identical to current default_pipeline.yaml)
stages:
  - name: survey
    agent_role: survey
    description: "Literature survey: arXiv, Semantic Scholar, citation graph"
    ...
  - name: ideation
    agent_role: ideation
    description: "Generate research hypotheses from survey findings"
    ...
  - name: direction_selection_gate
    agent_role: orchestrator
    ...
  - name: theory
    agent_role: theory
    ...
  - name: theory_review_gate
    agent_role: orchestrator
    ...
  - name: experiment
    agent_role: experiment
    ...
  - name: writer
    agent_role: writer
    ...
```

### 4.2 Survey Pipeline (new)

```yaml
# eurekalab/orchestrator/pipelines/survey_pipeline.yaml
stages:
  - name: survey
    agent_role: survey
    description: "Broad literature search across the domain"
    inputs:
      domain: "{{brief.domain}}"
      query: "{{brief.query}}"
      search_breadth: "wide"
    depends_on: []
    max_retries: 3

  - name: taxonomy
    agent_role: analyst
    description: "Organize papers into a hierarchical taxonomy"
    inputs:
      domain: "{{brief.domain}}"
      task_type: "taxonomy_construction"
    depends_on: [survey]
    max_retries: 2

  - name: taxonomy_review_gate
    agent_role: orchestrator
    description: "Review and refine the taxonomy structure"
    depends_on: [taxonomy]
    gate_required: false

  - name: deep_analysis
    agent_role: analyst
    description: "Analyze each category: methods, results, strengths, weaknesses"
    inputs:
      task_type: "category_analysis"
    depends_on: [taxonomy_review_gate]
    max_retries: 2

  - name: comparison
    agent_role: analyst
    description: "Build comparison tables and identify trends"
    inputs:
      task_type: "comparison_synthesis"
    depends_on: [deep_analysis]
    max_retries: 2

  - name: gap_identification
    agent_role: analyst
    description: "Identify open problems and future directions"
    inputs:
      task_type: "gap_analysis"
    depends_on: [comparison]
    max_retries: 1

  - name: writer
    agent_role: writer
    description: "Write complete survey paper with taxonomy, tables, and open problems"
    depends_on: [gap_identification]
    max_retries: 3
```

### 4.3 Systematic Review Pipeline (new)

```yaml
# eurekalab/orchestrator/pipelines/review_pipeline.yaml
stages:
  - name: protocol_design
    agent_role: analyst
    description: "Define research questions, search strategy, inclusion/exclusion criteria"
    inputs:
      domain: "{{brief.domain}}"
      query: "{{brief.query}}"
      task_type: "protocol_design"
    depends_on: []
    max_retries: 2

  - name: protocol_review_gate
    agent_role: orchestrator
    description: "Review search protocol before executing"
    depends_on: [protocol_design]
    gate_required: false

  - name: systematic_search
    agent_role: survey
    description: "Execute systematic search across databases"
    inputs:
      domain: "{{brief.domain}}"
      query: "{{brief.query}}"
      search_breadth: "systematic"
    depends_on: [protocol_review_gate]
    max_retries: 3

  - name: screening
    agent_role: analyst
    description: "Apply inclusion/exclusion criteria, filter papers"
    inputs:
      task_type: "screening"
    depends_on: [systematic_search]
    max_retries: 2

  - name: quality_assessment
    agent_role: analyst
    description: "Score included studies on methodological rigor"
    inputs:
      task_type: "quality_assessment"
    depends_on: [screening]
    max_retries: 1

  - name: data_extraction
    agent_role: analyst
    description: "Extract structured data from each included paper"
    inputs:
      task_type: "data_extraction"
    depends_on: [quality_assessment]
    max_retries: 2

  - name: synthesis
    agent_role: analyst
    description: "Synthesize findings: thematic grouping, summary tables"
    inputs:
      task_type: "synthesis"
    depends_on: [data_extraction]
    max_retries: 2

  - name: writer
    agent_role: writer
    description: "Write systematic review with PRISMA flow, synthesis tables"
    depends_on: [synthesis]
    max_retries: 3
```

### 4.4 Experimental Pipeline (new)

```yaml
# eurekalab/orchestrator/pipelines/experimental_pipeline.yaml
stages:
  - name: survey
    agent_role: survey
    description: "Literature survey: establish baselines and gaps"
    inputs:
      domain: "{{brief.domain}}"
      query: "{{brief.query}}"
    depends_on: []
    max_retries: 3

  - name: hypothesis_formulation
    agent_role: ideation
    description: "Generate testable hypotheses with variables and expected effects"
    inputs:
      domain: "{{brief.domain}}"
      ideation_mode: "experimental"
    depends_on: [survey]
    max_retries: 2

  - name: hypothesis_review_gate
    agent_role: orchestrator
    description: "Select hypothesis and approve experimental design"
    depends_on: [hypothesis_formulation]
    gate_required: false

  - name: experiment_design
    agent_role: analyst
    description: "Design experiment: datasets, baselines, metrics, statistical tests"
    inputs:
      task_type: "experiment_design"
    depends_on: [hypothesis_review_gate]
    max_retries: 2

  - name: experiment
    agent_role: experiment
    description: "Run experiments and collect results"
    depends_on: [experiment_design]
    max_retries: 1

  - name: analysis
    agent_role: analyst
    description: "Statistical analysis: significance tests, effect sizes, ablations"
    inputs:
      task_type: "statistical_analysis"
    depends_on: [experiment]
    max_retries: 2

  - name: writer
    agent_role: writer
    description: "Write experimental paper: methods, results, discussion"
    depends_on: [analysis]
    max_retries: 3
```

### 4.5 Discussion Pipeline (new)

```yaml
# eurekalab/orchestrator/pipelines/discussion_pipeline.yaml
stages:
  - name: survey
    agent_role: survey
    description: "Focused literature search for evidence and counterevidence"
    inputs:
      domain: "{{brief.domain}}"
      query: "{{brief.query}}"
    depends_on: []
    max_retries: 3

  - name: thesis_formulation
    agent_role: ideation
    description: "Define core thesis with supporting claims"
    inputs:
      domain: "{{brief.domain}}"
      ideation_mode: "argumentative"
    depends_on: [survey]
    max_retries: 2

  - name: thesis_review_gate
    agent_role: orchestrator
    description: "Review and approve thesis before building arguments"
    depends_on: [thesis_formulation]
    gate_required: false

  - name: evidence_gathering
    agent_role: analyst
    description: "Deep-dive into supporting and opposing evidence"
    inputs:
      task_type: "evidence_gathering"
    depends_on: [thesis_review_gate]
    max_retries: 2

  - name: counterargument_analysis
    agent_role: analyst
    description: "Steel-man counterarguments and develop rebuttals"
    inputs:
      task_type: "counterargument_analysis"
    depends_on: [evidence_gathering]
    max_retries: 2

  - name: synthesis
    agent_role: analyst
    description: "Weave arguments into coherent narrative with implications"
    inputs:
      task_type: "argument_synthesis"
    depends_on: [counterargument_analysis]
    max_retries: 2

  - name: writer
    agent_role: writer
    description: "Write discussion paper with argumentative structure"
    depends_on: [synthesis]
    max_retries: 3
```

---

## 5. Agent Changes

### 5.1 New Agent: AnalystAgent

A **single flexible agent** that handles all the non-proof "core work" stages. It reads `task.inputs["task_type"]` from the pipeline YAML to determine its behavior.

**Location:** `eurekalab/agents/analyst/agent.py`

**Task types it handles:**
| task_type | Paper Type | What It Does |
|-----------|-----------|-------------|
| `taxonomy_construction` | Survey | Cluster papers into categories |
| `category_analysis` | Survey | Analyze each category's methods/results |
| `comparison_synthesis` | Survey | Build comparison tables, trends |
| `gap_analysis` | Survey | Identify open problems |
| `protocol_design` | Review | Define PRISMA protocol |
| `screening` | Review | Apply inclusion/exclusion criteria |
| `quality_assessment` | Review | Score study quality |
| `data_extraction` | Review | Extract structured data |
| `synthesis` | Review/Discussion | Thematic synthesis |
| `experiment_design` | Experimental | Design experiment protocol |
| `statistical_analysis` | Experimental | Run statistical tests |
| `evidence_gathering` | Discussion | Collect pro/con evidence |
| `counterargument_analysis` | Discussion | Steel-man objections |
| `argument_synthesis` | Discussion | Build argument narrative |

**System prompt template:**
```python
_ANALYST_PROMPTS = {
    "taxonomy_construction": """You are organizing {n} papers from {domain} into a
hierarchical taxonomy. For each category: name, description, which papers belong,
and key distinguishing criteria. Output JSON with the taxonomy structure.""",

    "screening": """You are applying inclusion/exclusion criteria to papers.
Protocol: {protocol}
For each paper, decide: include or exclude (with reason).
Output JSON: included (paper_ids), excluded (paper_id + reason).""",

    # ... etc for each task_type
}
```

**Design rationale:** One agent with many prompts (vs. many specialized agents) because:
1. All task_types share the same basic interaction pattern: read bus → LLM call → parse output → write to bus
2. The pipeline YAML already parameterizes behavior via `inputs.task_type`
3. Adding a new task_type is just adding a prompt, not a new agent class

### 5.2 IdeationAgent — Paper-Type-Aware Prompts

The ideation agent stays but its system prompt changes based on `paper_type`:

| paper_type | Ideation Goal | Output Format |
|-----------|---------------|---------------|
| `proof` | Generate mathematical hypotheses | `{hypothesis, proof_sketch, novelty_score}` |
| `survey` | Propose taxonomy structures | `{taxonomy_proposal, coverage_gaps}` |
| `review` | Define research questions + protocol | `{questions, databases, criteria}` |
| `experimental` | Generate testable hypotheses | `{hypothesis, null_hypothesis, variables, test_method}` |
| `discussion` | Formulate thesis + claims | `{thesis, sub_claims, key_tensions}` |

### 5.3 WriterAgent — Polymorphic Templates

The writer needs completely different system prompts and section structures per paper type:

| paper_type | Required Sections | Required Artifacts |
|-----------|-------------------|-------------------|
| `proof` | Introduction, Preliminaries, Main Results, Experiments, Related Work, Conclusion | TheoryState |
| `survey` | Introduction, Background, Taxonomy, Detailed Analysis, Comparison, Open Problems, Conclusion | SynthesisState, Taxonomy |
| `review` | Introduction, Methods (PRISMA), Results, Discussion, Limitations, Conclusion | ScreeningLog, SynthesisState |
| `experimental` | Introduction, Related Work, Methods, Results, Discussion, Conclusion | HypothesisSpec, ExperimentResult |
| `discussion` | Introduction, Background, [Thesis], [Arguments], Counterarguments, Implications, Conclusion | ThesisState |

**Key change:** The writer's `_make_result` must NOT require `theory_state`. It should check `brief.paper_type` and require the appropriate artifact:

```python
if brief.paper_type == "proof":
    if not theory_state:
        return self._make_result(task, False, {}, error="Missing TheoryState")
elif brief.paper_type == "survey":
    if not synthesis_state:
        return self._make_result(task, False, {}, error="Missing SynthesisState")
# ... etc
```

### 5.4 TheoryAgent — Becomes Proof-Only

No changes to the theory agent itself. It simply doesn't appear in non-proof pipelines. The pipeline YAML controls this — if theory isn't in the stages list, it doesn't run.

### 5.5 SurveyAgent — Minor Context Enhancement

The survey agent's system prompt gains awareness of paper_type to adjust search breadth:

| paper_type | Search Strategy |
|-----------|----------------|
| `proof` | Targeted (find gaps for theorems) — current behavior |
| `survey` | Broad (maximize coverage across the domain) |
| `review` | Systematic (follow protocol, exhaustive database search) |
| `experimental` | Baseline-focused (find existing benchmarks, datasets, methods) |
| `discussion` | Evidence-focused (find supporting and opposing arguments) |

---

## 6. Pipeline Selection Logic

### 6.1 PipelineManager Changes

```python
# eurekalab/orchestrator/pipeline.py
_PIPELINES_DIR = Path(__file__).parent / "pipelines"

_PIPELINE_BY_TYPE = {
    "proof": _PIPELINES_DIR / "proof_pipeline.yaml",
    "survey": _PIPELINES_DIR / "survey_pipeline.yaml",
    "review": _PIPELINES_DIR / "review_pipeline.yaml",
    "experimental": _PIPELINES_DIR / "experimental_pipeline.yaml",
    "discussion": _PIPELINES_DIR / "discussion_pipeline.yaml",
}

class PipelineManager:
    def build(self, brief: ResearchBrief, spec_path: Path | None = None) -> TaskPipeline:
        if spec_path is None:
            paper_type = getattr(brief, 'paper_type', 'proof')
            spec_path = _PIPELINE_BY_TYPE.get(paper_type, _PIPELINE_BY_TYPE["proof"])
        spec = self._load_spec(spec_path)
        return self._build_from_spec(spec, brief)
```

### 6.2 MetaOrchestrator Changes

The `run()` method needs to be **paper-type-aware** for gates and special handling:

```python
# Conditional gate handling
if task.name == "direction_selection_gate" and brief.paper_type == "proof":
    await self._handle_direction_gate(brief)
elif task.name == "thesis_review_gate" and brief.paper_type == "discussion":
    await self._handle_thesis_gate(brief)
elif task.name == "protocol_review_gate" and brief.paper_type == "review":
    await self._handle_protocol_gate(brief)
# ... etc
```

Better approach: **generalize gates**. Instead of hardcoded gate names, check `task.gate_required` (already exists in YAML) and use a generic gate handler.

### 6.3 AgentRole Extension

```python
# eurekalab/types/agents.py
class AgentRole(str, Enum):
    SURVEY = "survey"
    IDEATION = "ideation"
    THEORY = "theory"
    EXPERIMENT = "experiment"
    WRITER = "writer"
    ANALYST = "analyst"     # NEW: handles all non-proof core work
    ORCHESTRATOR = "orchestrator"
```

---

## 7. CLI Changes

### 7.1 Add `--paper-type` to All Entry Commands

```python
@click.option("--paper-type", "-t",
              default="proof",
              type=click.Choice(["proof", "survey", "review", "experimental", "discussion"]),
              help="Type of paper to produce")
```

Add to: `prove`, `explore`, `from-papers`, `from-bib`, `from-draft`, `from-zotero`.

### 7.2 Defaults Per Command

| Command | Default paper_type | Rationale |
|---------|-------------------|-----------|
| `prove` | `proof` | User explicitly wants a proof |
| `explore` | `survey` | Exploration naturally maps to surveying |
| `from-papers` | `survey` | Starting from papers → survey or review |
| `from-bib` | `survey` | User has a bibliography → survey |
| `from-draft` | (inferred) | Infer from draft content |
| `from-zotero` | `survey` | User's library → survey |

### 7.3 UI Changes

The `NewSessionForm` needs a paper_type selector (6 mode cards → grid with paper_type dropdown):

```typescript
const PAPER_TYPES = [
  { key: 'proof', icon: '📐', label: 'Proof Paper', desc: 'Theorems, lemmas, formal proofs' },
  { key: 'survey', icon: '🗺️', label: 'Survey', desc: 'Taxonomy, comparison, open problems' },
  { key: 'review', icon: '📋', label: 'Systematic Review', desc: 'PRISMA methodology, screening' },
  { key: 'experimental', icon: '🧪', label: 'Experimental', desc: 'Hypothesis testing, statistical analysis' },
  { key: 'discussion', icon: '💬', label: 'Discussion', desc: 'Position paper, argument, synthesis' },
];
```

---

## 8. Implementation Phases

### Phase 1: Foundation (paper_type plumbing)
- Add `paper_type` field to InputSpec, ResearchBrief
- Add `--paper-type` CLI option to all entry commands
- Pipeline selection by paper_type in PipelineManager
- Rename `default_pipeline.yaml` → `proof_pipeline.yaml`
- Symlink or default fallback so existing code works
- **Test:** All existing tests pass (paper_type defaults to "proof")

### Phase 2: Survey Pipeline
- Create `survey_pipeline.yaml`
- Create `AnalystAgent` with `taxonomy_construction`, `category_analysis`, `comparison_synthesis`, `gap_analysis` task types
- New artifacts: `Taxonomy`, `SynthesisState`, `ComparisonTable`
- Writer: add survey-specific system prompt + section structure
- Ideation: add survey-mode prompt (propose taxonomies instead of hypotheses)
- **Test:** `eurekalab explore "transformer architectures" --paper-type survey` produces a survey paper

### Phase 3: Systematic Review Pipeline
- Create `review_pipeline.yaml`
- Add `protocol_design`, `screening`, `quality_assessment`, `data_extraction`, `synthesis` task types to AnalystAgent
- New artifacts: `ScreeningLog`, `ExclusionRecord`
- Writer: add review-specific system prompt (PRISMA structure)
- **Test:** `eurekalab explore "effects of meditation on anxiety" --paper-type review` produces a systematic review

### Phase 4: Discussion Pipeline
- Create `discussion_pipeline.yaml`
- Add `evidence_gathering`, `counterargument_analysis`, `argument_synthesis` task types to AnalystAgent
- New artifacts: `ThesisState`, `EvidenceItem`, `CounterargumentItem`
- Writer: add discussion-specific prompt (argumentative structure)
- Ideation: add discussion-mode prompt (formulate thesis + claims)
- **Test:** `eurekalab explore "AI alignment risks" --paper-type discussion` produces a discussion paper

### Phase 5: Experimental Pipeline
- Create `experimental_pipeline.yaml`
- Add `experiment_design`, `statistical_analysis` task types to AnalystAgent
- New artifacts: `HypothesisSpec`, `Hypothesis`
- Enhance existing ExperimentAgent for broader experiment types
- Writer: add experimental-specific prompt (methods + results + discussion)
- Ideation: add experimental-mode prompt (testable hypotheses with variables)
- **Test:** `eurekalab explore "does model size improve reasoning?" --paper-type experimental`

### Phase 6: UI + Polish
- Add paper_type selector to NewSessionForm
- Update frontend types
- Version bump to 1.0.0

---

## 9. Key Design Decisions

### Why one AnalystAgent instead of many specialized agents?
All non-proof "core work" follows the same pattern: read artifacts from bus → LLM call with task-specific prompt → parse structured output → write to bus. The pipeline YAML already parameterizes behavior via `inputs.task_type`. Adding a new capability is just adding a prompt string, not writing a new agent class.

### Why not just modify the existing agents?
The Theory Agent is deeply specialized for proof loops (7 inner stages, lemma DAG, verification). Trying to make it also do "thematic analysis" would be worse than creating a clean new agent. The Survey and Experiment agents are already reusable. The Ideation agent needs prompt branching but not structural changes.

### Why not a single "universal" pipeline?
Each paper type has genuinely different stages (PRISMA screening vs. theorem proving vs. argument mapping). A universal pipeline would either skip stages or force unnecessary ones. Separate YAML files are explicit, maintainable, and independently testable.

### What about mixed-type papers?
A paper that's "partly survey, partly experimental" can use the experimental pipeline (which includes a survey stage). The taxonomy from the survey can be incorporated via `additional_context`. We don't need a combinatorial explosion of pipeline types — pick the primary type, enrich from others.
