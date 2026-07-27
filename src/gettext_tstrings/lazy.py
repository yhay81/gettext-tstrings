"""Deferred t-string translation for strings defined before a language is known.

Module-level labels, form fields, and enum values are created at import time but
must render in the language chosen per request. A t-string captures its values
eagerly; :class:`LazyString` defers only the catalog lookup and rendering to the
moment the string is used, resolving the translations bound to the current
context (see :func:`gettext_tstrings.use_translations`).
"""

from __future__ import annotations

from collections.abc import Callable
from string.templatelib import Template

from .core import get_translations, gettext, pgettext


class LazyString:
    """A translatable string that renders when first used, not when defined.

    Deliberately unhashable: the rendered text depends on the language active at
    call time, so a hash would silently change across language switches and
    corrupt sets and dict keys. Call ``str()`` first to use one as a key.
    """

    __slots__ = ("_render",)

    __hash__ = None  # type: ignore[assignment]

    def __init__(self, render: Callable[[], str]) -> None:
        self._render = render

    def __str__(self) -> str:
        return self._render()

    def __format__(self, format_spec: str) -> str:
        return format(self._render(), format_spec)

    def __repr__(self) -> str:
        return f"LazyString({str(self)!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LazyString):
            return str(self) == str(other)
        if isinstance(other, str):
            return str(self) == other
        return NotImplemented


def lazy_gettext(template: Template, /) -> LazyString:
    """Defer translation of one t-string to first use."""
    return LazyString(lambda: gettext(template, translations=get_translations()))


def lazy_pgettext(context: str, template: Template, /) -> LazyString:
    """Defer translation of one contextual t-string to first use."""
    return LazyString(lambda: pgettext(context, template, translations=get_translations()))
