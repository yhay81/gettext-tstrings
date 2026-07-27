"""Small extraction and runtime example.

Shows the bound ``Translator``, per-request context binding, and a lazily
translated module-level label.
"""

from __future__ import annotations

import gettext

from gettext_tstrings import Translator, lazy_gettext, tr, use_translations

# 言語が決まる前(インポート時)に定義され、使用時に翻訳される遅延ラベル。
GREETING_LABEL = lazy_gettext(t"Welcome")


def main() -> None:
    translations = gettext.translation(
        "messages",
        localedir="locales",
        languages=["ja"],
        fallback=True,
    )

    # 明示的に束縛したプロセッサを ``_`` として使う。
    _ = Translator(translations)

    name = "Ada"
    n = 3
    print(_(t"Hello {name}"))
    print(_.ngettext(t"One file", t"{n} files", n))

    # リクエスト単位の言語切り替え: 文脈に束縛すると、モジュール関数と
    # 遅延ラベルの両方が現在の言語で解決される。
    with use_translations(translations):
        print(tr(t"Hello {name}"))
        print(str(GREETING_LABEL))


if __name__ == "__main__":
    main()
