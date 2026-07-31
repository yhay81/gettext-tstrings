---
description: "pybabelによるt-stringメッセージの抽出と、msgfmtおよび同梱Babel checkerによるカタログ検証を説明します。"
---

# 抽出

抽出は、ソースコード中のマークされたすべてのメッセージを、翻訳者向けの
`.pot` templateへ集める工程です。[チュートリアル](tutorial.md)のループの
ステップ3にあたります。このページはその工程のリファレンスです。設定、独自の
関数名、CI向けのstrictモード、そしてカタログをその後守り続ける検証を
説明します。

抽出には`babel` extraが必要です。

```console
python -m pip install "gettext-tstrings[babel]"
```

## ワークフロー { #the-workflow }

`babel.cfg`を作成します。

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

その後は通常のBabelコマンドを使います。

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init`を実行するのは言語ごとに一度きりです。それ以降は、`pybabel update`が
新しいtemplateを既存のカタログへ折り込みます。この繰り返しのサイクルと、
その`fuzzy`エントリがリリースにとって何を意味するかは、
[実運用](workflow.md#the-cycle-after-the-first-translation)で一巡します。

`gettext_tstrings` extractorは通常の`_()`、`gettext()`、`ngettext()`呼び出しも
処理するため、混在したcodebaseを1つのmappingで抽出できます。`_()`、4つの標準
gettext名、`tr()` / `ntr()` alias、遅延用の`lazy_gettext()` /
`lazy_pgettext()`を認識します。

!!! warning "`-c`は省略できません"

    通常のgettext呼び出しと同じく、`pybabel extract`で翻訳者向けコメントを
    収集するには`-c "Translators:"`を渡す必要があります。

## 独自の関数名を登録する { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

iniファイルでは1つの文字列、TOML mappingではlistを指定します。文字列内の名前は
空白またはcommaで区切れます。4通りの表記すべてに対応します。

optionは`tr_functions`、`ntr_functions`、`gettext_functions`、
`ngettext_functions`、`pgettext_functions`、`npgettext_functions`です。

!!! danger "`-k`はt-stringへ届きません"

    `mytr(t"…")`のような独自helperは、上記optionのいずれかへ名前を登録する必要が
    あります。Babelの`--keyword`機構はt-string literalを読めないため、
    `pybabel extract -k mytr`は何も見つけず、警告も出しません。メッセージがPOTに
    入らないだけです。併せて抽出される通常のgettext呼び出しには、引き続き`-k`を
    使用できます。

    対応するのは標準の引数順だけです。通常はmessageが先、`pgettext`ではcontextの
    次にmessage、`npgettext`ではcontext、単数形、複数形の順です。

## 既定で堅牢 { #robust-by-default }

1つの不正なファイルで抽出全体が停止することはありません。

- extractorが拒否するt-string（属性アクセス、式、不正な引数）は警告して
  skipします。
- parseできないファイルも同様にskipします。
- `ast`では受理されても`tokenize`だけが拒否するファイルもskipします。そうしないと
  Babel自身のpassが停止するためです。

mapping optionで`strict = true`を指定すると、これらをすべてhard failureにできます。
CIではこの設定が適しています。

## 既存toolchainによるカタログ検証 { #your-existing-toolchain-validates-these-catalogs }

Babelは抽出した各メッセージへ標準flagを付けます。この1行だけで、すでに使っている
ツールのプレースホルダー検証が有効になります。

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

`こんにちは {nombre}`と翻訳すると、追加設定なしで誤りが検出されます。

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblateでは同じ検証が[Python brace format][weblate-checks]として文書化されており、
商用platformにも同じflagに基づくplaceholder QAがあります。その挙動は各製品に
属します。ここで検証しているのは以下の2ツールです。

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

さらに、このパッケージはBabel **checker**を登録します。そのため
`pybabel compile`は`gettext-tstrings` marker commentを持つすべてのメッセージへ
仕様の規則を適用します。

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

複数形メッセージでは対象のformも示します。Babelが報告する行番号はmsgidの行であり、
ロシア語のblockにはその下に3つの`msgstr`があるためです。

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile`はそれでも`.mo`を書き出します"

    上記エラーは報告され、終了statusは`1`ですが、不正なカタログもコンパイル
    されます。出荷を止められるのはその終了statusだけです。それを働かせるビルド
    ステップは[CIで防ぐこと](workflow.md#what-ci-gates)で示します。

2つの検証は重複していません。同梱checkerの方が厳密な箇所が少なくとも2つあります。

- msgidの波括弧がescapeされたものだけ（`Config {{raw}} only`）なら
  `python-brace-format` flagが付かないため、外部ツールは一切検証しません。
- 複数形はformごとに検証します。上記ファイルを`msgfmt --check-format`で読むと
  status `0`になります。兄弟formが保持するプレースホルダーを1つのformだけが
  省略してもmsgfmtでは受理され、こちらのcheckerでは拒否されます。

`msgfmt`が検証するのは、Python brace formatとしてparseできるプレースホルダー名だけ
です。ASCII名を使えば、toolchain内のすべてのツールがメッセージを検証できます。
ライブラリ自体は`str.isidentifier()`を満たすすべての名前を受理します。

## Templateとその他のツール { #templates-and-other-tools }

t-stringはPython構文なので、このライブラリの対象はPython sourceです。template言語は
それぞれのi18n機能（Jinja2の`{% trans %}`、Djangoのtemplate tag）とBabel extractor
を引き続き使います。すべて同じPOカタログへ入るため、混在したcodebaseでも1つの
翻訳ワークフローを維持できます。

現在の`pygettext`はt-stringをparseできないため、抽出にはBabelを使います。他の
extractorや将来の`pygettext`が同じ規約を実装できるよう、
[仕様](spec.md)として文書化しています。
