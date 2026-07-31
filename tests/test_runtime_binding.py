from __future__ import annotations

import gettext

import pytest

from gettext_tstrings import (
    InvalidTranslationError,
    LazyString,
    Translations,
    get_translations,
    lazy_gettext,
    lazy_pgettext,
    set_translations,
    tr,
    use_translations,
)


class StubTranslations(gettext.NullTranslations):
    def __init__(self, messages: dict[object, str]) -> None:
        super().__init__()
        self.messages = messages

    def gettext(self, message: str) -> str:
        return self.messages.get(message, message)

    def pgettext(self, context: str, message: str) -> str:
        return self.messages.get((context, message), message)


def test_use_translations_binds_and_restores_context() -> None:
    name = "Ada"
    ja = StubTranslations({"Hello {name}": "{name}さん、こんにちは"})

    assert tr(t"Hello {name}") == "Hello Ada"
    with use_translations(ja):
        assert tr(t"Hello {name}") == "Adaさん、こんにちは"
        assert get_translations() is ja
    assert tr(t"Hello {name}") == "Hello Ada"
    assert get_translations() is None


def test_explicit_translations_override_the_context() -> None:
    name = "Ada"
    context_catalog = StubTranslations({"Hello {name}": "context {name}"})
    explicit_catalog = StubTranslations({"Hello {name}": "explicit {name}"})

    with use_translations(context_catalog):
        assert tr(t"Hello {name}", translations=explicit_catalog) == "explicit Ada"


def test_set_translations_binds_without_a_block() -> None:
    name = "Ada"
    ja = StubTranslations({"Hello {name}": "{name}さん"})
    try:
        set_translations(ja)
        assert tr(t"Hello {name}") == "Adaさん"
    finally:
        set_translations(None)
    assert tr(t"Hello {name}") == "Hello Ada"


def test_lazy_gettext_renders_per_current_language() -> None:
    name = "Ada"
    ja = StubTranslations({"Hello {name}": "{name}さん、こんにちは"})
    fr = StubTranslations({"Hello {name}": "Bonjour {name}"})

    label = lazy_gettext(t"Hello {name}")
    assert isinstance(label, LazyString)

    with use_translations(ja):
        assert str(label) == "Adaさん、こんにちは"
    with use_translations(fr):
        assert str(label) == "Bonjour Ada"
    assert str(label) == "Hello Ada"


def test_lazy_pgettext_uses_context() -> None:
    filename = "report.txt"
    ja = StubTranslations({("button", "Open {filename}"): "{filename}を開く"})

    action = lazy_pgettext("button", t"Open {filename}")
    with use_translations(ja):
        assert str(action) == "report.txtを開く"


def test_lazy_string_supports_format_and_equality() -> None:
    label = lazy_gettext(t"Save")

    assert f"[{label}]" == "[Save]"
    assert label == "Save"
    assert label == lazy_gettext(t"Save")
    assert label != "Other"
    assert label != 123  # unsupported type compares unequal, does not raise
    assert repr(label) == "LazyString('Save')"


def test_lazy_string_is_unhashable() -> None:
    # The rendered result depends on the current language, so a hash would change
    # whenever the language is switched. Rather than silently break the set/dict
    # contract, stay unhashable and fail early.
    label = lazy_gettext(t"Save")

    with pytest.raises(TypeError, match="unhashable"):
        hash(label)
    with pytest.raises(TypeError, match="unhashable"):
        {label}  # noqa: B018
    assert str(label) in {"Save"}  # an explicit str() can still be used as a key


def test_lazy_strings_can_be_strict() -> None:
    # A deferred string renders wherever it is used, which is rarely a place
    # that knows whether this is a test run or production. The choice therefore
    # belongs where the message is written, and without it a damaged catalog
    # entry could only ever be reported through the logger.
    name = "Ada"
    broken = StubTranslations({"Hello {name}": "Bonjour {nom}"})

    lenient = lazy_gettext(t"Hello {name}")
    strict = lazy_gettext(t"Hello {name}", strict=True)

    with use_translations(broken):
        assert str(lenient) == "Hello Ada"
        with pytest.raises(InvalidTranslationError):
            str(strict)


def test_lazy_pgettext_can_be_strict() -> None:
    filename = "report.txt"
    broken = StubTranslations({("button", "Open {filename}"): "Ouvrir {fichier}"})

    strict = lazy_pgettext("button", t"Open {filename}", strict=True)

    with use_translations(broken), pytest.raises(InvalidTranslationError):
        str(strict)


def test_lazy_strings_stay_lenient_by_default() -> None:
    # The default matches every other entry point: a broken catalog renders the
    # source text rather than taking the application down.
    name = "Ada"
    broken = StubTranslations({"Hello {name}": "Bonjour {nom}"})

    with use_translations(broken):
        assert str(lazy_gettext(t"Hello {name}")) == "Hello Ada"


def test_translations_protocol_is_runtime_checkable() -> None:
    assert isinstance(gettext.NullTranslations(), Translations)
    assert not isinstance(object(), Translations)
