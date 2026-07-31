---
description: "完全なt-stringメッセージをgettextとBabelで翻訳し、値と書式指定をカタログの外に保ちます。"
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# 完全なメッセージを訳す、<br>Pythonのt-stringで。

`gettext-tstrings`は、Python 3.14以降のt-stringを標準のgettextカタログとBabel
のツール群へつなぎます。値と書式指定はアプリケーションのコードに残り、翻訳者は
完全なメッセージと`{name}`という単純なプレースホルダーを扱います。

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

カタログに入るのは`Hello {name}`です。翻訳では`{name}`を移動させたり繰り返したり
できます。プレースホルダーを削除したり、名前を変えたり、書式を付け替えたりすると、
カタログの検証がそのエラーを報告します。不正なエントリがそれでも本番へ届いた
場合、ライブラリは警告をログへ記録し、クラッシュせずにソースメッセージを
レンダリングします。

[5分のチュートリアルを始める :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[他の選択肢と比べる](comparison.md){ .md-button }

alpha版 · Python 3.14以降 · 標準のPO/MOカタログ · サードパーティの実行時依存なし
{ .home-facts }

このサイト自身が、ここに書かれていることを実践しています。ナビゲーション、
ラベル、複数形に対応したビルドレポートを含むどの言語版も、POカタログから
[`gettext-tstrings`自身](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)で描画しています。
{ .home-hero-note }

</div>

## あなたに向いているか { #is-this-for-you }

**いま向いているのは**、アプリケーションがPython 3.14以降で動いていて、すでに
gettextとBabelを使っている（あるいはそのPO/MOワークフローを採り入れたい）、
そしてレンダリング前に検査される名前付きプレースホルダーをt-stringの構文で
書きたい場合です。

**まだ向いていないのは**、Python 3.13以前が必要な場合、安定したPython APIが
必要な場合 — これはalpha版で、固まっているのは[仕様](spec.md)の部分です —
あるいは翻訳対象のテキストのほとんどが、Pythonソースではなくテンプレート言語の
中にある場合です。

すでにカタログがありますか。そのまま動き続けます。
`_("Hello {name}").format(name=name)`と`tr(t"Hello {name}")`は同じmsgidを
生成するので、既存の翻訳は乗り換えても失われません — 移行の全体像は
[移行](migration.md)で説明します。

## カタログが言えること { #what-the-catalog-may-say }

**翻訳は、自分が翻訳するメッセージの構造を変えられない。**約束はこれがすべてで、
このサイトの残りはすべてそこから導かれます。翻訳では`{name}`の順序を変えたり
繰り返したりでき、その周りの語はすべて書き換えられます。ただし、プレースホルダーを
省略すること、新しいものをでっち上げること、そこからあなたのオブジェクトへ手を
伸ばすこと、独自の書式指定を付けることはできません。

ライブラリはそれを入口で — カタログのコンパイル時に — 検査し、レンダリング時に
もう一度検査します。これが、レビューで見つかる誤りと、ユーザーに見つかる誤りとの
違いです。

!!! note "gettextが初めての方へ — ワークフロー全体を4文で"

    **gettext**は、Pythonに限らず広く使われている、ソフトウェアを翻訳するための
    標準的な仕組みです。コードが翻訳対象のメッセージをマークし、*抽出器*がそれらを
    templateファイル（`.pot`）へ集めます。翻訳者 — 多くの場合programmerでは
    ありません — が言語ごとに1つのカタログファイル（`.po`）を埋め、それが
    バイナリの`.mo`へコンパイルされ、アプリケーションが実行時に読み込みます。
    翻訳関数の慣習的な名前は`_`なので、`_(t"Hello {name}")`は「このメッセージを
    翻訳する」と読めます。**[チュートリアル](tutorial.md)**では、マーク、抽出、
    翻訳、コンパイル、実行という一連の流れを5分ほどで一巡します。

## 解決する課題 { #the-problem-it-solves }

f-stringはライブラリが受け取る時点ですでに補間済みです。`f"Hello {name}"`は
`"Hello Ada"`になっており、値の前後の断片を翻訳することは、ほとんどの言語で
文法を壊します。t-string（[PEP 750]）は、静的なテキスト、評価済みの値、元の式、
変換指定、フォーマット指定を分離したまま保持します。これはメッセージカタログが
必要とする分離そのものです。`%(name)s`、`.format()`、`$`文字列と比べて
[何が変わるのか](comparison.md)を確認できます。

ただし、gettextにもBabelにも、t-stringをどのようにメッセージへ変換するかの
規定はありません。このライブラリはその規約を定め、
[バージョン付きの仕様](spec.md)として文書化し、実装を検証する
[適合性テストスイート](spec.md#conformance)も提供します。

## 設計上の規則 { #the-design-rules }

- 文の断片ではなく、常に完全なメッセージを翻訳します。
- `{name}` のような単純な変数名だけを受け付けます。
- `!r` や `:.2f` はアプリケーション側で管理し、カタログには渡しません。
- 翻訳が既知のプレースホルダーを並べ替えたり繰り返したりすることは認めつつ、
  属性へ手を伸ばしたり書式を追加したりすることは防ぎます。
- 一般的なPOT、PO、MOファイルと、それらに対応する既存ツールを再利用します。

そして、意図的に手を出さないことの一覧も対になっています。数値、通貨、日付の
ローカライズはしません — [先に整形してください](guide.md#locale-aware-values)、
Babelで。HTML、shell、terminalといった出力先に応じたレンダリング結果のescape
もしません。そして翻訳が*正しい*かどうかは判定できません。判定できるのは
プレースホルダーが無傷かどうかだけです。

## インストール { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14以降が必要です。**レンダリングには依存パッケージがありません**。
標準ライブラリの `gettext` だけを使用します。

抽出とカタログ検証は[Babel]経由で行います。`pybabel` を実行する環境にextraを
インストールしてください。通常は本番イメージではなく、開発環境やCIです。

```console
python -m pip install "gettext-tstrings[babel]"
```

## 次に読むページ { #where-to-go-next }

**まずはここから** — gettextの経験は前提としません：

<div class="grid cards" markdown>

- **[チュートリアル](tutorial.md)** — 空のディレクトリから動く日本語翻訳まで
  5ステップ、すべてのコマンドを出力付きで示します。
- **[t-stringを選ぶ理由](comparison.md)** — 同じメッセージを4通りで記述し、
  `%(name)s`、`.format()`、`$`文字列がそれぞれカタログに何を渡すかを比較します。

</div>

**使う** — 実務のリファレンス：

<div class="grid cards" markdown>

- **[ガイド](guide.md)** — ランタイムAPI。どの入り口を使うか、複数形、
  リクエストごとの言語、遅延文字列、不正なカタログへの対応を説明します。
- **[抽出](extraction.md)** — `pybabel` のリファレンス。設定、独自の関数名、
  既存ツールが追加コストなしにカタログを検証する仕組みを説明します。
- **[実運用](workflow.md)** — チームが回すループ。更新サイクル、fuzzy
  エントリ、CIゲート、翻訳プラットフォーム、そして出荷を説明します。
- **[移行](migration.md)** — すでにカタログのあるプロジェクトへ、呼び出し箇所を
  1つずつ導入していく方法です。
- **[翻訳者向け](translators.md)** — `.po`ファイルを編集する人へそのまま渡せる
  1ページです。

</div>

**理解する** — 歴史から実装まで：

<div class="grid cards" markdown>

- **[背景](background.md)** — このライブラリが存在する理由。30年にわたる
  gettext、2つのPEP、そして答えのないまま閉じられた標準ライブラリの議論を
  辿ります。
- **[落とし穴](pitfalls.md)** — このサイトを35言語へ翻訳して実際に壊れたもの、
  そしてそのうち道具が捕まえられる半分を説明します。
- **[動作原理](internals.md)** — PEP 750のtemplateオブジェクトから
  レンダリング済み文字列まで、そして検査を安価にするキャッシュを説明します。

</div>

**リファレンス** — 契約：

<div class="grid cards" markdown>

- **[API](api.md)** — パッケージが公開するすべての要素を1ページにまとめています。
- **[仕様](spec.md)** — t-stringとmsgidの対応を、機械可読な適合性テストを備えた
  安定したバージョン付き契約として定義します。

</div>

## 開発状況 { #status }

| | |
| --- | --- |
| パッケージ版数 | 0.1.0a7 |
| APIの安定性 | alpha — Python APIは今後変更される可能性があります |
| [仕様](spec.md) | v1、[適合性テスト](spec.md#conformance)付き |
| Python | 3.14以降。3.14、3.14t（free-threaded）、3.15でテスト済み |
| Babel | 2.18以降。`pybabel`を動かす場所でのみ必要 |
| 実行時依存 | なし — 標準ライブラリの`gettext`のみ |
| カタログ形式 | 通常のPOT、PO、MO |
| 変更履歴 | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

現在はalpha版です。契約は意図的に小さく保たれ、
[仕様](spec.md)が安定部分です。Python APIは今後変更される可能性があります。
安定版までには、より多くの言語のfixture、継続的な性能計測、gettextとBabelの
実利用者によるAPIレビュー、対応するすべてのPython/Babelリリースでの互換性検証が
必要です。

[IssueとPull Request](https://github.com/yhay81/gettext-tstrings/issues)を歓迎します。
alpha版の今こそ、インターフェースを議論する価値があります。

## コミュニティに参加する { #join-the-community }

- 範囲が明確な
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  から取り組めます。
- 使い方の質問は
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)へ。
- 本番のgettextワークフローやAPIの提案は
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)へ。
- Pull Requestを作る前に
  [コントリビューションガイド](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  をお読みください。

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
