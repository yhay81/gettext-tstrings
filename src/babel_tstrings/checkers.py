"""Babel catalog checker for messages emitted by the t-string extractor."""

from __future__ import annotations

from collections.abc import Iterable

from babel.messages.catalog import Catalog, Message, TranslationError

from ._patterns import MARKER_COMMENT, parse_pattern, require_fields
from .errors import InvalidTranslationError


def _strings(value: str | Iterable[str] | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def check_tstring(catalog: Catalog | None, message: Message) -> None:
    """Validate placeholder integrity for extracted t-string messages."""
    del catalog
    if MARKER_COMMENT not in message.auto_comments:
        return

    source_patterns = _strings(message.id)
    try:
        source_fields = [parse_pattern(pattern).fields for pattern in source_patterns]
        allowed = frozenset().union(*source_fields)
        required = frozenset.intersection(*source_fields)

        for translation in _strings(message.string):
            if not translation:
                continue
            require_fields(
                required=required,
                allowed=allowed,
                actual=parse_pattern(translation).fields,
            )
    except InvalidTranslationError as exc:
        raise TranslationError(str(exc)) from exc
