---
description: "通过 gettext 和 Babel 翻译完整的 t-string 消息，把值和格式都留在目录之外。"
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# 翻译整句话，<br>而不是字符串碎片。

`gettext-tstrings` 把 Python 3.14+ 的 t-string 接到标准 gettext 目录和 Babel
工具链上。值和格式留在应用程序代码里；目录拿到的是一条完整消息，其中只有简单的
`{name}` 占位符：

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[开始教程 :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[比较各种方案](comparison.md){ .md-button }

Alpha · Python 3.14+ · 普通 PO/MO 目录 · 无运行时依赖
{ .home-facts }

本站身体力行自己所记录的内容：每一个语言版本——导航、标签和支持复数规则的
构建报告——都由
[`gettext-tstrings` 自身](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
从 PO 目录渲染。
{ .home-hero-note }

</div>

## 它适合你吗？ { #is-this-for-you }

**现在就合适**：你的应用运行在 Python 3.14 或更高版本上；你已经在用 gettext 和
Babel，或者打算采用它们的 PO/MO 工作流；并且你想要带命名占位符、且在渲染之前
就被检查过的 t-string 语法。

**暂时还不合适**：你需要 Python 3.13 或更早的版本；你要求一个稳定的 Python
API——这是 alpha 版本，其中已经定型的部分是[规范](spec.md)；或者你几乎所有可翻译
文本都在某种 template 语言里，而不在 Python source 中。

已经有目录了？它们继续有效。`_("Hello {name}").format(name=name)` 与
`tr(t"Hello {name}")` 产出同一个 msgid，因此现有翻译能挺过这次切换——
[迁移](migration.md)完整讲了整个过程。

## 目录可以说什么 { #what-the-catalog-may-say }

目录收到的是完整消息 `Hello {name}`。翻译可以调整或重复 `{name}`，也可以改写它
周围的每一个词。但它不能删掉这个占位符、凭空造一个新的、借它伸手去碰你的对象，
也不能自行附加格式。

这就是全部的承诺：**一份译文无法改变它所翻译的那条消息的结构。** 本库在入口处
检查一次——目录编译的时候——渲染时再检查一次；万一有损坏的条目还是进了生产环境，
它会记录一条警告并渲染源消息，而不是崩溃。

!!! note "初次接触 gettext？四句话讲完整个工作流"

    **gettext** 是软件获得翻译的标准方式，在 Python 内外皆然。你的代码标记可翻译
    字符串；*提取器*把它们收集进模板文件（`.pot`）；翻译者——通常不是程序员——为
    每种语言填写一份目录文件（`.po`），再编译成二进制 `.mo`，由应用程序在运行时
    加载。翻译函数的约定名称是 `_`，因此 `_(t"Hello {name}")` 读作“翻译这句话”。
    **[教程](tutorial.md)**用大约五分钟走完整条路径——标记、提取、翻译、编译、
    运行。

## 它解决的问题 { #the-problem-it-solves }

在任何库看到 f-string 之前，插值已经完成——`f"Hello {name}"` 已经变成
`"Hello Ada"`，而围绕一个值去翻译前后的片段会破坏大多数语言的语法。t-string
（[PEP 750]）分别保留静态文本、已求值的值、源表达式、转换和格式说明——这恰好是
消息目录所需要的分离方式。
参阅[它带来了哪些变化](comparison.md)，了解它与 `%(name)s`、`.format()` 和
`$`-string 的区别。

不过，gettext 和 Babel 都没有规定如何将 t-string 变成一条消息。本库做出了这一
选择，将其写成[带版本的规范](spec.md)，并提供[一致性测试套件](spec.md#conformance)
来验证实现。

## 设计原则 { #the-design-rules }

- 始终翻译完整消息，而不是句子片段。
- 只接受 `{name}` 这样的简单变量名。
- `!r` 和 `:.2f` 由应用程序控制，不进入目录。
- 允许翻译调整和重复已知占位符，同时阻止它们访问属性或增加格式。
- 继续使用普通的 POT、PO、MO 文件以及现有工具。

与之对应的，是它刻意不碰的那份清单：它不本地化数字、货币或日期——请先
[用 Babel 把它们格式化好](guide.md#locale-aware-values)；它不为 HTML、shell 或
terminal 转义渲染结果；它也无法判断一份译文是否*正确*，只能判断其中的占位符是否
完好。

## 安装 { #install }

```console
python -m pip install gettext-tstrings
```

需要 Python 3.14 或更高版本。**渲染不需要任何依赖项**——只使用标准库的
`gettext`。

提取和目录验证通过 [Babel] 运行。请在执行 `pybabel` 的环境中安装相应 extra；
通常这是开发或 CI 环境，而不是生产镜像：

```console
python -m pip install "gettext-tstrings[babel]"
```

## 接下来 { #where-to-go-next }

**入门** — 不要求任何 gettext 经验：

<div class="grid cards" markdown>

- **[教程](tutorial.md)** — 从空目录到运行日语翻译只需五步，每条命令都附带
  其输出。
- **[为什么选择 t-string](comparison.md)** — 用四种方式编写同一条消息，并比较
  `%(name)s`、`.format()` 和 `$`-string 分别把什么交给目录。

</div>

**正式使用** — 日常工作的参考：

<div class="grid cards" markdown>

- **[指南](guide.md)** — 运行时 API：该用哪个入口点、复数、按请求选择语言、
  延迟字符串，以及目录出错时会发生什么。
- **[提取](extraction.md)** — `pybabel` 参考：配置、自定义函数名，以及现有工具
  如何免费验证这些目录。
- **[生产实践](workflow.md)** — 团队实际运转的循环：更新周期、fuzzy 条目、CI
  关卡、翻译平台，以及发布。
- **[迁移](migration.md)** — 在一个已经有目录的项目里引入本库，一个调用点一个
  调用点地推进。
- **[面向翻译者](translators.md)** — 可以直接交给编辑 `.po` 文件的人的一页。

</div>

**深入理解** — 从历史到实现：

<div class="grid cards" markdown>

- **[项目背景](background.md)** — 本库为何存在：三十年的 gettext、两个 PEP，
  以及无果而终的标准库讨论。
- **[常见陷阱](pitfalls.md)** — 把本站翻译成三十五种语言实际踩坏了什么，其中
  哪一半是工具能拦住的。
- **[工作原理](internals.md)** — 从 PEP 750 的 template 对象到渲染后的字符串，
  以及让检查变得廉价的缓存。

</div>

**参考** — 各项契约：

<div class="grid cards" markdown>

- **[API](api.md)** — 本包导出的全部内容，集中在一页。
- **[规范](spec.md)** — 将 t-string ↔ msgid 约定定义为稳定、带版本且拥有机器可读
  一致性测试套件的契约。

</div>

## 状态 { #status }

目前是 alpha 版本。契约刻意保持精简，其中稳定的部分是[规范](spec.md)；Python API
仍有可能调整。稳定发布之前，还需要更广泛的语言 fixture、持续性能跟踪、真正使用
gettext 和 Babel 的用户参与 API 评审，以及覆盖所有受支持 Python 与 Babel 版本的
兼容性测试。

欢迎提交 [Issue 和 Pull Request](https://github.com/yhay81/gettext-tstrings/issues)。
alpha 阶段正是讨论接口最有价值的时候。

## 加入社区 { #join-the-community }

- 从范围明确的
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  开始贡献。
- 在 [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)
  中询问使用问题。
- 在 [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)
  中分享生产 gettext 工作流和 API 想法。
- 提交 Pull Request 前，请阅读
  [贡献指南](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)。

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
