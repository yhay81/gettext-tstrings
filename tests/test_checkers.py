from __future__ import annotations

import pytest
from babel.messages.catalog import Catalog, Message, TranslationError

from gettext_tstrings.checkers import check_tstring


def marked_message(
    message_id: str | tuple[str, str],
    translation: str | tuple[str, ...],
) -> Message:
    return Message(
        message_id,
        string=translation,
        auto_comments=["gettext-tstrings"],
    )


def test_checker_accepts_reordered_placeholders() -> None:
    message = marked_message(
        "{category} moved to {target}",
        "{target}へ{category}を移動しました",
    )

    check_tstring(Catalog(locale="ja"), message)


@pytest.mark.parametrize(
    "translation",
    [
        "{category}を移動しました",
        "{category}を{target}と{extra}へ移動しました",
        "{category}を{target!r}へ移動しました",
    ],
)
def test_checker_rejects_incompatible_placeholders(translation: str) -> None:
    message = marked_message("{category} moved to {target}", translation)

    with pytest.raises(TranslationError, match="placeholder"):
        check_tstring(Catalog(locale="ja"), message)


def test_checker_allows_repeating_a_known_placeholder() -> None:
    message = marked_message(
        "{category} moved to {target}",
        "{category}を{target}から{target}へ移動しました",
    )

    check_tstring(Catalog(locale="ja"), message)


def test_checker_validates_every_plural_form() -> None:
    message = marked_message(
        ("{n} file", "{n} files"),
        ("{n} файл", "{n} файла", "файлов"),
    )

    with pytest.raises(TranslationError, match="missing"):
        check_tstring(Catalog(locale="ru"), message)


def test_checker_allows_branch_specific_plural_placeholders() -> None:
    message = marked_message(
        ("One file", "{n} files"),
        ("{n} файл", "{n} файла", "{n} файлов"),
    )

    check_tstring(Catalog(locale="ru"), message)


def test_checker_ignores_unmarked_brace_messages() -> None:
    message = Message("{name}", string="{other}")

    check_tstring(None, message)


def test_checker_ignores_untranslated_entries() -> None:
    message = marked_message("{name}", "")

    check_tstring(None, message)


def test_checker_ignores_none_translation() -> None:
    message = Message(
        "{name}",
        string=None,
        auto_comments=["gettext-tstrings"],
    )

    check_tstring(None, message)
