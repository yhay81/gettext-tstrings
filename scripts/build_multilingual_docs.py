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
from dataclasses import dataclass
from pathlib import Path

from gettext_tstrings import Translator

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


@dataclass(frozen=True, slots=True)
class Chrome:
    description: str
    home: str
    tutorial: str
    comparison: str
    guide: str
    extraction: str
    specification: str
    api: str
    dark_mode: str
    light_mode: str
    copyright: str


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
)

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
}


def _quote(value: str | Path) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _chrome(translations: gettext.NullTranslations) -> Chrome:
    _ = Translator(translations, strict=True)
    author = "Yusuke Hayashi"
    return Chrome(
        description=_(t"Safe gettext and Babel integration for Python t-strings."),
        home=_(t"Home"),
        tutorial=_(t"Tutorial"),
        comparison=_(t"Why t-strings"),
        guide=_.pgettext("navigation", t"Guide"),
        extraction=_(t"Extraction"),
        specification=_(t"Specification"),
        api=_(t"API"),
        dark_mode=_(t"Switch to dark mode"),
        light_mode=_(t"Switch to light mode"),
        copyright=_(t"Copyright © 2026 {author} · MIT License"),
    )


def _nav(chrome: Chrome) -> str:
    entries = (
        (chrome.home, "index.md"),
        (chrome.tutorial, "tutorial.md"),
        (chrome.comparison, "comparison.md"),
        (chrome.guide, "guide.md"),
        (chrome.extraction, "extraction.md"),
        (chrome.specification, "spec.md"),
        (chrome.api, "api.md"),
    )
    lines = ["nav = ["]
    lines.extend(f"  {{ {_quote(label)} = {_quote(path)} }}," for label, path in entries)
    lines.append("]\n")
    return "\n".join(lines)


def _replace_once(config: str, old: str, new: str) -> str:
    if config.count(old) != 1:
        msg = f"expected one occurrence in zensical.toml: {old!r}"
        raise ValueError(msg)
    return config.replace(old, new)


def _translated_config(language: Language, translations: Path) -> str:
    chrome = _chrome(
        gettext.translation("site", localedir=translations, languages=[language.locale])
    )
    config = BASE_CONFIG.read_text(encoding="utf-8")
    config = _replace_once(
        config,
        "[project]\n",
        '[project]\ndocs_dir = "docs"\nsite_dir = "site"\n',
    )
    config = _replace_once(
        config,
        'site_description = "Safe gettext and Babel integration for Python t-strings."',
        f"site_description = {_quote(chrome.description)}",
    )
    config = _replace_once(
        config,
        f'site_url = "{SITE_URL}"',
        f"site_url = {_quote(f'{SITE_URL}{language.url_path}/')}",
    )
    config = _replace_once(
        config, 'edit_uri = "edit/main/docs/"', f"edit_uri = {_quote(language.edit_uri)}"
    )
    config, count = NAV_PATTERN.subn(_nav(chrome), config, count=1)
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
        f"copyright = {_quote(chrome.copyright)}",
    )
    config = _replace_once(
        config, 'toggle.name = "Switch to dark mode"', f"toggle.name = {_quote(chrome.dark_mode)}"
    )
    return _replace_once(
        config,
        'toggle.name = "Switch to light mode"',
        f"toggle.name = {_quote(chrome.light_mode)}",
    )


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def _compile_catalogs() -> Path:
    localedir = BUILD_ROOT / "locales"
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
    _run([pybabel, "compile", "--domain", "site", "--directory", str(localedir)])
    return localedir


def _stage_project(language: Language) -> Path:
    project = BUILD_ROOT / language.code
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
    expected_direction = "rtl" if language.code == "ar" else "ltr"
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


def _build(language: Language, localedir: Path) -> None:
    zensical = shutil.which("zensical")
    if zensical is None:
        msg = "zensical is required; run this script through `uv run --group docs`"
        raise RuntimeError(msg)

    project: Path | None = None
    if language.code == "en":
        config = BASE_CONFIG
    else:
        project = _stage_project(language)
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
    _ = Translator(translations, strict=True)
    for n in PLURAL_PROBES[language.code]:
        _.ngettext(t"Built {n} localized page", t"Built {n} localized pages", n)
    n = sum(1 for _ in language.source.glob("*.md"))
    LOGGER.info(_.ngettext(t"Built {n} localized page", t"Built {n} localized pages", n))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--language",
        choices=("all", *(language.code for language in LANGUAGES)),
        default="all",
        help="build all languages or one language (default: all)",
    )
    args = parser.parse_args()

    shutil.rmtree(BUILD_ROOT, ignore_errors=True)
    BUILD_ROOT.mkdir(parents=True)
    localedir = _compile_catalogs()

    selected = (
        LANGUAGES
        if args.language == "all"
        else tuple(language for language in LANGUAGES if language.code == args.language)
    )
    if args.language == "all":
        shutil.rmtree(SITE_ROOT, ignore_errors=True)
    for language in selected:
        _build(language, localedir)


if __name__ == "__main__":
    main()
