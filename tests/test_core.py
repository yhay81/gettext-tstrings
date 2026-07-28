from __future__ import annotations

import gettext
import logging
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
    # キリル文字の U+0430 を含むホモグリフ名は ASCII の "name" と見分けが
    # つかないため、エラーメッセージでは可視化されたエスケープ形で示される。
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
    name = "Ada"
    translations = StubTranslations({"Hello {name}": "Hello"})

    with caplog.at_level(logging.WARNING, logger="gettext_tstrings"):
        assert tr(t"Hello {name}", translations=translations) == "Hello Ada"

    assert "missing ['name']" in caplog.text


def test_bound_translator_strict_mode_reraises() -> None:
    name = "Ada"
    strict = Translator(StubTranslations({"Hello {name}": "Hello"}), strict=True)
    lenient = Translator(StubTranslations({"Hello {name}": "Hello"}))

    with pytest.raises(InvalidTranslationError, match="missing"):
        strict(t"Hello {name}")
    assert lenient(t"Hello {name}") == "Hello Ada"


def test_invalid_plural_translation_falls_back_to_source() -> None:
    n = 2
    translations = StubTranslations(
        plurals={("{n} file", "{n} files"): ("{n} fichier", "fichiers cassés")},
    )

    # The plural branch's translation drops {n}; lenient mode renders the source.
    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == "2 files"
    with pytest.raises(InvalidTranslationError, match="missing"):
        ntr(t"{n} file", t"{n} files", n, translations=translations, strict=True)


def test_same_strings_with_different_specs_do_not_share_a_plan() -> None:
    # プランはstringsタプルをキーに引くため、staticテキストが同一で
    # 書式指定だけ異なる別サイトの照合ミスは即座に誤整形につながる。
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

    # 同じstringsで変数名だけ異なるサイトも独立したmsgidを持つ。
    other = 9
    assert compile_template(t"{other}").msgid == "{other}"
    assert compile_template(t"{amount}").msgid == "{amount}"


def test_dynamic_format_spec_sites_stay_bounded_and_correct() -> None:
    # ネスト書式指定(t"{v:{width}.2f}")は実行時にformat_specが変わるため
    # サイトが毎回増え得る。上限で消去され、メモリが無制限に伸びないこと。
    from gettext_tstrings.core import _MAX_SITES_PER_SHAPE, _PLANS

    translations = gettext.NullTranslations()
    value = 3.14159

    for width in range(4, 40):
        rendered = tr(t"[{value:{width}.2f}]", translations=translations)
        assert rendered == f"[{value:{width}.2f}]"

    template = t"[{value:{4}.2f}]"
    shapes = _PLANS[template.strings]
    assert isinstance(shapes, dict)  # 衝突でdictへ昇格済み
    assert all(len(sites) <= _MAX_SITES_PER_SHAPE for sites in shapes.values())


def test_bare_placeholder_shapes_do_not_share_a_bucket() -> None:
    # t"{name}" と t"{count}" はstringsが同一("", "")だが、先頭expressionで
    # 二段目を引くため互いの照合コストを負わない。
    from gettext_tstrings.core import _PLANS

    translations = gettext.NullTranslations()
    name = "Ada"
    count = 7

    assert tr(t"{name}", translations=translations) == "Ada"
    assert tr(t"{count}", translations=translations) == "7"

    template = t"{name}"
    shapes = _PLANS[template.strings]
    assert isinstance(shapes, dict)  # 2サイト目でdictへ昇格済み
    assert "name" in shapes and "count" in shapes
    assert len(shapes["name"]) == 1


def test_plural_with_empty_branch_msgid_skips_catalog() -> None:
    # 空msgidはカタログメタデータ用に予約(SPEC §2)。ヘッダを返す
    # カタログが相手でも、空ブランチを含む複数形はソースを描画する。
    header = "Project-Id-Version: demo\n"
    translations = StubTranslations(
        messages={"": header},
        plurals={("", ""): (header, header)},
    )

    assert tngettext(t"", t"", 1, translations=translations) == ""
    assert tngettext(t"", t"", 2, translations=translations) == ""
    assert tnpgettext("ctx", t"", t"", 1, translations=translations) == ""


def test_pattern_cache_eviction_preserves_correctness() -> None:
    # パターン辞書は上限到達で全消去されるが、以後の描画は再検証・再構築
    # されるだけで結果は変わらない。
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
    with pytest.raises(InvalidTranslationError, match="missing"):
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
    with pytest.raises(InvalidTranslationError, match="unexpected"):
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


def test_runtime_functions_require_a_template() -> None:
    with pytest.raises(TypeError, match=r"templatelib\.Template"):
        tr(cast("object", "Hello"))
    with pytest.raises(TypeError, match=r"templatelib\.Template"):
        tpgettext("ctx", cast("object", "Hello"))


def test_pair_path_renders_reordered_two_field_translations() -> None:
    # 相異なる2フィールドの特殊化(pair)を、str値・非str値・pgettext・
    # CompiledTemplateの各経路で確認する。
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
    # 複数形の単一フィールドstr近道と、書式付きフィールド反復のメモ化。
    label = "docs"
    n = 2
    # msgidは書式指定を含まない({n:03d}→{n})ため、カタログのキーもmsgid形。
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
    # stringsキー数の上限到達で全消去され、その後も正しく描画されること。
    # Template直接構築はリテラル由来のt-stringとメタデータが同一なので、
    # execでソースを合成せずに多数の相異なるstringsキーを作れる。
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
    # 同一stringsに先頭expressionが増え続けても上限で消去されること。
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
