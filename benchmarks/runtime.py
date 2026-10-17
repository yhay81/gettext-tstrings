"""Reproducible microbenchmarks for the runtime hot path.

Run from the repository root:

    uv run python benchmarks/runtime.py
    uv run python benchmarks/runtime.py --json benchmark.json

The table printed first is the same either way. benchmarks/README.md explains
the JSON record and how to compare two runs fairly.
"""

from __future__ import annotations

import argparse
import gettext
import json
import os
import platform
import statistics
import subprocess
import sys
import sysconfig
import timeit
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

from gettext_tstrings import Translator, compile_template, ntr, tr

NUMBER = 100_000
REPEAT = 7
# Bumped whenever a field changes meaning, so that old records stay readable.
SCHEMA = 1


@dataclass(frozen=True, slots=True)
class Result:
    name: str
    statement: str
    # Nanoseconds per operation, one sample per repeat.
    samples: tuple[float, ...]

    @property
    def median(self) -> float:
        return statistics.median(self.samples)


class Commit(TypedDict):
    sha: str | None
    # Whether tracked files differed from the commit; None outside a checkout.
    dirty: bool | None


class Interpreter(TypedDict):
    version: str
    implementation: str
    free_threaded: bool
    compiler: str


class Machine(TypedDict):
    system: str
    release: str
    architecture: str
    cpu: str | None
    cpu_count: int | None
    # "ubuntu24 20261012.1" on a GitHub-hosted runner, None anywhere else.
    runner_image: str | None


class Settings(TypedDict):
    number: int
    repeat: int
    timer: str
    statistic: str
    warm_up: str


class Case(TypedDict):
    name: str
    statement: str
    median_ns: float
    samples_ns: list[float]


class Record(TypedDict):
    schema: int
    recorded_at: str
    commit: Commit
    python: Interpreter
    machine: Machine
    settings: Settings
    results: list[Case]


def run_benchmarks(number: int = NUMBER, repeat: int = REPEAT) -> list[Result]:
    """Time representative cases: ``repeat`` samples of ``number`` calls each."""
    translations = gettext.NullTranslations()
    bound = Translator(translations)
    name = "Ada"
    category = "News"
    target = "Archive"
    n = 3
    template = t"Hello {name}"
    compiled = compile_template(template)

    # Warm the bounded structural and translation-pattern caches.
    tr(t"Hello {name}", translations=translations)
    tr(
        t"Category {category} moved to {target}",
        translations=translations,
    )
    ntr(t"One file", t"{n} files", n, translations=translations)

    namespace = locals() | {"compile_template": compile_template, "tr": tr, "ntr": ntr}
    statements = {
        "f-string": "f'Hello {name}'",
        "gettext(str).format": ("translations.gettext('Hello {name}').format(name=name)"),
        "compiled.render": "compiled.render(compiled.msgid)",
        "compile_template": "compile_template(template)",
        "tr (1 field)": "tr(t'Hello {name}', translations=translations)",
        "tr (2 fields)": (
            "tr(t'Category {category} moved to {target}', translations=translations)"
        ),
        "Translator (1 field)": "bound(t'Hello {name}')",
        "ngettext (1 field)": "ntr(t'One file', t'{n} files', n, translations=translations)",
    }
    results = []
    for label, statement in statements.items():
        samples = timeit.repeat(
            statement,
            globals=namespace,
            number=number,
            repeat=repeat,
        )
        results.append(Result(label, statement, tuple(s / number * 1e9 for s in samples)))
    return results


def _run(*command: str) -> str | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip()
    except OSError, subprocess.CalledProcessError:
        return None


def _cpu() -> str | None:
    # Hosted runners of one image still differ in CPU model, and the model moves
    # the numbers more than most changes to this package do.
    if sys.platform == "linux":
        try:
            lines = Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines()
        except OSError:
            return None
        models = (line.split(":", 1)[1].strip() for line in lines if line.startswith("model name"))
        return next(models, None)
    if sys.platform == "darwin":
        return _run("sysctl", "-n", "machdep.cpu.brand_string")
    return platform.processor() or None


def record(results: Sequence[Result], number: int = NUMBER, repeat: int = REPEAT) -> Record:
    """The results, with what is needed to tell whether two of them compare."""
    status = _run("git", "status", "--porcelain", "--untracked-files=no")
    # GitHub sets these two in mixed case, and Linux environment names are
    # case-sensitive, so the capitalized spelling would never be found.
    image = os.environ.get("ImageOS")  # noqa: SIM112
    image_version = os.environ.get("ImageVersion", "?")  # noqa: SIM112
    return {
        "schema": SCHEMA,
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": {
            "sha": _run("git", "rev-parse", "HEAD") or os.environ.get("GITHUB_SHA"),
            "dirty": None if status is None else bool(status),
        },
        "python": {
            "version": platform.python_version(),
            "implementation": sys.implementation.name,
            "free_threaded": bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
            "compiler": platform.python_compiler().strip(),
        },
        "machine": {
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "cpu": _cpu(),
            "cpu_count": os.cpu_count(),
            "runner_image": f"{image} {image_version}" if image else None,
        },
        "settings": {
            "number": number,
            "repeat": repeat,
            "timer": "time.perf_counter",
            "statistic": "median of the repeats, in nanoseconds per call",
            "warm_up": "each cached path is called once before timing, and timeit "
            "turns the garbage collector off while it times",
        },
        "results": [
            {
                "name": result.name,
                "statement": result.statement,
                "median_ns": round(result.median, 2),
                "samples_ns": [round(sample, 2) for sample in result.samples],
            }
            for result in results
        ],
    }


def markdown(document: Record) -> str:
    """A compact table of one record, for a job summary."""
    python, machine, settings = document["python"], document["machine"], document["settings"]
    sha = (document["commit"]["sha"] or "unknown")[:12]
    # f-string never touches this package, so the ratio to it says how much of
    # a number is the machine.
    baseline = next(case["median_ns"] for case in document["results"] if case["name"] == "f-string")
    where = [
        f"`{sha}`",
        f"{python['implementation']} {python['version']}",
        f"{machine['system']} {machine['architecture']}",
        machine["cpu"],
        machine["runner_image"],
    ]
    lines = [
        "### Runtime microbenchmarks",
        "",
        " · ".join(part for part in where if part),
        "",
        "| Case | Median ns/op | Fastest | Slowest | vs f-string |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        f"| {case['name']} | {case['median_ns']:.1f} | {min(case['samples_ns']):.1f} "
        f"| {max(case['samples_ns']):.1f} | {case['median_ns'] / baseline:.2f} |"
        for case in document["results"]
    )
    lines += [
        "",
        f"Median of {settings['repeat']} repeats of {settings['number']:,} calls each. "
        "Compare runs as benchmarks/README.md describes.",
        "",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Time the runtime hot path.")
    parser.add_argument(
        "--json",
        type=Path,
        metavar="FILE",
        help="also write the results, and the environment they came from, as JSON",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        metavar="FILE",
        help="also append a Markdown table, for example to $GITHUB_STEP_SUMMARY",
    )
    args = parser.parse_args(argv)

    results = run_benchmarks()
    print(f"Python {platform.python_version()} ({sys.implementation.name})")
    print(platform.platform())
    print()
    for result in results:
        print(f"{result.name:24} {result.median:10.1f} ns/op")

    if args.json is None and args.markdown is None:
        return
    document = record(results)
    if args.json is not None:
        args.json.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", "utf-8")
    if args.markdown is not None:
        with args.markdown.open("a", encoding="utf-8") as summary:
            summary.write(markdown(document))


if __name__ == "__main__":
    main()
