import subprocess
from pathlib import Path

from oblak.core.config import get_settings
from oblak.verifier.reports import Finding, VerificationReport


class ClamAvScanner:
    def analyze(self, source_dir: Path) -> VerificationReport:
        settings = get_settings()
        report = VerificationReport()
        if not settings.enable_clamav:
            report.add(Finding("clamav-disabled", "info", "ClamAV scan skipped by configuration"))
            return report
        completed = subprocess.run(
            [settings.clamav_command, "-r", str(source_dir)],
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        if completed.returncode == 1:
            report.add(Finding("malware-detected", "critical", completed.stdout.strip() or "Malware detected"))
        elif completed.returncode > 1:
            report.add(Finding("clamav-error", "medium", completed.stderr.strip() or "ClamAV failed"))
        else:
            report.add(Finding("clamav-clean", "info", "ClamAV scan passed"))
        return report
