---
description: "gettext_tstrings 匯出的每一個名稱：函式、Translator、上下文繫結、延遲字串，以及各種例外。"
---

# API

以下所有內容都由 `gettext_tstrings` 匯出，除此之外都不是公開 API。本頁是簽章參考；
每個函式的實例演練請見[指南](guide.md)。

## 翻譯 { #translating }

每個函式都以位置引數接收它的 t-string，並接受兩個關鍵字引數：`translations`
（會依序回退到上下文繫結，再回退到標準函式庫的全域函式）以及 `strict`
（見[指南](guide.md#what-happens-when-a-catalog-is-wrong)）。

| 函式 | 簽章 |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext` 的別名 |
| `ntr` | `ngettext` 的別名 |

### `Translator`

一個繫結了單一翻譯物件的 frozen dataclass，讓呼叫點不必一再重複傳入它。

```python
Translator(translations, strict=False)
```

它是可呼叫的（`_(t"…")`），並帶有 `gettext`、`ngettext`、`pgettext`、`npgettext`，
以及 `tr` / `ntr` 別名。

## 上下文繫結 { #context-binding }

| 名稱 | 用途 |
| --- | --- |
| `use_translations(translations)` | 在 `with` 區塊期間繫結，結束後還原。 |
| `set_translations(translations)` | 不需要區塊即可繫結，適用於由 framework 管理的生命週期。 |
| `get_translations()` | 讀取目前的繫結，若無則為 `None`。 |

這個繫結是一個 `ContextVar`，所以它是逐上下文的，在並行之下也安全。

## 延遲字串 { #deferred-strings }

| 名稱 | 用途 |
| --- | --- |
| `lazy_gettext(template, /)` | 把翻譯延後到第一次使用時。 |
| `lazy_pgettext(context, template, /)` | 帶上下文的形式。 |
| `LazyString` | 兩者的回傳值。可透過 `str()` 與 `format()` 渲染，與渲染後的文字相等，並且刻意不可雜湊。 |

## 較低層 { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

編譯一個 t-string，並重用它已快取的靜態 plan。

### `CompiledTemplate`

| 成員 | 意義 |
| --- | --- |
| `.msgid` | 穩定的 gettext 訊息識別碼。 |
| `.placeholders` | 依首次出現順序排列的佔位符名稱。 |
| `.render(pattern)` | 驗證一個 pattern 並渲染它。只要不相符就**一律拋出例外**。 |

## 型別與例外 { #types-and-errors }

### `Translations`

一個 `runtime_checkable` 的 `Protocol`，涵蓋那四個標準方法，且全部僅限位置引數：

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`、`gettext.GNUTranslations` 以及 Babel 的 `Translations`
都滿足它。

### 例外

| 類別 | 何時拋出 |
| --- | --- |
| `TStringError` | 以下兩者的基底類別。 |
| `InvalidTemplateError` | **來源** t-string 違反了這套約定——複雜的插值，或是同一名稱重複出現卻帶著不同的格式設定。 |
| `InvalidTranslationError` | **翻譯**違反了這套約定。在預設的寬鬆模式下，這會被記錄下來，並改為渲染原文。 |

## 擷取 entry point { #extraction-entry-points }

安裝時自動註冊；你透過名稱指涉它們，而不是用 import。

| 群組 | 名稱 | 由誰使用 |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg` 裡的 `method`。 |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`，自動套用。 |

## 效能 { #performance }

完整的說明——什麼被快取了、快取以什麼為 key，以及實測數字——在
[熱路徑](internals.md#the-hot-path)。簡短版：驗證會被快取，永遠不會被略過，而整趟
渲染只花掉零點幾微秒。你可以在自己的目標環境上跑這個基準測試：

```console
uv run python benchmarks/runtime.py
```
