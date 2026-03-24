"""ConsensusMerger — independent experiment validation. Implemented in Task 6."""

from eurekaclaw.ensemble.mergers.base import BaseMerger
from eurekaclaw.knowledge_bus.bus import KnowledgeBus
from eurekaclaw.types.agents import AgentResult
from eurekaclaw.types.tasks import Task


class ConsensusMerger(BaseMerger):
    async def merge(self, results, task, bus):
        raise NotImplementedError("ConsensusMerger not yet implemented")
