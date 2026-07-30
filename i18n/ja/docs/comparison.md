---
description: "%形式、.format()、t-stringで同じ翻訳対象メッセージを記述し、カタログが制御できる範囲を比較します。"
---

# t-stringを選ぶ理由

翻訳対象のメッセージへ値を埋め込む方法は、すべて同じ問いに答える必要があります。
*カタログにフォーマット言語のどこまでを制御させるのか？* 以下の3方式の違いは、
ほぼこの答えの違いです。

## %形式

```python
_("Hello %(name)s") % {"name": name}
```

カタログ文字列にはprintf構文が含まれます。翻訳者が最も壊しやすい箇所は、
値の表示方法を指定する末尾の1文字という、最も意味が分かりにくい部分です。

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

翻訳者にとって重要な点はすべて改善されています。プレースホルダーには名前があり、
失われやすい末尾文字はなく、自由に並べ替えられます。

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

## t-string

```python
tr(t"Hello {name}")
```

msgidは引き続き `Hello {name}` なので、カタログもツールも変わりません。違うのは、
翻訳がフォーマット文字列ではなくなる点です。翻訳は元メッセージのプレースホルダーと
照合され、このライブラリがレンダリングします。受け付けるのは単純な名前だけです。
`t"Hello {name}"` に対しては次のようになります。

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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| プレースホルダーに名前がある | はい | はい | はい |
| 翻訳者が並べ替えられる | はい | はい | はい |
| 1文字の欠落で壊れる | **はい** | いいえ | いいえ |
| カタログが書式を制御する | はい | はい | **いいえ** |
| カタログから属性へアクセスできる | いいえ | **はい** | **いいえ** |
| 不正なカタログがレンダリング時に例外を送出 | **はい** | **はい** | [既定では](guide.md#what-happens-when-a-catalog-is-wrong)いいえ |
| PO/MOと`msgfmt`に対応 | はい | はい | はい |

## 代償

f-stringをこの方法で使うことはできません。ライブラリが受け取る時点では完成した
文字列なので、翻訳すると文の断片を翻訳することになります。分離を可能にするのが
t-string（[PEP 750]）であり、そのためPython 3.14が最低バージョンです。

もう一つの代償は制約そのものです。補間は単純な名前でなければなりません。

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

これは実際の制約であり、同時に上記すべての利点を得るための条件です。翻訳者にも、
読めない式ではなく意味のある名前が渡ります。

  [PEP 750]: https://peps.python.org/pep-0750/
