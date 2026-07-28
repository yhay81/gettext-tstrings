from __future__ import annotations

import gettext
import logging
import re
from importlib.metadata import version
from types import SimpleNamespace
from typing import Any, cast

import pytest

from gettext_tstrings import (
    InvalidTemplateError,
    InvalidTranslationError,
    Translator,
    __version__,
    compile_template,
    ntr,
    tr,
    use_translations,
)
from gettext_tstrings import gettext as tgettext
from gettext_tstrings import ngettext as tngettext
from gettext_tstrings import npgettext as tnpgettext
from gettext_tstrings import pgettext as tpgettext


class StubTranslations:
    # Implement only the public Protocol (gettext_tstrings.Translations).
    # Subclassing gettext.NullTranslations would turn the rename of typeshed's
    # msgid1/msgid2 parameters into an LSP violation (positional-only does not
    # fix it). The Protocol is what users implement, so satisfy it directly.
    def __init__(
        self,
        messages: dict[str, str] | None = None,
        plurals: dict[tuple[str, str], tuple[str, str]] | None = None,
        contexts: dict[tuple[str, str], str] | None = None,
        context_plurals: dict[tuple[str, str, str], tuple[str, str]] | None = None,
    ) -> None:
        self.messages = messages or {}
        self.plurals = plurals or {}
        self.contexts = contexts or {}
        self.context_plurals = context_plurals or {}

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
        translated = self.context_plurals.get((context, singular, plural))
        if translated is None:
            return singular if n == 1 else plural
        return translated[0] if n == 1 else translated[1]


def test_version_matches_package_metadata() -> None:
    assert __version__ == version("gettext-tstrings")


def test_public_api_surface_is_pinned() -> None:
    # __all__ is the public contract. A name dropping out or appearing is a
    # breaking change for users, so pin the list explicitly.
    import gettext_tstrings

    assert sorted(gettext_tstrings.__all__) == [
        "CompiledTemplate",
        "InvalidTemplateError",
        "InvalidTranslationError",
        "LazyString",
        "TStringError",
        "Translations",
        "Translator",
        "compile_template",
        "get_translations",
        "gettext",
        "lazy_gettext",
        "lazy_pgettext",
        "ngettext",
        "npgettext",
        "ntr",
        "pgettext",
        "set_translations",
        "tr",
        "use_translations",
    ]
    assert all(hasattr(gettext_tstrings, name) for name in gettext_tstrings.__all__)


def test_identity_translation() -> None:
    name = "Ada"
    assert tr(t"Hello {name}", translations=gettext.NullTranslations()) == "Hello Ada"


def test_module_functions_use_global_gettext_fallbacks() -> None:
    name = "Ada"
    n = 2

    assert tgettext(t"Hello {name}") == "Hello Ada"
    assert tpgettext("greeting", t"Hello {name}") == "Hello Ada"
    assert tngettext(t"One file", t"{n} files", n) == "2 files"
    assert tnpgettext("inbox", t"One message", t"{n} messages", n) == "2 messages"


def test_constant_fast_paths() -> None:
    translations = gettext.NullTranslations()

    assert tr(t"Static", translations=translations) == "Static"
    assert ntr(t"One", t"Many", 2, translations=translations) == "Many"


def test_translation_can_reorder_placeholders() -> None:
    category = "News"
    target = "Archive"
    translations = StubTranslations(
        {
            'Category "{category}" moved to "{target}"': (
                "「{target}」へ「{category}」カテゴリを移動しました"
            ),
        },
    )

    result = tr(
        t'Category "{category}" moved to "{target}"',
        translations=translations,
    )

    assert result == "「Archive」へ「News」カテゴリを移動しました"


def test_formatting_and_conversion_stay_in_source() -> None:
    amount = 1234.5
    label = "total"
    translations = StubTranslations(
        {
            "Value {amount} ({label})": "{label}: {amount}",
        },
    )

    result = tr(t"Value {amount:,.2f} ({label!r})", translations=translations)

    assert result == "'total': 1,234.50"


