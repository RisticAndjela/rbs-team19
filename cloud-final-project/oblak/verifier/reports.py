from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["info", "low", "medium", "high", "critical"]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    file: str | None = None
    line: int | None = None


@dataclass
class VerificationReport:
    accepted: bool = True
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)
        if finding.severity in {"high", "critical"}:
            self.accepted = False

    def to_dict(self) -> dict:
        return {
            "accepted": self.accepted,
            "findings": [finding.__dict__ for finding in self.findings],
        }
