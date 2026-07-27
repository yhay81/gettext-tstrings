"""Public exceptions raised by babel-tstrings."""


class TStringError(ValueError):
    """Base class for invalid t-strings and translations."""


class InvalidTemplateError(TStringError):
    """The source t-string cannot be represented safely as a gettext message."""


class InvalidTranslationError(TStringError):
    """A translated message has invalid or incompatible placeholders."""
