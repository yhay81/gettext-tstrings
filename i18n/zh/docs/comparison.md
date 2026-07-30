---
description: "用 %-format、.format()、flufl.i18n $-string 和 t-string 编写同一条可翻译消息，并比较各自如何绑定值及处理损坏的目录。"
---

# 为什么选择 t-string

把一个值放入可翻译消息的四种方式，在同一句话上进行比较。先说结论：

- 使用 **%-format**，翻译者删掉一个字母，就会变成生产环境中的崩溃。
- 使用 **str.format**，翻译可以读取代码传入对象的属性——包括机密信息。
- 使用 **$-string**（flufl.i18n），值会从调用函数的变量中被隐式取出，点号
  占位符还能进一步访问属性。
- 使用 **t-string**，格式保留在你的代码中，翻译会在运行时接受检查，损坏的目录
  会回退到源文本，而不是崩溃。

本页其余部分就是证据，逐一分析每种方法。

!!! note "每条翻译消息都经过三方之手"

    **目录**是存放翻译的文件——供人编辑时是 `.po`，编译成 `.mo` 后供应用程序
    加载（[教程](tutorial.md)对两者都有介绍）。每条消息都经过三方之手：
    **开发者**编写源字符串；**翻译者**编辑目录——常常在外部平台上进行，远离
    任何代码审查；**应用程序**在运行时把两者一起渲染。下面每种格式化风格都对
    同一个问题给出了不同回答：*目录可以控制格式语言的多少部分？* 在示例中，
    `_` 是翻译函数的约定名称，`tr` 是本库使用的名称。

## %-format

```python
_("Hello %(name)s") % {"name": name}
```

可能出的问题：翻译中删掉一个字母，渲染就会崩溃。

目录字符串携带 printf 语法，其中包括一个尾随类型字母——`%(name)s` 中的
`s`——它既容易忽略，也容易损坏：

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
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

它删除了尾随类型字母，同时保留了有名称且可自由调整顺序的占位符。可能出的问题
转移到了交换的另一侧：翻译获得了操纵你的对象的权力。

`str.format` 是一种小型表达式语言；对字符串调用它，就意味着允许该字符串使用
这种语言：

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

现在把那些字面字符串换成 `_()` 返回的任意内容。如果 `Hello {name}` 的某条翻译
变成了 `{conf.api_key}`，渲染它就会打印出你的 API key——决定读取什么的是目录，
而不是你的代码。目录不是代码，但会像数据一样流转：发送到翻译平台，经过多人处理，
以 `.po` 返回，编译成 `.mo`，有时甚至直接从外部项目引入。`.format()` 让这条路径
上的每个环节都有机会通过字符串访问你传入对象的属性。

## `$`-string 与 flufl.i18n

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

标准库的 [`string.Template`][stdlib-template] 提供 `$name` 插值语言，但它本身并不是翻译 API。
[`flufl.i18n`][flufl-i18n] 将这种风格与 gettext 目录查询结合起来。请注意，这个值
从未被传入：flufl.i18n 从调用方的全局变量和局部变量构建替换命名空间——调用点存在
的任何变量都可供消息使用。可选的 `extras` 映射优先于两者。面向翻译者的语法没有
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

目录仍会看到 `Hello {name}`，并继续使用普通的 PO/MO 目录。区别在于翻译*被允许
说什么*，以及由谁来检查。

本库会在渲染前根据源消息的占位符验证每一条翻译，且只接受简单名称。对于
`t"Hello {name}"`：

| 翻译包含 | 拒绝原因 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

被拒绝并不意味着崩溃：默认情况下，本库会记录一条警告并渲染源文本，因此损坏的
目录永远不会让应用程序宕机——[这正是 gettext 自身遵守的契约](guide.md#what-happens-when-a-catalog-is-wrong)。

格式仍留在编写它的地方，也就是代码中：

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` 永远不会进入目录，因此翻译不能更改它，翻译者也无需面对它。

还有一个区别在于工具链：t-string 是新语法，因此目前把它们提取进 `.pot` 需要
能够识别 t-string 的提取器，例如本包[为 Babel 提供](extraction.md)的那个。

## 并排比较

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 占位符有名称吗？ | 是 | 是 | 是 | 是 |
| 翻译者可以调整占位符顺序吗？ | 是 | 是 | 是 | 是 |
| 值来自哪里？ | 显式映射 | 显式参数 | 调用方的局部变量和全局变量，外加可选的 `extras` | t-string 内部捕获的值 |
| 目录能改变值的格式化方式吗？ | 能 | 能 | 不能 | 不能 |
| 目录能深入对象内部（属性访问）吗？ | 不能 | 能 | 能，使用点号名称 | 不能 |
| 翻译*删掉*了一个占位符——渲染什么？ | 值静默消失 | 值静默消失 | 值静默消失 | 源文本，并附带警告（[默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻译*增加*了一个未知占位符——渲染什么？ | 抛出异常 | 抛出异常 | 占位符以文本形式保持可见 | 源文本，并附带警告（[默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 渲染时会检查占位符吗？ | 否 | 否 | 否 | 是（见下文） |
| Babel 推断哪个 PO 标志，供现有工具验证？ | `python-format` | `python-brace-format` | 无 | `python-brace-format` |
| 使用普通 PO/MO 目录吗？ | 是 | 是 | 是 | 是 |
| 需要自定义源代码提取器吗？ | 否 | 否 | 否 | 是，目前需要 |

关于渲染时检查：单数消息要求占位符完全匹配。复数消息同样会检查，依据的是允许
目标语言复数形式与源语言不同的[并集/交集规则](spec.md)；更严格的逐形式检查在
编译目录时运行（[提取](extraction.md)）。

格式标志这一行涉及的是能够识别占位符的验证，而不是目录兼容性。“无”表示标准
gettext 工具仍能读取和编译消息，但 `msgfmt --check-format` 没有可应用的
`$` 占位符语法。

## 代价

f-string 完全无法这样使用——任何库看到它时，它已经是一条完成的字符串，因此翻译它
意味着翻译片段。t-string（[PEP 750]）在保持类似 f-string 的语法和显式值绑定的
同时，让静态文本与值保持分离。`$`-string 已经提供了一种简洁的替代方案，但其绑定
和失败模型不同。`flufl.i18n` 是一个成熟的软件包，可运行于 Python 3.10 及更高
版本；`gettext-tstrings` 目前处于 alpha 阶段，而由于 t-string 是新语法，它要求
Python 3.14 或更新版本。

另一个代价正是这种限制：插值必须是简单名称。

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
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