def test_str_values_still_apply_the_source_format_spec() -> None:
    # A str value passes through the fast path (_Field.plain) of every render
    # route, skipping format(). If that breaks, format specs are silently
    # ignored across the whole API, so pin one case per route. The existing
    # format-spec tests all use a float or ``!r`` and miss this combination.
    name = "Ada"
    second = "Bo"
    third = "Cy"
    null = gettext.NullTranslations()

    assert tr(t"[{name:>5}]", translations=null) == "[  Ada]"
    assert tpgettext("nav", t"[{name:>5}]", translations=null) == "[  Ada]"
    assert compile_template(t"[{name:>5}]").render("[{name}]") == "[  Ada]"
    assert tngettext(t"[{name:>5}]", t"[{name:>5}]s", 1, translations=null) == "[  Ada]"
    assert tngettext(t"[{name:>5}]", t"[{name:>5}]s", 2, translations=null) == "[  Ada]s"
    assert tr(t"{name:>5}{second:>4}{third:>4}", translations=null) == "  Ada  Bo  Cy"


def test_literal_braces_round_trip() -> None:
    value = "on"
    compiled = compile_template(t"Config {{raw}} is {value}")

    assert compiled.msgid == "Config {{raw}} is {value}"
    assert compiled.render(compiled.msgid) == "Config {raw} is on"
    assert compiled.render("Literal {{name:}} {value}") == "Literal {name:} on"


def test_compiled_template_exposes_stable_placeholder_order() -> None:
    first = 1
    second = 2
    compiled = compile_template(t"{first}, {second}, {first}")

    assert compiled.placeholders == ("first", "second")
    assert compiled.msgid == "{first}, {second}, {first}"


def test_complex_interpolation_is_rejected() -> None:
    user = SimpleNamespace(name="Ada")

    with pytest.raises(InvalidTemplateError, match="simple variable names"):
        compile_template(t"Hello {user.name}")


def test_repeated_placeholder_must_keep_same_source_format() -> None:
    amount = 3.5

    with pytest.raises(InvalidTemplateError, match="different formatting"):
        compile_template(t"{amount:.1f} / {amount:.2f}")


@pytest.mark.parametrize(
    ("translation", "message"),
    [
        ("Hello", "is missing"),
        ("Hello {name} {extra}", "not in the source message"),
        ("Hello {name!r}", "adds formatting"),
        ("Hello { name }", "space inside the braces"),
        ("Hello {name }", "space inside the braces"),
        ("Hello {name:}", "adds formatting"),
        ("Hello {name.__class__}", "must be a plain name"),
        ("Hello {name", "invalid translation pattern"),
    ],
)
def test_invalid_translation_placeholders_are_rejected_in_strict_mode(
    translation: str,
    message: str,
) -> None:
    name = "Ada"
    translations = StubTranslations({"Hello {name}": translation})

    with pytest.raises(InvalidTranslationError, match=message):
        tr(t"Hello {name}", translations=translations, strict=True)


def test_confusable_placeholder_names_are_escaped_in_errors() -> None:
    name = "Ada"
    # A homoglyph name holding Cyrillic U+0430 is indistinguishable from ASCII
    # "name", so the error message shows it in visible, escaped form.
    translations = StubTranslations({"Hello {name}": "Hello {nаme}"})  # noqa: RUF001

    with pytest.raises(InvalidTranslationError) as excinfo:
        tr(t"Hello {name}", translations=translations, strict=True)

    assert "\\u0430" in str(excinfo.value)


@pytest.mark.parametrize(
    "translation",
    [
        "Hello",
        "Hello {name} {extra}",
        "Hello {name!r}",
        "Hello {name.__class__}",
        "Hello {name",
    ],
)
def test_invalid_translation_falls_back_to_source_by_default(translation: str) -> None:
    name = "Ada"
    translations = StubTranslations({"Hello {name}": translation})

    # A broken catalog must never crash a render: the source text is reproduced.
    assert tr(t"Hello {name}", translations=translations) == "Hello Ada"


