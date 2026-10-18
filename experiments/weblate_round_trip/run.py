# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "babel==2.18.0",
#   "gettext-tstrings",
# ]
#
# [tool.uv.sources]
# gettext-tstrings = { path = "../..", editable = true }
# ///
"""Round-trip this package's catalogs through Weblate, and report what survived.

Run from the repository root:

    uv run experiments/weblate_round_trip/run.py

It needs uv and a PostgreSQL 13+ server installation with the contrib
extensions (pg_trgm, btree_gin); set PG_BIN to its bin directory if it is not
where weblate_side.py looks. Nothing is installed: Weblate runs in an
environment of its own and against a throwaway cluster.

The steps are #15's: extract a template from messages.py with the package's
Babel extractor, import it into a Weblate gettext component, enter broken and
valid translations there and record what Weblate's checks say, export, compare
the export with the template, compile it with pybabel (the package's checker
included) and GNU msgfmt, and render messages.py's own calls against it. The
template and both exports are kept in catalogs/. The exit status is non-zero
when any expectation fails, including the two places Weblate's check and this
package's rules disagree, so that the day either changes is a day the
documentation needs to.
"""

from __future__ import annotations

import gettext
import json
import logging
import platform
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import Any

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po

from gettext_tstrings import use_translations

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
CATALOGS = HERE / "catalogs"
LANGUAGE = "pl"
COMMAND = "uv run experiments/weblate_round_trip/run.py"
VALUES = {
    "name": "Ada",
    "item": "raport.pdf",
    "folder": "Archiwum",
    "player": "Ada",
    "opponent": "Bob",
}
# What each call in messages.py must render once Weblate's export is compiled,
# written out independently of the catalog. The plural form depends on n.
PLURALS = {1: "1 plik", 2: "2 pliki", 5: "5 plików"}
EXPECTED = {
    "singular": "Witaj ponownie, Ada",
    "context: button": "Otwórz",
    "context: state": "Otwarte",
    "reordered": "Do folderu Archiwum przeniesiono raport.pdf",
    "repeated in the source": "Ada pokonuje gracza Bob i Ada przechodzi dalej",
    "repeated in the translation": "Cześć, Ada! Miło cię znowu widzieć, Ada",
}


class Report:
    def __init__(self) -> None:
        self.failures = 0

    def check(self, label: str, failures: list[str], summary: str) -> None:
        if failures:
            self.failures += 1
            print(f"FAIL  {label}")
            for failure in failures[:8]:
                print(f"        {failure}")
        else:
            print(f"ok    {label}: {summary}")


