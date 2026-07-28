"""Run the published spec v1 conformance suite against this implementation.

``conformance/v1.json`` is the machine-readable form of SPEC.md: another
extractor, IDE, type checker, or future ``pygettext`` can run the same cases to
show it targets the same convention. Running it here keeps the reference
implementation and the published contract from drifting apart.
"""

from __future__ import annotations

import gettext
import json
from pathlib import Path
from string.templatelib import Interpolation, Template
from typing import Any

import pytest

from gettext_tstrings import compile_template, ntr, tr
from gettext_tstrings.errors import InvalidTemplateError, InvalidTranslationError

SUITE = json.loads((Path(__file__).parent.parent / "conformance" / "v1.json").read_text("utf-8"))

_ERRORS = {"template": InvalidTemplateError, "translation": InvalidTranslationError}


def _template(parts: list[Any]) -> Template:
    """Build a Template from the suite's part list, without evaluating source."""
    return Template(
        *(
            part
            if isinstance(part, str)
            else Interpolation(
                part["value"],
                part["expression"],
                part.get("conversion"),
                part.get("format_spec", ""),
            )
            for part in parts
        ),
    )


class _Catalog(gettext.NullTranslations):
    """Return one fixed pattern, standing in for a catalog lookup."""

    def __init__(self, pattern: str) -> None:
        super().__init__()
        self.pattern = pattern

    def gettext(self, message: str) -> str:
        return self.pattern

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        return self.pattern


def _ids(cases: list[dict[str, Any]]) -> list[str]:
    return [f"{case['spec']}: {case['name']}" for case in cases]


def test_the_suite_declares_the_spec_version_it_targets() -> None:
    assert SUITE["spec_version"] == 1


@pytest.mark.parametrize(
    "case",
    SUITE["msgid_derivation"],
    ids=_ids(SUITE["msgid_derivation"]),
)
def test_msgid_derivation(case: dict[str, Any]) -> None:
    source = _template(case["source"])

    if "error" in case:
        with pytest.raises(_ERRORS[case["error"]]):
            compile_template(source)
        return

    assert compile_template(source).msgid == case["msgid"]


@pytest.mark.parametrize(
    "case",
    SUITE["plural_msgid_derivation"],
    ids=_ids(SUITE["plural_msgid_derivation"]),
)
def test_plural_msgid_derivation(case: dict[str, Any]) -> None:
    singular = _template(case["singular"])
    plural = _template(case["plural"])

    if "error" in case:
        # Incompatible branch formatting is only detectable once the branches
        # are merged, which is what a plural call does.
        with pytest.raises(_ERRORS[case["error"]]):
            ntr(singular, plural, 1, translations=gettext.NullTranslations())
        return

    assert [compile_template(singular).msgid, compile_template(plural).msgid] == case["msgids"]


@pytest.mark.parametrize("case", SUITE["rendering"], ids=_ids(SUITE["rendering"]))
def test_rendering(case: dict[str, Any]) -> None:
    source = _template(case["source"])
    catalog = _Catalog(case["pattern"])

    if "error" in case:
        with pytest.raises(_ERRORS[case["error"]]):
            tr(source, translations=catalog, strict=True)
        return

    assert tr(source, translations=catalog, strict=True) == case["expected"]


@pytest.mark.parametrize(
    "case",
    SUITE["plural_rendering"],
    ids=_ids(SUITE["plural_rendering"]),
)
def test_plural_rendering(case: dict[str, Any]) -> None:
    singular = _template(case["singular"])
    plural = _template(case["plural"])
    catalog = _Catalog(case["pattern"])

    if "error" in case:
        with pytest.raises(_ERRORS[case["error"]]):
            ntr(singular, plural, case["n"], translations=catalog, strict=True)
        return

    assert ntr(singular, plural, case["n"], translations=catalog, strict=True) == case["expected"]
