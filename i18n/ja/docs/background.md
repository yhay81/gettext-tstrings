---
description: "30年にわたるgettext、10年を隔てた2つのPEP、そしてnot plannedとして閉じられた標準ライブラリの議論。このライブラリが存在する理由を、出典へのリンク付きで辿ります。"
---

# 背景

このライブラリは、2つの長い物語 — ソフトウェアがどのように翻訳されるかという
物語と、Pythonが文字列をどのように補間するかという物語 — の交点にあります。
両者は2025年についに交差し、そして、小さく慎重な規約こそが必要になるちょうど
その地点で止まりました。このページでは、出典へのリンクとともに両方の物語を
語ります。このサイトの設計判断は、それが答えている問いが見えるときのほうが
評価しやすいからです。

## gettextのエコシステム { #the-gettext-ecosystem }

[GNU gettext]は、1990年代半ば以降、フリーソフトウェアが翻訳されるための方法で
あり続けています。コード内の文字列をマークし、templateへ抽出し、翻訳者へ
言語ごとに1つのカタログファイルを渡し、コンパイルし、実行時に読み込む。この
ループの周りには、POエディター、レビューワークフロー、同じファイル形式を扱う
翻訳プラットフォームという一大エコシステムが育ち、Pythonも20年以上にわたり
標準ライブラリに[`gettext`モジュール][stdlib-gettext]を備えてきました。翻訳の
ランタイム側は、一度も問題ではありませんでした。

