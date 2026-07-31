---
description: "%形式、.format()、flufl.i18nの$文字列、t-stringで同じ翻訳対象メッセージを記述し、翻訳者のミス、カタログに与える権限、導入コストの3点で比較します。"
---

# t-stringを選ぶ理由

翻訳対象のメッセージへ値を埋め込む4つの方法を、同じメッセージで比較します。
4つとも、プレースホルダーに名前を付け、翻訳者による並べ替えを許します。
違いが出るのは、翻訳が誤っていたときに何が起こるか、カタログがプログラムの
どこまで手を伸ばせるか、そして採用に何がかかるかです。

まず表を置きます。気になる行を見つけて、その裏にある節だけを読めるように
するためです。

!!! note "翻訳されるメッセージには3者が関わる"

    **カタログ**とは翻訳のファイルです。人が編集する間は`.po`で、
    アプリケーションが読み込むために`.mo`へコンパイルされます
    （[チュートリアル](tutorial.md)で両方を扱います）。すべてのメッセージには
    3者が関わります。**開発者**がソース文字列を書き、**翻訳者**がカタログを
    編集し — 多くの場合、コードレビューから遠く離れた外部プラットフォーム上で
    です — **アプリケーション**が実行時に両者を組み合わせてレンダリングします。
    以下の各書式スタイルは、同じ問いに異なる答えを出します。
    *カタログにフォーマット言語のどこまでを制御させるのか？*
    例中の`_`は翻訳関数の慣習的な名前で、`tr`はこのライブラリの関数です。

## 比較 { #side-by-side }

