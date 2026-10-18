"""The benchmark's machine-readable record, which the Benchmark workflow uploads.

The numbers are deliberately not tested: on a shared runner any threshold is a
flaky check, which is why nothing in CI gates on time. What is tested is what a
later comparison depends on — every case is present, the environment it ran in
is recorded, and the summary and the printed table come from the same run.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).parent.parent
RUNTIME = ROOT / "benchmarks" / "runtime.py"
CASES = [
    "f-string",
    "gettext(str).format",
    "compiled.render",
    "compile_template",
    "tr (1 field)",
    "tr (2 fields)",
    "Translator (1 field)",
    "ngettext (1 field)",
]


def _load_runtime() -> Any:
    spec = importlib.util.spec_from_file_location("benchmark_runtime", RUNTIME)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # dataclass() resolves annotations through sys.modules, so the module has to
    # be registered before it executes.
    sys.modules["benchmark_runtime"] = module
    spec.loader.exec_module(module)
    return module


def test_the_record_carries_every_case_and_its_environment() -> None:
    runtime = _load_runtime()
    document = runtime.record(runtime.run_benchmarks(number=10, repeat=3), number=10, repeat=3)

    assert [case["name"] for case in document["results"]] == CASES
    for case in document["results"]:
        assert len(case["samples_ns"]) == 3
        assert min(case["samples_ns"]) <= case["median_ns"] <= max(case["samples_ns"])
    assert document["settings"]["number"] == 10
    assert document["settings"]["repeat"] == 3
    assert document["python"]["version"] == platform.python_version()
    assert document["python"]["implementation"] == sys.implementation.name
    assert document["machine"]["architecture"] == platform.machine()
    if (ROOT / ".git").exists():
        assert re.fullmatch(r"[0-9a-f]{40}", document["commit"]["sha"])
    # The record is written with json.dumps and read back by whoever compares
    # two runs, so it has to survive the round trip unchanged.
    assert json.loads(json.dumps(document)) == document


def test_the_summary_tables_every_case_against_the_f_string() -> None:
    runtime = _load_runtime()
    document = runtime.record(runtime.run_benchmarks(number=10, repeat=3), number=10, repeat=3)

    rows = [line for line in runtime.markdown(document).splitlines() if line.startswith("| ")]
    header, rule, *cases = rows
    assert header.startswith("| Case |")
    assert rule.startswith("| --- |")
    assert [row.split(" | ")[0].removeprefix("| ") for row in cases] == CASES
    assert cases[0].endswith("| 1.00 |")


def test_the_command_line_keeps_its_table_and_appends_the_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    runtime = _load_runtime()
    quick = runtime.run_benchmarks(number=10, repeat=3)
    monkeypatch.setattr(runtime, "run_benchmarks", lambda: quick)
    record = tmp_path / "benchmark.json"
    # $GITHUB_STEP_SUMMARY may already hold what earlier steps wrote.
    summary = tmp_path / "summary.md"
    summary.write_text("written by an earlier step\n", encoding="utf-8")

    runtime.main(["--json", str(record), "--markdown", str(summary)])

    printed = capsys.readouterr().out.splitlines()
    assert printed[0] == f"Python {platform.python_version()} ({sys.implementation.name})"
    assert printed[3:] == [f"{result.name:24} {result.median:10.1f} ns/op" for result in quick]
    written = json.loads(record.read_text(encoding="utf-8"))
    assert [case["name"] for case in written["results"]] == CASES
    assert summary.read_text(encoding="utf-8").startswith(
        "written by an earlier step\n### Runtime microbenchmarks\n"
    )
