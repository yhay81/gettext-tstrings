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
import importlib.util
import logging
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, cast

import pytest
from babel.messages.extract import DEFAULT_KEYWORDS, extract
from babel.messages.pofile import read_po

from gettext_tstrings import (
    InvalidTranslationError,
    __version__,
    compile_template,
    lazy_gettext,
    use_translations,
)
from gettext_tstrings.extract import extract_tstrings

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
I18N = ROOT / "i18n"
README = ROOT / "README.md"
SITE_BUILDER = ROOT / "scripts" / "build_multilingual_docs.py"
LANGUAGES = (
    "ja",
    "zh",
    "es",
    "fr",
    "de",
    "pt-BR",
    "ko",
    "ru",
    "ar",
    "it",
    "pl",
    "tr",
    "hi",
    "id",
    "vi",
    "uk",
    "cs",
    "nl",
    "sv",
    "el",
    "he",
    "fa",
    "th",
    "is",
    "zh-Hant",
    "sl",
    "bn",
    "ro",
    "lv",
    "cy",
    "lt",
    "hu",
    "ur",
    "sw",
    "ga",
)
# Babel spells a locale with an underscore, so ``pt-BR`` and ``zh-Hant`` — the
# URL-shaped tags this repository names its editions by — have to be converted
# before a catalog can be read against them.
LOCALES = {language: language.replace("-", "_") for language in LANGUAGES}
EXTRACTOR = cast("Any", extract_tstrings)
INLINE_LINK_RE = re.compile(
    r"(?<!!)(?<!\\)\[[^\]]+\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)",
)
REFERENCE_LINK_DEFINITION_RE = re.compile(
    r"^[ \t]{0,3}\[(?!\^)[^\]\n]+\]:\s*(?:<([^>\n]+)>|([^ \t\n]+))",
    re.MULTILINE,
)

SITE_MESSAGES = {
    (None, "Safe gettext and Babel integration for Python t-strings."),
    (None, "Start here"),
    (None, "Home"),
    (None, "Tutorial"),
    (None, "Why t-strings"),
    (None, "Use it"),
    ("navigation", "Guide"),
    (None, "Extraction"),
    (None, "In production"),
    (None, "Migration"),
    (None, "For translators"),
    (None, "Understand it"),
    (None, "Background"),
    (None, "Pitfalls"),
    (None, "How it works"),
    (None, "Reference"),
    (None, "API"),
    (None, "Specification"),
    (None, "Switch to dark mode"),
    (None, "Switch to light mode"),
    (None, "Copyright © 2026 {author} · MIT License"),
    (None, ("Built {n} localized page", "Built {n} localized pages")),
    (
        "build report",
        ("Rendered {n} page in {seconds}s", "Rendered {n} pages in {seconds}s"),
    ),
}

# Interpolated by the lenient-warning test; the name is part of the msgid.
author = "Yusuke Hayashi"

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


def _markdown_link_targets(page: Path) -> Counter[str]:
    markdown = page.read_text(encoding="utf-8")
    targets = Counter(INLINE_LINK_RE.findall(markdown))
    targets.update(
        target
        for match in REFERENCE_LINK_DEFINITION_RE.finditer(markdown)
        if (target := match.group(1) or match.group(2))
    )
    return targets


def test_markdown_link_targets_ignore_text_translation_and_wrapping(tmp_path: Path) -> None:
    english = tmp_path / "english.md"
    translated = tmp_path / "translated.md"
    english.write_text(
        """[Guide](guide.md)
[Again](guide.md "Guide title")
[Spec](spec.md)
[Conformance](spec.md#conformance)
  [external]: https://example.test/path
   [spec]: <spec.md> "Spec title"
[^note]: footnote.md
![Alt text](image.png)
\\[escaped](escaped.md)
paragraph [not a definition]: prose.md
    [code]: code.md""",
        encoding="utf-8",
    )
    translated.write_text(
        """[Lugha kadhaa kwa wakati
mmoja](guide.md)
[Tena](guide.md "Guide title")
[Uainishaji](spec.md)
[Utiifu](spec.md#conformance)
  [nje]: https://example.test/path
   [uainishaji]: <spec.md> "Spec title"
[^note]: footnote.md
![Maandishi mbadala](image.png)
\\[imeepushwa](escaped.md)
paragraph [not a definition]: prose.md
    [code]: code.md""",
        encoding="utf-8",
    )

    expected = Counter(
        {
            "guide.md": 2,
            "spec.md": 2,
            "spec.md#conformance": 1,
            "https://example.test/path": 1,
        },
    )
    assert _markdown_link_targets(english) == expected
    assert _markdown_link_targets(translated) == expected


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


