# Collaboration Spectrum — Adaptive AI Involvement

**Status:** Proposal
**Date:** 2026-03-29

---

## 1. The Insight

The previous plan pushed too far toward "AI never writes." The reality: different researchers need different things at different stages. A PhD student working on their first survey needs more help than a senior researcher who just wants AI to check their citations. And the same person might want full AI autonomy for literature search but manual control for writing.

**The right model isn't a binary.** It's a spectrum of AI involvement that the user controls per stage.

---

## 2. User Profiles

### Profile A: "Do It For Me" (Novice / Time-Pressed)
- Early-career researcher or someone outside their expertise
- Wants AI to handle as much as possible
- Needs: AI generates drafts, proposes everything, user approves
- Current pipeline already serves this well
- Risk: over-reliance, AI junk output
- Mitigation: AI flags low-confidence sections, critical review always runs

### Profile B: "Work With Me" (Collaborative)
- Mid-career researcher who knows the domain
- Wants AI as a co-pilot, not autopilot
- Needs: AI proposes, user refines. AI searches, user curates. AI drafts, user rewrites.
- This is the missing mode — requires dialogue at each stage
- Most common use case for a serious research tool

### Profile C: "Check My Work" (Expert / Review-Only)
- Senior researcher with a draft or clear direction
- Wants AI for grunt work (search, citation check) and critical review
- Needs: AI reviews their writing, identifies gaps, plays devil's advocate
- Doesn't want AI to generate text (except for finding missing references)
- Most aligned with the "thinking scaffold" philosophy

**Key insight:** These aren't fixed personas. The same user might be Profile A for literature search (let AI find papers) and Profile C for writing (review my draft, don't rewrite it). The system should allow **per-stage configuration**.

---

## 3. The Three Modes

At each pipeline stage, the user can operate in one of three modes:

| Mode | AI Role | User Role | When to Use |
|------|---------|-----------|-------------|
| **Autopilot** | AI executes autonomously, presents results | User reviews and approves | Routine stages, time pressure, outside expertise |
| **Co-pilot** | AI proposes, explains, debates. User decides | User drives direction, AI assists | Core research stages, collaborative exploration |
| **Review** | User does the work, AI provides critical feedback | User creates, AI critiques | Writing, expert-level work, "thinking scaffold" |

### How This Maps to Existing Infrastructure

**Autopilot** = current pipeline behavior. Already built. Works for all stages.

**Co-pilot** = enhanced gates with dialogue. Partially built (direction gate, theory review gate). Needs: richer interaction at survey, ideation, and writing stages.

**Review** = new capability. Partially built (content gap report, theory review). Needs: dedicated reviewer agent, section-by-section feedback, writing critique.

---

## 4. Stage-by-Stage Analysis

### Literature Search

| Mode | What Happens | Tools Used |
|------|-------------|-----------|
| **Autopilot** | Survey agent runs, finds papers, presents summary | SurveyAgent, arXiv, S2, OpenAlex (existing) |
| **Co-pilot** | AI presents papers in batches, user accepts/rejects, AI adjusts search | SurveyAgent + ContentGapAnalyzer + interactive selection (partially built) |
| **Review** | User provides their bibliography, AI identifies gaps and suggests additions | BibLoader, ContentGapAnalyzer, from-bib/from-zotero (existing) |

**What's already built:** Autopilot and Review modes are fully functional. Co-pilot needs: paper-level accept/reject UI, search transparency (show queries), iterative search rounds.

**Gap:** No way to see *why* a paper was selected or reject individual papers through the UI.

### Ideation / Direction

| Mode | What Happens | Tools Used |
|------|-------------|-----------|
| **Autopilot** | 5 directions generated, best auto-selected | IdeationAgent, DivergentConvergentPlanner (existing) |
| **Co-pilot** | AI proposes directions with pros/cons, user discusses and refines through dialogue | IdeationAgent + IdeationPool + inject-idea (partially built) |
| **Review** | User states their direction, AI critiques it: "Have you considered...", "A reviewer would ask..." | New: CritiqueAgent or mode on IdeationAgent |

**What's already built:** Autopilot works. IdeationPool + inject-idea provide partial co-pilot support. Direction gate allows manual override.

**Gap:** No critique mode where AI challenges the user's own direction. No pros/cons on proposed directions.

### Analysis / Core Work

