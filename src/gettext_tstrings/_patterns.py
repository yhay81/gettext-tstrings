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


def _has_explicit_field_modifier(pattern: str) -> bool:
    """単一波括弧のフィールド内に ``!`` または ``:`` があるかを返す。

    ``Formatter.parse()`` は ``{name}`` と ``{name:}`` のformat_specを
    どちらも空文字列にするため、後者だけは元パターンから補う必要がある。
    二重波括弧内はリテラルなので読み飛ばす。
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
        while index < len(pattern) and pattern[index] != "}":
            if pattern[index] in "!:":
                return True
            index += 1
        index += 1
    return False


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

            # 翻訳側では式のstripを行わない。``{ name }`` は str.format も
            # msgfmt も拒否する非python-brace-formatなので、ここで弾かないと
            # 既存ツールが検証できないパターンを通してしまう。
            if field_name != field_name.strip():
                raise InvalidTranslationError(
                    f"translation placeholder {{{field_name}}} must not pad its name "
                    "with whitespace",
                )
            name = validate_name(field_name)
            if format_spec or conversion:
                raise InvalidTranslationError(
                    f"translation placeholder {{{name}}} must not add "
                    "a conversion or format specifier",
                )
            fields.add(name)
            chunks.append((literal, name))
        if _has_explicit_field_modifier(pattern):
            raise InvalidTranslationError(
                "translation placeholders must not add a conversion or format specifier",
            )
    except (TypeError, ValueError) as exc:
        # TypeError は Translations 実装が str 以外(dict.get の None など)を
        # 返したとき。生のまま漏らすと strict/lenient の外でアプリが落ち、
        # 「壊れたカタログは描画を落とさない」契約(SPEC §5)から外れる。
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

    # 非ASCIIのホモグリフ名はASCII名と見分けがつかないため、
    # 各名前を ascii() で可視化してから並べる。
    details: list[str] = []
    if missing:
        details.append(f"missing [{', '.join(ascii(n) for n in sorted(missing))}]")
    if unexpected:
        details.append(f"unexpected [{', '.join(ascii(n) for n in sorted(unexpected))}]")
    raise InvalidTranslationError(
        f"{label} placeholders do not match source: {', '.join(details)}",
    )
