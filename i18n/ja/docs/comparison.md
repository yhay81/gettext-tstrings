---
description: "%形式、.format()、flufl.i18nの$文字列、t-stringで同じ翻訳対象メッセージを記述し、それぞれの値の結び付け方と、壊れたカタログの扱いを比較します。"
---

# t-stringを選ぶ理由

翻訳対象のメッセージへ値を埋め込む方法は、すべて同じ問いに答える必要があります。
*カタログにフォーマット言語のどこまでを制御させるのか？* 以下の4方式は、
値をどこから取得するか、カタログがプレースホルダーを変更したときに何が起こるかも
異なります。

## %形式

```python
_("Hello %(name)s") % {"name": name}
```

カタログ文字列にはprintf構文が含まれます。そこには見落としやすく、
1文字の変更で壊れ得る末尾の型文字も含まれます。

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

POエディターでの1文字の変更が、本番環境のtracebackになります。
GNU `msgfmt --check-format` は検出できますが、メッセージに
`python-format` フラグがあり、かつカタログがアプリケーションへ届くまでに
実際にmsgfmtを通る場合に限られます。

## str.format

```python
_("Hello {name}").format(name=name)
```

末尾の型文字がなくなり、名前が付いて自由に並べ替えられるプレースホルダーは
維持されます。

問題は別の側にあります。`str.format` は小さな式言語であり、文字列に対して
呼び出すことは、その文字列へ式言語を使う権限を与えることになります。

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

カタログはコードではありませんが、データとして移動します。翻訳プラットフォームへ
渡り、複数の人の手を経て`.po`として戻り、`.mo`へコンパイルされ、ときには外部
プロジェクトからそのまま取り込まれます。`.format()` は、この経路のすべての段階に、
渡されたオブジェクトの属性へアクセスできる文字列を置くことになります。

## `$`文字列とflufl.i18n

```python
name = "Ada"
_("Hello $name")
```

標準ライブラリの[`string.Template`][stdlib-template]は`$name`という補間言語を提供しますが、
それ自体は翻訳APIではありません。[`flufl.i18n`][flufl-i18n]は、この形式とgettextの
カタログ検索を組み合わせます。置換に使う名前空間は呼び出し元のグローバル変数と
ローカル変数から構築され、任意の`extras`マッピングはその両方より優先されます。
翻訳者が扱う構文には末尾の型文字や書式指定がなく、プレースホルダーも自由に
並べ替えられます。

置換値が見つからなくても例外にはなりません。`name = "Ada"`で、呼び出し元の
名前空間に`nombre`がないとき、カタログの翻訳`Hello $nombre`は
`Hello $nombre`とレンダリングされ、未解決のプレースホルダーが見える形で残ります。
この[文書化された挙動]は、呼び出しを失敗させず、翻訳済みメッセージの残りを
保持します。ただし、属性の解決中や値の変換中に発生した例外は伝播することがあります。

関連する点で、`flufl.i18n`は素の`string.Template`より高機能です。
その[独自Template]は`$settings.api_key`のようなドット付きプレースホルダーを
受け付け、[translator]は呼び出し元の値に対してそのパスを解決します。
翻訳側のプレースホルダーは、利用可能なローカル変数やグローバル変数を指定でき、
ドット構文ならその属性もたどれます。メッセージに属性が必要な場合には便利ですが、
呼び出し元のフレームもカタログの置換名前空間の一部になります。以下の比較は
`flufl.i18n` 6.0.0を対象とし、`string.Template`のあらゆる使い方を
表すものではありません。

## t-string

```python
tr(t"Hello {name}")
```

カタログには引き続き`Hello {name}`が渡され、通常のPO/MOカタログを利用できます。
ソース抽出は異なり、現在のツールには、このパッケージが提供するもののような
t-string対応の抽出器が必要です。翻訳は元メッセージのプレースホルダーと照合され、このライブラリが
レンダリングします。受け付けるのは単純な名前だけです。
`t"Hello {name}"`に対しては次のようになります。

| 翻訳に含まれるもの | 拒否理由 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

書式指定はソースに置かれたままです。

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` はカタログへ届きません。翻訳が変更することも、翻訳者が目にすることも
ありません。

## 比較

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| プレースホルダーに名前がある | はい | はい | はい | はい |
| 翻訳者が並べ替えられる | はい | はい | はい | はい |
| 値の取得元 | 明示的なマッピング | 明示的な引数 | 呼び出し元のグローバル変数とローカル変数（任意の`extras`で上書き可能） | t-stringが取り込んだ補間値 |
| カタログが値の変換や書式指定を制御する | はい | はい | いいえ | いいえ |
| カタログから属性へのアクセスを要求できる | いいえ | はい | はい（ドット付きの名前） | いいえ |
| ソースのプレースホルダーがレンダリング時に削除された場合 | 何も表示せず省略 | 何も表示せず省略 | 何も表示せず省略 | [既定では](guide.md#what-happens-when-a-catalog-is-wrong)ソースパターンを完全にレンダリング |
| 追加されたプレースホルダーの値がレンダリング時にない場合 | 例外 | 例外 | 未解決のまま表示 | [既定では](guide.md#what-happens-when-a-catalog-is-wrong)ソースパターンを完全にレンダリング |
| 実行時にソースのプレースホルダー集合を検査（単数形） | いいえ | いいえ | いいえ | はい |
| この例についてBabelが推論するPO書式フラグ | `python-format` | `python-brace-format` | なし | `python-brace-format` |
| 通常のPO/MOカタログを使用 | はい | はい | はい | はい |
| 独自のソース抽出器が必要 | いいえ | いいえ | いいえ | 現時点では、はい |

書式フラグの行は、カタログの互換性ではなく、プレースホルダーを認識した検証に
関するものです。「なし」でも、標準のgettextツールはメッセージを読み取り、
コンパイルできますが、`msgfmt --check-format`には適用できる
`$`プレースホルダーの文法がありません。

## 代償

f-stringをこの方法で使うことはできません。ライブラリが受け取る時点では完成した
文字列なので、翻訳すると文の断片を翻訳することになります。t-string（[PEP 750]）は
f-stringに似た構文を保ち、値を明示的に結び付けながら、この分離を可能にします。
`$`文字列も、値の結び付け方と失敗時の挙動が異なる簡潔な選択肢としてすでに
利用できます。`flufl.i18n`は成熟したパッケージで、現行リリースはPython 3.10を
サポートします。一方、`gettext-tstrings`は現在アルファ版で、ネイティブt-stringを
使うためPython 3.14が最低バージョンです。

もう一つの代償は制約そのものです。補間は単純な名前でなければなりません。

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

これは実際の制約です。ソース側での値の結び付けや実行時のプレースホルダー検査と
組み合わせることで、カタログ文字列による式の評価を防ぎ、プレースホルダー名を
意味のあるものに保ちます。

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [文書化された挙動]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [独自Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
