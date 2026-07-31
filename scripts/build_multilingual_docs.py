"""Build the English documentation and every translated site.

Zensical currently assigns one canonical language to a project. Each language
is therefore built as its own project and emitted below the same site root.
The translated project configuration is rendered through gettext-tstrings so
the documentation site dogfoods the package it documents.
"""

from __future__ import annotations

import argparse
import gettext
import json
import logging
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from babel.messages.pofile import read_po

from gettext_tstrings import (
    LazyString,
    Translator,
    lazy_gettext,
    lazy_pgettext,
    npgettext,
    use_translations,
)

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://gettext-tstrings.yhay81.com/"
BUILD_ROOT = ROOT / "build" / "docs-i18n"
SITE_ROOT = ROOT / "site"
BASE_CONFIG = ROOT / "zensical.toml"
LOGGER = logging.getLogger("gettext_tstrings.docs")


@dataclass(frozen=True, slots=True)
class Language:
    code: str
    locale: str
    html_language: str
    url_path: str
    source: Path
    output: Path
    edit_uri: str


# Lower-cased against convention on purpose: this name is interpolated into a
# translatable message, so it *is* part of that message's msgid. Spelling it
# AUTHOR would derive a different key and send every catalog's translation of
# the copyright line back through the fuzzy cycle — the rename hazard the
# documentation warns about, demonstrated on this file the first time it moved
# to module scope.
author = "Yusuke Hayashi"

# The site chrome, written the way an application writes its menu entries and
# form labels: defined once at import, rendered in whichever language is bound
# when they are used. That is what LazyString is for, and using it here means
# adding a page touches this one table instead of a dataclass, a constructor,
# and a nav builder.
#
# A LazyString captures its interpolated values eagerly and defers only the
# catalog lookup — `author` is read at import, its translation at render.
# strict=True because a documentation build is CI: a chrome translation that
# breaks its placeholders should stop the build, not quietly ship in English.
SITE_DESCRIPTION = lazy_gettext(
    t"Safe gettext and Babel integration for Python t-strings.",
    strict=True,
)
COPYRIGHT = lazy_gettext(t"Copyright © 2026 {author} · MIT License", strict=True)
DARK_MODE = lazy_gettext(t"Switch to dark mode", strict=True)
LIGHT_MODE = lazy_gettext(t"Switch to light mode", strict=True)

# Section label, then the pages under it. The grouping is what a reader arrives
# needing: where to start, what to use, what to understand, what to look up.
# "Guide" carries a context because the word is a homonym: the sidebar entry and
# the noun in prose need not translate alike.
NAV: tuple[tuple[LazyString, tuple[tuple[LazyString, str], ...]], ...] = (
    (
        lazy_gettext(t"Start here", strict=True),
        (
            (lazy_gettext(t"Home", strict=True), "index.md"),
            (lazy_gettext(t"Tutorial", strict=True), "tutorial.md"),
            (lazy_gettext(t"Why t-strings", strict=True), "comparison.md"),
        ),
    ),
    (
        lazy_gettext(t"Use it", strict=True),
        (
            (lazy_pgettext("navigation", t"Guide", strict=True), "guide.md"),
            (lazy_gettext(t"Extraction", strict=True), "extraction.md"),
            (lazy_gettext(t"In production", strict=True), "workflow.md"),
            (lazy_gettext(t"Migration", strict=True), "migration.md"),
            (lazy_gettext(t"For translators", strict=True), "translators.md"),
        ),
    ),
    (
        lazy_gettext(t"Understand it", strict=True),
        (
            (lazy_gettext(t"Background", strict=True), "background.md"),
            (lazy_gettext(t"Pitfalls", strict=True), "pitfalls.md"),
            (lazy_gettext(t"How it works", strict=True), "internals.md"),
        ),
    ),
    (
        lazy_gettext(t"Reference", strict=True),
        (
            (lazy_gettext(t"API", strict=True), "api.md"),
            (lazy_gettext(t"Specification", strict=True), "spec.md"),
        ),
    ),
)