| Mode | What Happens | Tools Used |
|------|-------------|-----------|
| **Autopilot** | TheoryAgent proves / AnalystAgent analyzes autonomously | Theory pipeline, AnalystAgent (existing) |
| **Co-pilot** | AI proposes analysis structure, user guides. For proofs: AI proposes lemma structure, user approves each step | TheoryAgent with step-by-step gates (partially built via theory_review_gate) |
| **Review** | User provides their analysis, AI identifies logical gaps and missing evidence | New: analysis review capability |

**What's already built:** Autopilot is full. Theory review gate provides some co-pilot for proofs.

**Gap:** No way to present analysis structure for approval before execution. No review of user-provided analysis.

### Writing

| Mode | What Happens | Tools Used |
|------|-------------|-----------|
| **Autopilot** | WriterAgent produces complete paper | WriterAgent (existing, all 5 paper types) |
| **Co-pilot** | AI generates a draft, user edits, AI reviews edits | WriterAgent + new ReviewerAgent |
| **Review** | User writes, AI reviews section by section with structured feedback | New: ReviewerAgent |

**What's already built:** Autopilot is fully functional with polymorphic writer.

**Gap:** No co-pilot or review mode for writing. This is the biggest missing piece.

### Rigor Check

| Mode | What Happens | Tools Used |
|------|-------------|-----------|
| **Autopilot** | ConsistencyChecker runs, reports pass/fail | ConsistencyChecker (existing, proof papers only) |
| **Co-pilot** | AI presents issues, user discusses resolution | ConsistencyChecker + dialogue |
| **Review** | Comprehensive peer review of user's paper: structured feedback with major/minor | New: ReviewerAgent in full-review mode |

**What's already built:** Autopilot for proof papers. Nothing for other paper types.

**Gap:** No general rigor check for non-proof papers. No structured peer review output.

---

## 5. What Needs Building (Using What We Have)

### Priority 1: Collaboration Level Control
- Add `collaboration_level: Literal["autopilot", "copilot", "review"]` to session configuration
- Default: "copilot" (the balanced middle ground)
- Can be set globally or overridden per stage
- UI: simple 3-way toggle in the session form and in Settings

**Existing code to leverage:** `InputSpec` already has paper_type; add collaboration_level. `GateController` already handles human/auto/none — extend to support richer interaction.

### Priority 2: Enhanced Gate Interactions (Co-pilot mode)
- **Literature gate**: After survey, show papers with relevance explanations, let user accept/reject individual papers, request additional searches
- **Direction gate**: Show pros/cons for each direction, let user modify or propose own
- **Analysis gate**: Show proposed outline/structure before execution
- **Writing gate**: Present draft for user editing before finalization

**Existing code to leverage:** GateController, IdeationPool, ContentGapAnalyzer, all UI panels. The gate infrastructure is there — it just needs richer content at each gate.

### Priority 3: ReviewerAgent (Review mode)
- New agent that critiques user-provided text
- Section-by-section review with: clarity, rigor, evidence, completeness
- Major/minor/suggestion classification
- Can review at any time during the session (not just at the end)

**Existing code to leverage:** BaseAgent framework, LLM client, KnowledgeBus for storing reviews alongside other artifacts.

### Priority 4: Writing Support Panel
- Draft editor in the UI where users can write or edit AI-generated text
- Inline review comments from ReviewerAgent
- "Generate scaffold for this section" button (clearly labeled as AI-generated)
- Track which text is user-written vs. AI-generated

**Existing code to leverage:** PaperPanel already shows paper content. Extend with editing + review overlay.

### Priority 5: Search Transparency
- Show search queries, result counts, ranking factors
- Per-paper: why was this included? Why was it ranked here?
- Let user modify search queries directly

**Existing code to leverage:** SurveyAgent already logs queries. Surface this in the UI.

---

## 6. Configuration Model

### Session-Level Setting
```python
class InputSpec(BaseModel):
    # ... existing fields ...
    collaboration_level: Literal["autopilot", "copilot", "review"] = "copilot"
```

### Per-Stage Override (Advanced)
```python
class StageConfig(BaseModel):
    stage: str  # "survey", "ideation", "analysis", "writing", "rigor"
    level: Literal["autopilot", "copilot", "review"]
```

### How It Affects the Pipeline

| Stage | autopilot | copilot | review |
|-------|-----------|---------|--------|
| Survey | Run autonomously | Run, then present papers for curation | Skip (user provides bibliography) |
| Ideation | Auto-select best direction | Present options with dialogue | User provides direction, AI critiques |
| Analysis | Run autonomously | Propose structure, wait for approval | User provides analysis, AI reviews |
| Writing | Generate full paper | Generate draft, user edits | User writes, AI reviews |
| Rigor | Auto-check (proof papers) | Present issues for discussion | Full peer review |

