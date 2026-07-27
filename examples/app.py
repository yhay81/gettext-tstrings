"""Small extraction and runtime example."""

from __future__ import annotations

import gettext

from babel_tstrings import Translator


def main() -> None:
    translations = gettext.translation(
        "messages",
        localedir="locales",
        languages=["ja"],
        fallback=True,
    )
    _ = Translator(translations)

    name = "Ada"
    n = 3
    print(_(t"Hello {name}"))
    print(_.ngettext(t"One file", t"{n} files", n))


if __name__ == "__main__":
    main()
