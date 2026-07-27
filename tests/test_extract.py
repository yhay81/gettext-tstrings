from __future__ import annotations

import io

import pytest
from babel.messages.extract import DEFAULT_KEYWORDS, extract

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


def test_ignores_dynamic_call_targets() -> None:
    assert extract_messages('(factory())(t"Hello")') == []


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ('tr("not a template")', "must be a t-string"),
        ("tr(t'{user.name}')", "simple variable names"),
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


def test_unparsable_source_is_skipped_with_warning() -> None:
    # `name =` tokenizes cleanly (Babel returns nothing) but ast.parse rejects it;
    # our AST pass must not add an abort that stock Babel does not have.
    with pytest.warns(UserWarning, match="unparsable source"):
        assert extract_messages("name = \n") == []


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