def test_markdown_link_targets_include_inline_and_reference_definitions(tmp_path: Path) -> None:
    page = tmp_path / "page.md"
    page.write_text(
        """[Guide](guide.md)
[Again](guide.md "Guide title")
  [external]: https://example.test/path
   [spec]: <spec.md> "Spec title"
[^note]: footnote.md
![Alt text](image.png)
\\[escaped](escaped.md)
paragraph [not a definition]: prose.md
    [code]: code.md""",
        encoding="utf-8",
    )

    assert _markdown_link_targets(page) == Counter(
        {
            "guide.md": 2,
            "https://example.test/path": 1,
            "spec.md": 1,
        },
    )


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


# Every fence type whose contents are program input or output, and so must
# survive translation byte for byte. ``mermaid`` is deliberately absent: its
# node labels are prose and each edition translates them.
VERBATIM_FENCES = frozenset(
    {
        "python",
        "pycon",
        "console",
        "po",
        "text",
        "yaml",
        "ini",
        "toml",
        "json",
        "dockerfile",
    },
)


def _verbatim_blocks(page: Path) -> list[tuple[str, str]]:
    """Every verbatim code block on a page, in order, unindented.

    The pattern accepts an indented fence because content tabs indent their
    blocks — the first version of this check matched only column-zero fences,
    and the tabbed examples silently escaped it.
    """
    blocks: list[tuple[str, str]] = []
    for match in re.finditer(
        r"^([ \t]*)```(\w+)\n(.*?)\n\1```$",
        page.read_text(encoding="utf-8"),
        re.DOTALL | re.MULTILINE,
    ):
        indent, fence, body = match.groups()
        if fence not in VERBATIM_FENCES:
            continue
        if indent:
            body = "\n".join(line.removeprefix(indent) for line in body.split("\n"))
        blocks.append((fence, body))
    return blocks


@pytest.mark.parametrize("language", LANGUAGES)
def test_translated_pages_preserve_verbatim_blocks(language: str) -> None:
    for english in DOCS.glob("*.md"):
        translated = I18N / language / "docs" / english.name
        assert _verbatim_blocks(translated) == _verbatim_blocks(english), translated


@pytest.mark.parametrize("language", LANGUAGES)
def test_translated_pages_preserve_markdown_link_targets(language: str) -> None:
    for english in DOCS.glob("*.md"):
        translated = I18N / language / "docs" / english.name
        assert _markdown_link_targets(translated) == _markdown_link_targets(english), translated


@pytest.mark.parametrize("language", LANGUAGES)
def test_site_chrome_catalog_is_complete(language: str) -> None:
    with (I18N / language / "LC_MESSAGES" / "site.po").open(encoding="utf-8") as file:
        catalog = read_po(file, locale=LOCALES[language])

    messages = {(message.context, message.id): message for message in catalog if message.id}
    assert set(messages) == SITE_MESSAGES
    assert all(message.string and not message.fuzzy for message in messages.values())
    assert all("gettext-tstrings" in message.auto_comments for message in messages.values())

    # Non-empty is not translated: a catalog whose msgstr merely repeats the
    # msgid passed every check above, and one shipped that way once, as a
    # scaffolding stub nobody replaced. Short labels may legitimately coincide
    # ("API" nearly everywhere, "Home" in Italian), so the sentinel is the
    # full-sentence messages, which no real translation leaves untouched.
    must_differ = [
        (None, "Safe gettext and Babel integration for Python t-strings."),
        (None, "Switch to dark mode"),
        (None, "Switch to light mode"),
    ]
    for key in must_differ:
        assert messages[key].string != messages[key].id, key
    for message in messages.values():
        if not message.pluralizable:
            continue
        # A pluralizable message's id and string are both sequences of forms.
        forms = cast("tuple[str, ...]", message.string)
        source = cast("tuple[str, ...]", message.id)
        assert all(form not in source for form in forms), (
            f"plural forms left in English: {message.id}"
        )


