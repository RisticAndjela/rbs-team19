from pathlib import Path

from oblak.core.config import get_settings
from oblak.verifier.reports import Finding, VerificationReport


class LlmAnalyzer:
    """Provider adapter. The default mock keeps the project runnable without paid APIs."""

    def analyze(self, source_dir: Path) -> VerificationReport:
        settings = get_settings()
        report = VerificationReport()
        if not settings.enable_llm_analysis:
            return report
        if settings.llm_provider != "mock":
            report.add(Finding("llm-adapter-open", "info", "Real LLM provider should be connected here"))
            return report
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")[:2000]
            for path in source_dir.rglob("*.py")
        ).lower()
        suspicious_terms = ["reverse shell", "exfiltrate", "keylogger", "crypto miner"]
        for term in suspicious_terms:
            if term in combined:
                report.add(Finding("llm-suspicious-intent", "high", f"Suspicious intent phrase: {term}"))
        report.add(Finding("llm-mock-complete", "info", "Mock LLM analysis completed"))
        return report
