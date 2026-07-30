from __future__ import annotations

import gettext
from collections.abc import Callable

import pytest

from gettext_tstrings import Translator, npgettext, ntr, pgettext, tr


def test_japanese_catalog(load_translations: Callable[[str], gettext.GNUTranslations]) -> None:
    translations = load_translations("ja")
    name = "Ada"
    n = 3

    assert tr(t"Hello {name}", translations=translations) == "Adaさん、こんにちは"
    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == "3個のファイル"


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (1, "1 файл"),
        (2, "2 файла"),
        (5, "5 файлов"),
        (21, "21 файл"),
    ],
)
def test_russian_plural_catalog(
    load_translations: Callable[[str], gettext.GNUTranslations],
    n: int,
    expected: str,
) -> None:
    translations = load_translations("ru")

    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == expected


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (0, "0 ملفات"),  # zero form  (n == 0)
        (1, "1 ملف"),  # one form   (n == 1)
        (2, "2 ملفان"),  # two form   (n == 2)
        (3, "3 ملفات"),  # few form   (n%100 in 3..10)
        (11, "11 ملفًا"),  # many form  (n%100 in 11..99)
        (100, "100 ملف"),  # other form (n%100 == 0, i.e. 100, 200, …)
    ],
)
def test_arabic_plural_catalog(
    load_translations: Callable[[str], gettext.GNUTranslations],
    n: int,
    expected: str,
) -> None:
    translations = load_translations("ar")

    assert ntr(t"{n} file", t"{n} files", n, translations=translations) == expected


def test_translator_with_real_mo(
    load_translations: Callable[[str], gettext.GNUTranslations],
) -> None:
    t_ = Translator(load_translations("ja"))
    name = "Grace"

    assert t_.tr(t"Hello {name}") == "Graceさん、こんにちは"


def test_context_catalog(load_translations: Callable[[str], gettext.GNUTranslations]) -> None:
    translations = load_translations("ja")
    name = "report.txt"
    n = 1

    assert pgettext("button", t"Open {name}", translations=translations) == "report.txtを開く"
    assert (
        npgettext(
            "inbox",
            t"One message",
            t"{n} messages",
            n,
            translations=translations,
        )
        == "1件のメッセージ"
    )


def test_bound_context_catalog(
    load_translations: Callable[[str], gettext.GNUTranslations],
) -> None:
    translator = Translator(load_translations("ja"))
    name = "report.txt"

    assert translator.pgettext("button", t"Open {name}") == "report.txtを開く"
