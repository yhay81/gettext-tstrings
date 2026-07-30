---
description: "用 %-format、.format()、flufl.i18n $-string 和 t-string 编写同一条可翻译消息，并比较各自如何绑定值及处理损坏的目录。"
---

# 为什么选择 t-string

把一个值放入可翻译消息的每种方式都必须回答同一个问题：*目录可以控制格式语言的
多少部分？* 以下四种答案在值来自何处，以及目录更改占位符时会发生什么方面也有所不同。

## %-format

```python
_("Hello %(name)s") % {"name": name}
```

目录字符串携带 printf 语法，其中包括一个容易忽略、仅修改一个字符就可能损坏的
尾随类型字母：

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

在 PO 编辑器中改动一个字符，就会在生产环境中造成 traceback。GNU
`msgfmt --check-format` 的确能捕获它，但前提是消息带有 `python-format` 标志，
并且目录在进入应用程序前确实经过 msgfmt。

## str.format

```python
_("Hello {name}").format(name=name)
```

它删除了尾随类型字母，同时保留了有名称且可自由调整顺序的占位符。

问题出在另一侧。`str.format` 是一种小型表达式语言；对字符串调用它，就意味着允许
该字符串使用这种语言：

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

目录不是代码，但会像数据一样流转：发送到翻译平台，经过多人处理，以 `.po` 返回，
编译成 `.mo`，有时甚至直接从外部项目引入。`.format()` 让这条路径上的每个环节都有
机会通过字符串访问你传入对象的属性。

## `$`-string 与 flufl.i18n

```python
name = "Ada"
_("Hello $name")
```

标准库的 [`string.Template`][stdlib-template] 提供 `$name` 插值语言，但它本身并不是翻译 API。
[`flufl.i18n`][flufl-i18n] 将这种风格与 gettext 目录查询结合起来。它从调用方的全局变量和
局部变量构建替换命名空间；可选的 `extras` 映射优先于两者。面向翻译者的语法没有
尾随类型字母或格式说明符，占位符也可以自由调整顺序。

找不到替换值时不会抛出异常。如果 `name = "Ada"`，而调用方的命名空间中没有
`nombre`，目录翻译 `Hello $nombre` 会渲染为 `Hello $nombre`：未解析的占位符
仍然可见。这一[已有文档说明的行为]会保留翻译消息的其余部分，而不会让调用失败。
不过，解析属性或转换值时抛出的异常仍可能向上传播。

在一个相关方面，`flufl.i18n` 比原始的 `string.Template` 功能更强。它的
[自定义 Template] 接受 `$settings.api_key` 这样的点号占位符，而其 [translator]
会针对调用方的值解析这些路径。翻译中的占位符可以指向任何可用的调用方局部变量或
全局变量，并可通过点号语法遍历其属性。当消息需要属性时，这很方便；与此同时，
调用方的栈帧也成为目录替换命名空间的一部分。下面比较的是 `flufl.i18n` 6.0.0，
而不是 `string.Template` 的所有可能用法。

## t-string

```python
tr(t"Hello {name}")
```

目录仍会看到 `Hello {name}`，并继续使用普通的 PO/MO 目录。源代码提取有所不同：
当前工具需要能够识别 t-string 的提取器，例如本包提供的提取器。本库会根据源消息的占位符验证翻译并进行渲染，
且只接受简单名称。对于
`t"Hello {name}"`：

| 翻译包含 | 拒绝原因 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

格式仍留在编写它的地方：

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` 永远不会进入目录，因此翻译不能更改它，翻译者也无需面对它。

## 并排比较

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 占位符有名称 | 是 | 是 | 是 | 是 |
| 翻译者可以调整顺序 | 是 | 是 | 是 | 是 |
| 值来自 | 显式映射 | 显式参数 | 调用方的全局变量和局部变量，可由可选的 `extras` 覆盖 | t-string 捕获的插值 |
| 目录控制值转换／格式说明符 | 是 | 是 | 否 | 否 |
| 目录可以请求属性访问 | 否 | 是 | 是，使用点号名称 | 否 |
| 渲染时删除了源占位符 | 静默省略 | 静默省略 | 静默省略 | [默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)完整渲染源模式 |
| 渲染时新增的占位符不可用 | 抛出异常 | 抛出异常 | 保持可见 | [默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)完整渲染源模式 |
| 运行时检查源占位符集合（单数） | 否 | 否 | 否 | 是 |
| Babel 为此示例推断的 PO 格式标志 | `python-format` | `python-brace-format` | 无 | `python-brace-format` |
| 使用普通 PO/MO 目录 | 是 | 是 | 是 | 是 |
| 需要自定义源代码提取器 | 否 | 否 | 否 | 是，目前需要 |

格式标志这一行涉及的是能够识别占位符的验证，而不是目录兼容性。“无”表示标准
gettext 工具仍能读取和编译消息，但 `msgfmt --check-format` 没有可应用的
`$` 占位符语法。

## 代价

f-string 完全无法这样使用——任何库看到它时，它已经是一条完成的字符串，因此翻译它
意味着翻译片段。t-string（[PEP 750]）在保持类似 f-string 的语法并显式绑定值的
同时实现这种分离。`$`-string 已经提供了一种简洁的替代方案，但其绑定和失败模型
不同。`flufl.i18n` 是一个成熟的软件包，其当前版本支持 Python 3.10；
`gettext-tstrings` 目前处于 alpha 阶段，而原生 t-string 使 Python 3.14 成为
它的最低版本。

另一个代价正是这种限制：插值必须是简单名称。

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

这是一项真实的约束。它与源代码侧的值绑定和运行时占位符检查一起，防止目录字符串
求值表达式，并保持占位符名称具有实际意义。

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [已有文档说明的行为]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [自定义 Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
