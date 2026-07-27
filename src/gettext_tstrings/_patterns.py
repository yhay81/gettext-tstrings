"""Shared brace-pattern parsing helpers."""

from __future__ import annotations

import keyword
from dataclasses import dataclass
from functools import lru_cache
from string import Formatter

from .errors import InvalidTranslationError

MARKER_COMMENT = "gettext-tstrings"
_FORMATTER = Formatter()


@dataclass(frozen=True, slots=True)
class Pattern:
    """A validated, cached translation pattern."""

    chunks: tuple[tuple[str, str | None], ...]
    fields: frozenset[str]


def escape_literal(text: str) -> str:
    """Escape braces in literal t-string segments for a brace-format pattern."""
    return text.replace("{", "{{").replace("}", "}}")


def validate_name(name: str) -> str:
    """Return a safe, simple placeholder name or raise."""
    normalized = name.strip()
    if not normalized.isidentifier() or keyword.iskeyword(normalized):
        raise InvalidTranslationError(
            f"placeholder {name!r} is not a simple Python identifier",
        )
    return normalized


@lru_cache(maxsize=4096)
def parse_pattern(pattern: str) -> Pattern:
    """Parse and cache a restricted brace pattern.

    Only bare named placeholders are accepted. Formatting and conversion are
    controlled by the source t-string and never by a catalog translation.
    """
    chunks: list[tuple[str, str | None]] = []
    fields: set[str] = set()
    try:
        for literal, field_name, format_spec, conversion in _FORMATTER.parse(pattern):
            if field_name is None:
                chunks.append((literal, None))
                continue

            name = validate_name(field_name)
            if format_spec or conversion:
                raise InvalidTranslationError(
                    f"translation placeholder {{{name}}} must not add "
                    "a conversion or format specifier",
                )
            fields.add(name)
            chunks.append((literal, name))
    except ValueError as exc:
        raise InvalidTranslationError(f"invalid translation pattern: {exc}") from exc
    return Pattern(tuple(chunks), frozenset(fields))


def require_fields(
    *,
    required: frozenset[str],
    allowed: frozenset[str],
    actual: frozenset[str],
    label: str = "translation",
) -> None:
    """Require all necessary fields and reject unknown ones.

    Placeholder occurrence counts are deliberately unrestricted: repeating a
    known value can be grammatically necessary in a target language.
    """
    missing = required - actual
    unexpected = actual - allowed
    if not missing and not unexpected:
        return

    details: list[str] = []
    if missing:
        details.append(f"missing {sorted(missing)!r}")
    if unexpected:
        details.append(f"unexpected {sorted(unexpected)!r}")
    raise InvalidTranslationError(
        f"{label} placeholders do not match source: {', '.join(details)}",
    )
