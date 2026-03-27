"""AnalystAgent — flexible agent for non-proof core work.

Handles taxonomy construction, systematic review screening, statistical
analysis, evidence gathering, counterargument analysis, and more.
The specific behavior is determined by ``task.inputs["task_type"]`` which
is set in the pipeline YAML.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from eurekalab.agents.base import BaseAgent
from eurekalab.config import settings
from eurekalab.types.agents import AgentRole
from eurekalab.types.tasks import Task

logger = logging.getLogger(__name__)

# Task-type-specific system prompts
_ANALYST_PROMPTS: dict[str, str] = {
    "survey_analysis": """\
You are the Analyst Agent of EurekaLab, working on a **survey paper**.

Your task is to analyze the bibliography and produce a structured survey:
1. **Taxonomy**: Organize the papers into a hierarchical categorization
   (3-7 top-level categories, with subcategories where appropriate).
2. **Per-category analysis**: For each category, summarize the key methods,
   results, strengths, and limitations.
3. **Comparison tables**: Build comparison dimensions (e.g., method type,
   dataset used, performance metric, computational cost) and populate a
   comparison matrix.
4. **Trend analysis**: Identify temporal trends, emerging sub-fields,
   and methodological shifts.
5. **Open problems**: List 5-10 open research questions with difficulty
   estimates and potential approaches.

Output a JSON object with keys:
  "taxonomy": [{"name": str, "description": str, "paper_ids": [str], "subcategories": [...]}]
  "comparison_dimensions": [str]
  "comparison_table": [{"paper_id": str, "values": {"dimension": "value"}}]
  "trends": str (2-3 paragraphs)
  "open_problems": [{"problem": str, "difficulty": "easy|medium|hard", "approach_hint": str}]
""",

    "systematic_review": """\
You are the Analyst Agent of EurekaLab, working on a **systematic review**.

Follow PRISMA methodology:
1. **Screening**: Apply the inclusion/exclusion criteria from the research
   direction to each paper. Classify as included or excluded (with reason).
2. **Quality assessment**: Score each included paper on methodological rigor
   (1-5 scale) across dimensions: study design, sample size, measurement
   validity, analysis rigor, reporting quality.
3. **Data extraction**: For each included paper, extract: objective, methods,
   key findings, limitations, sample/dataset details.
4. **Synthesis**: Group findings by theme. Identify consensus, contradictions,
   and gaps. Compute summary statistics if applicable.

Output a JSON object with keys:
  "screening": {"included": [{"paper_id": str, "reason": str}], "excluded": [{"paper_id": str, "reason": str}]}
  "quality_scores": [{"paper_id": str, "overall": float, "dimensions": {"dim": score}}]
  "extraction_table": [{"paper_id": str, "objective": str, "methods": str, "findings": str, "limitations": str}]
  "themes": [{"name": str, "description": str, "evidence": [str], "consensus_level": str}]
  "prisma_counts": {"identified": int, "screened": int, "eligible": int, "included": int}
""",

    "experiment_design": """\
You are the Analyst Agent of EurekaLab, designing an **experiment**.

Based on the selected hypothesis and the literature survey:
1. **Operationalize variables**: Define independent, dependent, and control
   variables with measurement methods.
2. **Design protocol**: Specify datasets/benchmarks, baseline methods,
   evaluation metrics, parameter configurations, and number of runs.
3. **Statistical plan**: Pre-register which statistical tests will be used
   (t-test, ANOVA, bootstrap CI, etc.), significance thresholds, and
   multiple comparison corrections.
4. **Code sketch**: Outline the experiment code structure (pseudocode or
   Python skeleton).

Output a JSON object with keys:
  "variables": {"independent": [...], "dependent": [...], "control": [...]}
  "datasets": [{"name": str, "description": str, "source": str}]
  "baselines": [{"name": str, "description": str}]
  "metrics": [{"name": str, "description": str, "higher_is_better": bool}]
  "statistical_tests": [{"test": str, "when": str, "threshold": float}]
  "code_sketch": str
""",

    "argument_analysis": """\
You are the Analyst Agent of EurekaLab, working on a **discussion paper**.

Build a structured argument:
1. **Evidence gathering**: For each sub-claim of the thesis, find supporting
   and opposing evidence in the bibliography. Rate evidence strength.
2. **Counterargument analysis**: Identify the 3-5 strongest objections to
   the thesis. Steel-man each one (present it as strongly as possible).
   Then develop a rebuttal for each.
3. **Synthesis**: Weave the evidence, counterarguments, and rebuttals into
   a coherent argumentative narrative. Identify implications and limitations.
4. **Recommendations**: Based on the synthesis, propose 3-5 concrete
   actionable recommendations.

Output a JSON object with keys:
  "evidence": [{"claim": str, "supporting": [{"paper_id": str, "excerpt": str, "strength": str}], "opposing": [...]}]
  "counterarguments": [{"objection": str, "strength": str, "sources": [str], "rebuttal": str}]
  "synthesis": str (3-5 paragraphs)
  "implications": [str]
  "recommendations": [str]
  "limitations": [str]
""",
}


class AnalystAgent(BaseAgent):
    """Flexible agent for non-proof core work stages.

    The behavior is controlled by ``task.inputs["task_type"]`` which maps
    to a specific system prompt from ``_ANALYST_PROMPTS``.
    """

    role = AgentRole.ANALYST

    def get_tool_names(self) -> list[str]:
        return ["arxiv_search", "semantic_scholar_search", "web_search"]

    def _role_system_prompt(self, task: Task) -> str:
        task_type = task.inputs.get("task_type", "survey_analysis")
        prompt = _ANALYST_PROMPTS.get(task_type)
        if not prompt:
            logger.warning("AnalystAgent: unknown task_type '%s', falling back to survey_analysis", task_type)
            prompt = _ANALYST_PROMPTS["survey_analysis"]
        return prompt

    async def execute(self, task: Task) -> Any:
        brief = self.bus.get_research_brief()
        if not brief:
            return self._make_result(task, False, {}, error="No ResearchBrief found on bus")

        bib = self.bus.get_bibliography()
        papers_context = ""
        if bib and bib.papers:
            paper_summaries = []
            for p in bib.papers[:30]:  # cap at 30 papers
                summary = f"- [{p.paper_id}] {p.title}"
                if p.abstract:
                    summary += f": {p.abstract[:200]}"
                paper_summaries.append(summary)
            papers_context = "\n".join(paper_summaries)

        task_type = task.inputs.get("task_type", "survey_analysis")
        domain = brief.domain
        direction = ""
        if brief.selected_direction:
            direction = f"\nSelected direction: {brief.selected_direction.title}\n{brief.selected_direction.hypothesis}"

        user_message = (
            f"Domain: {domain}\n"
            f"Query: {brief.query}\n"
            f"{direction}\n\n"
            f"Bibliography ({len(bib.papers) if bib else 0} papers):\n"
            f"{papers_context}\n\n"
            f"Analyze these papers and produce the structured output described in your instructions."
        )

        if brief.additional_context:
            user_message += f"\n\nAdditional context:\n{brief.additional_context}"

        system = self._role_system_prompt(task)
        text, tokens = await self.run_agent_loop(
            task, user_message,
            max_turns=settings.survey_max_turns,
            max_tokens=settings.max_tokens_agent,
        )

        # Store analysis result on bus as a generic artifact
        self.bus.put(f"analysis_{task_type}", text)

        return self._make_result(
            task,
            success=True,
            output={"task_type": task_type, "analysis_length": len(text)},
            text_summary=f"Analysis complete ({task_type}): {len(text)} chars",
        )
