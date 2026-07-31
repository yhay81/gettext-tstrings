---
description: "用 %-format、.format()、flufl.i18n $-string 和 t-string 编写同一条可翻译消息，从翻译者的失误、目录的权限和接入成本三方面比较。"
---

# 为什么选择 t-string

把一个值放入可翻译消息的四种方式，在同一条消息上进行比较。四者都为占位符命名，
也都允许翻译者调整顺序；它们的差别在于翻译出错时会发生什么、目录能触及你程序的
多少部分，以及采用它们的成本。

表格放在最前面，这样你可以先找到自己关心的那一行，再只读它背后的那一节。

!!! note "每条翻译消息都经过三方之手"

    **目录**是存放翻译的文件——供人编辑时是 `.po`，编译成 `.mo` 后供应用程序
    加载（[教程](tutorial.md)对两者都有介绍）。每条消息都经过三方之手：
    **开发者**编写源字符串；**翻译者**编辑目录——常常在外部平台上进行，远离
    任何代码审查；**应用程序**在运行时把两者一起渲染。下面每种格式化风格都对
    同一个问题给出了不同回答：*目录可以控制格式语言的多少部分？* 在示例中，
    `_` 是翻译函数的约定名称，`tr` 是本库使用的名称。

## 并排比较 { #side-by-side }

