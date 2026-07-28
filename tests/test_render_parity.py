"""手同期された描画末尾コピー間の挙動一致を固定するドリフト防止テスト。

core.pyは性能上の理由で描画末尾のコピーを複数持つ(gettext()のインライン
展開・_render_pattern・_render_with_values・_render_plural_pattern)。
片方だけ修正して他方を直し忘れるドリフトは、APIごとの個別テストでは
すり抜け得る(変異検証で実証済み)ため、ここで全経路の出力を突き合わせる。
"""

from __future__ import annotations

import gettext as stdlib_gettext
from typing import Any

import pytest

from gettext_tstrings import compile_template, ngettext, pgettext, tr


class Stub(stdlib_gettext.NullTranslations):
    def __init__(
        self,
        messages: dict[str, str] | None = None,
        plurals: dict[tuple[str, str], tuple[str, str]] | None = None,
        contexts: dict[tuple[str, str], str] | None = None,
    ) -> None:
        super().__init__()
        self.messages = messages or {}
        self.plurals = plurals or {}
        self.contexts = contexts or {}

    def gettext(self, message: str) -> str:
        return self.messages.get(message, message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        translated = self.plurals.get((singular, plural))
        if translated is None:
            return singular if n == 1 else plural
        return translated[0] if n == 1 else translated[1]

    def pgettext(self, context: str, message: str) -> str:
        return self.contexts.get((context, message), message)


class Formatted:
    """``__format__`` が ``__str__`` と異なる値。strショートカットの誤適用を露出させる。"""

    def __format__(self, format_spec: str) -> str:
        return f"<F:{format_spec}>"

    def __str__(self) -> str:
        return "<S>"


def _all_paths_one_field(pattern: str, a: Any) -> dict[str, str]:
    """1フィールドのソースを全描画経路で描画する。"""
    return {
        "gettext": tr(t"{a}", translations=Stub(messages={"{a}": pattern})),
        "pgettext": pgettext("k", t"{a}", translations=Stub(contexts={("k", "{a}"): pattern})),
        "compiled": compile_template(t"{a}").render(pattern),
        "ngettext(n=1)": ngettext(
            t"{a}",
            t"{a}!",
            1,
            translations=Stub(plurals={("{a}", "{a}!"): (pattern, pattern)}),
        ),
        "ngettext(n=2)": ngettext(
            t"{a}",
            t"{a}!",
            2,
            translations=Stub(plurals={("{a}", "{a}!"): (pattern, pattern)}),
        ),
    }


def _all_paths_two_fields(pattern: str, a: Any, b: Any) -> dict[str, str]:
    """2フィールドのソースを全描画経路で描画する。"""
    return {
        "gettext": tr(t"{a} {b}", translations=Stub(messages={"{a} {b}": pattern})),
        "pgettext": pgettext(
            "k",
            t"{a} {b}",
            translations=Stub(contexts={("k", "{a} {b}"): pattern}),
        ),
        "compiled": compile_template(t"{a} {b}").render(pattern),
        "ngettext(n=1)": ngettext(
            t"{a} {b}",
            t"{a} {b}!",
            1,
            translations=Stub(plurals={("{a} {b}", "{a} {b}!"): (pattern, pattern)}),
        ),
        "ngettext(n=2)": ngettext(
            t"{a} {b}",
            t"{a} {b}!",
            2,
            translations=Stub(plurals={("{a} {b}", "{a} {b}!"): (pattern, pattern)}),
        ),
    }


@pytest.mark.parametrize("value", ["Ada", 7, Formatted()], ids=["str", "int", "custom"])
@pytest.mark.parametrize(
    "pattern",
    ["{a}", "p {a} s", "p {a} {a} s"],
    ids=["bare", "prefix-suffix", "repeat"],
)
def test_one_field_render_paths_agree(pattern: str, value: Any) -> None:
    # 参照値はSPECの規則(format(value, "")をプレーン差し込み)を素朴に適用する。
    expected = pattern.replace("{a}", format(value, ""))

    results = _all_paths_one_field(pattern, value)

    assert results == dict.fromkeys(results, expected)


@pytest.mark.parametrize(
    ("a", "b"),
    [("Ada", 7), (7, Formatted()), (Formatted(), "Ada")],
    ids=["str-int", "int-custom", "custom-str"],
)
@pytest.mark.parametrize(
    "pattern",
    ["{b} / {a}", "p {a} m {b} s", "{a} {a} {b}"],
    ids=["reorder", "pair-segments", "repeat-general"],
)
def test_two_field_render_paths_agree(pattern: str, a: Any, b: Any) -> None:
    expected = pattern.replace("{a}", format(a, "")).replace("{b}", format(b, ""))

    results = _all_paths_two_fields(pattern, a, b)

    assert results == dict.fromkeys(results, expected)
