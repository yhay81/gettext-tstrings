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


def _modified_field_name(pattern: str) -> str | None:
    """Return the first field name carrying a conversion or format spec, else None.

    ``Formatter.parse()`` reports an empty format spec for both ``{name}`` and
    ``{name:}``, so whether a field carries a modifier can only be read off the
    original pattern. Since that scan has to happen anyway, it is the only
    detector: what ``Formatter`` reports adds nothing. Doubled braces are
    literal text and are skipped.
    """
    index = 0
    while index < len(pattern):
        if pattern[index] != "{":
            index += 1
            continue
        if index + 1 < len(pattern) and pattern[index + 1] == "{":
            index += 2
            continue

        index += 1
        start = index
        while index < len(pattern) and pattern[index] != "}":
            if pattern[index] in "!:":
                return pattern[start:index]
            index += 1
        index += 1
    return None


@lru_cache(maxsize=4096)
def parse_pattern(pattern: str) -> Pattern:
    """Parse and cache a restricted brace pattern.

    Only bare named placeholders are accepted. Formatting and conversion are
    controlled by the source t-string and never by a catalog translation.
    """
    chunks: list[tuple[str, str | None]] = []
    fields: set[str] = set()
    try:
        # _modified_field_name reads modifiers off the original pattern, so the
        # format spec and conversion Formatter reports here go unused.
        for literal, field_name, _spec, _conversion in _FORMATTER.parse(pattern):
            if field_name is None:
                chunks.append((literal, None))
                continue

            # Do not strip the name on the translation side. ``{ name }`` is
            # not python-brace-format: both str.format and msgfmt reject it, so
            # accepting it here would emit patterns no existing tool validates.
            if field_name != field_name.strip():
                raise InvalidTranslationError(
                    f"translation placeholder {{{field_name}}} must not pad its name "
                    "with whitespace",
                )
            name = validate_name(field_name)
            fields.add(name)
            chunks.append((literal, name))
        modified = _modified_field_name(pattern)
        if modified is not None:
            raise InvalidTranslationError(
                f"translation placeholder {{{modified}}} must not add "
                "a conversion or format specifier",
            )
    except (TypeError, ValueError) as exc:
        # TypeError means a Translations implementation returned something
        # other than str — dict.get(...) returning None, typically. Letting it
        # escape would crash the render outside the strict/lenient switch,
        # breaking the promise that a broken catalog never does (SPEC §5).
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

    # A non-ASCII homoglyph is indistinguishable from its ASCII lookalike, so
    # each name is escaped with ascii() before it is shown.
    details: list[str] = []
    if missing:
        details.append(f"missing [{', '.join(ascii(n) for n in sorted(missing))}]")
    if unexpected:
        details.append(f"unexpected [{', '.join(ascii(n) for n in sorted(unexpected))}]")
    raise InvalidTranslationError(
        f"{label} placeholders do not match source: {', '.join(details)}",
    )
