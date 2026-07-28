from __future__ import annotations

import codecs
import io

import pytest
from babel.messages.extract import DEFAULT_KEYWORDS, extract

from gettext_tstrings import compile_template
from gettext_tstrings.extract import ExtractionError, extract_tstrings


def extract_messages(
    source: str,
    *,
    options: dict[str, str] | None = None,
) -> list[tuple[int, str | tuple[str, ...], list[str], str | None]]:
    return list(
        extract(
            extract_tstrings,
            io.BytesIO(source.encode()),
            keywords=DEFAULT_KEYWORDS,
            comment_tags=["Translators:"],
            options=options,
        ),
    )


def test_extracts_tstrings_and_ordinary_gettext_in_source_order() -> None:
    source = """\
def greet(name, n):
    plain = _("Plain message")
    # Translators: Greeting on the home page.
    greeting = tr(t"Hello {name}")
    files = ntr(t"{n} file", t"{n} files", n)
    return plain, greeting, files
"""

    messages = extract_messages(source)

    assert messages == [
        (2, "Plain message", [], None),
        (
            4,
            "Hello {name}",
            ["Translators: Greeting on the home page.", "gettext-tstrings"],
            None,
        ),
        (5, ("{n} file", "{n} files"), ["gettext-tstrings"], None),
    ]


def test_extraction_hides_source_formatting_and_escapes_literal_braces() -> None:
    source = """\
def show(amount):
    return tr(t"Total {{gross}}: {amount:,.2f}")
"""

    assert extract_messages(source)[0][1] == "Total {{gross}}: {amount}"


def test_extraction_preserves_the_runtime_placeholder_name() -> None:
    source = 'def greet(ｎａｍｅ):\n    return tr(t"Hello {ｎａｍｅ}")\n'  # noqa: RUF001
    name = "Ada"
    template = t"Hello {ｎａｍｅ}"

    assert extract_messages(source)[0][1] == compile_template(template).msgid


def test_configured_aliases_are_extracted() -> None:
    source = """\
def greet(name):
    return translate(t"Hello {name}")
"""

    messages = extract_messages(source, options={"tr_functions": "translate"})

    assert messages[0][1] == "Hello {name}"


def test_qualified_default_call_is_extracted() -> None:
    source = """\
def greet(name):
    return i18n.tr(t"Hello {name}")
"""

    assert extract_messages(source)[0][1] == "Hello {name}"


def test_extracts_standard_gettext_names_and_underscore_for_tstrings() -> None:
    source = """\
def greet(name):
    first = gettext(t"Hello {name}")
    second = _(t"Welcome {name}")
    return first, second
"""

    assert [message[1] for message in extract_messages(source)] == [
        "Hello {name}",
        "Welcome {name}",
    ]


def test_extracts_canonical_ngettext() -> None:
    source = """\
def files(n):
    return ngettext(t"One file", t"{n} files", n)
"""

    assert extract_messages(source)[0][1] == ("One file", "{n} files")


def test_standard_string_gettext_still_uses_babel_extractor() -> None:
    assert extract_messages('gettext("Plain")') == [(1, "Plain", [], None)]


def test_extracts_context_and_contextual_plurals() -> None:
    source = """\
def messages(name, n):
    action = pgettext("button", t"Open {name}")
    inbox = npgettext("inbox", t"One message", t"{n} messages", n)
    return action, inbox
"""

    assert extract_messages(source) == [
        (2, "Open {name}", ["gettext-tstrings"], "button"),
        (3, ("One message", "{n} messages"), ["gettext-tstrings"], "inbox"),
    ]


def test_multiline_translator_comment_and_text_file_object() -> None:
    source = """\
# Translators: Greeting.
# Keep this concise.
tr(t"Hello")
"""
    raw = list(
        extract_tstrings(
            io.StringIO(source),
            DEFAULT_KEYWORDS.keys(),
            ["Translators:"],
            {},
        ),
    )

    # Simple messages are emitted with a None funcname so extraction never
    # depends on the caller's keyword set (see _extract_call).
    assert raw == [
        (
            3,
            None,
            "Hello",
            ["Translators: Greeting.", "Keep this concise.", "gettext-tstrings"],
        ),
    ]


