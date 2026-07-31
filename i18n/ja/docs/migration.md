---
description: "すでにgettextカタログのあるプロジェクトへt-stringを導入する方法です。何がそのまま残り、何がfuzzyになり、呼び出し箇所を1つずつどう移していくかを説明します。"
---

# 移行

プロジェクトですでにgettextを使っているなら、このライブラリを採用できるかを
決める問いは限られています。手元のカタログを無効にしてしまうのか、まだ変える
つもりのないコードと共存できるのか、そして移行のどこまでを一度にやらなければ
ならないのか。短い答えから並べます。

| 問い | 答え |
| --- | --- |
| 既存の`.po`と`.mo`はそのまま使えるか？ | 使えます。同じファイル、同じツールです。 |
| 旧来の呼び出しと新しい呼び出しは1つのファイルに同居できるか？ | できます。1つのextractor mappingが両方を拾います。 |
| msgidは変わるか？ | `.format()`からなら変わりません。`%`形式からなら変わります。 |
| プロジェクト全体を一度に移す必要があるか？ | ありません。呼び出し箇所1つでも有効な変更です。 |
| Jinja、Djangoテンプレート、JavaScriptはどうなるか？ | 手つかずのまま、同じカタログを使い続けます。 |

このページの残りは、それぞれの詳細です。

## `.format()`から：msgidは変わらない { #from-format-the-msgid-does-not-change }

移行の費用がほとんどかからないのがこの場合です。`str.format`のメッセージと
t-stringのメッセージは*同じ*カタログkeyを導きます。どちらでもkeyは`{name}`を
残したままのテキストだからです。

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

そのため既存の翻訳は結び付いたままです。次のカタログを出発点とします。

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

呼び出しを変更し、再抽出して、更新します。

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

戻ってくるエントリの違いはメタデータ2行だけで、他は何も変わりません。t-string
メッセージであることを示すmarker commentと、ソースの行番号です。

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

`fuzzy`フラグは付かず、どの言語でも再翻訳は要りません。メッセージはすぐに
表示されます。

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check`はカタログを古いと報告します"

    そのmarker commentと動いた行番号だけで、`pybabel update --check`はカタログの
    再生成が必要だと言います。翻訳だけでなくエントリ全体を比較するからです。
    コード変更と同じcommitで本物の`pybabel update`を実行し、カタログも一緒に
    commitしてください。すでに[CIゲート](workflow.md#what-ci-gates)が求めている
    のと同じ習慣です。

## `%`形式から：msgidが変わり、翻訳はfuzzyになる { #from--format-the-msgid-changes-so-translations-go-fuzzy }

printf構文はメッセージの*内側*にあるため、これを置き換えるとカタログkeyが
書き換わります。回避する方法はなく、`%(name)s`を手放すことの正直な代償です。

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update`は、新しいメッセージが削除されたメッセージの近縁だと認識し、
古い翻訳をfuzzy付きで引き継ぎます。

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

この状態について知っておくことが3つあります。

- **実行時に壊れるものはありません。** fuzzyエントリはコンパイル済みの`.mo`から
  除外されるため、人が組を確認するまでアプリケーションはソースメッセージを
  表示します。書き換えられたメッセージが通るのと
  [同じ劣化の仕方](workflow.md#the-cycle-after-the-first-translation)です。
- **`pybabel compile`はその1件ずつを報告し**、非ゼロで終了します。引き継がれた
  `{name}`ではない`%(name)s`が正しい波括弧プレースホルダーではないからです。
  その一覧は誤報ではなく作業リストです。並んだエントリは本当に編集を必要と
  しています。
- **古い`python-format`フラグも一緒に付いてきます。** `fuzzy`フラグと一緒に
  削除してください。さもないと`msgfmt --check-format`が、波括弧形式の
  メッセージにprintfの規則を当て続けます。

名前付きのprintfプレースホルダーなら編集は機械的です。`%(name)s`が`{name}`に
なるだけで、他は動きません。ですから大きなカタログでも、再翻訳ではなく、
スクリプトによる一括処理と翻訳者のレビューで済みます。位置指定の`%s`は機械的
ではありません。引き継ぐ名前がなく、その名前を選ぶことこそが今回の変更の
主眼だからです。

そのため実務上の順序は、`%`形式のメッセージを意図的に — モジュール単位、
リリース単位、言語単位で — 移すことです。すべてのカタログを一度に赤くする
一括作業は避けてください。

## 旧来の呼び出しと新しい呼び出しは同居する { #old-and-new-calls-coexist }

t-stringを読むextractorは通常のgettext呼び出しも読むため、移行途中のファイルも
mapping 1つで足ります。

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

どちらのメッセージも同じtemplateへ入り、このライブラリの追加検査を有効にする
marker commentが付くのはt-stringの方だけです。

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

認識するのは`_()`、4つの標準gettext名、`tr()` / `ntr()` alias、遅延用の
`lazy_gettext()` / `lazy_pgettext()`です。独自のhelperは
[mappingへ名前を登録](extraction.md#registering-your-own-function-names)する
必要があります。

実行時にも、2つのスタイルは同じように独立しています。`gettext.translation()`が
翻訳オブジェクトを1つ返し、`_`もこのライブラリの入り口も、そこから読みます。

## 移らないもの { #what-does-not-move }

- **テンプレート言語。** Jinja2の`{% trans %}`、Djangoのtemplate tag、そして
  それぞれのBabel extractorは、そのまま動き続け、同じPOカタログへ流れ込み
  続けます。t-stringはPythonの構文であり、対象はPythonソースです。
- **カタログファイル。** 形式の変更も、新しいファイルも、変換工程もありません。
- **翻訳プラットフォーム。** `.po`によるやり取りは同一で、t-stringメッセージが
  持つ`python-brace-format`フラグは`.format()`のメッセージが持つものと同じ
  フラグです。プレースホルダーQAはそのまま働きます。
- **Python以外のコード。** 同じプロジェクト内のJavaScriptやCのカタログは
  影響を受けません。

## 移行のチェックリスト { #a-migration-checklist }

1. `pybabel`を実行する場所へ`babel` extraを追加し、`babel.cfg`の`python`
   mappingを`gettext_tstrings`メソッドへ変更します。これでmapping 1つが両方の
   スタイルを拾い、通常の呼び出しには`-k`が引き続き効きます。
2. まず`.format()`の呼び出し箇所を変換します。再抽出して`pybabel update`を
   実行し、カタログをコードと一緒にcommitします。fuzzyエントリは出ないはずです。
3. `%`形式の呼び出し箇所を、レビューできる大きさの単位で変換します。引き継がれた
   プレースホルダーを書き換え、`fuzzy`と`python-format`のフラグを外します。
4. 制約が拒否するものを直します。補間は単純な名前でなければならないので、
   `t"Hello {user.name}"`はまずローカル変数にします。これは呼び出し箇所の編集
   であり、カタログの編集ではありません。
5. 一巡し終えたらextractor mappingの`strict = true`を有効にします。抽出できない
   メッセージがtemplateから消えるのではなく、
   [ビルドを落とす](extraction.md#lenient-locally-strict-in-ci)ようになります。
6. [実運用](workflow.md#what-ci-gates)の実行時チェックを追加します。出荷する
   言語ごとに1つのメッセージを、strictな`Translator`でレンダリングします。

ステップ2と3は普通のcommitです。この一覧に、一斉切り替えの日を要するものは
ありません。
