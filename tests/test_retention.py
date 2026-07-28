"""キャッシュが補間値を保持しないことを守る。

READMEの性能節は「both caches are bounded and never retain interpolated
values」と公言している。プランは静的構造(strings と各補間のメタデータ)だけを
持ち、実行時の値は描画の間だけ触る、という設計そのものの主張。

この保証はどのテストにも守られていなかった。実際、_Site に補間タプルを持たせる
リグレッションを注入しても既存テストは全て緑のまま通る。ここで各描画経路について
弱参照が切れることを確かめる。
"""

from __future__ import annotations

import gc
import gettext
import logging
import weakref

import pytest

from gettext_tstrings import compile_template, ngettext, pgettext, tr


class _Probe:
    """弱参照を張れる補間値。"""

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
    # 2回目以降はプランがキャッシュヒットする経路。温めてから確かめる。
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
    # 定数以外の全経路: 2フィールド(pair)、3フィールド(chunks)、文脈、複数形、
    # そして低レベルのCompiledTemplate。
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
    # 壊れたパターンは plan.invalid に記録される。記録するのはパターン文字列
    # だけで、そのとき描画しようとした値ではない。
    class Broken(gettext.NullTranslations):
        def gettext(self, message: str) -> str:
            return "Broken without the placeholder"

    probe = _Probe()
    ref = weakref.ref(probe)

    # 警告を出させない。捕捉されたログレコードは例外を保持し、その traceback の
    # フレーム経由でテンプレートを掴むため、pytest側の事情で弱参照が切れなくなる
    # (素のPythonでは解放される)。ここで測りたいのはライブラリ側の保持だけ。
    with caplog.at_level(logging.CRITICAL, logger="gettext_tstrings"):
        assert tr(t"Rejected {probe}", translations=Broken()) == "Rejected probe"

    del probe
    gc.collect()
    assert ref() is None
