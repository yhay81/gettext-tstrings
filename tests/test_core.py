from __future__ import annotations

import gettext
from importlib.metadata import version
from types import SimpleNamespace
from typing import cast

import pytest

from gettext_tstrings import (
    InvalidTemplateError,
    InvalidTranslationError,
    Translator,
    __version__,
    compile_template,
    ntr,
    tr,
)
from gettext_tstrings import gettext as tgettext
from gettext_tstrings import ngettext as tngettext
from gettext_tstrings import npgettext as tnpgettext
from gettext_tstrings import pgettext as tpgettext


class StubTranslations(gettext.NullTranslations):
    def __init__(
        self,
        messages: dict[str, str] | None = None,
        plurals: dict[tuple[str, str], tuple[str, str]] | None = None,
        contexts: dict[tuple[str, str], str] | None = None,
        context_plurals: dict[tuple[str, str, str], tuple[str, str]] | None = None,
    ) -> None:
        super().__init__()
        self.messages = messages or {}
        self.plurals = plurals or {}
        self.contexts = contexts or {}
        self.context_plurals = context_plurals or {}

    def gettext(self, message: str) -> str:
        return self.messages.get(message, message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        translated = self.plurals.get((singular, plural))
        if translated is None:
            return singular if n == 1 else plural
        return translated[0] if n == 1 else translated[1]

    def pgettext(self, context: str, message: str) -> str:
        return self.contexts.get((context, message), message)

    def npgettext(self, context: str, singular: str, plural: str, n: int) -> str:
        translated = self.context_plurals.get((context, singular, plural))
        if translated is None:
            return singular if n == 1 else plural
        return translated[0] if n == 1 else translated[1]


def test_version_matches_package_metadata() -> None:
    assert __version__ == version("gettext-tstrings")


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


def test_literal_braces_round_trip() -> None:
    value = "on"
    compiled = compile_template(t"Config {{raw}} is {value}")

    assert compiled.msgid == "Config {{raw}} is {value}"
    assert compiled.render(compiled.msgid) == "Config {raw} is on"


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
        ("Hello", "missing"),
        ("Hello {name} {extra}", "unexpected"),
        ("Hello {name!r}", "must not add"),
        ("Hello {name.__class__}", "simple Python identifier"),
        ("Hello {name", "invalid translation pattern"),
    ],
)
def test_invalid_translation_placeholders_are_rejected(
    translation: str,
    message: str,
) -> None:
    name = "Ada"
    translations = StubTranslations({"Hello {name}": translation})

    with pytest.raises(InvalidTranslationError, match=message):
        tr(t"Hello {name}", translations=translations)


def test_plural_translation() -> None:
    n = 3
    translations = StubTranslations(
        plurals={
            ("{n} file", "{n} files"): ("{n} fichier", "{n} fichiers"),
        },
    )

    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == "3 fichiers"


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
        compile_template(cast("object", "Hello"))
