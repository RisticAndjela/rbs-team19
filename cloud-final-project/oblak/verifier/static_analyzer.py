import ast
from pathlib import Path

from oblak.verifier.reports import Finding, VerificationReport

DANGEROUS_IMPORTS = {"socket", "subprocess", "multiprocessing", "ctypes", "resource"}
DANGEROUS_CALLS = {"eval", "exec", "compile", "__import__", "open"}


class StaticAnalyzer:
    def analyze(self, source_dir: Path) -> VerificationReport:
        report = VerificationReport()
        handler = source_dir / "handler.py"
        if not handler.exists():
            report.add(Finding("missing-handler", "critical", "handler.py is required"))
            return report

        for python_file in source_dir.rglob("*.py"):
            self._analyze_file(python_file, source_dir, report)
        return report

    def _analyze_file(self, file_path: Path, root: Path, report: VerificationReport) -> None:
        relative = str(file_path.relative_to(root))
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            report.add(Finding("syntax-error", "critical", str(exc), relative, exc.lineno))
            return

        if file_path.name == "handler.py" and not self._has_handler(tree):
            report.add(Finding("missing-handler-callable", "critical", "handler(event, context) is required", relative))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_import(alias.name, report, relative, node.lineno)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self._check_import(node.module, report, relative, node.lineno)
            elif isinstance(node, ast.Call):
                name = self._call_name(node)
                if name in DANGEROUS_CALLS:
                    report.add(Finding("dangerous-call", "high", f"Dangerous call: {name}", relative, node.lineno))

    def _check_import(self, module: str, report: VerificationReport, file: str, line: int) -> None:
        root_module = module.split(".", 1)[0]
        if root_module in DANGEROUS_IMPORTS:
            report.add(Finding("dangerous-import", "high", f"Dangerous import: {module}", file, line))

    def _call_name(self, node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None

    def _has_handler(self, tree: ast.AST) -> bool:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "handler" and len(node.args.args) >= 2:
                return True
        return False
