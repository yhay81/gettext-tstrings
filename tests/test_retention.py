"""Guard the promise that caches never retain interpolated values.

The performance section of the README states that both caches are bounded and
never retain interpolated values. That is a claim about the design itself: a
plan holds only static structure (the strings and each interpolation's
metadata), and runtime values are touched only for the duration of a render.

No test guarded that promise. Injecting a regression that stores the
interpolation tuple on _Site leaves the existing suite entirely green. These
tests check that weak references break on every render path.
"""

from __future__ import annotations

import gc
import gettext
import logging
import weakref

import pytest

from gettext_tstrings import compile_template, ngettext, pgettext, tr


class _Probe:
    """Interpolated value that a weak reference can point at."""

    def __format__(self, format_spec: str, /) -> str:
        return "probe"

    def __str__(self) -> str:
        return "probe"


def test_single_field_render_does_not_retain_its_value() -> None:
    probe = _Probe()
    ref = weakref.ref(probe)
    null = gettext.NullTranslations()

    assert tr(t"Retention {probe}", translations=null) == "Retention probe"

    del probe
    gc.collect()
    assert ref() is None


def test_warm_cache_does_not_retain_values_across_calls() -> None:
    # From the second call on, the plan comes from a cache hit. Warm it, then check.
    null = gettext.NullTranslations()
    for _ in range(50):
        warm = _Probe()
        assert tr(t"Warm {warm}", translations=null) == "Warm probe"

    probe = _Probe()
    ref = weakref.ref(probe)
    assert tr(t"Warm {probe}", translations=null) == "Warm probe"

    del probe
    gc.collect()
    assert ref() is None


def test_every_render_path_releases_its_values() -> None:
    # Every path but the constant one: two fields (pair), three fields (chunks),
    # context, plural, and the low-level CompiledTemplate.
    null = gettext.NullTranslations()
    probes = [_Probe() for _ in range(6)]
    refs = [weakref.ref(probe) for probe in probes]
    first, second, third, ctx, one, many = probes

    assert tr(t"{first} {second}", translations=null) == "probe probe"
    assert tr(t"{first} {second} {third}", translations=null) == "probe probe probe"
    assert pgettext("nav", t"Open {ctx}", translations=null) == "Open probe"
    assert ngettext(t"One {one}", t"Many {many}", 2, translations=null) == "Many probe"
    assert compile_template(t"Compiled {first}").render("Compiled {first}") == "Compiled probe"

    probes.clear()
    del first, second, third, ctx, one, many
    gc.collect()
    assert [ref() for ref in refs] == [None] * 6


def test_a_rejected_translation_does_not_retain_its_values(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # A broken pattern is remembered in plan.invalid. What gets remembered is the
    # pattern string alone, not the values that render was about to use.
    class Broken(gettext.NullTranslations):
        def gettext(self, message: str) -> str:
            return "Broken without the placeholder"

    probe = _Probe()
    ref = weakref.ref(probe)

    # Keep the warning from being emitted. A captured log record holds the exception,
    # whose traceback frames keep the template alive, so the weak reference would
    # survive for reasons that belong to pytest rather than to the library (plain
    # Python releases it). What we measure here is retention by the library alone.
    with caplog.at_level(logging.CRITICAL, logger="gettext_tstrings"):
        assert tr(t"Rejected {probe}", translations=Broken()) == "Rejected probe"

    del probe
    gc.collect()
    assert ref() is None
