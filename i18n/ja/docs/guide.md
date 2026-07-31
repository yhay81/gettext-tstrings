---
description: "ランタイムAPIのガイドです。どの入り口を使うか、カタログの束縛、リクエストごとの言語、遅延文字列、ロケールに応じた値、不正な翻訳の報告方法を説明します。"
---

# ガイド

このページはランタイムのリファレンスです。カタログが用意できた後に
*アプリケーションコード*がこのライブラリで行うすべてを説明します。
マーク、抽出、翻訳、コンパイル、実行という一連のループをまだ見ていない場合は、
[チュートリアル](tutorial.md)が5分で一巡します。カタログの作成と検証は
[抽出](extraction.md)で、チームがこのループを回し続ける方法 — 更新サイクル、
CI、翻訳プラットフォーム — は[実運用](workflow.md)で説明します。

## どの入り口を使うか { #which-entry-point-should-i-use }

メッセージを翻訳する手段をこのパッケージがいくつも公開しているのは、
アプリケーションが言語を束縛する方法がいくつもあるからです。プログラムが
「いまどの言語なのか」をどう決めているかで選んでください。

| あなたの状況 | 使うもの |
| --- | --- |
| プロセス全体で1つの言語 — CLI、デスクトップアプリ、スクリプト | `Translator`を`_`として呼び出す |
| リクエストごと、または非同期タスクごとに1つの言語 — Webアプリケーション | 処理を`use_translations()`で囲み、`tr()`を呼ぶ |
| import時に定義されるメッセージ — フォームラベル、enum、定数 | `lazy_gettext()`または`lazy_pgettext()` |
| 個数が文言を決める | 上記のいずれの形でも`ngettext()` / `npgettext()` |
| カタログを介さずpatternをレンダリングする | `compile_template()` |

以下では、この5つをこの順で説明します。

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
    name = request.user.display_name
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

`strict`は、レンダリングされる場所ではなく、メッセージが書かれる場所で決めます。

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

遅延文字列は最終的に使われる場所でレンダリングされます。templateの中、
フォームの中、ログ行の中 — そしてその場所は、これがテスト実行なのか本番なのかを
知らないのが普通です。定義時に`strict=True`を渡すことで、呼び出し箇所で
レンダリングされない文字列に対しても、[CIでは大きな声で、本番では寛容に](#what-happens-when-a-catalog-is-wrong)という
同じ選択を適用できます。

複数形は実行時の個数に依存するため、個数が分かる場所で`ngettext`を使って即時に
レンダリングします。

## 複数の言語を同時に扱う { #several-languages-at-once }

1つのリクエストが複数の言語を必要とすることはよくあります。読み手向けにページを
レンダリングしつつ、別の言語に設定されたアカウントへ通知をキューへ入れる場合や、
各参加者の発言をそれぞれの言語で引用するダイジェストなどです。束縛は入れ子にでき、
内側のブロックを抜ければ外側の束縛が戻ります。

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

宛先の一覧に対しては遅延文字列が働きます。メッセージはimport時に一度だけ書かれ、
言語ごとに一度レンダリングされます。

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

束縛は共有オブジェクト上のスタックではなく`ContextVar`です。そのため、重なり合う
リクエストが互いの言語を拾ってしまうことはありません。ブロックに入ったのと同じ順で
そのまま*抜けていく*場合 — プッシュダウンスタックが取り違えるのはこの交錯です —
であっても同じです。言語ごとにカタログを読み込む費用は小さく、
`gettext.translation()`は各`.mo`を一度だけ解析し、解析済みカタログを共有する
コピーを渡します。

!!! warning "ワーカースレッドが束縛を引き継ぐかはビルド次第"

    素の`threading.Thread`や`ThreadPoolExecutor.submit`は、呼び出し側の
    コンテキストのコピーから始まることも、空のコンテキストから始まることも
    あります。どちらになるかを決めるのは`sys.flags.thread_inherit_context`で、
    free-threadedビルドでは既定でtrue、それ以外では既定でfalseです。つまり
    同じコードが、3.14tでは束縛した言語を、3.14ではプロセスグローバルな
    カタログを描画します。既定に頼らず、コンテキストを渡してください。

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread`はこれをすでに行っています。

## ロケールに応じた値 { #locale-aware-values }

このライブラリが決めるのは、翻訳済みメッセージの*どこに*値が現れるかです。
値そのものをローカライズはしません。`{amount:,.2f}`は挙動が固定された
Pythonのフォーマット指定 — 3桁ごとにカンマ、小数部の前にピリオド — であり、
メッセージが何語であっても同じ文字を生成します。

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

ドイツ語ではこの数を`1.234,50`と書き、フランス語では`1 234,50`と書きます。
ヒンディー語は`1234567`を`1,234,567`ではなく`12,34,567`と区切ります。数値、
通貨、日付、時刻、単位は[Babel][babel-numbers]の担当です。先に値を整形し、
出来上がった文字列を配置してください。

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

個数付きメッセージでは、数が2つの仕事をします。複数形を選ぶことと、テキストに
現れることです。ローカライズされるのは後者だけです。選択には生の個数を残し、
表示には整形済みの文字列を渡してください。

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

呼び出しの前に整形することは、フォーマット指定をカタログの外に保つことでも
あります。翻訳者が目にするのは、数値とその描画方法の指示ではなく、完成した
1つのテキストです。

## カタログが不正な場合 { #what-happens-when-a-catalog-is-wrong }

翻訳のプレースホルダーがソースと一致しない場合を考えます。欠落したfield、未知の
field、書式を変えたfieldが検証をすり抜け、手編集のMO、vendorのカタログ、
checkerを省略したpipelineから届くかもしれません。既定動作は、例外の送出ではなく
ソースメッセージのレンダリングです。不正なカタログでアプリケーションを停止させ
ないというgettext自身の契約に合わせています。

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

これらのメッセージは、問題を修正できる人のために書かれています。カタログの問題を
直すのはprogrammerより翻訳者である場合が多いためです。そこで、プレースホルダーが
存在するように見えて実際には存在しない場合は、欠落していると繰り返す代わりに、
その理由を説明します。全角の波括弧、二重になった`{{name}}`、目に見えない
no-break space、Latin文字に紛れたCyrillic文字 — それぞれに固有の文面があり、
[翻訳者向け](translators.md#reading-a-failure-message)に例とともに一覧して
あります。あのページは`.po`を編集する人へそのまま渡せるように書かれています。

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
