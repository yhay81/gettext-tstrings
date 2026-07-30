---
description: "通过 gettext 和 Babel 翻译完整的 t-string 消息，同时将格式控制保留在目录之外。"
---

# gettext-tstrings

面向 Python 3.14+ t-string 的安全 gettext 与 Babel 集成。

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

目录收到的是完整句子 `Hello {name}`。翻译可以调整或重复 `{name}`，但不能删除它、
凭空增加其他名称，也不能自行添加格式。

## 它解决的问题

在任何库看到 f-string 之前，插值已经完成，因此翻译 f-string 实际上只能翻译句子
片段。t-string（[PEP 750]）分别保留静态文本、已求值的值、源表达式、转换和格式
说明——这恰好是消息目录所需要的分离方式。参阅[它带来了哪些变化](comparison.md)，
了解它与 `%(name)s` 和 `.format()` 的区别。

不过，gettext 和 Babel 都没有规定如何将 t-string 变成一条消息。本库做出了这一
选择，将其写成[带版本的规范](spec.md)，并提供[一致性测试套件](spec.md#conformance)
来验证实现。

## 它选择的设计

- 始终翻译完整消息，而不是句子片段。
- 只接受 `{name}` 这样的简单变量名。
- `!r` 和 `:.2f` 由应用程序控制，不进入目录。
- 允许翻译者调整和重复已知占位符，但不能访问属性，也不能增加格式行为。
- 继续使用普通的 POT、PO、MO 文件以及现有工具。

## 本站自身就在使用

这份文档不只是一个翻译演示。导航、主题文字、版权行和支持复数规则的构建结果，
都由 `gettext-tstrings` 自身从 PO 目录渲染。
[多语言构建器](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
在每次严格构建中实际执行带上下文的消息、具名占位符以及全部十种语言的复数规则。

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

- **[为什么选择 t-string](comparison.md)** — 用三种方式编写同一条消息，并比较
  `%(name)s`、`.format()` 和 t-string 分别把什么交给目录。
- **[指南](guide.md)** — 运行时 API、按请求选择语言、延迟字符串，以及目录出错时的
  处理方式。
- **[提取](extraction.md)** — `pybabel` 工作流、配置，以及现有工具如何直接验证
  这些目录。
- **[规范](spec.md)** — 将 t-string ↔ msgid 约定定义为稳定、带版本且拥有机器可读
  一致性测试套件的契约。
- **[API](api.md)** — 本包导出的全部内容。

</div>

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
