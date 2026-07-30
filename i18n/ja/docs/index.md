---
description: "完全なt-stringメッセージをgettextとBabelで翻訳し、書式指定をカタログの外に保ちます。"
---

# gettext-tstrings

Python 3.14以降のt-stringに対応する、安全なgettext/Babel統合です。

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

カタログには完全な文 `Hello {name}` が渡されます。翻訳では `{name}` の順序を
変えたり繰り返したりできますが、省略したり、未知の名前を追加したり、独自の
書式指定を付けたりすることはできません。

## 解決する課題

f-stringはライブラリが受け取る時点ですでに補間済みなので、翻訳できるのは文の
断片だけです。t-string（[PEP 750]）は、静的なテキスト、評価済みの値、元の式、
変換指定、フォーマット指定を分離したまま保持します。これはメッセージカタログが
必要とする分離そのものです。`%(name)s` や `.format()` と比べて
[何が変わるのか](comparison.md)を確認できます。

ただし、gettextにもBabelにも、t-stringをどのようにメッセージへ変換するかの
規定はありません。このライブラリはその規約を定め、
[バージョン付きの仕様](spec.md)として文書化し、実装を検証する
[適合性テストスイート](spec.md#conformance)も提供します。

## 採用した設計

- 文の断片ではなく、常に完全なメッセージを翻訳します。
- `{name}` のような単純な変数名だけを受け付けます。
- `!r` や `:.2f` はアプリケーション側で管理し、カタログには渡しません。
- 翻訳者は既知のプレースホルダーを並べ替えたり繰り返したりできます。ただし、
  属性アクセスや書式動作の追加はできません。
- 一般的なPOT、PO、MOファイルと、それらに対応する既存ツールを再利用します。

## このサイト自身で実証

このドキュメントは、単に翻訳されたデモではありません。ナビゲーション、
テーマの文言、著作権表示、複数形に対応したビルド結果を、POカタログから
`gettext-tstrings` 自身で描画しています。
[多言語ビルダー](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)は、
厳格ビルドのたびに文脈付きメッセージ、名前付きプレースホルダー、10言語すべての
複数形規則を実際に通します。

## インストール

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

## 次に読むページ

<div class="grid cards" markdown>

- **[t-stringを選ぶ理由](comparison.md)** — 同じメッセージを3通りで記述し、
  `%(name)s`、`.format()`、t-stringがカタログに何を渡すかを比較します。
- **[ガイド](guide.md)** — ランタイムAPI、リクエストごとの言語、遅延文字列、
  不正なカタログへの対応を説明します。
- **[抽出](extraction.md)** — `pybabel` のワークフローと設定、既存ツールによる
  カタログ検証を説明します。
- **[仕様](spec.md)** — t-stringとmsgidの対応を、機械可読な適合性テストを備えた
  安定したバージョン付き契約として定義します。
- **[API](api.md)** — パッケージが公開するすべての要素をまとめています。

</div>

## 開発状況

現在はalpha版です。契約は意図的に小さく保たれ、
[仕様](spec.md)が安定部分です。Python APIは今後変更される可能性があります。
安定版までには、より多くの言語のfixture、継続的な性能計測、gettextとBabelの
実利用者によるAPIレビュー、対応するすべてのPython/Babelリリースでの互換性検証が
必要です。

[IssueとPull Request](https://github.com/yhay81/gettext-tstrings/issues)を歓迎します。
alpha版の今こそ、インターフェースを議論する価値があります。

## コミュニティに参加する

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
