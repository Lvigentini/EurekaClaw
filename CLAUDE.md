# EurekaClaw

Multi-agent system for theoretical research — proof-heavy, formalism-rich, math-dense domains.

## Quick Reference

- **Version:** 0.3.0
- **Python:** 3.11+
- **Entry:** `eurekaclaw/cli.py` (Click CLI), `eurekaclaw/main.py` (EurekaSession)
- **Tests:** `pytest tests/ -v` (177 tests, ~6s)
- **Package:** `pip install -e "."` (or `pip install -e ".[all]"` for all extras)

## Architecture

### Pipeline
```
survey → ideation → direction_gate → theory → theory_review_gate → experiment → writer
```

Pipeline is defined in `eurekaclaw/orchestrator/pipelines/default_pipeline.yaml` and executed by `MetaOrchestrator` in `eurekaclaw/orchestrator/meta_orchestrator.py`.

### Key Components
| Component | Path | Purpose |
|-----------|------|---------|
| KnowledgeBus | `eurekaclaw/knowledge_bus/bus.py` | Central artifact store, reactive subscriptions |
| MetaOrchestrator | `eurekaclaw/orchestrator/meta_orchestrator.py` | Pipeline execution, gates, feedback |
| VersionStore | `eurekaclaw/versioning/store.py` | Git-like session versioning |
| IdeationPool | `eurekaclaw/orchestrator/ideation_pool.py` | Continuous ideation, injected ideas |
| GateController | `eurekaclaw/orchestrator/gate.py` | Human/auto gates, content status |
| Config | `eurekaclaw/config.py` | Pydantic Settings, all env vars |

### Data Models
All in `eurekaclaw/types/artifacts.py` and `eurekaclaw/types/tasks.py`:
- `Paper` — with content_tier, full_text, local_pdf_path, zotero_item_key
- `Bibliography` — papers + citation_graph
- `ResearchBrief` — session state: directions, selected_direction, draft info
- `TheoryState` — proven_lemmas (dict[str, ProofRecord]), lemma_dag, open_goals
- `InputSpec` — mode (detailed/reference/exploration), draft_path, draft_instruction
- `ResearchOutput` — final artifacts (latex_paper, bibliography_json, etc.)

### Entry Points (CLI)
| Command | What |
|---------|------|
| `prove` | Prove a specific conjecture |
| `explore` | Open exploration of a domain |
| `from-papers` | Start from arXiv IDs |
| `from-bib` | Start from .bib file + local PDFs |
| `from-draft` | Start from a draft paper |
| `from-zotero` | Start from a Zotero collection |
| `inject paper/idea/draft` | Mid-session injection |
| `history/diff/checkout` | Version management |
| `push-to-zotero` | Sync results back to Zotero |

## Conventions

- All agents extend `BaseAgent` in `eurekaclaw/agents/base.py`
- LLM calls go through `eurekaclaw/llm/base.py` (normalized response types)
- Config uses Pydantic Settings with `alias=ENV_VAR_NAME` pattern
- Tests use `tmp_path` fixtures, mock external APIs, no network calls in unit tests
- Commits follow conventional commits: `feat:`, `fix:`, `chore:`, `docs:`
- Version in both `pyproject.toml` and `eurekaclaw/__init__.py` — keep in sync

## Important Patterns

- **Circular imports:** `versioning/snapshot.py` ↔ `knowledge_bus/bus.py` — use lazy imports (inside methods, not at module level)
- **proven_lemmas** is `dict[str, ProofRecord]`, NOT a list
- **Content tiers:** Paper.content_tier is one of: full_text, abstract, metadata, missing
- **PDF extraction:** pdfplumber (default) or docling; controlled by `PAPER_READER_PDF_BACKEND`
- **OAuth auth:** ccproxy handles Claude Pro/Max OAuth tokens; configured via `ANTHROPIC_AUTH_MODE=oauth`
- **Version commits:** auto-triggered by `bus.persist_incremental()` — every stage completion creates a version
