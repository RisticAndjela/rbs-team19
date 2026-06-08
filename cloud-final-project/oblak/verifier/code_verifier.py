from pathlib import Path

from oblak.core.config import get_settings
from oblak.verifier.clamav import ClamAvScanner
from oblak.verifier.llm import LlmAnalyzer
from oblak.verifier.regex_analyzer import RegexAnalyzer
from oblak.verifier.reports import VerificationReport
from oblak.verifier.static_analyzer import StaticAnalyzer


class CodeVerifier:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.analyzers = [StaticAnalyzer(), RegexAnalyzer(), ClamAvScanner(), LlmAnalyzer()]

    def verify(self, source_dir: Path) -> VerificationReport:
        final = VerificationReport()
        self._validate_requirements(source_dir, final)
        for analyzer in self.analyzers:
            partial = analyzer.analyze(source_dir)
            for finding in partial.findings:
                final.add(finding)
        return final

    def _validate_requirements(self, source_dir: Path, report: VerificationReport) -> None:
        requirements = source_dir / "requirements.txt"
        if not requirements.exists():
            return
        lines = [line for line in requirements.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) > self.settings.max_requirements_lines:
            from oblak.verifier.reports import Finding

            report.add(Finding("too-many-dependencies", "high", "requirements.txt is too large"))