**翻译者出错的时候。** 一份目录会经过许多人的手，而其中出的岔子大多是无心的：

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 翻译*删掉*了一个占位符——渲染什么？ | 值静默消失 | 值静默消失 | 值静默消失 | 源消息，并附带警告（[默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻译*增加*了一个未知占位符——渲染什么？ | 抛出异常 | 抛出异常 | 占位符以文本形式保持可见 | 源消息，并附带警告（[默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻译*重新格式化*了一个占位符——渲染什么？ | 目录要求的格式，或者在类型字母与值不再匹配时抛出异常 | 目录要求的格式 | `$`-string 无法表达 | 源消息，并附带警告 |
| 渲染时会检查占位符吗？ | 否 | 否 | 否 | 是（见下文） |

**目录拥有多大权限。** 译文是来自你仓库之外的数据，而各种风格交给它的权力大小
各不相同：

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 值来自哪里？ | 显式映射 | 显式参数 | 调用方的局部变量和全局变量，外加可选的 `extras` | t-string 内部捕获的值 |
| 目录能改变值的格式化方式吗？ | 能 | 能 | 不能 | 不能 |
| 目录能深入对象内部（属性访问）吗？ | 不能 | 能 | 能，使用点号名称 | 不能 |
| “当前语言”存放在哪里？ | 应用程序放到哪里就在哪里 | 应用程序放到哪里就在哪里 | 共享应用程序对象上的语言代码栈 | 一个 `ContextVar`，按任务或请求隔离 |

**接入需要付出什么。** 只要工具链合适，上面这一切都是免费的；下面才是可能不合适
的地方：

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 最低 Python 版本 | 任意 | 任意 | 3.10 | **3.14** |
| 成熟度 | 标准库 | 标准库 | 稳定发布 | **alpha** |
| 使用普通 PO/MO 目录吗？ | 是 | 是 | 是 | 是 |
| 需要自定义源代码提取器吗？ | 否 | 否 | 否 | 是，目前需要 |
| Babel 推断哪个 PO 标志，供现有工具验证？ | `python-format` | `python-brace-format` | 无 | `python-brace-format` |

关于渲染时检查：单数消息要求占位符完全匹配。复数消息同样会检查，依据的是允许
目标语言复数形式与源语言不同的[并集/交集规则](spec.md)；更严格的逐形式检查在
编译目录时运行（[提取](extraction.md)）。

格式标志这一行涉及的是能够识别占位符的验证，而不是目录兼容性。“无”表示标准
gettext 工具仍能读取和编译消息，但 `msgfmt --check-format` 没有可应用的
`$` 占位符语法。

## 兼容性与成熟度 { #compatibility-and-maturity }

最后一张表的前两行才是真正决定采不采用的，所以值得把它们直说，而不是塞在格子里。

`%`-format 和 `.format()` 内置于 Python，完全不需要任何依赖。
[`flufl.i18n`][flufl-i18n] 是一个成熟的软件包，已经正式发布并在生产中使用，
可运行于 Python 3.10 及更高版本。`gettext-tstrings` 目前处于 **alpha** 阶段，
并且要求 **Python 3.14 或更新版本**，因为 t-string 是 3.14 中的新语法——它没有
向后移植版本，也不可能有。它的[规范](spec.md)是其中稳定的部分；Python API 在
1.0 之前仍有可能调整。

四者都不用付出的代价是目录兼容性。它们全都产出普通的 POT/PO/MO 文件，任何 PO
编辑器、翻译平台和 GNU gettext 工具都已经能读——因此下面这个选择是可逆的，而更换
目录*格式*就不是。[迁移](migration.md)讲的是如何搬动一个已有项目。

下面各节逐一展开每种方法的取舍细节。

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

可能出的问题：损坏的占位符会变成运行时异常，除非目录校验先一步把它抓住。

目录字符串携带 printf 语法，其中包括一个尾随类型字母——`%(name)s` 中的
`s`——它既容易忽略，也容易损坏：

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

在 PO 编辑器中改动一个字符，就会在运行时造成异常，除非目录验证先一步抓住它。
GNU `msgfmt --check-format` 的确能捕获这一个，但前提是消息带有 `python-format`
标志，并且目录在进入应用程序前确实经过 msgfmt。

## str.format { #strformat }

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
以 `.po` 返回，编译成 `.mo`，有时甚至完全从项目之外引入。`.format()` 让这条路径
上的每个环节都能对你传入的对象做属性访问。

## `$`-string 与 flufl.i18n { #-strings-and-flufli18n }

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
仍然可见。这一[已有文档说明的行为][documented behavior]会保留翻译消息的其余部分，
而不会让调用失败。不过，解析属性或转换值时抛出的异常仍可能向上传播。

在一个相关方面，`flufl.i18n` 比原始的 `string.Template` 功能更强。它的
[自定义 Template][custom Template] 接受 `$settings.api_key` 这样的点号占位符，
而其 [translator] 会针对调用方的值解析这些路径。翻译中的占位符可以指向任何可用的
调用方局部变量或全局变量，并可通过点号语法遍历其属性。当消息需要属性时，这很方便；
与此同时，调用方的栈帧也成为目录替换命名空间的一部分。这里比较的是 `flufl.i18n`
6.0.0，而不是 `string.Template` 的所有可能用法。

它还回答了另外两种格式化风格完全丢给应用程序的一个问题：*当前*是哪种语言，
以及如何切换。[应用程序对象][application object]维护一个语言栈，`_.push(code)`
与 `_.pop()` 负责移动它，`with _.using(code):` 可以嵌套，而[策略][strategy]会
根据语言代码找到对应目录，于是应用程序自己从不直接处理目录对象。需要在同一个
工作单元中产出多种语言文本的服务器——给读者的页面，以及给某个语言设置不同的
账户的通知——正是它存在的理由。

这个栈存放在那个应用程序对象上，而整个进程共享它。因此两个相互重叠的请求会共用
同一个栈，*在时间上*并非严格嵌套的代码块就会把错误的语言交给彼此：

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

本库保留了同样的能力——绑定同样会嵌套，并以相同的方式解除——但把它放在
`ContextVar` 中，而不是共享的栈里，因此上面那种交错会按任务各自解析。对应写法见
[同时使用多种语言](guide.md#several-languages-at-once)。本库不提供的是从语言代码
到目录的查找：你传入一个翻译对象，常见情况下就是一次 `gettext.translation()`
调用，而标准库会缓存解析后的目录。

## t-string { #t-strings }

```python
tr(t"Hello {name}")
```

目录仍会看到 `Hello {name}`，并继续是一份普通的 PO/MO 目录。区别在于翻译*被允许
说什么*，以及由谁来检查。

本库会在渲染前根据源消息的占位符验证每一条翻译，且只接受简单名称。对于
`t"Hello {name}"`：

| 翻译包含 | 拒绝原因 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

被拒绝并不意味着崩溃：默认情况下，本库会记录一条警告并渲染源消息，因此损坏的
目录永远不会让应用程序宕机——[这正是 gettext 自身遵守的契约](guide.md#what-happens-when-a-catalog-is-wrong)。

格式仍留在编写它的地方，也就是代码中：

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` 永远不会进入目录，因此翻译不能更改它，翻译者也无需面对它。不过它是一种
*固定*格式，而不是本地化格式——按语言选择数位和分隔符是
[Babel 的工作，应在调用之前完成](guide.md#locale-aware-values)。

还有一个区别在于工具链：t-string 是新语法，因此目前把它们提取进 `.pot` 需要
能够识别 t-string 的提取器，例如本包[为 Babel 提供](extraction.md)的那个。

## 这项限制的代价 { #the-cost-of-the-restriction }

除了 Python 版本要求之外，上述这一切的代价就是一条规则：插值必须是简单名称。

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

这是一项真实的约束，而它正是上面那些保证的来源。它与源代码侧的值绑定和运行时
占位符检查一起，防止目录字符串求值表达式，并让占位符名称对翻译它的人保持有意义。

f-string 完全无法这样使用——任何库看到它时，它已经是一条完成的字符串，因此翻译它
意味着翻译片段。t-string（[PEP 750]）在保持类似 f-string 的语法和显式值绑定的
同时，让静态文本与值保持分离。

Python 如何走到今天这一步——相隔十年的两个 PEP，以及无果而终的标准库讨论——
在[项目背景](background.md)中连同来源一并讲述。

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
