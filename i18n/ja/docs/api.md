---
description: "gettext_tstringsが公開する関数、Translator、コンテキスト束縛、遅延文字列、例外の一覧です。"
---

# API

以下はすべて`gettext_tstrings`から公開されています。それ以外は公開APIではありません。
このページはシグネチャのリファレンスです。各関数の具体的な使用例は
[ガイド](guide.md)を参照してください。

## 翻訳 { #translating }

各関数はt-stringを位置専用引数として受け取り、2つのキーワード引数を受け付けます。
`translations`（コンテキスト束縛、次に標準ライブラリのグローバル関数へfallback）と、
`strict`（[ガイド](guide.md#what-happens-when-a-catalog-is-wrong)を参照）です。

| 関数 | シグネチャ |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext`のalias |
| `ntr` | `ngettext`のalias |

### `Translator`

1つの翻訳オブジェクトを束縛するfrozen dataclassです。呼び出し側で毎回渡す必要が
なくなります。

```python
Translator(translations, strict=False)
```

呼び出し可能（`_(t"…")`）で、`gettext`、`ngettext`、`pgettext`、
`npgettext`と、`tr` / `ntr`のaliasを持ちます。

## コンテキスト束縛 { #context-binding }

| 名前 | 用途 |
| --- | --- |
| `use_translations(translations)` | `with`ブロックの間だけ束縛し、その後復元します。 |
| `set_translations(translations)` | ライフサイクルをframeworkが管理する場合に、ブロックなしで束縛します。 |
| `get_translations()` | 現在の束縛を読み取ります。未束縛なら`None`です。 |

束縛には`ContextVar`を使うためコンテキストごとに独立し、並行実行でも安全です。

## 遅延文字列 { #deferred-strings }

| 名前 | 用途 |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | 翻訳を最初に使う時点まで遅延します。 |
| `lazy_pgettext(context, template, /, *, strict=False)` | コンテキスト付きの形式です。 |
| `LazyString` | 上記2関数の戻り値です。`str()`と`format()`、f-stringでレンダリングされ、表示文字列と等値比較でき、意図的にhash不能です。 |

## 低レベルAPI { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

キャッシュされた静的planを再利用してt-stringをコンパイルします。

### `CompiledTemplate`

| メンバー | 意味 |
| --- | --- |
| `.msgid` | 安定したgettextメッセージ識別子です。 |
| `.placeholders` | 最初に現れた順のプレースホルダー名です。 |
| `.render(pattern)` | 1つのパターンを検証してレンダリングします。不一致では**常に例外を送出**します。 |

## 型と例外 { #types-and-errors }

### `Translations`

標準の4メソッドを位置専用引数で定義した`runtime_checkable`な`Protocol`です。

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`、`gettext.GNUTranslations`、Babelの`Translations`は
すべてこのProtocolを満たします。

### 例外

| クラス | 送出される状況 |
| --- | --- |
| `TStringError` | 以下2クラスの基底クラスです。 |
| `InvalidTemplateError` | **ソース**t-stringが規約に違反した場合です。複雑な補間や、同じ名前を異なる書式で繰り返した場合などです。 |
| `InvalidTranslationError` | **翻訳**が規約に違反した場合です。既定のlenientモードではログへ記録し、ソース文字列をレンダリングします。 |

## 抽出entry point { #extraction-entry-points }

インストール時に自動登録されます。importではなく名前で参照します。

| グループ | 名前 | 使用箇所 |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg`の`method` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`（自動） |

## 性能 { #performance }

何がキャッシュされるか、キャッシュのキーは何か、計測された数値はいくつか —
その全容は[ホットパス](internals.md#the-hot-path)にあります。要点だけ言えば、
検証はキャッシュされ、省略されることはなく、レンダリング全体のコストは
1マイクロ秒の何分の一かです。対象環境でベンチマークを実行できます。

```console
uv run python benchmarks/runtime.py
```