LANGUAGES = (
    Language("en", "en", "en", "", ROOT / "docs", SITE_ROOT, "edit/main/docs/"),
    Language(
        "ja",
        "ja",
        "ja",
        "ja",
        ROOT / "i18n" / "ja" / "docs",
        SITE_ROOT / "ja",
        "edit/main/i18n/ja/docs/",
    ),
    Language(
        "zh",
        "zh",
        "zh-Hans",
        "zh",
        ROOT / "i18n" / "zh" / "docs",
        SITE_ROOT / "zh",
        "edit/main/i18n/zh/docs/",
    ),
    Language(
        "es",
        "es",
        "es",
        "es",
        ROOT / "i18n" / "es" / "docs",
        SITE_ROOT / "es",
        "edit/main/i18n/es/docs/",
    ),
    Language(
        "fr",
        "fr",
        "fr",
        "fr",
        ROOT / "i18n" / "fr" / "docs",
        SITE_ROOT / "fr",
        "edit/main/i18n/fr/docs/",
    ),
    Language(
        "de",
        "de",
        "de",
        "de",
        ROOT / "i18n" / "de" / "docs",
        SITE_ROOT / "de",
        "edit/main/i18n/de/docs/",
    ),
    Language(
        "pt-BR",
        "pt_BR",
        "pt-BR",
        "pt-br",
        ROOT / "i18n" / "pt-BR" / "docs",
        SITE_ROOT / "pt-br",
        "edit/main/i18n/pt-BR/docs/",
    ),
    Language(
        "ko",
        "ko",
        "ko",
        "ko",
        ROOT / "i18n" / "ko" / "docs",
        SITE_ROOT / "ko",
        "edit/main/i18n/ko/docs/",
    ),
    Language(
        "ru",
        "ru",
        "ru",
        "ru",
        ROOT / "i18n" / "ru" / "docs",
        SITE_ROOT / "ru",
        "edit/main/i18n/ru/docs/",
    ),
    Language(
        "ar",
        "ar",
        "ar",
        "ar",
        ROOT / "i18n" / "ar" / "docs",
        SITE_ROOT / "ar",
        "edit/main/i18n/ar/docs/",
    ),
    Language(
        "it",
        "it",
        "it",
        "it",
        ROOT / "i18n" / "it" / "docs",
        SITE_ROOT / "it",
        "edit/main/i18n/it/docs/",
    ),
    Language(
        "pl",
        "pl",
        "pl",
        "pl",
        ROOT / "i18n" / "pl" / "docs",
        SITE_ROOT / "pl",
        "edit/main/i18n/pl/docs/",
    ),
    Language(
        "tr",
        "tr",
        "tr",
        "tr",
        ROOT / "i18n" / "tr" / "docs",
        SITE_ROOT / "tr",
        "edit/main/i18n/tr/docs/",
    ),
    Language(
        "hi",
        "hi",
        "hi",
        "hi",
        ROOT / "i18n" / "hi" / "docs",
        SITE_ROOT / "hi",
        "edit/main/i18n/hi/docs/",
    ),
    Language(
        "id",
        "id",
        "id",
        "id",
        ROOT / "i18n" / "id" / "docs",
        SITE_ROOT / "id",
        "edit/main/i18n/id/docs/",
    ),
    Language(
        "vi",
        "vi",
        "vi",
        "vi",
        ROOT / "i18n" / "vi" / "docs",
        SITE_ROOT / "vi",
        "edit/main/i18n/vi/docs/",
    ),
    Language(
        "uk",
        "uk",
        "uk",
        "uk",
        ROOT / "i18n" / "uk" / "docs",
        SITE_ROOT / "uk",
        "edit/main/i18n/uk/docs/",
    ),
    Language(
        "cs",
        "cs",
        "cs",
        "cs",
        ROOT / "i18n" / "cs" / "docs",
        SITE_ROOT / "cs",
        "edit/main/i18n/cs/docs/",
    ),
    Language(
        "nl",
        "nl",
        "nl",
        "nl",
        ROOT / "i18n" / "nl" / "docs",
        SITE_ROOT / "nl",
        "edit/main/i18n/nl/docs/",
    ),
    Language(
        "sv",
        "sv",
        "sv",
        "sv",
        ROOT / "i18n" / "sv" / "docs",
        SITE_ROOT / "sv",
        "edit/main/i18n/sv/docs/",
    ),
    Language(
        "el",
        "el",
        "el",
        "el",
        ROOT / "i18n" / "el" / "docs",
        SITE_ROOT / "el",
        "edit/main/i18n/el/docs/",
    ),
    Language(
        "he",
        "he",
        "he",
        "he",
        ROOT / "i18n" / "he" / "docs",
        SITE_ROOT / "he",
        "edit/main/i18n/he/docs/",
    ),
    Language(
        "fa",
        "fa",
        "fa",
        "fa",
        ROOT / "i18n" / "fa" / "docs",
        SITE_ROOT / "fa",
        "edit/main/i18n/fa/docs/",
    ),
    Language(
        "th",
        "th",
        "th",
        "th",
        ROOT / "i18n" / "th" / "docs",
        SITE_ROOT / "th",
        "edit/main/i18n/th/docs/",
    ),
    Language(
        "is",
        "is",
        "is",
        "is",
        ROOT / "i18n" / "is" / "docs",
        SITE_ROOT / "is",
        "edit/main/i18n/is/docs/",
    ),
    Language(
        "zh-Hant",
        "zh_Hant",
        "zh-Hant",
        "zh-hant",
        ROOT / "i18n" / "zh-Hant" / "docs",
        SITE_ROOT / "zh-hant",
        "edit/main/i18n/zh-Hant/docs/",
    ),
    Language(
        "sl",
        "sl",
        "sl",
        "sl",
        ROOT / "i18n" / "sl" / "docs",
        SITE_ROOT / "sl",
        "edit/main/i18n/sl/docs/",
    ),
    Language(
        "bn",
        "bn",
        "bn",
        "bn",
        ROOT / "i18n" / "bn" / "docs",
        SITE_ROOT / "bn",
        "edit/main/i18n/bn/docs/",
    ),
    Language(
        "ro",
        "ro",
        "ro",
        "ro",
        ROOT / "i18n" / "ro" / "docs",
        SITE_ROOT / "ro",
        "edit/main/i18n/ro/docs/",
    ),
    Language(
        "lv",
        "lv",
        "lv",
        "lv",
        ROOT / "i18n" / "lv" / "docs",
        SITE_ROOT / "lv",
        "edit/main/i18n/lv/docs/",
    ),
    Language(
        "cy",
        "cy",
        "cy",
        "cy",
        ROOT / "i18n" / "cy" / "docs",
        SITE_ROOT / "cy",
        "edit/main/i18n/cy/docs/",
    ),
    Language(
        "lt",
        "lt",
        "lt",
        "lt",
        ROOT / "i18n" / "lt" / "docs",
        SITE_ROOT / "lt",
        "edit/main/i18n/lt/docs/",
    ),
    Language(
        "hu",
        "hu",
        "hu",
        "hu",
        ROOT / "i18n" / "hu" / "docs",
        SITE_ROOT / "hu",
        "edit/main/i18n/hu/docs/",
    ),
    Language(
        "ur",
        "ur",
        "ur",
        "ur",
        ROOT / "i18n" / "ur" / "docs",
        SITE_ROOT / "ur",
        "edit/main/i18n/ur/docs/",
    ),
    Language(
        "sw",
        "sw",
        "sw",
        "sw",
        ROOT / "i18n" / "sw" / "docs",
        SITE_ROOT / "sw",
        "edit/main/i18n/sw/docs/",
    ),
    Language(
        "ga",
        "ga",
        "ga",
        "ga",
        ROOT / "i18n" / "ga" / "docs",
        SITE_ROOT / "ga",
        "edit/main/i18n/ga/docs/",
    ),
)

