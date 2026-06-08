from pathlib import Path

from oblak.verifier.code_verifier import CodeVerifier


def test_accepts_benign_handler(tmp_path: Path):
    (tmp_path / "handler.py").write_text("def handler(event, context):\n    return {'ok': True}\n", encoding="utf-8")
    report = CodeVerifier().verify(tmp_path)
    assert report.accepted is True


def test_rejects_eval(tmp_path: Path):
    (tmp_path / "handler.py").write_text("def handler(event, context):\n    return eval('1+1')\n", encoding="utf-8")
    report = CodeVerifier().verify(tmp_path)
    assert report.accepted is False
    assert any(f.rule_id == "dangerous-call" for f in report.findings)


def test_rejects_missing_handler(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    report = CodeVerifier().verify(tmp_path)
    assert report.accepted is False
