from __future__ import annotations

import asyncio
import contextvars
import gettext
import sys
import threading

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


# Defined at import, the way an application defines a form label — so the two
# concurrent tasks below share one object and must still render it differently.
MODULE_LEVEL_LABEL = lazy_gettext(t"Shared label")


def test_use_translations_binds_and_restores_context() -> None:
    name = "Ada"
    ja = StubTranslations({"Hello {name}": "{name}さん、こんにちは"})

    assert tr(t"Hello {name}") == "Hello Ada"
    with use_translations(ja):
        assert tr(t"Hello {name}") == "Adaさん、こんにちは"
        assert get_translations() is ja
    assert tr(t"Hello {name}") == "Hello Ada"
    assert get_translations() is None


def test_language_contexts_nest_and_unwind() -> None:
    # Rendering several languages in one call stack — a reply quoted in the
    # recipient's language inside a page rendered in the reader's — needs the
    # inner block to restore the outer one exactly.
    name = "Ada"
    ja = StubTranslations({"Hello {name}": "{name}さん、こんにちは"})
    fr = StubTranslations({"Hello {name}": "Bonjour {name}"})

    with use_translations(ja):
        with use_translations(fr):
            assert tr(t"Hello {name}") == "Bonjour Ada"
        assert tr(t"Hello {name}") == "Adaさん、こんにちは"
    assert get_translations() is None


def test_concurrent_tasks_do_not_share_a_language() -> None:
    # The binding is a ContextVar rather than a stack on a shared object, so two
    # requests that overlap cannot pick up each other's language. The delays
    # make the tasks leave their blocks in the order they entered them, which is
    # exactly the interleaving a pushdown stack gets wrong.
    name = "Ada"
    catalogs = {
        "ja": StubTranslations({"Hello {name}": "{name}さん、こんにちは"}),
        "fr": StubTranslations({"Hello {name}": "Bonjour {name}"}),
    }

    async def request(language: str, delay: float) -> str:
        with use_translations(catalogs[language]):
            await asyncio.sleep(delay)
            return tr(t"Hello {name}")

    async def both() -> list[str]:
        return list(await asyncio.gather(request("ja", 0.01), request("fr", 0.02)))

    assert asyncio.run(both()) == ["Adaさん、こんにちは", "Bonjour Ada"]


def test_concurrent_tasks_keep_translation_contexts_isolated() -> None:
    # The test above builds its interleaving out of two sleep durations, which
    # makes the overlap a matter of timing. The barrier here makes it a fact:
    # neither task renders until both are inside their own binding. It also
    # checks the binding rather than only the output — what get_translations()
    # returns inside each block, and that leaving one restores nothing rather
    # than the other task's catalog.
    #
    # MODULE_LEVEL_LABEL is the part nothing else covers. The lazy tests below
    # switch languages one after another; a label defined once at import and
    # rendered by two tasks at the same moment is the shape the guide
    # recommends for a per-recipient loop, and it has to resolve per task.
    name = "Ada"
    ja = StubTranslations(
        {
            "Hello {name}": "{name}さん、こんにちは",
            "Shared label": "共有ラベル",
        }
    )
    fr = StubTranslations(
        {
            "Hello {name}": "Bonjour {name}",
            "Shared label": "Libellé partagé",
        }
    )
    barrier = asyncio.Barrier(2)
    active_contexts: list[Translations | None] = []

    async def request(catalog: StubTranslations) -> tuple[str, str]:
        with use_translations(catalog):
            assert get_translations() is catalog
            active_contexts.append(get_translations())
            await barrier.wait()
            assert active_contexts.count(ja) == 1
            assert active_contexts.count(fr) == 1
            await asyncio.sleep(0)
            assert get_translations() is catalog
            rendered = tr(t"Hello {name}"), str(MODULE_LEVEL_LABEL)
        assert get_translations() is None
        return rendered

    async def both() -> list[tuple[str, str]]:
        return list(await asyncio.gather(request(ja), request(fr)))

    assert asyncio.run(both()) == [
        ("Adaさん、こんにちは", "共有ラベル"),
        ("Bonjour Ada", "Libellé partagé"),
    ]
    assert len(active_contexts) == 2
    assert active_contexts.count(ja) == 1
    assert active_contexts.count(fr) == 1
    assert get_translations() is None


def test_a_worker_thread_inherits_the_binding_only_when_the_build_says_so() -> None:
    # Whether a bare thread starts from a copy of the caller's context or an
    # empty one is sys.flags.thread_inherit_context, which defaults true on
    # free-threaded builds and false everywhere else — so the same code renders
    # a different language on 3.14t than on 3.14. Passing the context is what
    # makes the hand-off mean the same thing on both, and it is what
    # asyncio.to_thread already does. Found by CI, not by reasoning.
    name = "Ada"
    ja = StubTranslations({"Hello {name}": "{name}さん、こんにちは"})
    rendered: dict[str, str] = {}

    def render(key: str) -> None:
        rendered[key] = tr(t"Hello {name}")

    with use_translations(ja):
        bare = threading.Thread(target=render, args=("bare",))
        bare.start()
        bare.join()

        carried = threading.Thread(target=contextvars.copy_context().run, args=(render, "carried"))
        carried.start()
        carried.join()

    inherited = "Adaさん、こんにちは"
    assert rendered == {
        "bare": inherited if sys.flags.thread_inherit_context else "Hello Ada",
        "carried": inherited,
    }


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
