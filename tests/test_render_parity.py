"""Drift guard pinning the hand-synced copies of the render tail to one behavior.

core.py keeps several copies of the render tail for speed: the one inlined into
gettext(), _render_pattern, _render_with_values, and _render_plural_pattern.
Fixing one copy and forgetting another is drift that per-API tests can miss
(mutation testing proved it), so every path's output is compared here.
"""

from __future__ import annotations

from typing import Any

import pytest

from gettext_tstrings import compile_template, ngettext, pgettext, tr


class Stub:
    # Implements only the public Protocol (gettext_tstrings.Translations).
    # Subclassing gettext.NullTranslations would turn the rename of typeshed's
    # declared msgid1/msgid2 parameter names into an LSP violation (making them
    # positional-only does not fix it). Users implement the Protocol, so
    # satisfying it directly is the faithful stub.
    def __init__(
        self,
        messages: dict[str, str] | None = None,
        plurals: dict[tuple[str, str], tuple[str, str]] | None = None,
        contexts: dict[tuple[str, str], str] | None = None,
    ) -> None:
        self.messages = messages or {}
        self.plurals = plurals or {}
        self.contexts = contexts or {}

    def gettext(self, message: str, /) -> str:
        return self.messages.get(message, message)

    def ngettext(self, singular: str, plural: str, n: int, /) -> str:
        translated = self.plurals.get((singular, plural))
        if translated is None:
            return singular if n == 1 else plural
        return translated[0] if n == 1 else translated[1]

    def pgettext(self, context: str, message: str, /) -> str:
        return self.contexts.get((context, message), message)

    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str:
        return singular if n == 1 else plural


class Formatted:
    """Value whose ``__format__`` differs from ``__str__``, exposing a misapplied str shortcut."""

    def __format__(self, format_spec: str) -> str:
        return f"<F:{format_spec}>"

    def __str__(self) -> str:
        return "<S>"


def _all_paths_one_field(pattern: str, a: Any) -> dict[str, str]:
    """Render a one-field source through every render path."""
    return {
        "gettext": tr(t"{a}", translations=Stub(messages={"{a}": pattern})),
        "pgettext": pgettext("k", t"{a}", translations=Stub(contexts={("k", "{a}"): pattern})),
        "compiled": compile_template(t"{a}").render(pattern),
        "ngettext(n=1)": ngettext(
            t"{a}",
            t"{a}!",
            1,
            translations=Stub(plurals={("{a}", "{a}!"): (pattern, pattern)}),
        ),
        "ngettext(n=2)": ngettext(
            t"{a}",
            t"{a}!",
            2,
            translations=Stub(plurals={("{a}", "{a}!"): (pattern, pattern)}),
        ),
    }


def _all_paths_two_fields(pattern: str, a: Any, b: Any) -> dict[str, str]:
    """Render a two-field source through every render path."""
    return {
        "gettext": tr(t"{a} {b}", translations=Stub(messages={"{a} {b}": pattern})),
        "pgettext": pgettext(
            "k",
            t"{a} {b}",
            translations=Stub(contexts={("k", "{a} {b}"): pattern}),
        ),
        "compiled": compile_template(t"{a} {b}").render(pattern),
        "ngettext(n=1)": ngettext(
            t"{a} {b}",
            t"{a} {b}!",
            1,
            translations=Stub(plurals={("{a} {b}", "{a} {b}!"): (pattern, pattern)}),
        ),
        "ngettext(n=2)": ngettext(
            t"{a} {b}",
            t"{a} {b}!",
            2,
            translations=Stub(plurals={("{a} {b}", "{a} {b}!"): (pattern, pattern)}),
        ),
    }


@pytest.mark.parametrize("value", ["Ada", 7, Formatted()], ids=["str", "int", "custom"])
@pytest.mark.parametrize(
    "pattern",
    ["{a}", "p {a} s", "p {a} {a} s"],
    ids=["bare", "prefix-suffix", "repeat"],
)
def test_one_field_render_paths_agree(pattern: str, value: Any) -> None:
    # The expected value applies SPEC's rule naively: a plain field is format(value, "").
    expected = pattern.replace("{a}", format(value, ""))

    results = _all_paths_one_field(pattern, value)

    assert results == dict.fromkeys(results, expected)


@pytest.mark.parametrize(
    ("a", "b"),
    [("Ada", 7), (7, Formatted()), (Formatted(), "Ada")],
    ids=["str-int", "int-custom", "custom-str"],
)
@pytest.mark.parametrize(
    "pattern",
    ["{b} / {a}", "p {a} m {b} s", "{a} {a} {b}"],
    ids=["reorder", "pair-segments", "repeat-general"],
)
def test_two_field_render_paths_agree(pattern: str, a: Any, b: Any) -> None:
    expected = pattern.replace("{a}", format(a, "")).replace("{b}", format(b, ""))

    results = _all_paths_two_fields(pattern, a, b)

    assert results == dict.fromkeys(results, expected)
