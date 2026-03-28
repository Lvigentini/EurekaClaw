# EurekaLab Documentation

EurekaLab is a multi-agent autonomous research system that produces publication-quality papers — proof papers, surveys, systematic reviews, experimental studies, and discussion papers — from your terminal or browser UI.

## User Documentation

| Document | Description |
|---|---|
| [user-guide.md](user-guide.md) | **Start here** — installation, usage walkthrough, troubleshooting |
| [paper-types.md](paper-types.md) | The 5 paper types: proof, survey, review, experimental, discussion |
| [cli.md](cli.md) | CLI commands and options (30+ commands) |
| [configuration.md](configuration.md) | All `.env` settings and their effects |
| [UI.md](UI.md) | Browser UI — architecture, components, gate system |

## Reference Documentation

| Document | Description |
|---|---|
| [architecture.md](architecture.md) | System overview, pipeline stages, data flow |
| [api.md](api.md) | Python API — `EurekaSession`, `KnowledgeBus`, data models |
| [agents.md](agents.md) | Each agent's role, inputs, outputs, and tool usage |
| [tools.md](tools.md) | Research tools: arXiv, Semantic Scholar, OpenAlex, CrossRef, Lean4, etc. |
| [memory.md](memory.md) | Three-tier memory system |
| [skills.md](skills.md) | Skill registry, injection, and distillation |
| [domains.md](domains.md) | Domain plugin system and how to add new domains |
| [token-limits.md](token-limits.md) | Token budget management per agent |

## Development Documentation

| Document | Description |
|---|---|
| [changelog.md](changelog.md) | Version history and release notes |
| [planning/](planning/) | Architecture plans and design decisions |

## Quick Start

```bash
# Survey a research domain (default paper type for explore)
eurekalab explore "transformer architectures" --paper-type survey

# Prove a conjecture
eurekalab prove "The sample complexity is O(d/eps^2)" --domain "ML theory"

# Start from your bibliography
eurekalab from-bib refs.bib --pdfs ./papers/ --domain "ML theory" --paper-type review

# Start from a draft paper
eurekalab from-draft paper.tex "Help me strengthen the theory"

# Launch browser UI
eurekalab ui --open-browser
```

## Architecture at a Glance

```
InputSpec (mode + paper_type)
    │
    ▼
MetaOrchestrator → selects pipeline YAML by paper_type
    │
    ├── proof_pipeline.yaml
    │     survey → ideation → theory → experiment → writer
    │
    ├── survey_pipeline.yaml
    │     survey → ideation → analyst → writer
    │
    ├── review_pipeline.yaml (PRISMA)
    │     survey → ideation → analyst → writer
    │
    ├── experimental_pipeline.yaml
    │     survey → ideation → analyst → experiment → writer
    │
    └── discussion_pipeline.yaml
          survey → ideation → analyst → writer

Agents:
  SurveyAgent    — literature search (arXiv, Semantic Scholar, OpenAlex)
  IdeationAgent  — hypotheses / taxonomy / protocol / thesis (paper-type-aware)
  TheoryAgent    — 7-stage proof pipeline (proof papers only)
  AnalystAgent   — taxonomy, screening, evidence, experiment design (non-proof)
  ExperimentAgent — numerical validation / experiment execution
  WriterAgent    — paper generation (polymorphic by paper type)

Storage:
  KnowledgeBus   — central artifact store
  SessionDB      — SQLite metadata + version history (~/.eurekalab/eurekalab.db)
  VersionStore   — git-like session versioning (checkout, diff, rollback)
```