**翻訳者がミスをしたとき。** カタログは多くの人の手を渡り、そこで起こる問題の
ほとんどは偶発的なものです。

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 翻訳がプレースホルダーを*削除*した場合、何がレンダリングされるか？ | 値は何も表示せず消える | 値は何も表示せず消える | 値は何も表示せず消える | ソースメッセージ＋警告（[既定では](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻訳が未知のプレースホルダーを*追加*した場合、何がレンダリングされるか？ | 例外 | 例外 | プレースホルダーがテキストとして見える形で残る | ソースメッセージ＋警告（[既定では](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻訳がプレースホルダーの*書式を変えた*場合、何がレンダリングされるか？ | カタログが指示したとおり。型文字が値に合わなくなれば例外 | カタログが指示したとおり | `$`文字列では表現できない | ソースメッセージ＋警告 |
| プレースホルダーはレンダリング時に検査されるか？ | いいえ | いいえ | いいえ | はい（下記参照） |

**カタログにどこまでの権限を与えるか。** 翻訳はリポジトリの外から来るデータで
あり、スタイルごとに渡す力の大きさが違います。

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 値はどこから来るか？ | 明示的なマッピング | 明示的な引数 | 呼び出し元のローカル変数とグローバル変数（任意の`extras`を追加可能） | t-string内に取り込まれた値 |
| カタログは値の書式を変えられるか？ | はい | はい | いいえ | いいえ |
| カタログはオブジェクトの中へ届くか（属性アクセス）？ | いいえ | はい | はい（ドット付きの名前） | いいえ |
| 「現在の言語」はどこに置かれるか？ | アプリケーションが置いた場所 | アプリケーションが置いた場所 | 共有アプリケーションオブジェクト上にある言語コードのスタック | `ContextVar`（タスクまたはリクエストごと） |

**導入に何がかかるか。** ツールが噛み合えば上記はすべて無償で手に入ります。
噛み合わない可能性があるのがここです。

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 必要な最小のPython | 制限なし | 制限なし | 3.10 | **3.14** |
| 成熟度 | 標準ライブラリ | 標準ライブラリ | 安定版リリース | **alpha** |
| 通常のPO/MOカタログを使用するか？ | はい | はい | はい | はい |
| 独自のソース抽出器が必要か？ | いいえ | いいえ | いいえ | 現時点では、はい |
| 既存ツールの検証用にBabelが推論するPOフラグは？ | `python-format` | `python-brace-format` | なし | `python-brace-format` |

レンダリング時の検査について：単数形メッセージはプレースホルダーの完全一致を
検査します。複数形メッセージも、対象言語の複数形がソース言語と異なることを
許す[和集合／積集合の規則](spec.md)に基づいて検査されます。formごとのより
厳密な検査は、カタログのコンパイル時に実行されます（[抽出](extraction.md)）。

書式フラグの行は、カタログの互換性ではなく、プレースホルダーを認識した検証に
関するものです。「なし」でも、標準のgettextツールはメッセージを読み取り、
コンパイルできますが、`msgfmt --check-format`には適用できる
`$`プレースホルダーの文法がありません。

## 互換性と成熟度 { #compatibility-and-maturity }

最後の表の最初の2行は採用の可否を決める行なので、セルの中ではなくはっきりと
文章で述べておきます。

`%`形式と`.format()`はPythonに組み込まれており、依存パッケージは一切要りません。
[`flufl.i18n`][flufl-i18n]は成熟したパッケージで、リリース済みかつ本番で使われて
おり、Python 3.10以降で動作します。`gettext-tstrings`は**alpha版**であり、
**Python 3.14以降**を必要とします。t-stringが3.14の新しい構文であるためで、
バックポートは存在せず、あり得ません。安定しているのは[仕様](spec.md)の部分で、
Python APIは1.0までまだ動く可能性があります。

どれについても発生しないのが、カタログの互換性という費用です。4つとも通常の
POT/PO/MOファイルを生成し、あらゆるPOエディタ、翻訳プラットフォーム、GNU
gettextツールがすでにそれを読めます。ですからここでの選択は、カタログの
*形式*を変える場合とは違って、後から取り消せます。既存プロジェクトを移す話は
[移行](migration.md)で扱います。

以下の各節では、方式ごとにトレードオフを詳しく見ていきます。

## %形式 { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

何が起こり得るか：翻訳で1文字消えるだけで、レンダリングがクラッシュします。

カタログ文字列にはprintf構文が含まれます。そこには`%(name)s`の`s`という、
見落としやすく壊しやすい末尾の型文字も含まれます。

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

POエディターでの1文字の変更が、カタログ検証で先に捕まらない限り、実行時の
例外になります。GNU `msgfmt --check-format` はこれを検出できますが、
メッセージに`python-format` フラグがあり、かつカタログがアプリケーションへ
届くまでに実際にmsgfmtを通る場合に限られます。

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

末尾の型文字がなくなり、名前が付いて自由に並べ替えられるプレースホルダーは
維持されます。何が起こり得るかは、やり取りの反対側へ移ります。翻訳が
あなたのオブジェクトに対する力を得るのです。

`str.format` は小さな式言語であり、文字列に対して
呼び出すことは、その文字列へ式言語を使う権限を与えることになります。

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

次に、これらの文字列リテラルを`_()`が返すものに置き換えてみてください。
`Hello {name}`の翻訳が`{conf.api_key}`として返ってくれば、レンダリングは
あなたのAPIキーを出力します。何が読み取られるかを決めたのは、コードではなく
カタログです。カタログはコードではありませんが、データとして移動します。
翻訳プラットフォームへ渡り、複数の人の手を経て`.po`として戻り、`.mo`へ
コンパイルされ、ときには外部プロジェクトからそのまま取り込まれます。
`.format()` は、この経路のすべての段階に、渡されたオブジェクトの属性へ
アクセスできる文字列を置くことになります。

## `$`文字列とflufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

標準ライブラリの[`string.Template`][stdlib-template]は`$name`という補間言語を提供しますが、
それ自体は翻訳APIではありません。[`flufl.i18n`][flufl-i18n]は、この形式とgettextの
カタログ検索を組み合わせます。値がどこにも渡されていないことに注目してください。
flufl.i18nは置換に使う名前空間を呼び出し元のグローバル変数とローカル変数から
構築します。呼び出し箇所に存在する変数はすべてメッセージから利用できます。
任意の`extras`マッピングはその両方より優先されます。
翻訳者が扱う構文には末尾の型文字や書式指定がなく、プレースホルダーも自由に
並べ替えられます。

置換値が見つからなくても例外にはなりません。`name = "Ada"`で、呼び出し元の
名前空間に`nombre`がないとき、カタログの翻訳`Hello $nombre`は
`Hello $nombre`とレンダリングされ、未解決のプレースホルダーが見える形で残ります。
この[文書化された挙動][documented behavior]は、呼び出しを失敗させず、翻訳済み
メッセージの残りを保持します。ただし、属性の解決中や値の変換中に発生した例外は
伝播することがあります。

関連する点で、`flufl.i18n`は素の`string.Template`より高機能です。
その[独自Template][custom Template]は`$settings.api_key`のようなドット付き
プレースホルダーを受け付け、[translator]は呼び出し元の値に対してそのパスを
解決します。翻訳側のプレースホルダーは、利用可能なローカル変数やグローバル変数を
指定でき、ドット構文ならその属性もたどれます。メッセージに属性が必要な場合には
便利ですが、呼び出し元のフレームもカタログの置換名前空間の一部になります。
ここでの比較は`flufl.i18n` 6.0.0を対象とし、`string.Template`のあらゆる使い方を
表すものではありません。

さらに`flufl.i18n`は、他の2つの書式スタイルが完全にアプリケーション任せに
している問いにも答えます。*どの*言語がいま有効で、それをどう切り替えるか、という
問いです。[アプリケーションオブジェクト][application object]が言語のスタックを保持し、
`_.push(code)`と`_.pop()`がそれを動かし、`with _.using(code):`が入れ子を作ります。
そして[strategy]が言語コードからカタログを見つけるため、アプリケーション自身が
カタログオブジェクトを扱うことはありません。1つの作業単位のあいだに複数の言語で
テキストを生成しなければならないサーバー — 読み手向けのページと、設定言語の異なる
誰かへの通知 — こそ、この仕組みが存在する理由です。

そのスタックはアプリケーションオブジェクト上にあり、プロセス全体がそれを共有します。
したがって重なり合う2つのリクエストは1つのスタックを共有し、*時間的に*厳密な
入れ子になっていないブロックは、互いに誤った言語を渡し合います。

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

このライブラリは同じ機能 — 束縛は同じように入れ子になり、同じように巻き戻ります —
を、共有スタックではなく`ContextVar`の中に置きます。そのため上記の交錯はタスクごとに
解決されます。対応する書き方は
[複数の言語を同時に扱う](guide.md#several-languages-at-once)にあります。
提供しないのは言語コードからカタログへの検索です。渡すのは翻訳オブジェクトで、
よくある場合は`gettext.translation()`の呼び出し1回で得られ、解析済みカタログは
標準ライブラリがキャッシュします。

## t-string { #t-strings }

```python
tr(t"Hello {name}")
```

カタログには引き続き`Hello {name}`が渡され、通常のPO/MOカタログを利用できます。
違いは、翻訳が*何を言うことを許されるか*と、それを誰が検査するかです。

このライブラリは、レンダリングの前にすべての翻訳を元メッセージの
プレースホルダーと照合して検証します。受け付けるのは単純な名前だけです。
`t"Hello {name}"`に対しては次のようになります。

| 翻訳に含まれるもの | 拒否理由 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

拒否はクラッシュを意味しません。既定ではライブラリが警告をログに記録し、
ソースメッセージをレンダリングするため、不正なカタログがアプリケーションを
停止させることはありません —
[gettext自身が守っているのと同じ契約](guide.md#what-happens-when-a-catalog-is-wrong)です。

書式指定は、それが書かれた場所、つまりコードに置かれたままです。

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` はカタログへ届きません。翻訳が変更することも、翻訳者が目にすることも
ありません。ただしこれは*固定の*書式であって、ローカライズされた書式では
ありません。言語ごとに桁と区切り記号を選ぶのは
[呼び出しの前に行うBabelの仕事](guide.md#locale-aware-values)です。

もう一つの違いはツールです。t-stringは新しい構文なので、`.pot`への抽出には
現在のところt-string対応の抽出器が必要です。このパッケージが
[Babel向けに提供する](extraction.md)ものはその一つです。

## 制約の代償 { #the-cost-of-the-restriction }

Pythonのバージョン要件を別にすれば、ここまでの代償は規則1つです。補間は単純な
名前でなければなりません。

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

これは実際の制約であり、同時に、上に挙げた保証を生んでいるのもこの制約です。
ソース側での値の結び付けや実行時のプレースホルダー検査と組み合わせることで、
カタログ文字列による式の評価を防ぎ、プレースホルダー名を、それを翻訳する人に
とって意味のあるものに保ちます。

f-stringをこの方法で使うことはできません。ライブラリが受け取る時点では完成した
文字列なので、翻訳すると文の断片を翻訳することになります。t-string（[PEP 750]）は
f-stringに似た構文と明示的な値の結び付けを保ちながら、静的なテキストと値を
分離したまま保持します。

Pythonがどのようにしてこの岐路へ辿り着いたのか — 10年を隔てた2つのPEP、
そして答えのないまま閉じられた標準ライブラリの議論 — は、
[背景](background.md)で出典とともに語られています。

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