# Editions written right to left. _validate_build derives the expected <body>
# direction from this set, so a new RTL language only needs a line here.
RTL_LANGUAGES = frozenset({"ar", "he", "fa", "ur"})

NAV_PATTERN = re.compile(r"nav = \[\n.*?\n\]\n", re.DOTALL)
PLURAL_PROBES = {
    "en": (1, 2),
    "ja": (0, 1, 2),
    "zh": (0, 1, 2),
    "es": (1, 2),
    "fr": (1, 2),
    "de": (1, 2),
    "pt-BR": (1, 2),
    "ko": (0, 1, 2),
    "ru": (1, 2, 5),
    "ar": (0, 1, 2, 3, 11, 100),
    "it": (1, 2),
    "pl": (1, 2, 5),
    "tr": (1, 2),
    "hi": (1, 2),
    "id": (0, 1, 2),
    "vi": (0, 1, 2),
    "uk": (1, 2, 5),
    "cs": (1, 2, 5),
    "nl": (1, 2),
    "sv": (1, 2),
    "el": (1, 2),
    "he": (1, 2, 3, 20),
    "fa": (1, 2),
    "th": (0, 1, 2),
    "is": (1, 2, 11),
    "zh-Hant": (0, 1, 2),
    "sl": (1, 2, 3, 5),
    "bn": (1, 2),
    "ro": (1, 2, 20),
    "lv": (0, 1, 2),
    "cy": (0, 1, 2, 3, 6),
    "lt": (1, 2, 11),
    "hu": (0, 1, 2),
    "ur": (1, 2),
    "sw": (1, 2),
    "ga": (1, 2, 3, 7, 11),
}