def pybabel(*args: str) -> subprocess.CompletedProcess[str]:
    # The console script, not `python -m babel.messages.frontend`: that module
    # discards main()'s return value, so it exits 0 even when the checker found
    # errors, and the exit status is what this experiment reads.
    return subprocess.run(
        [Path(sys.executable).with_name("pybabel"), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def relative(path: Path) -> str:
    # Relative to the repository, so that the messages quoted in the README
    # carry no machine's home directory.
    return str(path.relative_to(ROOT))


def read(path: Path) -> Catalog:
    with path.open("rb") as file:
        return read_po(file, locale=LANGUAGE if path.suffix == ".po" else None)


def extract(work: Path) -> None:
    template = CATALOGS / "messages.pot"
    result = pybabel(
        "extract", "--mapping-file", "babel.cfg", "--add-comments", "Translators:",
        "--add-location", "file", "--project", "gettext-tstrings Weblate experiment",
        "--copyright-holder", "Yusuke Hayashi", "--output-file", str(template),
        str((HERE / "messages.py").relative_to(ROOT)),
    )  # fmt: skip
    result.check_returncode()
    target = work / "in" / "locale" / LANGUAGE / "LC_MESSAGES"
    target.mkdir(parents=True)
    pybabel("init", "-i", str(template), "-o", str(target / "messages.po"), "-l", LANGUAGE)
    shutil.copyfile(template, work / "in" / "messages.pot")


def through_weblate(work: Path) -> dict[str, Any]:
    subprocess.run(
        [
            "uv",
            "run",
            "--script",
            str(HERE / "weblate_side.py"),
            str(work / "in"),
            str(work / "out"),
        ],
        check=True,
    )
    shutil.copyfile(work / "out" / f"{LANGUAGE}.po", CATALOGS / f"{LANGUAGE}.po")
    shutil.copyfile(
        work / "out" / f"{LANGUAGE}.unchecked.po", CATALOGS / f"{LANGUAGE}.unchecked.po"
    )
    results = json.loads((work / "out" / "results.json").read_text(encoding="utf-8"))
    (CATALOGS / "weblate-results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return results


def names(checks: list[dict[str, str]]) -> list[str]:
    return [f"{check['check']}: {check['says']}" for check in checks]


def weblate_checks(results: dict[str, Any], report: Report) -> None:
    broken = {entry["case"]: entry["checks"] for entry in results["broken"]}
    valid = {entry["case"]: entry["checks"] for entry in results["valid"]}
    caught = ["renamed placeholder", "conversion added", "second plural form drops {n}"]
    failures = [f"{case}: no check fired" for case in caught if not broken[case]]
    # Whatever fires must be the format check itself, not something incidental.
    failures += [
        f"{case}: {names(checks)}"
        for case, checks in broken.items()
        if any(c["check"] != "python_brace_format" for c in checks)
    ]
    report.check(
        "Weblate's Python brace format check on broken translations",
        failures,
        "it caught a renamed placeholder, an added conversion, and a plural form that drops {n}",
    )
    first_form = broken["first plural form drops {n}"]
    report.check(
        "DIFFERENCE, a plural form used for one number only may drop {n} in Weblate",
        [f"Weblate now says: {names(first_form)}"] if first_form else [],
        "Polish 'plik' for n == 1, without {n}, raised no check; this package requires {n} "
        "in every form",
    )
    quiet = [case for case in valid if case != "repeated in the translation"]
    failures = [f"{case}: {names(valid[case])}" for case in quiet if valid[case]]
    report.check(
        "valid translations, reordered and repeated as in the source",
        failures,
        f"no check fired on {len(quiet)} of them",
    )
    repeated = valid["repeated in the translation"]
    report.check(
        "DIFFERENCE, repeating a placeholder more often than the source does",
        []
        if [c["check"] for c in repeated] == ["python_brace_format"]
        and "extra: {name}" in repeated[0]["says"]
        else [f"Weblate now says: {names(repeated)}"],
        "Weblate flagged the second {name} as extra; this package allows a value to repeat",
    )


def survival(report: Report) -> None:
    template, exported = read(CATALOGS / "messages.pot"), read(CATALOGS / f"{LANGUAGE}.po")
    failures = []
    for message in template:
        if not message.id:
            continue
        key = (message.id, message.context)
        out = exported.get(*key)
        if out is None:
            failures.append(f"{key} is gone")
            continue
        fields = ("auto_comments", "user_comments", "flags", "locations", "context")
        failures.extend(
            f"{key} {field}: {getattr(message, field)} -> {getattr(out, field)}"
            for field in fields
            if getattr(out, field) != getattr(message, field)
        )
        forms = len(out.string) if isinstance(out.string, tuple) else 1
        if message.pluralizable and forms != 3:
            failures.append(f"{key} has {forms} forms, not 3")
    count = sum(1 for message in template if message.id)
    report.check(
        "what the export kept",
        failures,
        f"all {count} messages came back with their marker and translator comments, flags, "
        "msgctxt, locations, and three Polish plural forms",
    )

    # Weblate rewrites the Plural-Forms expression; it must still mean the same.
    ours = gettext.c2py(template_plural())
    theirs = gettext.c2py(exported.plural_expr)
    mismatched = [n for n in range(1001) if ours(n) != theirs(n)]
    report.check(
        "the rewritten Plural-Forms header",
        [f"n={n}: {ours(n)} vs {theirs(n)}" for n in mismatched],
        f"Weblate wrote '{exported.plural_expr}', which picks the same form as Babel's for "
        "n = 0..1000",
    )


def template_plural() -> str:
    return Catalog(locale=LANGUAGE).plural_expr


def compile_with_babel(work: Path, report: Report) -> tuple[Path, Path]:
    valid, unchecked = work / f"{LANGUAGE}.mo", work / "unchecked.mo"
    ok = pybabel(
        "compile", "-i", relative(CATALOGS / f"{LANGUAGE}.po"), "-o", str(valid), "-l", LANGUAGE
    )
    broken = pybabel(
        "compile", "-i", relative(CATALOGS / f"{LANGUAGE}.unchecked.po"),
        "-o", str(unchecked), "-l", LANGUAGE,
    )  # fmt: skip
    errors = [line for line in broken.stderr.splitlines() if line.startswith("error:")]
    expected = [
        "{name} is missing; {imie} is not in the source message",
        "msgstr[0]: translation does not match the source placeholders: {n} is missing",
        "placeholder {name} adds formatting",
    ]
    failures = [f"the valid export: {ok.stderr.strip()}"] if ok.returncode else []
    if broken.returncode != 1 or len(errors) != len(expected):
        failures.append(f"the unchecked export: exit {broken.returncode}, {errors}")
    failures += [
        f"no error says {text!r}" for text in expected if not any(text in e for e in errors)
    ]
    report.check(
        "pybabel compile, with this package's checker",
        failures,
        "the valid export compiled cleanly; the unchecked one exited 1 with an error for each "
        "of its three broken translations, the plural form Weblate let through included",
    )
    for line in errors:
        print(f"        {line}")
    return valid, unchecked


def check_with_msgfmt(report: Report) -> None:
    msgfmt = shutil.which("msgfmt")
    if msgfmt is None:
        print("skip  GNU msgfmt --check-format: msgfmt is not installed")
        return
    runs = [
        subprocess.run(
            [msgfmt, "--check-format", "-o", "/dev/null", relative(CATALOGS / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        for name in (f"{LANGUAGE}.po", f"{LANGUAGE}.unchecked.po")
    ]
    valid, broken = runs
    failures = [f"the valid export: {valid.stderr.strip()}"] if valid.returncode else []
    said = broken.stderr
    if not (broken.returncode == 1 and "found 2 fatal errors" in said and "'imie'" in said
            and "not a valid Python brace format string" in said):  # fmt: skip
        failures.append(f"the unchecked export: exit {broken.returncode}: {said.strip()}")
    report.check(
        "GNU msgfmt --check-format",
        failures,
        "the valid export passed; the unchecked one failed on the renamed placeholder and the "
        "conversion, and let the plural form without {n} through",
    )
    for line in said.strip().splitlines():
        print(f"        {line}")


def render(valid: Path, unchecked: Path, report: Report) -> None:
    sys.path.insert(0, str(HERE))
    from messages import messages

    # A broken translation renders the source text and logs a warning rather
    # than raising, so the warnings are the evidence that nothing fell back.
    warnings = Collect()
    logging.getLogger("gettext_tstrings").addHandler(warnings)

    def rendering(compiled: Path) -> dict[int, dict[str, str]]:
        with compiled.open("rb") as file:
            catalog = gettext.GNUTranslations(file)
        with use_translations(catalog):
            return {n: messages(n=n, **VALUES) for n in PLURALS}

    failures = []
    for n, rendered in rendering(valid).items():
        want = EXPECTED | {"plural": PLURALS[n]}
        failures += [
            f"n={n} {key}: {rendered[key]!r}" for key in want if rendered[key] != want[key]
        ]
    failures += [f"warning: {message}" for message in warnings.messages]
    report.check(
        "rendering messages.py against Weblate's export",
        failures,
        f"all {len(EXPECTED) + 1} calls rendered in Polish for n = 1, 2 and 5, with no warning",
    )

    # What a translator who ignored Weblate's checks would ship. Nothing may
    # raise: each broken message renders its source text, and says so once.
    # The messages translated only in the valid pass are still untranslated.
    warnings.messages.clear()
    fallback = {
        "singular": "Welcome back, Ada",
        "context: button": "Open",
        "context: state": "Open",
        "reordered": "Moved raport.pdf to Archiwum",
        "repeated in the source": "Ada beat Bob, and Ada moves on",
        "repeated in the translation": "Hello Ada",
    }
    plurals = {1: "1 file", 2: "2 pliki", 5: "5 plików"}
    failures = []
    for n, rendered in rendering(unchecked).items():
        want = fallback | {"plural": plurals[n]}
        failures += [
            f"n={n} {key}: {rendered[key]!r}" for key in want if rendered[key] != want[key]
        ]
    sources = ["'Welcome back, {name}'", "'{n} file'", "'Hello {name}'"]
    if len(warnings.messages) != 3 or not all(
        source in message and "using source text" in message
        for source, message in zip(sources, warnings.messages, strict=False)
    ):
        failures.append(f"warnings: {warnings.messages}")
    report.check(
        "rendering the unchecked export",
        failures,
        "the three broken messages rendered their source text with one warning each, and the "
        "Polish plural forms that are valid still rendered for n = 2 and 5",
    )


class Collect(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


def versions(results: dict[str, Any]) -> None:
    print(f"{'command':18} {COMMAND}")
    print(f"{'python':18} {platform.python_version()} ({sys.implementation.name})")
    for package in ("gettext-tstrings", "babel"):
        print(f"{package:18} {version(package)}")
    for package, value in results["versions"].items():
        label = "weblate's python" if package == "python" else package
        print(f"{label:18} {value}")
    msgfmt = shutil.which("msgfmt")
    if msgfmt is not None:
        found = subprocess.run([msgfmt, "--version"], capture_output=True, text=True, check=False)
        print(f"{'msgfmt':18} {found.stdout.splitlines()[0]}")
    component = results["component"]
    print(f"{'component':18} " + ", ".join(f"{k}={v!r}" for k, v in component.items()))
    print()


def main() -> int:
    CATALOGS.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="weblate-round-trip-") as tmp:
        work = Path(tmp)
        extract(work)
        results = through_weblate(work)
        versions(results)
        report = Report()
        weblate_checks(results, report)
        survival(report)
        valid, unchecked = compile_with_babel(work, report)
        check_with_msgfmt(report)
        render(valid, unchecked, report)
    print()
    print("all expectations held" if not report.failures else f"{report.failures} failed")
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