未解決だったのは常に、*カタログ文字列がどのような姿をしているか*でした。
`%(name)s`のメッセージは、1文字消えただけで本番環境のクラッシュになるprintf
構文を翻訳者に手渡します。`.format()`のメッセージは、生きたオブジェクトへの
属性アクセスをカタログに手渡します（[t-stringを選ぶ理由](comparison.md)で、
実際の失敗とともに両方を確認できます）。そして、今のPythonコードが最も好む
構文であるf-stringは、そもそも参加できません。ライブラリが受け取る時点で、
すでに完成した文字列だからです。それでも試みる人は後を絶たず、Babelのissue
トラッカーにはその試みが集まっています（[#594][babel-594]、[#715][babel-715]）。
これは機能の不足ではなく、構造的な失敗です。

## 10年を隔てた2つのPEP { #two-peps-ten-years-apart }

2015年、Alyssa CoghlanとNick Humrichは[PEP 501]を書き、補間templateを提案
しました。その筆頭の動機はi18nで、PEP自身の言葉では「i18n翻訳のためのより
クリーンな構文を提供すること」でした。この提案は延期されました。議論の中で、
i18nのユースケースが、より単純なユースケースにはない重要な追加の考慮事項を
伴うと分かったことも、その一因です。

10年後、[PEP 750] — Jim Baker、Guido van Rossum、Paul Everitt、Koudai Aono、
Lysandros Nikolaou、Dave Peckによる — がこのアイデアをt-stringとして復活させ、
[2025年4月に承認され][sc-resolution]、2025年10月の[Python 3.14]で出荷されました。
PEP 501はこれを受けて取り下げられました。このページにとって重要な点が1つ
あります。i18nはPEP 750の明示的な動機に*含まれていない*のです。PEP 750は
仕組みを一般化し — どのライブラリでも利用できるtemplate型として — 翻訳の
問いを、PEP 501が10年前に保留したのとまったく同じ場所、つまり未解決のまま
残しました。

つまりPython 3.14の時点で、言語にはメッセージカタログが必要とするデータ構造
そのものが備わりながら、それをカタログとして使うための規約は存在しません
でした。

## 標準ライブラリでの議論 { #the-stdlib-discussion }

3.14のリリース2ヶ月前、Adrian Mönnich（ThiefMaster、Indicoプロジェクトの
maintainer）は、そのギャップを標準ライブラリ自身で埋めることを提案しました。
2025年8月にdiscuss.python.orgで開かれたスレッド
[Support t-strings in gettext][discuss-thread]には、`gettext`と`pygettext`の
両方にt-string対応を加える、動作する[Pull Request][cpython-pr]が添えられて
いました。

このスレッドは全文を読む価値があります。後にこのライブラリが答えなければ
ならなかった難しい問いを、すべて浮かび上がらせているからです。

- **補間には何を許すのか？** 単純な名前だけか、それとも派生プレースホルダー名を
  付けた属性アクセスや呼び出しまでか。どの答えも、利便性と、msgidの安定性や
  カタログの安全性とを秤にかけることになります。
- **複数形は何を要求するのか？** 対象言語の複数形体系が、ソース言語のものと
  異なる場合には。
- **そもそもgettextが正しいターゲットなのか？** PEP 750の策定中から、t-stringは
  i18nには向かないと論じていたBarry Warsawは、自身の[`flufl.i18n`][flufl-i18n]と
  その`$`文字列スタイルをより親しみやすい道具として挙げました。gettext自体を
  離れて[Fluent]のような新しいシステムへ向かうべきだと論じる人もいました。
- **そしてメタな問い。** 標準ライブラリが何を出荷するにせよ、それは事実上二度と
  変更できません。これほど多くの選択が未決のままの規約を最初の一発で凍結する
  のは、危険な賭けです。

合意は形成されませんでした。CPythonのissueは
[「not planned」として閉じられ][cpython-issue]、Pull Requestは3.14リリースの
数日後、2025年10月にマージされないまま閉じられました。能力は言語に存在するのに、
規約には居場所がなかったのです。

## まずパッケージとして { #why-a-package-first }

それが、このプロジェクトが標準ライブラリの外側から埋めることを選んだギャップ
です。そこには意図的な賭けがあります。規約は、自由にバージョンを重ね、採用を
一件ずつ積み上げられる場所でこそ速く成熟する。最初から正しくなければならない
標準ライブラリは、規約が*行き着くべき*場所であって、練り上げる場所ではない、
という賭けです。

具体的には、スレッドで争点となったすべての問いに、ここでは文書化された答えが
あり、それぞれ専用のページを持っています。

- 補間は**単純な名前のみ**とし、msgidを安定した意味のあるものに保ちます —
  規則は[ガイド](guide.md#safety-and-scope)で、その理由は
  [動作原理](internals.md#from-template-to-msgid)で示します。
- **書式指定はカタログの外**に完全にとどまります
  （[t-stringを選ぶ理由](comparison.md)）。
- **複数形**は、対象言語の複数形体系がソース言語と異なることを許す
  和集合／積集合の規則に従います（[仕様 §4](spec.md)）。
- 壊れたカタログは**クラッシュせずにfallback**し、gettext自身の契約を守ります
  （[ガイド](guide.md#what-happens-when-a-catalog-is-wrong)）。
- そして規約全体が、機械可読な適合性テストスイートを備えた
  [バージョン付きの仕様](spec.md)です。別の実装 — 将来の標準ライブラリ実装を
  含む — がそのまま採用して相互運用できるように書かれています。

議論は終わっていませんし、このプロジェクトはその参加者であって、裁定者では
ありません。これらの選択に関わる本番でのgettext経験をお持ちなら、
[同じスレッド][discuss-thread]とこのリポジトリの[Discussions][gh-discussions]が
議論の場です。

## 年表 { #timeline }

| 時期 | 出来事 |
| --- | --- |
| 1990年代半ば | GNU gettextが、翻訳者とプラットフォームが今も使い続けるPO/POT/MOワークフローを確立します。 |
| 2015年 | [PEP 501]が、i18nを筆頭の動機として補間templateを提案。延期されます。 |
| 2016年 | Python 3.6でf-stringが登場します — 補間は専用の構文を手に入れ、翻訳はそれを使えません。 |
| 2024年7月 | [PEP 750]がt-stringを提案します。 |
| 2025年4月 | PEP 750が[承認][sc-resolution]され、PEP 501はこれを受けて取り下げられます。 |
| 2025年8月 | スレッド[Support t-strings in gettext][discuss-thread]が、標準ライブラリへの[Pull Request][cpython-pr]とともに開かれます。 |
| 2025年10月 | [Python 3.14]がt-stringを出荷。標準ライブラリのissueは[not planned][cpython-issue]として閉じられます。 |
| 2026年 | `gettext-tstrings`がalpha版として、[仕様v1](spec.md)とその適合性テストスイートとともに出荷されます。 |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
