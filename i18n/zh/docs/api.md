---
description: "gettext_tstrings 导出的全部名称：函数、Translator、上下文绑定、延迟字符串和异常。"
---

# API

以下内容全部由 `gettext_tstrings` 导出，其他内容均不是公共 API。
本页是签名参考；每个函数的完整示例请参阅[指南](guide.md)。

## 翻译 { #translating }

每个函数都以位置参数接收 t-string，并接受两个关键字参数：`translations`
（依次回退到上下文绑定和标准库全局函数）以及 `strict`
（参阅[指南](guide.md#what-happens-when-a-catalog-is-wrong)）。

| 函数 | 签名 |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext` 的别名 |
| `ntr` | `ngettext` 的别名 |

### `Translator`

一个绑定翻译对象的 frozen dataclass，使调用点无需重复传入该对象。

```python
Translator(translations, strict=False)
```

它可调用（`_(t"…")`），并提供 `gettext`、`ngettext`、`pgettext`、
`npgettext` 以及 `tr` / `ntr` 别名。

## 上下文绑定 { #context-binding }

| 名称 | 用途 |
| --- | --- |
| `use_translations(translations)` | 在 `with` 块期间绑定，随后恢复。 |
| `set_translations(translations)` | 不使用代码块进行绑定，适合由 framework 管理的生命周期。 |
| `get_translations()` | 读取当前绑定；若没有则返回 `None`。 |

绑定使用 `ContextVar`，因此按上下文隔离，并发时安全。

## 延迟字符串 { #deferred-strings }

| 名称 | 用途 |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | 将翻译推迟到首次使用。 |
| `lazy_pgettext(context, template, /, *, strict=False)` | 带上下文的形式。 |
| `LazyString` | 两者的返回值。通过 `str()`、`format()` 和 f-string 渲染，可与渲染文本比较，并刻意设为不可哈希。 |

## 底层 API { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

复用缓存的静态 plan 来编译 t-string。

### `CompiledTemplate`

| 成员 | 含义 |
| --- | --- |
| `.msgid` | 稳定的 gettext 消息标识符。 |
| `.placeholders` | 按首次出现顺序排列的占位符名称。 |
| `.render(pattern)` | 验证并渲染一个 pattern；不匹配时**始终抛出异常**。 |

## 类型和错误 { #types-and-errors }

### `Translations`

一个 `runtime_checkable` 的 `Protocol`，包含四个标准方法，且参数均为仅位置参数：

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`、`gettext.GNUTranslations` 和 Babel 的
`Translations` 都满足该 Protocol。

### 异常

| 类 | 抛出时机 |
| --- | --- |
| `TStringError` | 以下两个异常的基类。 |
| `InvalidTemplateError` | **源** t-string 违反约定，例如复杂插值，或以不同格式重复同一名称。 |
| `InvalidTranslationError` | **翻译**违反约定。默认 lenient 模式会记录日志并渲染源文本。 |

## 提取 entry point { #extraction-entry-points }

安装时自动注册；通过名称引用，而不是 import。

| 组 | 名称 | 用途 |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg` 中的 `method` |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`（自动） |

## 性能 { #performance }

完整说明——缓存了什么、缓存以什么为键，以及实测数字——见
[热路径](internals.md#the-hot-path)。简而言之：验证会被缓存但绝不跳过，整个渲染
只需不到一微秒。可在自己的目标环境运行基准：

```console
uv run python benchmarks/runtime.py
```