# The plural forms the internals page's showcase table quotes, per catalog.
# Each one must be a real msgstr in that language's site.po, and each must
# appear in every edition's internals page — the table is data, not prose.
QUOTED_PLURAL_FORMS = {
    "ja": ["ローカライズ済みページを{n}件ビルドしました"],
    "tr": ["{n} yerelleştirilmiş sayfa oluşturuldu"],
    "it": ["Generata {n} pagina localizzata", "Generate {n} pagine localizzate"],
    "ru": [
        "Собрана {n} локализованная страница",
        "Собраны {n} локализованные страницы",
        "Собрано {n} локализованных страниц",
    ],
    "pl": [
        "Zbudowano {n} zlokalizowaną stronę",
        "Zbudowano {n} zlokalizowane strony",
        "Zbudowano {n} zlokalizowanych stron",
    ],
    "lv": [
        "Izveidota {n} lokalizēta lapa",
        "Izveidotas {n} lokalizētas lapas",
        "Izveidots {n} lokalizētu lapu",
    ],
    "sl": [
        "Zgrajena {n} lokalizirana stran",
        "Zgrajeni {n} lokalizirani strani",
        "Zgrajene {n} lokalizirane strani",
        "Zgrajenih {n} lokaliziranih strani",
    ],
    "ga": [
        "Tógadh {n} leathanach logánaithe",
        "Tógadh {n} leathanaigh logánaithe",
    ],
    "ar": ["تم إنشاء صفحة مترجمة واحدة ({n})", "تم إنشاء {n} صفحات مترجمة"],
}


def test_the_plural_showcase_quotes_real_catalog_forms() -> None:
    for language, quoted in QUOTED_PLURAL_FORMS.items():
        with (I18N / language / "LC_MESSAGES" / "site.po").open(encoding="utf-8") as file:
            catalog = read_po(file, locale=LOCALES[language])
        plural = next(message for message in catalog if message.pluralizable)
        rendered = cast("tuple[str, ...]", plural.string)
        for form in quoted:
            assert form in rendered, (language, form)

    pages = [DOCS / "internals.md"]
    pages += [I18N / language / "docs" / "internals.md" for language in LANGUAGES]
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for quoted in QUOTED_PLURAL_FORMS.values():
            for form in quoted:
                assert form in text, (page, form)


def _slugify(heading: str) -> str:
    """The anchor python-markdown derives from an English heading.

    This mirrors the toc extension's default slugify: drop everything but word
    characters, spaces, and hyphens, then collapse runs of whitespace into
    hyphens. ``%-format`` becomes ``-format`` — the leading hyphen is real.
    """
    text = re.sub(r"[^\w\s-]", "", heading).strip().lower()
    return re.sub(r"\s+", "-", text)


def _english_anchor(heading: str) -> str:
    """The anchor an English heading actually renders with.

    A heading that pins its own ``{ #… }`` attribute keeps that value; every
    other heading gets the slug python-markdown derives from its text.
    """
    explicit = re.search(r"\{ #([^ }]+) \}\s*$", heading)
    return explicit.group(1) if explicit else _slugify(heading)


def _section_headings(page: Path) -> list[str]:
    """The ``##`` headings of a page, with fenced code blocks masked out."""
    text = re.sub(
        r"^([ \t]*)```\w*\n.*?\n\1```$",
        "",
        page.read_text(encoding="utf-8"),
        flags=re.DOTALL | re.MULTILINE,
    )
    return re.findall(r"^## (.+)$", text, re.MULTILINE)


@pytest.mark.parametrize("language", LANGUAGES)
def test_translated_headings_carry_english_anchors(language: str) -> None:
    # A translated heading auto-generates a slug from its *translated* text,
    # so every cross-page link into it breaks silently unless the heading pins
    # the English anchor with an explicit ``{ #… }`` attribute. Requiring the
    # attribute on every section heading — not only the ones currently linked
    # to — is what keeps the next new page free to link anywhere.
    for english in DOCS.glob("*.md"):
        expected = [_english_anchor(heading) for heading in _section_headings(english)]
        translated = I18N / language / "docs" / english.name
        anchors = [
            match.group(1) if match else None
            for match in (
                re.search(r"\{ #([^ }]+) \}\s*$", heading)
                for heading in _section_headings(translated)
            )
        ]
        assert anchors == expected, translated


def test_every_edition_is_registered_everywhere() -> None:
    """An edition has to appear in all three registries, or it silently vanishes.

    A language is named in the builder (which builds it), in ``zensical.toml``
    (which puts it in the language switcher), and in this file's ``LANGUAGES``
    (which tests it). Adding one to only some of them fails quietly: the site
    builds an edition nothing checks, or checks one nothing links to. Both
    happened while these editions were being added.
    """
    builder = SITE_BUILDER.read_text(encoding="utf-8")
    built = set(re.findall(r'ROOT / "i18n" / "([^"]+)" / "docs"', builder))
    config = (ROOT / "zensical.toml").read_text(encoding="utf-8")
    switcher = set(re.findall(r'link = "/([^/"]+)/", lang =', config))
    tested = {language.lower() for language in LANGUAGES}

    assert {code.lower() for code in built} == tested, "builder and tests disagree"
    assert switcher == tested, "language switcher and tests disagree"


