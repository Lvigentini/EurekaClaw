# Getting Started

Welcome to EurekaLab! This guide walks you through your first research session.

## What EurekaLab Does

EurekaLab is an AI research assistant that takes a research question and produces a complete academic paper. It:

1. **Searches the literature** — finds relevant papers from arXiv, Semantic Scholar, and OpenAlex
2. **Generates ideas** — proposes research directions, taxonomies, or hypotheses
3. **Does the core work** — proves theorems, builds surveys, runs experiments, or constructs arguments
4. **Writes the paper** — produces a complete draft in LaTeX and Markdown

## Your First Session

### Option 1: Explore a Topic (recommended for first-timers)

Click **Research** in the sidebar, select the **Explore** mode, enter a research domain, and click **Launch**. EurekaLab will survey the field and produce a paper.

### Option 2: From the Terminal

```bash
eurekalab explore "transformer architectures" --paper-type survey
```

This will:
- Search for papers on transformer architectures
- Propose a taxonomy of approaches
- Analyze and compare methods
- Write a survey paper with comparison tables and open problems

## Choosing a Paper Type

EurekaLab can produce 5 types of paper. Select the type using the `--paper-type` option or the dropdown in the UI:

| Type | What You Get |
|------|-------------|
| **Survey** | Taxonomy, comparison tables, trends, open problems |
| **Proof** | Mathematical theorems with formal proofs |
| **Review** | Systematic review with PRISMA methodology |
| **Experimental** | Hypothesis testing with statistical analysis |
| **Discussion** | Position paper with thesis and counterarguments |

**Tip:** If you're not sure, start with **Survey** — it gives you the broadest overview of a field.

## What Happens During a Session

1. The **Survey Agent** searches for relevant papers
2. You'll see a **Content Status** report showing how many papers have full text
3. The **Ideation Agent** proposes research directions
4. You can **approve or modify** the direction at the gate
5. The core work runs (proving, analyzing, or experimenting)
6. The **Writer Agent** produces your paper
7. Output files (`.md`, `.tex`, `.pdf`) are saved to the results directory

## Pausing and Resuming

Press **Ctrl+C** at any time to pause. Your progress is saved automatically. Resume with:

```bash
eurekalab resume <session-id>
```

Or click **Continue research** in the UI.
