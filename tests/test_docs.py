"""Keep the documentation's quoted output honest.

The documentation site prints failure messages verbatim, which is the whole
point of them — a reader should recognise what they are looking at. Nothing tied
those transcripts to the code, so rewording a message left the published pages
quoting text the library no longer produces, and the site served it for a day.

These tests close that gap from both ends: the library really does produce each
quoted sentence, and each quoted sentence really does appear in the pages. They
say nothing about whether the surrounding prose is right.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, cast

import pytest
from babel.messages.extract import DEFAULT_KEYWORDS, extract
from babel.messages.pofile import read_po

from gettext_tstrings import InvalidTranslationError, compile_template
from gettext_tstrings.extract import extract_tstrings

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
I18N = ROOT / "i18n"
README = ROOT / "README.md"
SITE_BUILDER = ROOT / "scripts" / "build_multilingual_docs.py"
LANGUAGES = ("ja", "zh", "es", "fr", "de", "pt-BR", "ko", "ru", "ar")
LOCALES = {language: ("pt_BR" if language == "pt-BR" else language) for language in LANGUAGES}
EXTRACTOR = cast("Any", extract_tstrings)

SITE_MESSAGES = {
    (None, "Safe gettext and Babel integration for Python t-strings."),
    (None, "Home"),
    (None, "Tutorial"),
    (None, "Why t-strings"),
    ("navigation", "Guide"),
    (None, "Extraction"),
    (None, "Specification"),
    (None, "API"),
    (None, "Switch to dark mode"),
    (None, "Switch to light mode"),
    (None, "Copyright © 2026 {author} · MIT License"),
    (None, ("Built {n} localized page", "Built {n} localized pages")),
}

MISMATCH = "translation does not match the source placeholders: "

# Against the source message ``Hello {name}``: a translation, the message the
# library raises for it, and the part of that message a page quotes. The two
# differ where a page factors the shared opening out into its prose.
QUOTED_FAILURES = [
    (
        "こんにちは {nombre}",
        MISMATCH + "{name} is missing; {nombre} is not in the source message",
        MISMATCH + "{name} is missing; {nombre} is not in the source message",
    ),
    (
        "こんにちは ｛name｝",  # noqa: RUF001 - full-width braces are the case under test
        MISMATCH + "{name} is missing (the braces around it are not the ASCII { and })",
        "{name} is missing (the braces around it are not the ASCII { and })",
    ),
    (
        "こんにちは {{name}}",
        MISMATCH
        + "{name} is missing (it is written {{name}}, which is how a literal brace is escaped)",
        "{name} is missing (it is written {{name}}, which is how a literal brace is escaped)",
    ),
    (
        "こんにちは name",
        MISMATCH + "{name} is missing (the name appears, but not inside braces)",
        "{name} is missing (the name appears, but not inside braces)",
    ),
    (
        "こんにちは {名前}",
        MISMATCH + "{name} is missing; {名前} is not in the source message",
        "{name} is missing; {名前} is not in the source message",
    ),
    (
        # A no-break space, as invisible in this file as it is in a catalog,
        # hence the escape.
        "こんにちは {\u00a0name}",
        "placeholder {<U+00A0>name} has a space inside the braces; write {name}",
        "placeholder {<U+00A0>name} has a space inside the braces; write {name}",
    ),
    (
        # A Cyrillic "a" that no reader can tell from the Latin one, which is
        # why the message escapes it. Written as an escape here for the same
        # reason: the source of a test should not need a hex editor either.
        "こんにちは {n\u0430me}",
        MISMATCH + "{name} is missing; {n\u0430me} (n\\u0430me) is not in the source message",
        "{n\u0430me} (n\\u0430me) is not in the source message",
    ),
    (
        "{name.__class__.__mro__}",
        "placeholder {name.__class__.__mro__} must be a plain name, "
        "copied from the source message unchanged",
        "placeholder {name.__class__.__mro__} must be a plain name, "
        "copied from the source message unchanged",
    ),
    (
        "Hello {name!r}",
        "placeholder {name} adds formatting; write {name} on its own, "
        "because the source message decides how the value is formatted",
        "placeholder {name} adds formatting; write {name} on its own, "
        "because the source message decides how the value is formatted",
    ),
    (
        "Hello {0}",
        "placeholder {0} must be a plain name, copied from the source message unchanged",
        "placeholder {0} must be a plain name, copied from the source message unchanged",
    ),
]


def _flatten(text: str) -> str:
    """Collapse the markup a page adds around a quoted sentence.

    Pages wrap these sentences across lines and split them across table cells,
    so neither line breaks nor the backticks that mark up code can take part in
    the comparison.
    """
    return re.sub(r"\s+", " ", text.replace("`", "").replace("&nbsp;", " "))


def _prose() -> str:
    pages = sorted(DOCS.glob("*.md"))
    return _flatten("\n".join(page.read_text(encoding="utf-8") for page in pages))


@pytest.mark.parametrize(("translation", "message", "quoted"), QUOTED_FAILURES)
def test_the_library_produces_each_quoted_message(
    translation: str,
    message: str,
    quoted: str,
) -> None:
    name = "Ada"
    compiled = compile_template(t"Hello {name}")

    with pytest.raises(InvalidTranslationError) as caught:
        compiled.render(translation)

    assert str(caught.value) == message
    # A page may quote part of a message, never a paraphrase of one.
    assert quoted in message


@pytest.mark.parametrize(("translation", "message", "quoted"), QUOTED_FAILURES)
def test_the_documentation_quotes_each_message(
    translation: str,
    message: str,
    quoted: str,
) -> None:
    # translation and message are unused here; keeping the full signature makes a
    # failure name the case rather than an index.
    assert translation and message
    assert _flatten(quoted) in _prose()


def test_every_python_block_parses() -> None:
    # t-strings are new syntax and these snippets are never executed, so a typo
    # in one stays invisible until a reader copies it. Parsing is as far as this
    # can go — the snippets show call sites and reference names defined
    # elsewhere — and it is where a t-string typo shows.
    blocks = [
        (page.name, index, block)
        for page in [*sorted(DOCS.glob("*.md")), README]
        for index, block in enumerate(
            re.findall(r"\n```python\n(.*?)\n```", page.read_text(encoding="utf-8"), re.DOTALL),
        )
    ]

    assert len(blocks) > 20, "the fence pattern probably stopped matching"
    for name, index, block in blocks:
        ast.parse(block, filename=f"{name}#python-{index}")


@pytest.mark.parametrize("language", LANGUAGES)
def test_translated_sites_cover_every_english_page(language: str) -> None:
    english = {page.name for page in DOCS.glob("*.md")}
    translated = {page.name for page in (I18N / language / "docs").glob("*.md")}

    assert translated == english


@pytest.mark.parametrize("language", LANGUAGES)
def test_translated_pages_preserve_python_examples(language: str) -> None:
    def python_blocks(page: Path) -> list[str]:
        return re.findall(
            r"\n```python\n(.*?)\n```",
            page.read_text(encoding="utf-8"),
            re.DOTALL,
        )

    for english in DOCS.glob("*.md"):
        translated = I18N / language / "docs" / english.name
        assert python_blocks(translated) == python_blocks(english), translated


@pytest.mark.parametrize("language", LANGUAGES)
def test_site_chrome_catalog_is_complete(language: str) -> None:
    with (I18N / language / "LC_MESSAGES" / "site.po").open(encoding="utf-8") as file:
        catalog = read_po(file, locale=LOCALES[language])

    messages = {(message.context, message.id): message for message in catalog if message.id}
    assert set(messages) == SITE_MESSAGES
    assert all(message.string and not message.fuzzy for message in messages.values())
    assert all("gettext-tstrings" in message.auto_comments for message in messages.values())


def test_site_catalog_matches_messages_extracted_from_builder() -> None:
    with SITE_BUILDER.open("rb") as file:
        extracted = list(
            extract(
                EXTRACTOR,
                file,
                keywords=DEFAULT_KEYWORDS,
                comment_tags=[],
                options={},
            ),
        )

    messages = {(context, message) for _, message, _, context in extracted}
    assert messages == SITE_MESSAGES