def test_text_file_object_respects_its_encoding_cookie() -> None:
    source = '# coding: latin-1\ngettext("café")\ntr(t"café")\n'

    raw = list(
        extract_tstrings(
            io.StringIO(source),
            DEFAULT_KEYWORDS.keys(),
            [],
            {},
        ),
    )

    assert [message[2] for message in raw] == ["café", "café"]


def test_configured_source_encoding_is_used_without_a_cookie() -> None:
    source = '# Translators: Greeting.\ntr(t"café")\ngettext("monde")\n'.encode("latin-1")

    messages = list(
        extract(
            extract_tstrings,
            io.BytesIO(source),
            keywords=DEFAULT_KEYWORDS,
            comment_tags=["Translators:"],
            options={"encoding": "latin-1"},
        ),
    )

    assert messages == [
        (2, "café", ["Translators: Greeting.", "gettext-tstrings"], None),
        (3, "monde", [], None),
    ]


def test_utf8_bom_is_preserved_when_comments_are_masked() -> None:
    source = codecs.BOM_UTF8 + '# Translators: Greeting.\ntr(t"café")\n'.encode()

    messages = list(
        extract(
            extract_tstrings,
            io.BytesIO(source),
            keywords=DEFAULT_KEYWORDS,
            comment_tags=["Translators:"],
            options={},
        ),
    )

    assert messages == [
        (2, "café", ["Translators: Greeting.", "gettext-tstrings"], None),
    ]


def test_translator_comment_can_follow_an_unrelated_comment() -> None:
    source = """\
# This note is not for translators.
# Translators: Greeting shown on the home page.
tr(t"Hello")
"""

    assert extract_messages(source)[0][2] == [
        "Translators: Greeting shown on the home page.",
        "gettext-tstrings",
    ]


def test_tstring_translator_comment_does_not_leak_to_ordinary_gettext() -> None:
    source = """\
# Translators: T-string greeting.
tr(t"Hello")
# Translators: Ordinary greeting.
gettext("World")
"""

    assert extract_messages(source) == [
        (2, "Hello", ["Translators: T-string greeting.", "gettext-tstrings"], None),
        (4, "World", ["Translators: Ordinary greeting."], None),
    ]


def test_rejected_tstring_comment_does_not_leak_to_ordinary_gettext() -> None:
    source = """\
# Translators: Rejected t-string.
tr(t"Hello {user.name}")
# Translators: Ordinary greeting.
gettext("World")
"""

    with pytest.warns(UserWarning, match="simple variable names"):
        messages = extract_messages(source)

    assert messages == [(4, "World", ["Translators: Ordinary greeting."], None)]


def test_fake_comment_inside_string_literal_is_ignored_and_does_not_crash() -> None:
    # 文字列リテラル内の「コメントに見える行」を行走査で拾うと、マスキングが
    # リテラルを破壊しBabelがTokenErrorで全体を停止していた(tokenize化で解決)。
    source = '''\
TEXT = """
# Translators: fake comment inside a string
"""
# Translators: real comment.
greeting = tr(t"Hello")
gettext("World")
'''

    assert extract_messages(source) == [
        (5, "Hello", ["Translators: real comment.", "gettext-tstrings"], None),
        (6, "World", [], None),
    ]


def test_form_feed_does_not_shift_translator_comment_lines() -> None:
    # \f はstr.splitlines()だけが行区切りに数えるため、行走査では以降の
    # 行番号がずれて翻訳者コメントが無言で欠落していた(tokenize化で解決)。
    source = 'PAGE = "a\fb"\n\n# Translators: after a form feed.\ngreeting = tr(t"Hello")\n'

    assert extract_messages(source) == [
        (4, "Hello", ["Translators: after a form feed.", "gettext-tstrings"], None),
    ]


def test_ordinary_helper_keeps_its_translator_comment() -> None:
    source = """\
# Translators: Ordinary custom helper.
translate("Hello")
"""

    with pytest.warns(UserWarning, match="must be a t-string"):
        messages = list(
            extract(
                extract_tstrings,
                io.BytesIO(source.encode()),
                keywords=DEFAULT_KEYWORDS | {"translate": None},
                comment_tags=["Translators:"],
                options={"tr_functions": "translate"},
            ),
        )

    assert messages == [(2, "Hello", ["Translators: Ordinary custom helper."], None)]


