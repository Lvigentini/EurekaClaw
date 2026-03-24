"""AdversarialMerger — cross-review ideation directions. Implemented in Task 5."""

from eurekaclaw.ensemble.mergers.base import BaseMerger
from eurekaclaw.knowledge_bus.bus import KnowledgeBus
from eurekaclaw.types.agents import AgentResult
from eurekaclaw.types.tasks import Task


class AdversarialMerger(BaseMerger):
    async def merge(self, results, task, bus):
        raise NotImplementedError("AdversarialMerger not yet implemented")
