"""Structured diagnostic findings, stable across CLI and JSON output."""
from dataclasses import dataclass, asdict
from typing import Literal

Severity = Literal["critical", "high", "medium", "low", "info"]

@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    title: str
    detail: str
    remediation: str
    line: int
    evidence: str = ""
    confidence: str = "review"
    category: str = "general"

    def to_dict(self) -> dict:
        return asdict(self)


def summarize(findings: list[Finding]) -> dict:
    counts = {x: 0 for x in ("critical", "high", "medium", "low", "info")}
    for item in findings:
        counts[item.severity] += 1
    return counts
