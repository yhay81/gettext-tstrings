---
description: "カタログの束縛、リクエストごとの言語、遅延文字列、不正な翻訳の報告方法を含むランタイムAPIのガイドです。"
---

# ガイド

このページはランタイムのリファレンスです。カタログが用意できた後に
*アプリケーションコード*がこのライブラリで行うすべてを説明します。
マーク、抽出、翻訳、コンパイル、実行という一連のループをまだ見ていない場合は、
[チュートリアル](tutorial.md)が5分で一巡します。カタログの作成と検証は
[抽出](extraction.md)で、チームがこのループを回し続ける方法 — 更新サイクル、
CI、翻訳プラットフォーム — は[実運用](workflow.md)で説明します。

## カタログを束縛する { #binding-a-catalog }

推奨する構成はgettextのクラスベースの使い方と同じです。標準の翻訳オブジェクトを
一度束縛し、呼び出し可能なprocessorを`_`として使います。

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

モジュールレベル関数は、標準ライブラリと同じ名前と位置専用の呼び出し規約を
採用しています。

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr`と`ntr`は、`gettext`と`ngettext`の完全なaliasです。

## リクエストごとの言語 { #per-request-language }

Web frameworkはリクエストごとに言語を選択します。そのリクエストの翻訳を現在の
コンテキストへ束縛すると、すべてのモジュールレベル呼び出しがその言語で解決されます。
並行するリクエスト間でも安全です。

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

リクエストのライフサイクルをframework自身が管理する場合は、
`set_translations(translations)`で`with`ブロックなしに束縛できます。
`get_translations()`は現在の束縛を返します。明示的な`translations=`引数は
常にコンテキストより優先されます。コンテキストが未束縛なら、標準ライブラリに
グローバルにインストールされたgettext関数へfallbackします。FlaskとASGI
ミドルウェアの実例は[実運用](workflow.md#binding-a-language-at-runtime)の
ページにあります。

## 遅延翻訳 { #deferred-translation }

t-stringは値を即時に取得します。そのため、import時に定義され、*使用時*に有効な
言語で表示されるべき文字列（フォームラベル、enum値、モジュール定数）には不向きです。

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString`は`str()`、`format()`、f-stringを通じてレンダリングされ、
レンダリング後のテキストと等値比較できます。

!!! note "意図的にhash不能"

    `LazyString`のテキストは有効な言語に依存します。hash値が言語切替によって
    変わると、それを保持するsetやdictが気付かないまま壊れます。keyが必要な場合は
    先に`str()`を呼び出してください。

複数形は実行時の個数に依存するため、個数が分かる場所で`ngettext`を使って即時に
レンダリングします。

## カタログが不正な場合 { #what-happens-when-a-catalog-is-wrong }

翻訳のプレースホルダーがソースと一致しない場合を考えます。欠落したfield、未知の
field、書式を変えたfieldが検証をすり抜け、手編集のMO、vendorのカタログ、
checkerを省略したpipelineから届くかもしれません。既定動作は例外ではなくソース
テキストの再現です。不正なカタログでアプリケーションを停止させないというgettext
自身の契約に合わせています。

`Hello {name}` が `こんにちは {nombre}` と翻訳されていてもレンダリングは成功し、
`gettext_tstrings` loggerへ警告が1件送られます。

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

警告はメッセージとpatternの組み合わせごとに1回だけ発生します。レンダリングごとでは
ないので、不正なカタログ項目がログを埋め尽くすことはありません。

テストとCIでは明示的に失敗させられます。

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

同じ検索が例外を送出します。文面は同じですが、「using source text」の部分は
付きません。

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## エラーメッセージを読む { #reading-a-failure-message }

これらのメッセージは、問題を修正できる人のために書かれています。カタログの問題を
直すのはprogrammerより翻訳者である場合が多いためです。画面上では文字が見えている
のに`{name}`がないとだけ報告しても手掛かりになりません。そのため、
プレースホルダーが存在するように見えて実際には存在しない場合、理由まで示します。
ソース`Hello {name}`に対して、次の各翻訳は
`translation does not match the source placeholders:`に続けて報告されます。

| 翻訳の内容 | 報告される理由 |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

目に見えない文字は別に扱います。波括弧内のno-break spaceは入力メソッドが生成する
ことがあり、editorでは見えません。そのため、見つけられない文字の名前ではなく
code pointで表示します。

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

文字体系が混在した名前、たとえばLatin文字と見分けがつかないCyrillicの`а`を含む
homoglyphの場合、読みやすい形とescapeした形の両方を示します。両者を区別できるのは
後者だけです。

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

同じ区別は、GreekまたはCyrillicだけで書かれた名前がASCIIのソース名と衝突する
場合にも適用されます。Latinの`a`とCyrillicの`а`という1文字の場合も同様です。

## カタログなしでpatternをレンダリングする { #rendering-a-pattern-without-a-catalog }

`compile_template`は同じ仕組みを1段下で公開します。t-stringをmsgidと束縛済みの
値の集合へ変換し、渡された任意のpatternをレンダリングします。

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render`は同じ規則で検証し、不一致では**常に例外を送出**します。ここにlenient
モードはありません。lenientは*カタログ*検索がソーステキストへfallbackするための
ものであり、直接渡したpatternにはfallback元がないためです。

## 安全性と範囲 { #safety-and-scope }

これは有効です。

```python
tr(t"Hello {name}")
```

次は意図的に拒否されます。

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

先に意味のある値を計算します。

```python
name = user.display_name()
tr(t"Hello {name}")
```

この制約によって安定したカタログkeyが生まれ、翻訳者には分かりやすい名前が渡り、
翻訳文字列が式言語になることを防ぎます。

保証の範囲は*構造と書式*です。翻訳は評価されず、属性アクセス、関数呼び出し、
変換指定、フォーマット指定を追加できません。2つの責任は、標準ライブラリのgettext
と同様に呼び出し側へ残ります。出力先（HTML、shell、terminal）に応じた
レンダリング結果の**escape**と、**カタログの完全性**です。悪意あるカタログは
プレースホルダーを繰り返して出力サイズを増幅できます。これはプレースホルダーを使う
すべてのi18nに共通する性質です。
