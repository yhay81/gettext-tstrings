"""Shared brace-pattern parsing helpers."""

from __future__ import annotations

import keyword
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from string import Formatter

from .errors import InvalidTranslationError

MARKER_COMMENT = "gettext-tstrings"
_FORMATTER = Formatter()

# Japanese mixes kana with han, and Korean mixes hangul with han, as a matter of
# course. Treating those as "mixed scripts" would annotate ordinary names.
_EAST_ASIAN = ("HIRAGANA", "KATAKANA", "CJK", "HANGUL", "IDEOGRAPHIC")


def _scripts(name: str) -> set[str]:
    """Return the writing systems the letters of a name are drawn from."""
    found: set[str] = set()
    for character in name:
        if not character.isalpha():
            continue
        try:
            script = unicodedata.name(character).split()[0]
        except ValueError:  # pragma: no cover - unnamed characters are not letters
            script = "?"
        found.add("EAST ASIAN" if script.startswith(_EAST_ASIAN) else script)
    return found


def show_name(name: str) -> str:
    """Render a placeholder name for a message the way a translator can act on.

    Three cases, and the reason for each:

    - A name holding something invisible — a no-break space, a zero-width space,
      a soft hyphen — is shown with that character replaced in place by its code
      point. Saying ``{name} has a space in it`` about a name that reads exactly
      ``{name}`` is a dead end for the reader; they need to see *where*.
    - A name whose letters come from more than one writing system, or that
      changes under NFKC, gets an escaped form alongside the readable one. This
      is the homoglyph case: a name spelled with a Cyrillic instead of a Latin
      "a" is indistinguishable from ``{name}`` on screen, and only the escaped
      form tells the two apart.
    - Everything else is shown as written. ``{名前}`` and ``{café}`` are ordinary
      names; escaping them would leave a reader unable to find what was meant.
    """
    if not name.isprintable():
        visible = "".join(c if c.isprintable() else f"<U+{ord(c):04X}>" for c in name)
        return f"{{{visible}}}"
    if unicodedata.normalize("NFKC", name) != name or len(_scripts(name)) > 1:
        return f"{{{name}}} ({ascii(name).strip(chr(39))})"
    return f"{{{name}}}"


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
            f"placeholder {show_name(name)} must be a plain name, "
            "copied from the source message unchanged",
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
                    f"placeholder {show_name(field_name)} has a space inside the "
                    f"braces; write {show_name(field_name.strip())}",
                )
            name = validate_name(field_name)
            fields.add(name)
            chunks.append((literal, name))
        modified = _modified_field_name(pattern)
        if modified is not None:
            raise InvalidTranslationError(
                f"placeholder {{{modified}}} adds formatting; write "
                f"{show_name(modified.split(chr(33))[0].split(chr(58))[0])} on its own, "
                "because the source message decides how the value is formatted",
            )
    except InvalidTranslationError:
        # Already this package's own diagnosis. Re-wrapping would stack a
        # generic prefix on a specific sentence and leave a __cause__ that
        # repeats it, which pytest then prints as two tracebacks.
        raise
    except (TypeError, ValueError) as exc:
        # TypeError means a Translations implementation returned something
        # other than str — dict.get(...) returning None, typically. Letting it
        # escape would crash the render outside the strict/lenient switch,
        # breaking the promise that a broken catalog never does (SPEC §5).
        raise InvalidTranslationError(f"invalid translation pattern: {exc}") from exc
    return Pattern(tuple(chunks), frozenset(fields))


# Braces a translator can end up with instead of the ASCII pair: the full-width
# ones an East Asian input method produces by default, and the small and
# ornamental forms. Enough to explain the mistakes that actually happen.
# ruff flags these as ambiguous, which is exactly why the table exists.
_LOOKALIKE_BRACES = str.maketrans(
    {"｛": "{", "｝": "}", "﹛": "{", "﹜": "}", "❴": "{", "❵": "}"},  # noqa: RUF001
)


def _why_missing(name: str, pattern: str) -> str:
    """Explain a placeholder the translation seems to contain but does not.

    Reporting only that ``{name}`` is missing is a dead end when the reader can
    see those very characters in front of them, which is what happens when an
    input method supplied full-width braces or a round trip doubled them.
    """
    if f"{{{{{name}}}}}" in pattern:
        return f" (it is written {{{{{name}}}}}, which is how a literal brace is escaped)"
    if f"{{{name}}}" in pattern.translate(_LOOKALIKE_BRACES):
        return " (the braces around it are not the ASCII { and })"
    if name in pattern:
        return " (the name appears, but not inside braces)"
    return ""


def require_fields(
    *,
    required: frozenset[str],
    allowed: frozenset[str],
    actual: frozenset[str],
    pattern: str = "",
) -> None:
    """Require all necessary fields and reject unknown ones.

    Placeholder occurrence counts are deliberately unrestricted: repeating a
    known value can be grammatically necessary in a target language.

    ``pattern`` is the translation being checked. It is only read to explain a
    missing placeholder, so callers that have nothing useful to pass may omit it.
    """
    missing = required - actual
    unexpected = actual - allowed
    if not missing and not unexpected:
        return

    details = [f"{show_name(n)} is missing{_why_missing(n, pattern)}" for n in sorted(missing)]
    details += [f"{show_name(n)} is not in the source message" for n in sorted(unexpected)]
    raise InvalidTranslationError(
        f"translation does not match the source placeholders: {'; '.join(details)}",
    )
