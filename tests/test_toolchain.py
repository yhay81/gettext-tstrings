"""End-to-end tests that run the real toolchain (pybabel / msgfmt).

They back the README's central claim — that existing gettext tools can validate
this catalog — with actual runs rather than with prose. The unit tests only look
as far as the extractor's return value, so this is the only path that drives
Babel's frontend for real.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from babel.messages.frontend import CommandLineInterface

SOURCE = """\
from gettext_tstrings import ntr, pgettext, tr


def demo(name, n, filename):
    # Translators: Shown on the home page.
    a = tr(t"Hello {name}")
    b = ntr(t"One file", t"{n} files", n)
    c = pgettext("button", t"Open {filename}")
    d = tr(t"Total: {amount:,.2f}")
    e = _("Plain gettext call")
    return a, b, c, d, e
"""


def _project(tmp_path: Path) -> Path:
    (tmp_path / "babel.cfg").write_text("[gettext_tstrings: **.py]\n", encoding="utf-8")
    (tmp_path / "app.py").write_text(SOURCE, encoding="utf-8")
    return tmp_path


def _extract(tmp_path: Path) -> str:
    pot = tmp_path / "messages.pot"
    # Babel ships no annotations for its frontend.
    exit_code = CommandLineInterface().run(  # type: ignore[no-untyped-call]
        [
            "pybabel",
            "extract",
            "-F",
            str(tmp_path / "babel.cfg"),
            "-c",
            "Translators:",
            "-o",
            str(pot),
            str(tmp_path),
        ],
    )
    assert exit_code in (0, None)
    return pot.read_text(encoding="utf-8")


def test_pybabel_extract_produces_a_standard_pot(tmp_path: Path) -> None:
    pot = _extract(_project(tmp_path))

    # t-string messages, plurals, msgctxt, and plain gettext calls all come through.
    assert 'msgid "Hello {name}"' in pot
    assert 'msgid "One file"' in pot
    assert 'msgid_plural "{n} files"' in pot
    assert 'msgctxt "button"' in pot
    assert 'msgid "Open {filename}"' in pot
    assert 'msgid "Plain gettext call"' in pot
    # Format specs never reach the catalog.
    assert 'msgid "Total: {amount}"' in pot
    assert ":,.2f" not in pot
    # Translator comments and the automatic marker.
    assert "#. Translators: Shown on the home page." in pot
    assert "#. gettext-tstrings" in pot


def test_extracted_messages_carry_the_python_brace_format_flag(tmp_path: Path) -> None:
    # This flag is what enables validation in GNU msgfmt and Weblate. The README's
    # claim rests on it.
    pot = _extract(_project(tmp_path))

    for block in pot.split("\n\n"):
        if 'msgid "Hello {name}"' in block or 'msgid "Open {filename}"' in block:
            assert "#, python-brace-format" in block


@pytest.mark.skipif(shutil.which("msgfmt") is None, reason="GNU gettext-tools not installed")
def test_gnu_msgfmt_rejects_a_broken_translation(tmp_path: Path) -> None:
    # The msgfmt transcript printed in the README really does reproduce.
    po = tmp_path / "ja.po"
    po.write_text(
        'msgid ""\n'
        'msgstr "Content-Type: text/plain; charset=UTF-8\\n"\n'
        "\n"
        "#, python-brace-format\n"
        'msgid "Hello {name}"\n'
        'msgstr "こんにちは {wrong}"\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [shutil.which("msgfmt") or "msgfmt", "--check-format", "-o", "/dev/null", str(po)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "format specification" in result.stderr


@pytest.mark.skipif(shutil.which("msgfmt") is None, reason="GNU gettext-tools not installed")
def test_gnu_msgfmt_accepts_a_reordered_translation(tmp_path: Path) -> None:
    # A correct translation that reorders the placeholders passes — the check is not
    # over-strict.
    po = tmp_path / "ja.po"
    po.write_text(
        'msgid ""\n'
        'msgstr "Content-Type: text/plain; charset=UTF-8\\n"\n'
        "\n"
        "#, python-brace-format\n"
        'msgid "Category {category} moved to {target}"\n'
        'msgstr "{target}へ{category}を移動しました"\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [shutil.which("msgfmt") or "msgfmt", "--check-format", "-o", "/dev/null", str(po)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(shutil.which("msgfmt") is None, reason="GNU gettext-tools not installed")
def test_the_shipped_checker_catches_what_msgfmt_lets_through(tmp_path: Path) -> None:
    # When only one plural form drops a placeholder, GNU msgfmt --check-format lets it
    # through. The shipped checker takes the strict side here.
    po = tmp_path / "messages.po"
    po.write_text(
        'msgid ""\n'
        'msgstr "Content-Type: text/plain; charset=UTF-8\\n'
        'Plural-Forms: nplurals=2; plural=(n!=1);\\n"\n'
        "\n"
        "#. gettext-tstrings\n"
        "#, python-brace-format\n"
        'msgid "{n} file"\n'
        'msgid_plural "{n} files"\n'
        'msgstr[0] "ファイル"\n'
        'msgstr[1] "{n} 個のファイル"\n',
        encoding="utf-8",
    )

    msgfmt = subprocess.run(
        [shutil.which("msgfmt") or "msgfmt", "--check-format", "-o", "/dev/null", str(po)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert msgfmt.returncode == 0, "if msgfmt starts rejecting this, this test's premise changes"

    locale_dir = tmp_path / "locales" / "ja" / "LC_MESSAGES"
    locale_dir.mkdir(parents=True)
    (locale_dir / "messages.po").write_text(po.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = CommandLineInterface().run(  # type: ignore[no-untyped-call]
        ["pybabel", "compile", "-d", str(tmp_path / "locales"), "-l", "ja"],
    )

    assert exit_code not in (0, None)


def test_pybabel_compile_runs_the_shipped_checker(tmp_path: Path) -> None:
    # The shipped checker really is invoked on the pybabel compile path, and it catches
    # a t-string-specific violation: a format spec on the translation side.
    locale_dir = tmp_path / "locales" / "ja" / "LC_MESSAGES"
    locale_dir.mkdir(parents=True)
    (locale_dir / "messages.po").write_text(
        'msgid ""\n'
        'msgstr "Content-Type: text/plain; charset=UTF-8\\n'
        'Plural-Forms: nplurals=1; plural=0;\\n"\n'
        "\n"
        "#. gettext-tstrings\n"
        "#, python-brace-format\n"
        'msgid "Hello {name}"\n'
        'msgstr "{name:>20}さん"\n',
        encoding="utf-8",
    )

    exit_code = CommandLineInterface().run(  # type: ignore[no-untyped-call]
        ["pybabel", "compile", "-d", str(tmp_path / "locales"), "-l", "ja"],
    )

    assert exit_code not in (0, None)