def _quote(value: str | Path) -> str:
    return json.dumps(str(value), ensure_ascii=False)


class _FailOnInvalidTranslation(logging.Handler):
    """Turn the library's lenient-mode warnings into a build failure.

    The chrome strings ask for ``strict=True`` and raise on their own, so what
    is left for this handler is everything rendered the way an application
    renders it — the build report, which is deliberately lenient. This is the
    practice the documentation recommends to every application: route the
    ``gettext_tstrings`` logger somewhere a human looks. Here "somewhere" is a
    non-zero exit.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # This build's own progress logger is a child of the library's, so its
        # records propagate here too. Only the library's own warnings are a
        # catalog defect; everything else passes through.
        if record.name != "gettext_tstrings" or record.levelno < logging.WARNING:
            return
        msg = f"the site catalog produced a translation warning: {record.getMessage()}"
        raise RuntimeError(msg)


def _nav() -> str:
    # str() on each label is what renders it, through whichever translations
    # the caller bound to the context.
    lines = ["nav = ["]
    for section, pages in NAV:
        lines.append(f"  {{ {_quote(str(section))} = [")
        lines.extend(f"    {{ {_quote(str(label))} = {_quote(path)} }}," for label, path in pages)
        lines.append("  ] },")
    lines.append("]\n")
    return "\n".join(lines)


def _replace_once(config: str, old: str, new: str) -> str:
    if config.count(old) != 1:
        msg = f"expected one occurrence in zensical.toml: {old!r}"
        raise ValueError(msg)
    return config.replace(old, new)


def _translated_config(language: Language, localedir: Path) -> str:
    # Bind the language to the context and let every lazy label resolve against
    # it, the way a web application binds a request's language and then calls
    # the module-level functions without threading a catalog through.
    translations = gettext.translation("site", localedir=localedir, languages=[language.locale])
    with use_translations(translations):
        return _render_config(language)


def _render_config(language: Language) -> str:
    config = BASE_CONFIG.read_text(encoding="utf-8")
    config = _replace_once(
        config,
        "[project]\n",
        '[project]\ndocs_dir = "docs"\nsite_dir = "site"\n',
    )
    config = _replace_once(
        config,
        'site_description = "Safe gettext and Babel integration for Python t-strings."',
        f"site_description = {_quote(str(SITE_DESCRIPTION))}",
    )
    config = _replace_once(
        config,
        f'site_url = "{SITE_URL}"',
        f"site_url = {_quote(f'{SITE_URL}{language.url_path}/')}",
    )
    config = _replace_once(
        config, 'edit_uri = "edit/main/docs/"', f"edit_uri = {_quote(language.edit_uri)}"
    )
    config, count = NAV_PATTERN.subn(_nav(), config, count=1)
    if count != 1:
        msg = "could not replace the navigation block in zensical.toml"
        raise ValueError(msg)
    config = _replace_once(
        config,
        'html_language = "en"',
        f"html_language = {_quote(language.html_language)}",
    )
    config = _replace_once(config, 'language = "en"', f"language = {_quote(language.code)}")
    config = _replace_once(
        config,
        'copyright = "Copyright &copy; 2026 Yusuke Hayashi &middot; MIT License"',
        f"copyright = {_quote(str(COPYRIGHT))}",
    )
    config = _replace_once(
        config, 'toggle.name = "Switch to dark mode"', f"toggle.name = {_quote(str(DARK_MODE))}"
    )
    return _replace_once(
        config,
        'toggle.name = "Switch to light mode"',
        f"toggle.name = {_quote(str(LIGHT_MODE))}",
    )


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def _compile_catalogs(build_root: Path, selected: tuple[Language, ...]) -> Path:
    localedir = build_root / "locales"
    for language in LANGUAGES[1:]:
        target = localedir / language.locale / "LC_MESSAGES"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            ROOT / "i18n" / language.code / "LC_MESSAGES" / "site.po",
            target / "site.po",
        )

    pybabel = shutil.which("pybabel")
    if pybabel is None:
        msg = "pybabel is required; run this script through `uv run --group docs`"
        raise RuntimeError(msg)

    # The whole loop the documentation teaches, run on the documentation's own
    # catalogs: extract this file's messages into a template, refuse to go on if
    # any catalog has fallen behind it, then compile. The template is derived
    # here rather than committed — these catalogs are maintained in the
    # repository instead of round-tripped through a translation platform, so a
    # checked-in POT would be a second copy to keep in sync rather than the
    # hand-off it is on a project with outside translators.
    template = build_root / "site.pot"
    _run(
        [
            pybabel,
            "extract",
            "--mapping-file",
            str(ROOT / "babel.cfg"),
            "--add-comments",
            "Translators:",
            # File without line numbers: a translator gets a useful pointer and
            # the template stops churning every time this file grows a line.
            "--add-location",
            "file",
            "--output-file",
            str(template),
            str(Path("scripts") / "build_multilingual_docs.py"),
        ],
    )
    # Only the editions being built. Checking every catalog here would make
    # `--language xx` fail because some *other* language has not caught up yet,
    # which is precisely the situation while a new message is being translated.
    _check_catalogs_current(template, localedir, selected)
    _run([pybabel, "compile", "--domain", "site", "--directory", str(localedir)])
    return localedir


def _check_catalogs_current(
    template: Path,
    localedir: Path,
    selected: tuple[Language, ...],
) -> None:
    """Fail when a catalog has fallen behind the freshly extracted template.

    This is the job of ``pybabel update --check``, which cannot do it here.
    That flag decides by ``Catalog.is_identical``, which looks each message up
    with ``catalog.get(key)`` while ``key`` for a contextual message is the
    ``(id, context)`` tuple that ``get`` does not accept — so the lookup returns
    None and *any* catalog carrying a ``msgctxt`` compares as changed, forever.
    This site's navigation uses a context on purpose, so ``--check`` reports all
    of its catalogs stale on every run and can never gate anything.

    Reproduced on Babel 2.18.0:

        c = Catalog(locale="ja"); c.add("Guide", "ガイド", context="navigation")
        c.is_identical(c)  # False

    Comparing the message sets directly is what the flag was wanted for.
    """
    with template.open("rb") as file:
        expected = {(message.context, message.id) for message in read_po(file) if message.id}

    for language in selected:
        if language.code == "en":
            continue
        path = localedir / language.locale / "LC_MESSAGES" / "site.po"
        with path.open("rb") as file:
            catalog = read_po(file)
        found = {(message.context, message.id) for message in catalog if message.id}
        missing = sorted(str(key) for key in expected - found)
        unexpected = sorted(str(key) for key in found - expected)
        if missing or unexpected:
            msg = (
                f"{language.code} catalog is out of date with the extracted template; "
                f"missing {missing}, no longer in the source {unexpected}"
            )
            raise ValueError(msg)


def _stage_project(language: Language, build_root: Path) -> Path:
    project = build_root / language.code
    docs = project / "docs"
    shutil.copytree(language.source, docs)
    shutil.copytree(ROOT / "docs" / "assets", docs / "assets")
    shutil.copytree(ROOT / "docs" / "stylesheets", docs / "stylesheets")
    shutil.copy2(ROOT / "docs" / ".assetsignore", docs / ".assetsignore")
    shutil.copytree(ROOT / "overrides", project / "overrides")
    return project


def _localized_url(language: Language, page_url: str = "") -> str:
    prefix = f"/{language.url_path}/" if language.url_path else "/"
    return f"{prefix}{page_url}"


def _validate_build(language: Language) -> None:
    expected_direction = "rtl" if language.code in RTL_LANGUAGES else "ltr"
    pages = sorted(language.source.glob("*.md"))

    for source in pages:
        page_url = "" if source.stem == "index" else f"{source.stem}/"
        output = language.output / page_url / "index.html"
        html = output.read_text(encoding="utf-8")
        normalized_html = re.sub(r"\s+", " ", html)
        expected = {
            f'<html lang="{language.html_language}"',
            f'<body dir="{expected_direction}"',
            f'<link rel="canonical" href="{SITE_URL.removesuffix("/")}'
            f'{_localized_url(language, page_url)}">',
            'class="md-header__button md-icon md-language-switcher"',
            'class="md-language-switcher__label"',
        }
        expected.update(
            f'href="{_localized_url(alternate, page_url)}" hreflang="{alternate.html_language}"'
            for alternate in LANGUAGES
        )
        missing = sorted(fragment for fragment in expected if fragment not in normalized_html)
        if missing:
            msg = f"{output} is missing generated metadata: {missing}"
            raise ValueError(msg)
        if html.count('aria-current="page"') != 1:
            msg = f"{output} must mark exactly one current language"
            raise ValueError(msg)

    if not (language.output / "search.json").is_file():
        msg = f"{language.output} has no localized search index"
        raise ValueError(msg)


def _build(language: Language, localedir: Path, build_root: Path) -> None:
    started = time.perf_counter()
    zensical = shutil.which("zensical")
    if zensical is None:
        msg = "zensical is required; run this script through `uv run --group docs`"
        raise RuntimeError(msg)

    project: Path | None = None
    if language.code == "en":
        config = BASE_CONFIG
    else:
        project = _stage_project(language, build_root)
        config = project / "zensical.toml"
        config.write_text(
            _translated_config(language, localedir),
            encoding="utf-8",
        )
    _run([zensical, "build", "--config-file", str(config), "--clean", "--strict"])
    if project is not None:
        shutil.rmtree(language.output, ignore_errors=True)
        shutil.copytree(project / "site", language.output)
    _validate_build(language)

    translations = (
        gettext.NullTranslations()
        if language.code == "en"
        else gettext.translation("site", localedir=localedir, languages=[language.locale])
    )

    # Two roles, two shapes — the split a real project makes. A test suite binds
    # one catalog and asserts loudly, so the verification pass uses Translator
    # with strict=True and walks every plural form the language declares, not
    # just the one this build happens to need.
    verifier = Translator(translations, strict=True)
    for n in PLURAL_PROBES[language.code]:
        verifier.ngettext(t"Built {n} localized page", t"Built {n} localized pages", n)

    # The application itself renders through the bound context and the default
    # lenient mode, and never crashes a user over a catalog. _FailOnInvalidTranslation
    # is what makes that safe here: leniency reports rather than hides.
    #
    # The reported line carries a context and a format spec on purpose. The
    # context is what "page" needs to be translatable at all in languages where
    # the build-report sense and the document sense are different words; the
    # `:.2f` never reaches the catalog, so no translator sees it and no
    # translation can change it. The unit is written `s` rather than "seconds"
    # because a message may only agree with one count, and that count is n.
    with use_translations(translations):
        n = sum(1 for _ in language.source.glob("*.md"))
        seconds = time.perf_counter() - started
        LOGGER.info(
            npgettext(
                "build report",
                t"Rendered {n} page in {seconds:.2f}s",
                t"Rendered {n} pages in {seconds:.2f}s",
                n,
            ),
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("gettext_tstrings").addHandler(_FailOnInvalidTranslation())
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--language",
        choices=("all", *(language.code for language in LANGUAGES)),
        default="all",
        help="build all languages or one language (default: all)",
    )
    args = parser.parse_args()

    # Staging is scoped to the selection so that two single-language builds can
    # run at once — which is exactly how the translated editions get worked on.
    # Sharing one root meant each run wiped the other's staging mid-build, and
    # the loser died inside zensical with an unrelated-looking error.
    building_all = args.language == "all"
    build_root = (
        BUILD_ROOT if building_all else BUILD_ROOT.with_name(f"{BUILD_ROOT.name}-{args.language}")
    )
    shutil.rmtree(build_root, ignore_errors=True)
    build_root.mkdir(parents=True)

    selected = (
        LANGUAGES
        if building_all
        else tuple(language for language in LANGUAGES if language.code == args.language)
    )
    localedir = _compile_catalogs(build_root, selected)
    if building_all:
        shutil.rmtree(SITE_ROOT, ignore_errors=True)
    for language in selected:
        _build(language, localedir, build_root)


if __name__ == "__main__":
    main()
