"""Reproducible microbenchmarks for the runtime hot path."""

from __future__ import annotations

import gettext
import platform
import statistics
import sys
import timeit
from collections.abc import Mapping

from gettext_tstrings import compile_template, tr

NUMBER = 100_000
REPEAT = 7


def run_benchmarks() -> Mapping[str, float]:
    """Return median nanoseconds per operation for representative cases."""
    translations = gettext.NullTranslations()
    name = "Ada"
    category = "News"
    target = "Archive"
    template = t"Hello {name}"
    compiled = compile_template(template)

    # Warm the bounded structural and translation-pattern caches.
    tr(t"Hello {name}", translations=translations)
    tr(
        t"Category {category} moved to {target}",
        translations=translations,
    )

    namespace = locals() | {"compile_template": compile_template, "tr": tr}
    statements = {
        "f-string": "f'Hello {name}'",
        "gettext(str).format": ("translations.gettext('Hello {name}').format(name=name)"),
        "compiled.render": "compiled.render(compiled.msgid)",
        "compile_template": "compile_template(template)",
        "tr (1 field)": "tr(t'Hello {name}', translations=translations)",
        "tr (2 fields)": (
            "tr(t'Category {category} moved to {target}', translations=translations)"
        ),
    }
    results: dict[str, float] = {}
    for label, statement in statements.items():
        samples = timeit.repeat(
            statement,
            globals=namespace,
            number=NUMBER,
            repeat=REPEAT,
        )
        results[label] = statistics.median(samples) / NUMBER * 1e9
    return results


def main() -> None:
    print(f"Python {platform.python_version()} ({sys.implementation.name})")
    print(platform.platform())
    print()
    for label, nanoseconds in run_benchmarks().items():
        print(f"{label:24} {nanoseconds:10.1f} ns/op")


if __name__ == "__main__":
    main()
