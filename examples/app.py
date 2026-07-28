"""Small extraction and runtime example.

Shows the bound ``Translator``, per-request context binding, and a lazily
translated module-level label.
"""

from __future__ import annotations

import gettext

from gettext_tstrings import Translator, lazy_gettext, tr, use_translations

# A lazy label: defined at import time, before a language is known, and
# translated when it is used.
GREETING_LABEL = lazy_gettext(t"Welcome")


def main() -> None:
    translations = gettext.translation(
        "messages",
        localedir="locales",
        languages=["ja"],
        fallback=True,
    )

    # Use an explicitly bound translator as ``_``.
    _ = Translator(translations)

    name = "Ada"
    n = 3
    print(_(t"Hello {name}"))
    print(_.ngettext(t"One file", t"{n} files", n))

    # Per-request language switching: binding to the context resolves both the
    # module-level functions and the lazy label in the current language.
    with use_translations(translations):
        print(tr(t"Hello {name}"))
        print(str(GREETING_LABEL))


if __name__ == "__main__":
    main()