### What the Pipeline Does Differently

**autopilot:** Current behavior. No changes needed. Pipeline runs, gates auto-approve.

**copilot:** Pipeline runs each stage but pauses at an *enhanced gate* after each one. The gate shows richer content (not just "approve?") and allows the user to modify, reject, or redirect. This is the default.

**review:** Pipeline only runs survey (to find papers). Everything else is user-driven. AI is available on-demand for critique, search, and analysis. Writing is done by the user with AI review.

---

## 7. UI Flow by Mode

### Autopilot
```
[Launch] → watch progress → [approve direction] → watch → [output]
```
Same as today. Minimal interaction. Good for quick exploration or time pressure.

### Copilot (default)
```
[Launch] → [review papers, accept/reject] → [discuss directions] →
[approve outline] → [review draft sections] → [output]
```
Pauses at each stage with rich interaction. User stays in control but AI does the heavy lifting.

### Review
```
[Provide bibliography + direction] → [write sections in Draft panel] →
[request AI review] → [address comments] → [final check] → [output]
```
User-driven from the start. AI is a tool called on demand, not a pipeline that runs.

---

## 8. Implementation Plan

### Phase 1: Collaboration Level Plumbing
- Add `collaboration_level` to InputSpec, ResearchBrief
- Add 3-way toggle to session creation form (Autopilot / Co-pilot / Review)
- Add to CLI: `--collab autopilot|copilot|review`
- GateController branches on level:
  - autopilot → auto-approve (existing `none` mode)
  - copilot → rich interactive gate (enhanced `human` mode)
  - review → skip stage or present review interface
- **No agent changes** — just routing and gate behavior

### Phase 2: Enhanced Gates (Co-pilot)
- **Paper curation gate**: after survey, show each paper with relevance, accept/reject/more buttons
- **Direction gate**: show pros/cons, "what could go wrong", user can edit or propose own
- **Structure gate**: show proposed outline, user can reorder/edit before analysis runs
- These are UI + GateController changes, not new agents

### Phase 3: ReviewerAgent
- New agent for section-by-section critical review
- Called on-demand (not in the pipeline)
- Produces structured feedback: major/minor/suggestion
- Tracks comments across revisions
- Works for all paper types

### Phase 4: Draft Panel
- Writing/editing area in the workspace
- Inline review comments from ReviewerAgent
- "Scaffold this section" button (optional, AI-generated, labeled)
- Version tracking for the user's writing (separate from pipeline versions)

### Phase 5: Search Transparency
- Show search queries and strategies in the Literature panel
- Per-paper relevance explanation
- Let user add their own search queries

---

## 9. What Stays, What Changes, What's New

### Stays (no changes)
- All 5 pipeline types (proof, survey, review, experimental, discussion)
- All entry modes (explore, prove, from-bib, from-draft, from-zotero)
- VersionStore, SessionDB, IdeationPool
- All agents (SurveyAgent, IdeationAgent, TheoryAgent, AnalystAgent, WriterAgent, ExperimentAgent)
- Zotero integration, content tiers, PDF extraction
- CLI and API endpoints

### Changes (modifications)
- GateController: richer interaction modes based on collaboration_level
- MetaOrchestrator: respect collaboration_level for stage execution
- UI workspace: panels evolve to support interactive review and editing
- InputSpec / ResearchBrief: new `collaboration_level` field

### New
- `collaboration_level` setting (autopilot / copilot / review)
- ReviewerAgent (critical review, structured feedback)
- Enhanced gate UI components (paper curation, direction debate, structure approval)
- Draft panel with inline review comments
- Search transparency panel

---

## 10. Why This Works

1. **Uses everything we built** — no throwaway. The pipeline, agents, versioning, paper types, Zotero — all still valuable.

2. **Serves all user types** — novices get autopilot, collaborators get co-pilot, experts get review mode.

3. **Gradual adoption** — users can start with autopilot (familiar) and increase involvement as they gain confidence.

4. **"Thinking scaffold" by default** — co-pilot mode (the default) naturally creates dialogue and critical engagement without requiring the user to do everything.

5. **AI-generated text is controlled** — autopilot produces full drafts (labeled), co-pilot produces editable drafts, review mode only produces feedback.

6. **Incremental implementation** — Phase 1 is just a new field + gate routing. Each phase adds value independently.
