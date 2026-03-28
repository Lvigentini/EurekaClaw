# Workflow Guide

This guide explains how to get the most out of EurekaLab's research process.

## Starting a Session

### Choose Your Entry Point

| If you have... | Use this command |
|----------------|-----------------|
| A research question | `eurekalab explore "your topic"` |
| A specific claim to prove | `eurekalab prove "your conjecture"` |
| Paper IDs from arXiv | `eurekalab from-papers 2401.12345` |
| A .bib file | `eurekalab from-bib refs.bib --pdfs ./papers/` |
| A draft paper | `eurekalab from-draft paper.tex "your instruction"` |
| A Zotero collection | `eurekalab from-zotero COLLECTION_ID` |

### Choose Your Paper Type

Add `--paper-type` to any command:

```bash
eurekalab explore "AI safety" --paper-type discussion
eurekalab from-bib refs.bib --domain "NLP" --paper-type review
```

## During a Session

### The Pipeline

Your session runs through several stages. You can see progress in the **Live** tab:

1. **Survey** — Finding and reading papers
2. **Ideation** — Generating research directions
3. **Direction Gate** — You approve or modify the direction
4. **Core Work** — Proving, analyzing, or experimenting (depends on paper type)
5. **Writing** — Producing the final paper

### Content Gaps

After the survey, you may see a **Content Gaps** banner showing papers where only the abstract was available. You can:
- **Provide PDFs**: Point to a local directory containing your papers
- **Skip**: Continue with abstracts only (less detailed results)

### Injecting Ideas Mid-Session

Pause the session (Ctrl+C or the Pause button), then inject new content:

```bash
# Add a paper you just found
eurekalab inject paper <session-id> 2401.12345

# Add an idea
eurekalab inject idea <session-id> "What about using spectral methods?"

# Add a draft section
eurekalab inject draft <session-id> notes.tex "Consider this approach"
```

Resume with `eurekalab resume <session-id>`.

In the UI, use the **Inject** drawer that appears when a session is paused.

## After a Session

### Your Output

Results are saved to `./results/` (or your custom output directory):

| File | Content |
|------|---------|
| `paper.md` | Markdown version of the paper |
| `paper.tex` | LaTeX source |
| `paper.pdf` | Compiled PDF (if pdflatex is available) |
| `references.bib` | Bibliography in BibTeX format |
| `theory_state.json` | Proof details (proof papers only) |

### Version History

Every stage creates a version. You can review the history:

```bash
eurekalab history <session-id>     # see all versions
eurekalab diff <session-id> 1 3    # compare two versions
eurekalab checkout <session-id> 2  # roll back to version 2
```

In the UI, use the **History** tab to browse versions.

### Push to Zotero

Send your discovered papers to Zotero:

```bash
eurekalab push-to-zotero <session-id> --collection "My Research"
```

## Managing Sessions

```bash
eurekalab sessions                             # list all sessions
eurekalab clean --older-than 30 --status failed  # remove old failed sessions
eurekalab housekeep --push-papers              # push all unfiled papers to Zotero
```

## Tips

- **Start broad, then narrow**: Use `explore` with `--paper-type survey` first to understand the field, then use `prove` or `from-papers` for specific work.
- **Use your Zotero library**: If you already have papers collected, `from-zotero` saves time by skipping redundant searches.
- **Inject ideas**: Don't just watch the pipeline run — pause and inject ideas when inspiration strikes.
- **Check content gaps**: Full-text papers produce much better results than abstract-only. Use institutional access or provide local PDFs.
- **Review version history**: If a session goes in the wrong direction, checkout an earlier version and try again.
