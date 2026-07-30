---
description: "空のディレクトリから日本語で挨拶するプログラムまでを5ステップで進めます。すべてのコマンドを実際の出力付きで示します。"
---

# チュートリアル

このページでは、空のディレクトリから日本語で挨拶するプログラムまでを作ります。
5つのステップで進め、gettextの経験は前提とせず、すべてのコマンドを実際の
出力付きで示します。各ステップで、正しく進んでいるかを確認できます。

Python 3.14以降が必要です。t-stringは3.14で導入された新しい構文だからです。

## 1. インストール

```console
python -m pip install "gettext-tstrings[babel]"
```

`[babel]` extraは[Babel]をインストールします。ステップ3でメッセージを
カタログファイルへ集めるツールです。これは開発時のツールであり、本番コードの
レンダリングは標準ライブラリだけで動きます。

## 2. コード内のメッセージをマークする

`app.py`を作成します。

```python
from gettext_tstrings import tr

name = "Ada"
print(tr(t"Hello {name}"))
```

`t"Hello {name}"`はf-stringに見えますが、`t` prefixはテキストと値をその場で
合成せず、分離したまま保持します。この分離があるからこそ、`tr()`は
`Hello {name}`という文全体の翻訳を検索し、その後で値を挿入できます。

今すぐ実行してみましょう。

```console
$ python app.py
Hello Ada
```

翻訳はまだインストールされていないため、ソーステキストがそのまま表示されます。
このライブラリを使うプログラムの実行に、カタログが*必須*になることはありません。
英語（あるいはあなたのソース言語）が組み込みのfallbackです。

## 3. メッセージを抽出する

翻訳者はソースコードを読みません。あなたと翻訳者の間を行き来するのは、
**カタログ**と呼ばれる小さなファイルです。その第一歩は、マークされたすべての
メッセージをコードから集めることです。

`babel.cfg`を作成して、Babelにメッセージの探し方を教えます。

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

次に、templateファイル（`.pot`）へ抽出します。

```console
$ mkdir -p locales
$ pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
```

`locales/messages.pot`には、メッセージごとに1つのエントリが入ります。

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

`msgid`は、コードが検索に使うkeyです。空の`msgstr`は翻訳を書き込む場所ですが、
このファイルには書き込みません。`.pot`は*template*であり、次のステップで
言語ごとにコピーします。

## 4. 翻訳してコンパイルする

templateから日本語カタログを作成します。

```console
$ pybabel init -i locales/messages.pot -d locales -l ja
creating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

`locales/ja/LC_MESSAGES/messages.po`を開き、`msgstr`を埋めます。

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

`{name}`はそのままにしてください。プレースホルダーは、翻訳された文の中で値が
自分の位置を見つけるための目印であり、翻訳では対象言語が必要とする位置へ自由に
動かせます。実際のプロジェクトでは、この`.po`ファイルを翻訳者へ渡すか、
翻訳プラットフォームへアップロードします。どちらでもフォーマットは同じです。

カタログはテキストとして編集されますが、読み込みはバイナリ形式（`.mo`）なので、
コンパイルします。

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
```

このコマンドは安全網でもあります。翻訳がプレースホルダーを壊していた場合、
たとえば`{name}`が`{nome}`になっていた場合は、通過を拒否します。

```console
$ pybabel compile -d locales
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nome} is not in the source message
1 errors encountered.
```

## 5. 実行する

`app.py`をコンパイル済みカタログへ向けます。

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales", languages=["ja"]))

name = "Ada"
print(_(t"Hello {name}"))
```

`_`は「これを翻訳する」を表すgettextの慣習的な名前です。ユーザー向けの
すべての文字列に付くため、短くなっています。`tr`と同じ関数を、1つのカタログへ
束縛したものです。

```console
$ python app.py
こんにちは Ada
```

これがループの全体です。**マーク → 抽出 → 翻訳 → コンパイル → 実行**。
このサイトの他のページはすべて、この5ステップのいずれかを掘り下げたものです。

## 次に読むページ

- [t-stringを選ぶ理由](comparison.md) — この設計が何から守ってくれるのかを、
  `%(name)s`、`.format()`、`$`文字列と比較します。
- [ガイド](guide.md) — 複数形、リクエストごとの言語、遅延文字列、それでも
  カタログが不正だったときに実行時に何が起こるかを説明します。
- [抽出](extraction.md) — `pybabel`の完全なリファレンス。独自の関数名、
  CI向けのstrictモード、カタログを守る検証を説明します。

  [Babel]: https://babel.pocoo.org/
