import re
from pathlib import Path

from oblak.verifier.reports import Finding, VerificationReport

PATTERNS = {
    "shell-command": re.compile(r"os\.system|popen\(|subprocess\.", re.I),
    "secret-literal": re.compile(r"(api[_-]?key|password|secret)\s*=\s*['\"][^'\"]+['\"]", re.I),
    "network-access": re.compile(r"requests\.|urllib\.|httpx\.|socket\.", re.I),
}


class RegexAnalyzer:
    def analyze(self, source_dir: Path) -> VerificationReport:
        report = VerificationReport()
        for file_path in source_dir.rglob("*.py"):
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            relative = str(file_path.relative_to(source_dir))
            for line_no, line in enumerate(text.splitlines(), start=1):
                for rule_id, pattern in PATTERNS.items():
                    if pattern.search(line):
                        severity = "medium" if rule_id == "secret-literal" else "high"
                        report.add(Finding(rule_id, severity, f"Suspicious pattern: {rule_id}", relative, line_no))
        return report