def test_ignores_dynamic_call_targets() -> None:
    assert extract_messages('(factory())(t"Hello")') == []


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ('tr("not a template")', "must be a t-string"),
        ("tr(t'{user.name}')", "simple variable names"),
        ("tr(t'{(name)}')", "simple variable names"),
        ("tr()", "requires a t-string"),
        ("ntr(t'{n} file', t'{n} files')", "singular, plural, and count"),
        ("ntr(t'{n:.1f} file', t'{n:.2f} files', n)", "different formatting"),
        ("tr(t'{n:.1f} {n:.2f}')", "different formatting"),
        ('pgettext(context, t"Open {name}")', "context must be a string literal"),
        (
            'npgettext("inbox", t"One", t"{n} messages")',
            "context, singular, plural, and count",
        ),
    ],
)
def test_invalid_calls_fail_extraction_in_strict_mode(source: str, message: str) -> None:
    with pytest.raises(ExtractionError, match=message):
        extract_messages(source, options={"strict": "true"})


def test_invalid_call_is_skipped_and_extraction_continues_by_default() -> None:
    # One rejected t-string must not abort extraction of the surrounding file.
    source = """\
def view(user, name):
    bad = tr(t"Hi {user.name}")
    good = tr(t"Hello {name}")
    return bad, good
"""
    with pytest.warns(UserWarning, match="simple variable names"):
        messages = extract_messages(source)

    assert [message[1] for message in messages] == ["Hello {name}"]


@pytest.mark.parametrize("source", ["name = \n", "name = (\n", '"""unterminated\n'])
def test_unparsable_source_is_skipped_with_warning(source: str) -> None:
    with pytest.warns(UserWarning, match="unparsable source"):
        assert extract_messages(source) == []


def test_unparsable_source_fails_extraction_in_strict_mode() -> None:
    with pytest.raises(ExtractionError, match="unparsable source"):
        extract_messages("name = \n", options={"strict": "true"})


def test_simple_tstring_extracts_without_default_keywords() -> None:
    # `pybabel extract --no-default-keywords -k tr` supplies a keyword set with
    # none of the canonical gettext names; simple messages must still extract.
    source = 'tr(t"Hello {name}")'
    messages = list(
        extract(
            extract_tstrings,
            io.BytesIO(source.encode()),
            keywords={"tr": None},
            comment_tags=["Translators:"],
            options={},
        ),
    )

    assert [message[1] for message in messages] == ["Hello {name}"]


def test_lazy_functions_are_extracted_by_default() -> None:
    source = """\
LABEL = lazy_gettext(t"Welcome")
OPEN = lazy_pgettext("button", t"Open {name}")
"""

    assert extract_messages(source) == [
        (1, "Welcome", ["gettext-tstrings"], None),
        (2, "Open {name}", ["gettext-tstrings"], "button"),
    ]


def test_official_example_round_trips_through_extraction_and_runtime() -> None:
    # 公式exampleの全メッセージ(遅延ラベル含む)が抽出され、翻訳して描画できる。
    import gettext as gettext_module
    import importlib.util
    from pathlib import Path

    from babel.messages.catalog import Catalog
    from babel.messages.mofile import write_mo

    from gettext_tstrings import use_translations

    example = Path(__file__).parent.parent / "examples" / "app.py"
    messages = extract_messages(example.read_text(encoding="utf-8"))
    msgids = [message[1] for message in messages]

    assert "Welcome" in msgids
    assert "Hello {name}" in msgids
    assert ("One file", "{n} files") in msgids

    catalog = Catalog(locale="ja")
    catalog.add("Welcome", "ようこそ")
    mo_file = io.BytesIO()
    write_mo(mo_file, catalog)
    mo_file.seek(0)
    translations = gettext_module.GNUTranslations(mo_file)

    spec = importlib.util.spec_from_file_location("example_app", example)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    with use_translations(translations):
        assert str(module.GREETING_LABEL) == "ようこそ"


def test_plural_without_canonical_keyword_is_skipped_with_warning() -> None:
    # Plural/contextual messages need Babel's canonical keyword spec; without it
    # they are skipped with a warning rather than crashing the run.
    source = 'ntr(t"{n} file", t"{n} files", n)'
    with pytest.warns(UserWarning, match="not in the extraction keyword set"):
        messages = list(
            extract(
                extract_tstrings,
                io.BytesIO(source.encode()),
                keywords={"ntr": None},
                comment_tags=["Translators:"],
                options={},
            ),
        )

    assert messages == []
