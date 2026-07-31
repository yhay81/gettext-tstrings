"""Catalog checker for messages emitted by the t-string extractor."""

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

    # A fuzzy entry is an unconfirmed machine guess that ``pybabel compile``
    # leaves out of the ``.mo``, so it can never reach a render. Reporting it
    # would make the compile step fail for as long as a reworded message waits
    # on a translator — a permanently red gate, which is the failure mode this
    # project's own documentation warns about — and it is loudest exactly when
    # a project is migrating from ``%``-format, where every carried-over
    # translation is fuzzy by construction. GNU ``msgfmt --check-format``
    # skips them for the same reason.
    if message.fuzzy:
        return

    source_patterns = _strings(message.id)
    if not source_patterns:
        return

    try:
        source_fields = [parse_pattern(pattern).fields for pattern in source_patterns]
        allowed = frozenset().union(*source_fields)
        required = frozenset.intersection(*source_fields)

        # Babel reports the msgid's line, so a plural block gives no clue which
        # form is at fault. Name it, exactly as msgfmt does for the same reason.
        # A singular block has one msgstr directly below, and needs no pointer.
        plural = not isinstance(message.id, str)
        for index, translation in enumerate(_strings(message.string)):
            if not translation:
                continue
            try:
                require_fields(
                    required=required,
                    allowed=allowed,
                    actual=parse_pattern(translation).fields,
                    pattern=translation,
                )
            except InvalidTranslationError as exc:
                slot = f"msgstr[{index}]: " if plural else ""
                raise TranslationError(f"{slot}{exc}") from exc
    except InvalidTranslationError as exc:
        raise TranslationError(str(exc)) from exc
