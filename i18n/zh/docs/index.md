---
description: "通过 gettext 和 Babel 翻译完整的 t-string 消息，同时将格式控制保留在目录之外。"
---

# gettext-tstrings

面向 Python 3.14+ t-string 的安全 gettext 与 Babel 集成。

用源语言把句子完整写一次，值就放在句子中：

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

目录收到的是完整句子 `Hello {name}`。翻译可以调整或重复 `{name}`，但不能删除它、
凭空增加其他名称，也不能自行添加格式——本库会检查这一点，目录损坏时会回退到
源文本，而不是崩溃。

!!! note "初次接触 gettext？四句话讲完整个工作流"

    **gettext** 是软件获得翻译的标准方式，在 Python 内外皆然。你的代码标记可翻译
    字符串；*提取器*把它们收集进模板文件（`.pot`）；翻译者——通常不是程序员——为
    每种语言填写一份目录文件（`.po`），再编译成二进制 `.mo`，由应用程序在运行时
    加载。翻译函数的约定名称是 `_`，因此 `_(t"Hello {name}")` 读作“翻译这句话”。
    **[教程](tutorial.md)**用大约五分钟走完整条路径——标记、提取、翻译、编译、
    运行。

## 它解决的问题

在任何库看到 f-string 之前，插值已经完成——`f"Hello {name}"` 已经变成
`"Hello Ada"`，而围绕一个值去翻译前后的片段会破坏大多数语言的语法。t-string
（[PEP 750]）分别保留静态文本、已求值的值、源表达式、转换和格式说明——这恰好是
消息目录所需要的分离方式。参阅[它带来了哪些变化](comparison.md)，了解它与
`%(name)s`、`.format()` 和 `$`-string 的区别。

不过，gettext 和 Babel 都没有规定如何将 t-string 变成一条消息。本库做出了这一
选择，将其写成[带版本的规范](spec.md)，并提供[一致性测试套件](spec.md#conformance)
来验证实现。

## 它选择的设计

- 始终翻译完整消息，而不是句子片段。
- 只接受 `{name}` 这样的简单变量名。
- `!r` 和 `:.2f` 由应用程序控制，不进入目录。
- 允许翻译者调整和重复已知占位符，但不能访问属性，也不能增加格式行为。
- 继续使用普通的 POT、PO、MO 文件以及现有工具。

## 安装

```console
python -m pip install gettext-tstrings
```

需要 Python 3.14 或更高版本。**渲染不需要任何依赖项**——只使用标准库的
`gettext`。

提取和目录验证通过 [Babel] 运行。请在执行 `pybabel` 的环境中安装相应 extra；
通常这是开发或 CI 环境，而不是生产镜像。

```console
python -m pip install "gettext-tstrings[babel]"
```

## 接下来

<div class="grid cards" markdown>

- **[教程](tutorial.md)** — 从这里开始：从空目录到运行日语翻译只需五步，每条
  命令都附带其输出。
- **[为什么选择 t-string](comparison.md)** — 用四种方式编写同一条消息，并比较
  `%(name)s`、`.format()` 和 `$`-string 分别把什么交给目录。
- **[指南](guide.md)** — 运行时 API：复数、按请求选择语言、延迟字符串，以及目录
  出错时的处理方式。
- **[提取](extraction.md)** — `pybabel` 参考：配置、自定义函数名，以及现有工具
  如何免费验证这些目录。
- **[规范](spec.md)** — 将 t-string ↔ msgid 约定定义为稳定、带版本且拥有机器可读
  一致性测试套件的契约。
- **[API](api.md)** — 本包导出的全部内容，集中在一页。

</div>

## 本站自身就在使用

这份文档不只是一个翻译演示。导航、主题文字、版权行和支持复数规则的构建结果，
都由 `gettext-tstrings` 自身从 PO 目录渲染。
[多语言构建器](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
在每次严格构建中实际执行带上下文的消息、具名占位符以及全部十种语言的复数规则。

## 状态

目前是 alpha 版本。契约刻意保持精简，其中稳定的部分是[规范](spec.md)；Python API
仍有可能调整。稳定发布之前，还需要更广泛的语言 fixture、持续性能跟踪、真正使用
gettext 和 Babel 的用户参与 API 评审，以及覆盖所有受支持 Python 与 Babel 版本的
兼容性测试。

欢迎提交 [Issue 和 Pull Request](https://github.com/yhay81/gettext-tstrings/issues)。
alpha 阶段正是讨论接口最有价值的时候。

## 加入社区

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
