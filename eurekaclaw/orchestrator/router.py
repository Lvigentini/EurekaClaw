"""TaskRouter — maps task agent_role to the correct agent instance."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eurekaclaw.agents.base import BaseAgent
from eurekaclaw.types.agents import AgentRole
from eurekaclaw.types.tasks import Task

if TYPE_CHECKING:
    from eurekaclaw.llm.base import LLMClient


class TaskRouter:
    """Resolves a Task to the appropriate BaseAgent."""

    def __init__(self, agents: dict[AgentRole, BaseAgent]) -> None:
        self._agents = agents

    def resolve(self, task: Task) -> BaseAgent:
        role = AgentRole(task.agent_role)
        agent = self._agents.get(role)
        if not agent:
            raise ValueError(f"No agent registered for role: {role}")
        return agent

    def create_agent(self, task: Task, client: "LLMClient") -> BaseAgent:
        """Create a NEW agent instance for parallel ensemble execution.

        Unlike resolve() which returns shared singletons, this creates
        independent instances safe for concurrent use.
        """
        from eurekaclaw.agents.survey.agent import SurveyAgent
        from eurekaclaw.agents.ideation.agent import IdeationAgent
        from eurekaclaw.agents.theory.agent import TheoryAgent
        from eurekaclaw.agents.experiment.agent import ExperimentAgent
        from eurekaclaw.agents.writer.agent import WriterAgent

        _AGENT_CLASSES = {
            AgentRole.SURVEY: SurveyAgent,
            AgentRole.IDEATION: IdeationAgent,
            AgentRole.THEORY: TheoryAgent,
            AgentRole.EXPERIMENT: ExperimentAgent,
            AgentRole.WRITER: WriterAgent,
        }
        role = AgentRole(task.agent_role)
        cls = _AGENT_CLASSES.get(role)
        if not cls:
            raise ValueError(f"No agent class for role: {role}")

        # Get shared dependencies from the existing singleton agent
        template = self._agents[role]
        return cls(
            bus=template.bus,
            tool_registry=template.tool_registry,
            skill_injector=template.skill_injector,
            memory=template.memory,
            client=client,
        )
