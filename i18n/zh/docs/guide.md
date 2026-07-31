---
description: "运行时 API：绑定目录、按请求选择语言、延迟字符串，以及损坏翻译的报告方式。"
---

# 指南

本页是运行时参考：目录就绪之后，*应用程序代码*用本库所做的一切都在这里。
如果你还没有见过完整的循环——标记、提取、翻译、编译、运行——[教程](tutorial.md)
会在五分钟内走完一遍；目录的创建与验证参阅[提取](extraction.md)；团队如何让
循环持续运转——更新周期、CI、翻译平台——参阅[生产实践](workflow.md)。

## 绑定目录 { #binding-a-catalog }

推荐方式与 gettext 基于类的用法一致：绑定一次标准翻译对象，并把可调用的处理器用作
`_`。

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

模块级函数沿用标准库的名称和仅位置参数调用约定：

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` 和 `ntr` 分别是 `gettext` 和 `ngettext` 的完全别名。

## 按请求选择语言 { #per-request-language }

Web framework 会为每个请求选择语言。把该请求的翻译绑定到当前上下文后，所有模块级
调用都会解析为对应语言，即使多个请求并发执行也能安全隔离：

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

对于自行管理请求生命周期的 framework，`set_translations(translations)` 可以不使用
`with` 块直接绑定；`get_translations()` 用于读取当前绑定。显式的
`translations=` 参数始终优先于上下文；未绑定的上下文会回退到标准库全局安装的
gettext 函数。Flask 与 ASGI 中间件的完整示例见
[生产实践](workflow.md#binding-a-language-at-runtime)页。

## 延迟翻译 { #deferred-translation }

t-string 会立即捕获其值。对于在 import 时定义、但必须在*使用时*根据当前语言渲染的
字符串——表单标签、枚举值、模块常量——这种行为并不合适。

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` 可通过 `str()`、`format()` 和 f-string 渲染，并与渲染后的文本进行
相等比较。

!!! note "刻意不可哈希"

    `LazyString` 的文本依赖当前语言。如果 hash 值在切换语言后改变，会悄无声息地
    损坏保存它的 set 或 dict。需要作为 key 时，请先调用 `str()`。

`strict` 在消息被*编写*的位置决定，而不是在它被渲染的位置：

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

延迟字符串会在它最终被使用的地方渲染——模板里、表单里、日志行里——而那个地方
通常并不知道当前是测试运行还是生产环境。在定义处传入 `strict=True`，正是让
[CI 中喧哗、生产中宽容](#what-happens-when-a-catalog-is-wrong)的同一套取舍，
也能适用于并非在调用点渲染的字符串。

复数形式依赖运行时数量，因此应在已知数量的位置用 `ngettext` 立即渲染。

## 同时使用多种语言 { #several-languages-at-once }

一个请求常常需要不止一种语言：为读者渲染页面的同时，还要给语言设置不同的账户
排入一条通知；或者一份摘要要用每位参与者各自的语言引用他们。绑定可以嵌套，
离开内层块后会恢复外层的绑定。

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

面对一组收件人时，延迟字符串正好派上用场：消息只在 import 时编写一次，然后按
每种语言各渲染一次。

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

绑定保存在 `ContextVar` 中，而不是共享对象上的栈里，因此相互重叠的请求不会拿到
彼此的语言——包括它们按*进入*的顺序*离开*各自代码块的情况，而这正是下推栈会
弄错的交错。按语言加载目录的开销很小：`gettext.translation()` 对每个 `.mo` 只
解析一次，然后分发共享同一份解析结果的副本。

!!! warning "工作线程是否继承绑定取决于所用的构建"

    裸的 `threading.Thread` 或 `ThreadPoolExecutor.submit`，要么从调用方上下文的
    副本开始，要么从空上下文开始，而决定这一点的是
    `sys.flags.thread_inherit_context`——在自由线程构建上默认为真，在其他任何地方
    都为假。因此同一份代码在 3.14t 上渲染绑定的语言，在 3.14 上渲染进程全局的
    目录。请传递上下文，而不要依赖默认值：

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` 已经替你做好了这件事。

## 目录出错时会发生什么 { #what-happens-when-a-catalog-is-wrong }

如果翻译的占位符与源消息不一致——缺失、未知或被重新格式化的字段绕过了验证，来自
手工编辑的 MO、供应商目录，或跳过 checker 的 pipeline——默认行为是还原源文本，
而不是抛出异常。这与 gettext 自身“不让损坏目录破坏应用程序”的契约一致。

当 `Hello {name}` 被翻译为 `こんにちは {nombre}` 时，渲染仍会成功，并向
`gettext_tstrings` logger 发送一次警告：

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

警告按消息与 pattern 的组合只触发一次，而不是每次渲染都触发，因此损坏的目录项
不会淹没日志。

测试和 CI 可以选择立即失败：

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

同一次查询随后会抛出异常，消息相同，但没有“using source text”部分：

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## 阅读错误消息 { #reading-a-failure-message }

这些消息是为能够解决问题的人编写的；目录问题的处理者往往是翻译者，而不是程序员。
如果读者眼前明明能看到那些字符，只报告 `{name}` 缺失并没有帮助。因此，当占位符
看似存在、实际却无效时，消息会说明原因。对于源消息 `Hello {name}`，下列每种翻译
都会在 `translation does not match the source placeholders:` 后给出对应说明：

| 翻译内容 | 给出的原因 |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

不可见字符会得到专门处理。输入法可能在花括号中产生 no-break space，而编辑器不会
显示它。因此消息会打印 code point，而不是让读者寻找一个看不见的字符：

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

名称混用不同书写系统时——例如 Cyrillic `а` 与 Latin 字母外观完全相同的
homoglyph 情况——会同时显示可读形式和转义形式，只有后者能揭示两者的差别：

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

当完全用 Greek 或 Cyrillic 写成的名称与 ASCII 源名称冲突时也会这样处理，包括
单字符 Latin `a` / Cyrillic `а` 的情况。

## 不使用目录渲染 pattern { #rendering-a-pattern-without-a-catalog }

`compile_template` 将同一机制向下暴露一层：它把 t-string 转成 msgid 和一组绑定值，
并渲染你提供的任意 pattern。

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` 使用相同规则验证，并在不匹配时**始终抛出异常**。这里没有 lenient 模式：
lenient 是为了让*目录*查询能够回退到源文本，而你直接传入的 pattern 没有可回退的
来源。

## 安全性与范围 { #safety-and-scope }

下面的代码有效：

```python
tr(t"Hello {name}")
```

下面的代码会被刻意拒绝：

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

请先计算一个有意义的值：

```python
name = user.display_name()
tr(t"Hello {name}")
```

这一限制产生稳定的目录 key，为翻译者提供有意义的名称，并阻止翻译字符串变成
表达式语言。

保证的范围是*结构和格式*：翻译永远不会被求值，也无法增加属性访问、调用、转换或
格式说明。与标准库 gettext 相同，两项责任仍属于调用方：针对输出目标（HTML、shell、
terminal）对渲染结果进行**转义**，以及维护**目录完整性**。恶意目录可以重复占位符
来放大输出长度，这是任何基于占位符的 i18n 都具有的性质。
