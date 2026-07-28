"""実ツールチェーン(pybabel / msgfmt)を通したend-to-endテスト。

READMEの中心的な主張 — 「既存のgettextツールがこのカタログを検証できる」 —
を、ドキュメントの記述ではなく実行結果で裏づける。単体テストは抽出器の
戻り値までしか見ないので、Babelのフロントエンドを実際に走らせる経路は
ここにしかない。
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

    # t-stringメッセージ、複数形、msgctxt、通常のgettext呼び出しが揃うこと。
    assert 'msgid "Hello {name}"' in pot
    assert 'msgid "One file"' in pot
    assert 'msgid_plural "{n} files"' in pot
    assert 'msgctxt "button"' in pot
    assert 'msgid "Open {filename}"' in pot
    assert 'msgid "Plain gettext call"' in pot
    # 書式指定はカタログへ出ない。
    assert 'msgid "Total: {amount}"' in pot
    assert ":,.2f" not in pot
    # 翻訳者コメントと自動マーカー。
    assert "#. Translators: Shown on the home page." in pot
    assert "#. gettext-tstrings" in pot


def test_extracted_messages_carry_the_python_brace_format_flag(tmp_path: Path) -> None:
    # このフラグがGNU msgfmtやWeblateの検証を有効にする。READMEの主張の要。
    pot = _extract(_project(tmp_path))

    for block in pot.split("\n\n"):
        if 'msgid "Hello {name}"' in block or 'msgid "Open {filename}"' in block:
            assert "#, python-brace-format" in block


@pytest.mark.skipif(shutil.which("msgfmt") is None, reason="GNU gettext-tools not installed")
def test_gnu_msgfmt_rejects_a_broken_translation(tmp_path: Path) -> None:
    # READMEに載せているmsgfmtのトランスクリプトが実際に再現すること。
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
    # 語順を入れ替えた正しい翻訳は通ること(拒否が厳しすぎないことの確認)。
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
    # 複数形の一形式だけがプレースホルダを落とした場合、GNU msgfmt の
    # --check-format は通してしまう。同梱チェッカーはここで厳しい側に立つ。
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
    assert msgfmt.returncode == 0, "この形をmsgfmtが弾くようになったら本テストの前提が変わる"

    locale_dir = tmp_path / "locales" / "ja" / "LC_MESSAGES"
    locale_dir.mkdir(parents=True)
    (locale_dir / "messages.po").write_text(po.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = CommandLineInterface().run(  # type: ignore[no-untyped-call]
        ["pybabel", "compile", "-d", str(tmp_path / "locales"), "-l", "ja"],
    )

    assert exit_code not in (0, None)


def test_pybabel_compile_runs_the_shipped_checker(tmp_path: Path) -> None:
    # 同梱チェッカーがpybabel compileの経路で実際に呼ばれ、
    # t-string固有の規則違反(翻訳側の書式指定)を検出すること。
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
