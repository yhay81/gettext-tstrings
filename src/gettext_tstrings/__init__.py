"""Gettext and extraction-tool integration for Python t-strings."""

from .core import (
    CompiledTemplate,
    Translations,
    Translator,
    compile_template,
    get_translations,
    gettext,
    ngettext,
    npgettext,
    ntr,
    pgettext,
    set_translations,
    tr,
    use_translations,
)
from .errors import InvalidTemplateError, InvalidTranslationError, TStringError
from .lazy import LazyString, lazy_gettext, lazy_pgettext

__all__ = [
    "CompiledTemplate",
    "InvalidTemplateError",
    "InvalidTranslationError",
    "LazyString",
    "TStringError",
    "Translations",
    "Translator",
    "compile_template",
    "get_translations",
    "gettext",
    "lazy_gettext",
    "lazy_pgettext",
    "ngettext",
    "npgettext",
    "ntr",
    "pgettext",
    "set_translations",
    "tr",
    "use_translations",
]

__version__ = "0.1.0a1"