def test_every_edition_states_the_current_version() -> None:
    """The compatibility table is the first thing an adopter reads. Pin it.

    A version quoted in prose is a version that goes stale the release after
    someone writes it, and this one sits in the table that answers "is this
    safe to depend on" — the worst place to be wrong. Every edition repeats
    the number, so a release that forgets the table fails here rather than
    shipping thirty-six pages that disagree with the package.
    """
    pages = [DOCS / "index.md"]
    pages += [I18N / language / "docs" / "index.md" for language in LANGUAGES]
    for page in pages:
        assert __version__ in page.read_text(encoding="utf-8"), page


def _prose_lines(text: str) -> list[str]:
    """The sentences of a page: no code blocks, no anchor attributes, no scraps.

    Code blocks are excluded because they *must* match English byte for byte.
    Anchor attributes are excluded because every translated heading carries the
    English one, so they differ on every page whether or not anything was
    translated. Short lines are excluded because table rules, list bullets and
    link definitions coincide across languages for reasons that say nothing.
    """
    text = re.sub(r"^([ \t]*)```\w*\n.*?\n\1```$", "", text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"\s*\{ #[^}]+ \}", "", text)
    return [line.strip() for line in text.splitlines() if len(line.strip()) > 20]


def test_every_edition_is_actually_translated() -> None:
    """An English page with the anchors pinned on is not a translation.

    Comparing whole files was not enough. One edition reached ``main`` as ten
    copies of the English source with only ``{ #anchor }`` attributes added —
    every other check passed, because the code blocks matched (they were the
    same file) and the catalog was genuinely translated. Comparing the prose
    separates them cleanly: that edition shared 87% of its sentences with
    English, and every real translation shares between 4% and 8% — the lines
    that legitimately coincide, like URLs and quoted program output.
    """
    limit = 0.25
    for language in LANGUAGES:
        shared = total = 0
        for english in DOCS.glob("*.md"):
            source = set(_prose_lines(english.read_text(encoding="utf-8")))
            lines = _prose_lines((I18N / language / "docs" / english.name).read_text("utf-8"))
            total += len(lines)
            shared += sum(1 for line in lines if line in source)
        assert shared / total < limit, f"{language} is {shared / total:.0%} English prose"


def _load_site_builder() -> Any:
    spec = importlib.util.spec_from_file_location("site_builder", SITE_BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # dataclass() resolves annotations through sys.modules, so the module has to
    # be registered before it executes.
    sys.modules["site_builder"] = module
    spec.loader.exec_module(module)
    return module


class _BreaksTheCopyright:
    """A catalog that damages one placeholder, the way a bad PO edit does."""

    def gettext(self, message: str, /) -> str:
        if message.startswith("Copyright"):
            return "Copyright © 2026 {auteur} · Licence MIT"
        return message

    def ngettext(self, singular: str, plural: str, n: int, /) -> str:
        return singular if n == 1 else plural

    def pgettext(self, context: str, message: str, /) -> str:
        return message

    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str:
        return singular if n == 1 else plural


def test_the_site_chrome_refuses_a_broken_translation() -> None:
    # The chrome asks for strict=True, so a damaged translation stops the build
    # where it is rendered rather than falling back to English and publishing.
    builder = _load_site_builder()

    with use_translations(_BreaksTheCopyright()), pytest.raises(InvalidTranslationError) as caught:
        str(builder.COPYRIGHT)

    assert "{auteur} is not in the source message" in str(caught.value)


def test_the_site_build_fails_on_a_lenient_warning() -> None:
    # What the chrome's strict mode does not cover is everything rendered the
    # way an application renders it — the build report, deliberately lenient so
    # the site exercises the default path. The handler is what keeps that
    # leniency honest here; without a test, deleting it would look harmless.
    builder = _load_site_builder()
    logger = logging.getLogger("gettext_tstrings")
    handler = builder._FailOnInvalidTranslation()
    logger.addHandler(handler)
    lenient = lazy_gettext(t"Copyright © 2026 {author} · MIT License")
    try:
        with use_translations(_BreaksTheCopyright()), pytest.raises(RuntimeError) as caught:
            str(lenient)
    finally:
        logger.removeHandler(handler)

    assert "{auteur} is not in the source message" in str(caught.value)


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
