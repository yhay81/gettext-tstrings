"""Gettext and extraction-tool integration for Python t-strings."""

from .core import (
    CompiledTemplate,
    Translations,
    Translator,
    compile_template,
    gettext,
    ngettext,
    npgettext,
    ntr,
    pgettext,
    tr,
)
from .errors import InvalidTemplateError, InvalidTranslationError, TStringError

__all__ = [
    "CompiledTemplate",
    "InvalidTemplateError",
    "InvalidTranslationError",
    "TStringError",
    "Translations",
    "Translator",
    "compile_template",
    "gettext",
    "ngettext",
    "npgettext",
    "ntr",
    "pgettext",
    "tr",
]

__version__ = "0.1.0a1"
