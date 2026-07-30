---
description: "比较用 %-format、.format() 和 t-string 编写同一条可翻译消息时，目录分别能控制什么。"
---

# 为什么选择 t-string

把一个值放入可翻译消息的每种方式都必须回答同一个问题：*目录可以控制格式语言的
多少部分？* 以下三种答案的主要差别就在这里。

## %-format

```python
_("Hello %(name)s") % {"name": name}
```

目录字符串携带 printf 语法，而翻译者最容易破坏的部分偏偏最难理解——末尾那个决定
如何渲染值的字母：

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

从翻译者的角度看各方面都更好：占位符有名称，没有容易丢失的尾随字符，而且可以
自由调整顺序。

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

## t-string

```python
tr(t"Hello {name}")
```

msgid 仍是 `Hello {name}`，因此目录和工具保持不变。变化在于翻译不再是格式字符串。
本库会根据源消息的占位符验证翻译并进行渲染，且只接受简单名称。对于
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

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| 占位符有名称 | 是 | 是 | 是 |
| 翻译者可以调整顺序 | 是 | 是 | 是 |
| 丢失一个字符就会损坏 | **是** | 否 | 否 |
| 目录控制格式 | 是 | 是 | **否** |
| 目录可以访问属性 | 否 | **是** | **否** |
| 损坏的目录在渲染时抛出异常 | **是** | **是** | [默认情况下](guide.md#what-happens-when-a-catalog-is-wrong)否 |
| 与 PO/MO 和 `msgfmt` 配合 | 是 | 是 | 是 |

## 代价

f-string 完全无法这样使用——任何库看到它时，它已经是一条完成的字符串，因此翻译它
意味着翻译片段。t-string（[PEP 750]）使这种分离成为可能，所以最低版本是
Python 3.14。

另一个代价正是这种限制：插值必须是简单名称。

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

这是一项真实的约束，也是换取上述所有特性的条件。它还让翻译者看到有意义的名称，
而不是无法理解的表达式。

  [PEP 750]: https://peps.python.org/pep-0750/