def test_invalid_translation_warning_includes_the_reason(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # The warning fires once per plan and pattern, so use a msgid of its own
    # that no other test shares.
    warned = "Ada"
    translations = StubTranslations({"Warn once {warned}": "Warn once"})

    with caplog.at_level(logging.WARNING, logger="gettext_tstrings"):
        assert tr(t"Warn once {warned}", translations=translations) == "Warn once Ada"

    assert "{warned} is missing" in caplog.text


def test_invalid_translation_warns_once_and_keeps_rendering(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # One broken catalog entry must not re-validate and re-warn on every render.
    flooded = "Ada"
    translations = StubTranslations({"Flood {flooded}": "Flood"})

    with caplog.at_level(logging.WARNING, logger="gettext_tstrings"):
        rendered = [tr(t"Flood {flooded}", translations=translations) for _ in range(5)]

    assert rendered == ["Flood Ada"] * 5
    assert caplog.text.count("invalid translation") == 1
    # strict raises every time, whatever was recorded.
    with pytest.raises(InvalidTranslationError, match="is missing"):
        tr(t"Flood {flooded}", translations=translations, strict=True)


def test_contextual_invalid_translation_warns_once_and_keeps_rendering(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Not only the plain singular path: pgettext must also look up the recorded
    # pattern and fall back.
    ctxflood = "Ada"
    translations = StubTranslations(contexts={("nav", "Ctx {ctxflood}"): "Ctx"})

    with caplog.at_level(logging.WARNING, logger="gettext_tstrings"):
        rendered = [
            tpgettext("nav", t"Ctx {ctxflood}", translations=translations) for _ in range(4)
        ]

    assert rendered == ["Ctx Ada"] * 4
    assert caplog.text.count("invalid translation") == 1
    with pytest.raises(InvalidTranslationError, match="is missing"):
        tpgettext("nav", t"Ctx {ctxflood}", translations=translations, strict=True)


def test_plural_invalid_translation_warns_once_and_keeps_rendering(
    caplog: pytest.LogCaptureFixture,
) -> None:
    nflood = 3
    translations = StubTranslations(
        plurals={("One flood", "{nflood} floods"): ("bad {gone}", "bad {gone}")},
    )

    with caplog.at_level(logging.WARNING, logger="gettext_tstrings"):
        rendered = [
            tngettext(t"One flood", t"{nflood} floods", nflood, translations=translations)
            for _ in range(4)
        ]

    assert rendered == ["3 floods"] * 4
    assert caplog.text.count("invalid plural translation") == 1
    with pytest.raises(InvalidTranslationError, match="not in the source message"):
        tngettext(
            t"One flood",
            t"{nflood} floods",
            nflood,
            translations=translations,
            strict=True,
        )


def test_contextual_constant_translation_renders_through_the_shared_tail() -> None:
    # A contextual constant message goes through _render_pattern's constant path.
    translations = StubTranslations(contexts={("nav", "Static ctx"): "固定"})

    assert tpgettext("nav", t"Static ctx", translations=translations) == "固定"


def test_invalid_pattern_record_clears_when_its_limit_is_reached() -> None:
    # The record of broken patterns is bounded too, so it cannot grow forever.
    from gettext_tstrings import core

    bounded = "Ada"
    plan = core._plan_for(t"Rec {bounded}".strings, t"Rec {bounded}".interpolations)
    for index in range(core._MAX_PATTERNS_PER_PLAN + 2):
        translations = StubTranslations({"Rec {bounded}": f"broken {index} {{gone}}"})
        assert tr(t"Rec {bounded}", translations=translations) == "Rec Ada"

    assert len(plan.invalid) <= core._MAX_PATTERNS_PER_PLAN


def test_bound_translator_strict_mode_reraises() -> None:
    name = "Ada"
    strict = Translator(StubTranslations({"Hello {name}": "Hello"}), strict=True)
    lenient = Translator(StubTranslations({"Hello {name}": "Hello"}))

    with pytest.raises(InvalidTranslationError, match="is missing"):
        strict(t"Hello {name}")
    assert lenient(t"Hello {name}") == "Hello Ada"


def test_invalid_plural_translation_falls_back_to_source() -> None:
    n = 2
    translations = StubTranslations(
        plurals={("{n} file", "{n} files"): ("{n} fichier", "fichiers cassés")},
    )

    # The plural branch's translation drops {n}; lenient mode renders the source.
    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == "2 files"
    with pytest.raises(InvalidTranslationError, match="is missing"):
        ntr(t"{n} file", t"{n} files", n, translations=translations, strict=True)


def test_same_strings_with_different_specs_do_not_share_a_plan() -> None:
    # Plans are keyed by the strings tuple, so mismatching two sites that share
    # the static text and differ only in format spec formats the value wrongly.
    amount = 1234.5
    translations = gettext.NullTranslations()

    two = tr(t"{amount:.2f}", translations=translations)
    three = tr(t"{amount:.3f}", translations=translations)
    converted = tr(t"{amount!r}", translations=translations)
    named = tr(t"{amount}", translations=translations)

    assert two == "1234.50"
    assert three == "1234.500"
    assert converted == "1234.5"
    assert named == "1234.5"

    # Sites sharing the strings but differing in variable name get their own msgid.
    other = 9
    assert compile_template(t"{other}").msgid == "{other}"
    assert compile_template(t"{amount}").msgid == "{amount}"


def test_dynamic_format_spec_sites_stay_bounded_and_correct() -> None:
    # A nested format spec (t"{v:{width}.2f}") changes format_spec at runtime, so
    # a site can be added on every call. Reaching the limit clears them, which is
    # what keeps memory from growing without bound.
    from gettext_tstrings.core import _MAX_SITES_PER_SHAPE, _PLANS

    translations = gettext.NullTranslations()
    value = 3.14159

    for width in range(4, 40):
        rendered = tr(t"[{value:{width}.2f}]", translations=translations)
        assert rendered == f"[{value:{width}.2f}]"

    template = t"[{value:{4}.2f}]"
    shapes = _PLANS[template.strings]
    assert isinstance(shapes, dict)  # promoted to a dict by the collision
    assert all(len(sites) <= _MAX_SITES_PER_SHAPE for sites in shapes.values())


def test_bare_placeholder_shapes_do_not_share_a_bucket() -> None:
    # t"{name}" and t"{count}" share the same strings ("", ""), but the second
    # level is keyed by the leading expression, so neither pays to compare
    # against the other.
    from gettext_tstrings.core import _PLANS

    translations = gettext.NullTranslations()
    name = "Ada"
    count = 7

    assert tr(t"{name}", translations=translations) == "Ada"
    assert tr(t"{count}", translations=translations) == "7"

    template = t"{name}"
    shapes = _PLANS[template.strings]
    assert isinstance(shapes, dict)  # promoted to a dict by the second site
    assert "name" in shapes and "count" in shapes
    assert len(shapes["name"]) == 1


def test_plural_with_empty_branch_msgid_skips_catalog() -> None:
    # An empty msgid is reserved for catalog metadata (SPEC §2). Even against a
    # catalog that returns the header, a plural with an empty branch renders the
    # source.
    header = "Project-Id-Version: demo\n"
    translations = StubTranslations(
        messages={"": header},
        plurals={("", ""): (header, header)},
    )

    assert tngettext(t"", t"", 1, translations=translations) == ""
    assert tngettext(t"", t"", 2, translations=translations) == ""
    assert tnpgettext("ctx", t"", t"", 1, translations=translations) == ""


def test_plural_with_one_empty_branch_msgid_skips_catalog() -> None:
    # Even when only one branch is empty, no catalog entry for that pair can
    # exist. Against a catalog that returns the header, the header must never
    # leak out as a UI string.
    header = "Project-Id-Version: demo\n"
    n = 2
    translations = StubTranslations(
        messages={"": header},
        plurals={("", "{n} files"): (header, header), ("One file", ""): (header, header)},
    )

    assert tngettext(t"", t"{n} files", 1, translations=translations) == ""
    assert tngettext(t"", t"{n} files", n, translations=translations) == "2 files"
    assert tngettext(t"One file", t"", 1, translations=translations) == "One file"
    assert tngettext(t"One file", t"", n, translations=translations) == ""


@pytest.mark.parametrize(
    "translation",
    ["{name:} さん", "{name:>8} さん", "{name!r} さん"],
    ids=["empty-format-spec", "format-spec", "conversion"],
)
def test_leading_placeholder_may_not_carry_a_modifier(translation: str) -> None:
    # The start of the pattern (index 0) is the scan boundary in
    # _has_explicit_field_modifier. Every modifier in the existing tests sits
    # elsewhere. ``{name:}`` in particular is invisible to the main loop, since
    # Formatter reports its format_spec as the empty string, so this function is
    # the only detector: if the boundary slips, nothing else catches it.
    name = "Ada"
    translations = StubTranslations({"{name} desu": translation})

    with pytest.raises(InvalidTranslationError, match="adds formatting"):
        tr(t"{name} desu", translations=translations, strict=True)


@pytest.mark.parametrize(
    "returned",
    [None, b"bytes", 42, ["one", "many"], {"a": 1}],
    ids=["none", "bytes", "int", "unhashable-list", "unhashable-dict"],
)
def test_a_catalog_returning_a_non_string_never_escapes_the_strict_switch(
    returned: object,
) -> None:
    # Translations is a public Protocol, so an outside implementation can return
    # something other than str (returning dict.get directly is a common shape).
    # A raw TypeError escaping would break the contract that a broken catalog
    # never fails a render.
    name = "Ada"

    class NonStringCatalog(StubTranslations):
        def gettext(self, message: str, /) -> str:
            return cast("str", returned)

    assert tr(t"Hello {name}", translations=NonStringCatalog()) == "Hello Ada"
    with pytest.raises(InvalidTranslationError, match="not str"):
        tr(t"Hello {name}", translations=NonStringCatalog(), strict=True)


def test_pattern_dict_clears_when_its_limit_is_reached() -> None:
    # The translation patterns piling up in one plan are bounded too. Unlike the
    # other three limits, this one asserted nothing about the limit itself and
    # passed even with the eviction code dead.
    from gettext_tstrings import core

    name = "Ada"
    plan = core._plan_for(t"Bounded {name}".strings, t"Bounded {name}".interpolations)
    for index in range(core._MAX_PATTERNS_PER_PLAN + 2):
        translations = StubTranslations({"Bounded {name}": f"L{index} {{name}}"})
        assert tr(t"Bounded {name}", translations=translations) == f"L{index} Ada"

    assert len(plan.patterns) <= core._MAX_PATTERNS_PER_PLAN
    assert tr(t"Bounded {name}", translations=gettext.NullTranslations()) == "Bounded Ada"


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [("{{{{:{a}", "{{:X"), ("{a}{{:", "X{:"), ("{{:}}{a}", "{:}X")],
    ids=["escapes-then-colon", "field-then-escape-colon", "escape-colon-brace"],
)
def test_escaped_braces_may_sit_beside_a_literal_colon(pattern: str, expected: str) -> None:
    # The scan in _has_explicit_field_modifier skips ``{{`` as two characters and
    # ``}`` as one. If the stride slips, a literal colon reads as a format spec
    # inside a field and a valid translation is rejected. Escaped braces sitting
    # beside a literal colon appeared in no test and in no conformance case.
    a = "X"
    translations = StubTranslations({"{a}": pattern})

    assert tr(t"{a}", translations=translations, strict=True) == expected


def test_contextual_empty_msgid_never_reaches_the_catalog() -> None:
    # An empty msgid is reserved for the catalog's metadata header (SPEC §2).
    # The guard on the gettext side was pinned, the one on the pgettext side was
    # not: remove it and the header string goes straight into the UI.
    header = "Content-Type: text/plain; charset=UTF-8\n"
    translations = StubTranslations(contexts={("nav", ""): header})

    assert tpgettext("nav", t"", translations=translations) == ""


def test_plural_only_placeholder_renders_through_the_general_path() -> None:
    # Send a placeholder that exists only in the plural branch through the
    # general render path (_render_plural_chunks) by using three chunks or more.
    # Picking the wrong branch shows up nowhere else.
    shared = "S"
    only = "O"
    n = 2
    translations = StubTranslations(
        plurals={("One {shared}", "{shared} and {only}"): ("x", "{only}/{shared}")},
    )

    rendered = tngettext(
        t"One {shared}",
        t"{shared} and {only}",
        n,
        translations=translations,
        strict=True,
    )

    assert rendered == "O/S"


def test_plural_functions_resolve_the_context_bound_translations() -> None:
    # use_translations() was exercised only through tr and lazy_*; the path where
    # ntr/ngettext/npgettext resolve the context binding went untested. It is the
    # core of a framework integration that switches language per request.
    n = 2
    translations = StubTranslations(
        plurals={("One file", "{n} files"): ("1件", "{n}件")},
        context_plurals={("inbox", "One message", "{n} messages"): ("1通", "{n}通")},
    )

    with use_translations(translations):
        assert tngettext(t"One file", t"{n} files", n) == "2件"
        assert tnpgettext("inbox", t"One message", t"{n} messages", n) == "2通"

    # Leaving the binding returns to the global fallback.
    assert tngettext(t"One file", t"{n} files", n) == "2 files"


def test_pattern_cache_eviction_preserves_correctness() -> None:
    # Reaching the limit clears the pattern dict outright, but later renders only
    # re-validate and rebuild; the result is unchanged.
    value = "x"
    compiled = compile_template(t"V {value}")

    for index in range(300):
        pattern = f"p{index} {{value}}"
        assert compiled.render(pattern) == f"p{index} x"
    assert compiled.render("V {value}") == "V x"


def test_empty_tstring_does_not_return_catalog_header() -> None:
    # gettext reserves the empty msgid for catalog metadata; t"" must render "".
    header_catalog = StubTranslations({"": "Project-Id-Version: demo\nLanguage: ja\n"})

    assert tr(t"", translations=header_catalog) == ""
    assert tpgettext("ctx", t"", translations=header_catalog) == ""


def test_invalid_contextual_translation_falls_back_to_source() -> None:
    filename = "report.txt"
    # The contextual translation drops {filename}.
    translations = StubTranslations(contexts={("button", "Open {filename}"): "Ouvrir"})

    assert tpgettext("button", t"Open {filename}", translations=translations) == "Open report.txt"
    with pytest.raises(InvalidTranslationError, match="is missing"):
        tpgettext("button", t"Open {filename}", translations=translations, strict=True)


def test_invalid_contextual_plural_falls_back_to_source() -> None:
    n = 2
    # The plural form of the contextual translation adds an unknown placeholder.
    translations = StubTranslations(
        context_plurals={
            ("inbox", "One message", "{n} messages"): ("{n} message", "{n} messages {bogus}"),
        },
    )

    assert (
        tnpgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
        == "2 messages"
    )
    with pytest.raises(InvalidTranslationError, match="not in the source message"):
        tnpgettext(
            "inbox",
            t"One message",
            t"{n} messages",
            n,
            translations=translations,
            strict=True,
        )


def test_plural_translation() -> None:
    n = 3
    translations = StubTranslations(
        plurals={
            ("{n} file", "{n} files"): ("{n} fichier", "{n} fichiers"),
        },
    )

    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == "3 fichiers"


def test_plural_common_placeholders_use_the_selected_source_values() -> None:
    value = "singular"
    singular = t"{value} item"
    value = "plural"
    plural = t"{value} items"
    translations = gettext.NullTranslations()

    assert ntr(singular, plural, 1, translations=translations) == "singular item"
    assert ntr(singular, plural, 2, translations=translations) == "plural items"

    first = "singular-first"
    second = "singular-second"
    singular_pair = t"{first} {second} item"
    first = "plural-first"
    second = "plural-second"
    plural_pair = t"{first} {second} items"
    reordered = StubTranslations(
        plurals={
            ("{first} {second} item", "{first} {second} items"): (
                "{second}:{first}",
                "{second}:{first}:{first}",
            ),
        },
    )

    assert (
        ntr(singular_pair, plural_pair, 2, translations=reordered)
        == "plural-second:plural-first:plural-first"
    )


def test_plural_translation_reorders_and_repeats_multiple_fields() -> None:
    n = 3
    total = 10
    translations = StubTranslations(
        plurals={
            ("{n} of {total} file", "{n} of {total} files"): (
                "{total}中{n}件",
                "{total}中{n}件、選択は{n}件",
            ),
        },
    )

    result = ntr(
        t"{n} of {total} file",
        t"{n} of {total} files",
        n,
        translations=translations,
    )

    assert result == "10中3件、選択は3件"


def test_plural_sources_can_use_branch_specific_placeholders() -> None:
    n = 1
    translations = StubTranslations(
        plurals={
            ("One file", "{n} files"): ("{n} fichier", "{n} fichiers"),
        },
    )

    result = ntr(
        t"One file",
        t"{n} files",
        n,
        translations=translations,
    )

    assert result == "1 fichier"


def test_plural_sources_require_same_formatting() -> None:
    n = 2

    with pytest.raises(InvalidTemplateError, match="different formatting"):
        ntr(
            t"{n:d} file",
            t"{n:04d} files",
            n,
            translations=gettext.NullTranslations(),
        )


def test_bound_translator() -> None:
    name = "Ada"
    n = 1
    bound = Translator(
        StubTranslations(
            messages={"Hello {name}": "{name}さん、こんにちは"},
            plurals={("{n} file", "{n} files"): ("{n}個", "{n}個")},
            context_plurals={
                ("inbox", "One message", "{n} messages"): ("{n}件", "{n}件"),
            },
        ),
    )

    assert bound.tr(t"Hello {name}") == "Adaさん、こんにちは"
    assert bound(t"Hello {name}") == "Adaさん、こんにちは"
    assert bound.ntr(t"{n} file", t"{n} files", n) == "1個"
    assert bound.npgettext("inbox", t"One message", t"{n} messages", n) == "1件"


def test_standard_names_are_canonical_and_short_names_are_aliases() -> None:
    assert tr is tgettext
    assert ntr is tngettext


def test_translation_may_repeat_a_placeholder_but_formats_it_once() -> None:
    class Formattable:
        calls = 0

        def __format__(self, format_spec: str) -> str:
            self.calls += 1
            return "value"

    value = Formattable()
    translations = StubTranslations(
        {"Source {value}": "{value}, again {value}, and {value}"},
    )

    result = tr(t"Source {value}", translations=translations)

    assert result == "value, again value, and value"
    assert value.calls == 1


def test_compile_requires_a_template() -> None:
    with pytest.raises(TypeError, match=r"templatelib\.Template"):
        compile_template(cast("Any", "Hello"))


def test_runtime_functions_require_a_template() -> None:
    with pytest.raises(TypeError, match=r"templatelib\.Template"):
        tr(cast("Any", "Hello"))
    with pytest.raises(TypeError, match=r"templatelib\.Template"):
        tpgettext("ctx", cast("Any", "Hello"))


def test_pair_path_renders_reordered_two_field_translations() -> None:
    # Check the two-distinct-field specialization (pair) through each route: a
    # str value, a non-str value, pgettext, and CompiledTemplate.
    category = "News"
    count = 7
    translations = StubTranslations(
        messages={"{category}: {count}": "{count} ({category})"},
        contexts={("tab", "{category}: {count}"): "{count} / {category}"},
    )

    assert tr(t"{category}: {count}", translations=translations) == "7 (News)"
    assert tpgettext("tab", t"{category}: {count}", translations=translations) == "7 / News"

    compiled = compile_template(t"{category}: {count}")
    assert compiled.render("{count} ({category})") == "7 (News)"
    assert repr(compiled) == "CompiledTemplate(msgid='{category}: {count}')"


def test_plural_pattern_with_str_value_and_repeated_formatted_field() -> None:
    # The plural single-field str shortcut, and the memo for a repeated
    # formatted field.
    label = "docs"
    n = 2
    # A msgid carries no format spec ({n:03d} becomes {n}), so the catalog keys
    # are in msgid form too.
    translations = StubTranslations(
        plurals={
            ("{label} file", "{label} files"): ("[{label}]", "[{label}] and [{label}]"),
            ("{n} file", "{n} files"): ("{n}", "{n} = {n}"),
        },
    )

    assert (
        ntr(t"{label} file", t"{label} files", n, translations=translations) == "[docs] and [docs]"
    )
    assert ntr(t"{n:03d} file", t"{n:03d} files", n, translations=translations) == "002 = 002"


def test_plans_cache_clears_when_key_limit_is_reached() -> None:
    # Reaching the limit on strings keys clears the cache, and rendering stays
    # correct afterwards. Constructing Template directly carries the same
    # metadata as a t-string from a literal, so many distinct strings keys can be
    # made without synthesizing source through exec.
    from string.templatelib import Template

    from gettext_tstrings import core

    translations = gettext.NullTranslations()
    name = "Ada"
    assert tr(t"Hello {name}", translations=translations) == "Hello Ada"

    for index in range(core._MAX_PLANS + 1):
        rendered = tr(Template(f"L{index} literal"), translations=translations)
        assert rendered == f"L{index} literal"

    assert len(core._PLANS) <= core._MAX_PLANS
    assert tr(t"Hello {name}", translations=translations) == "Hello Ada"


def test_shape_dict_clears_when_expression_limit_is_reached() -> None:
    # Leading expressions piling up under one strings key are cleared at the limit.
    from string.templatelib import Interpolation, Template

    from gettext_tstrings import core

    translations = gettext.NullTranslations()
    for index in range(core._MAX_SHAPES_PER_KEY + 2):
        template = Template("", Interpolation(index, f"v{index}", None, ""), "")
        assert tr(template, translations=translations) == str(index)

    probe = t"{index}"
    shapes = core._PLANS[probe.strings]
    assert isinstance(shapes, dict)
    assert len(shapes) <= core._MAX_SHAPES_PER_KEY + 1


@pytest.mark.parametrize(
    ("translation", "expected"),
    [
        ("こんにちは ｛name｝", "the braces around it are not the ASCII"),  # noqa: RUF001
        ("こんにちは {{name}}", "which is how a literal brace is escaped"),
        ("こんにちは [name]", "the name appears, but not inside braces"),
        ("こんにちは", "{name} is missing"),
    ],
    ids=["wide-braces", "doubled-braces", "no-braces", "really-absent"],
)
def test_a_missing_placeholder_says_why_when_the_name_is_visible(
    translation: str,
    expected: str,
) -> None:
    # Reporting only that {name} is missing is a dead end when the reader can
    # see those characters in front of them. An East Asian input method gives
    # full-width braces by default, and a round trip through a tool can double
    # them; both look like a placeholder and are not one.
    name = "Ada"
    translations = StubTranslations({"Hello {name}": translation})

    with pytest.raises(InvalidTranslationError, match=re.escape(expected)):
        tr(t"Hello {name}", translations=translations, strict=True)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("{nam\u200be}", "<U+200B>"),
        ("{name }", "<U+00A0>"),  # noqa: RUF001
        ("{na­me}", "<U+00AD>"),
    ],
    ids=["zero-width-space", "no-break-space", "soft-hyphen"],
)
def test_an_invisible_character_is_shown_where_it_sits(field: str, expected: str) -> None:
    # "{name} has a space in it, write {name}" is unreadable advice. The reader
    # has to be told which character, and where.
    name = "Ada"
    translations = StubTranslations({"Hello {name}": f"Hello {field}"})

    with pytest.raises(InvalidTranslationError, match=re.escape(expected)):
        tr(t"Hello {name}", translations=translations, strict=True)


def test_a_readable_non_ascii_name_is_not_escaped_but_a_homoglyph_is() -> None:
    # Escaping every non-ASCII name leaves a reader unable to find what they
    # wrote; escaping none of them hides a Cyrillic lookalike. Split on whether
    # the name mixes writing systems or changes under NFKC.
    from gettext_tstrings._patterns import show_name

    assert show_name("名前") == "{名前}"
    assert show_name("café") == "{café}"
    assert show_name("ファイル数") == "{ファイル数}"
    assert "\\u0430" in show_name("nаme")  # noqa: RUF001  Cyrillic among Latin
    assert "\\uff4e" in show_name("ｎａｍｅ")  # noqa: RUF001  folds to "name"
