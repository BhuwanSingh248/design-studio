"""Architectural design decision memory tracker."""
from dataclasses import dataclass


@dataclass
class ArchitecturalDecision:
    topic: str
    decision: str
    rationale: str


class DesignDecisionMemory:
    def __init__(self):
        self._decisions: list[ArchitecturalDecision] = []

    def record_decision(self, topic: str, decision: str, rationale: str) -> None:
        self._decisions.append(ArchitecturalDecision(topic, decision, rationale))

    def to_memory_prompt(self) -> str:
        if not self._decisions:
            return ""
        lines = ["Architectural Decisions:"]
        for d in self._decisions:
            lines.append(f"- [{d.topic}]: {d.decision} (Why: {d.rationale})")
        return "\n".join(lines)
