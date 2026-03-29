# Review Guide

The Review feature is one of EurekaLab's most powerful tools. It gives you structured, persona-driven feedback on your paper — like having a panel of reviewers at your disposal.

## How It Works

1. Go to the **Review** tab in any session (or use the terminal)
2. Choose a reviewer persona
3. Optionally add custom instructions
4. Click **Run Review**
5. Get structured feedback: strengths, issues (major/minor/suggestion), scores, and a recommendation

## The Three Built-In Personas

### Adversarial (tear it apart)
The toughest reviewer your paper could face. Attacks assumptions, methodology, claims, novelty, and completeness. If your paper survives this, it can survive anyone.

**Use when:** You want to find every weakness before a real reviewer does. Best used before submission to a competitive venue.

### Rigorous (fair peer review)
A thorough, balanced review. Evaluates methodology, clarity, novelty, and completeness. Classifies issues as major (must fix) or minor (should fix). The closest to what you'd get from a real peer review.

**Use when:** You want a realistic assessment of where your paper stands. Good for deciding if it's ready to submit.

### Constructive (focus on improvement)
Starts with what works well, then suggests specific improvements for every weakness. Every critique is paired with an actionable fix. Encouraging but honest.

**Use when:** You're in the middle of writing and want guidance on how to improve. Less intimidating than the adversarial reviewer.

## Custom Instructions

Stack custom focus on top of any persona:

- "Focus especially on whether my statistical methods are appropriate"
- "Check if my related work section covers the key papers in this area"
- "Evaluate whether the paper is suitable for NeurIPS"
- "Pay attention to the logical flow between sections 3 and 4"

## Multi-Round Reviews

You can run multiple reviews in sequence:

1. **Round 1:** Adversarial — find all the problems
2. Fix the major issues
3. **Round 2:** Rigorous — check if the fixes work
4. **Round 3:** Constructive — polish and refine

Each round's results are preserved. The system detects if previous issues have been addressed.

## From the Terminal

```bash
# Quick review with the rigorous persona
eurekalab review paper.tex

# Adversarial review
eurekalab review paper.tex --persona adversarial

# With custom instructions
eurekalab review paper.md --persona constructive --instructions "focus on the methodology section"
```

## Adding Custom Personas

Create a YAML file and install it:

```yaml
# my-reviewer.yaml
name: "My Custom Reviewer"
type: custom
icon: "🎯"
description: "Focuses on practical applicability"
review_prompt: |
  You are reviewing this paper for practical applicability.
  Focus on: real-world usefulness, implementation feasibility,
  and whether the results are actionable for practitioners.
  ...
```

```bash
eurekalab reviewer install my-reviewer.yaml
```

Your custom personas appear alongside the built-in ones in both the UI and CLI.

## Tips

- **Start with Constructive** if you're early in the writing process — it's less overwhelming
- **Use Adversarial before submission** — it'll catch things you missed
- **Custom instructions are powerful** — "Is this paper suitable for [specific journal]?" gives venue-targeted feedback
- **Multiple rounds work best** — fix issues between rounds for incremental improvement
- **Don't take it personally** — the adversarial reviewer is deliberately harsh. That's the point.
