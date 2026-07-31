---
description: "在已有 gettext 目录的项目中引入 t-string：哪些原封不动、哪些会变成 fuzzy，以及如何一个调用点一个调用点地迁移。"
---

# 迁移

如果你的项目已经在用 gettext，那么决定本库是否可采用的问题就很具体：它会不会
让现有目录作废，能不能与你暂时不打算修改的代码共存，以及这次迁移必须一次性完成
多少。答案如下，最短的先说：

| 问题 | 答案 |
| --- | --- |
| 现有的 `.po` 和 `.mo` 文件还能用吗？ | 能。同样的文件，同样的工具。 |
| 新旧调用能写在同一个文件里吗？ | 能，而且一份 extractor mapping 就能覆盖两者。 |
| msgid 会变吗？ | 从 `.format()` 迁移不会变。从 `%`-format 迁移会变。 |
| 整个项目必须一次性迁移吗？ | 不必。只改一个调用点也是一次有效的变更。 |
| Jinja、Django template、JavaScript 怎么办？ | 不受影响，目录照旧。 |

本页其余部分就是上述每一条背后的细节。

## 从 `.format()` 迁移：msgid 不变 { #from-format-the-msgid-does-not-change }

这种情况下迁移几乎没有代价。`str.format` 消息和 t-string 消息推导出的是*同一个*
目录 key，因为两种写法留在文本里的都是 `{name}`：

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

因此已有翻译仍会挂在这条消息上。假设目录里原本是

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

修改调用、重新提取、然后更新：

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

回来的条目只在两行元数据上有差别，其余完全相同——一条标明它是 t-string 消息的
marker 注释，以及一个源代码行号：

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

没有 `fuzzy` 标志，任何语言都不需要重新翻译。消息立刻就能渲染出来：

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` 会把目录报告为已过时"

    那条 marker 注释和挪动过的行号，已经足以让 `pybabel update --check` 认为
    目录需要重新生成，因为它比较的是整个条目，而不只是译文。请在修改代码的
    同一次提交中运行真正的 `pybabel update`，并把目录一起提交——这也正是
    [CI 关卡](workflow.md#what-ci-gates)本来就要求的习惯。

## 从 `%`-format 迁移：msgid 会变，因此翻译变成 fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

printf 语法就住在消息*内部*，因此替换它就会改写目录 key。这一点绕不过去，也是
告别 `%(name)s` 必须诚实付出的代价：

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` 会认出新消息与被删除的那条很接近，于是把旧译文带过来，并打上
fuzzy 标志：

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

关于这个状态，有三点需要知道：

- **运行时不会出任何问题。** fuzzy 条目会被排除在编译出的 `.mo` 之外，因此在有人
  确认这一对之前，应用程序渲染的是源消息——[与任何被改写的消息经历的降级完全
  相同](workflow.md#the-cycle-after-the-first-translation)。
- **`pybabel compile` 会逐条报告它们**，因为带过来的 `%(name)s` 不是合法的花括号
  占位符，并且它会以非零状态退出。那份清单是你的工作队列，不是误报；里面的条目
  确实需要编辑。
- **旧的 `python-format` 标志会一起被带过来**，应当与 `fuzzy` 标志一并删除，
  否则 `msgfmt --check-format` 会继续用 printf 规则去检查一条 brace-format 消息。

对于有名称的 printf 占位符，这个编辑是机械性的——`%(name)s` 变成 `{name}`，
其余一动不动——因此一份大目录只需一次脚本化处理加一遍翻译者复核，而不是重新翻译。
位置参数 `%s` 就不是机械性的：它没有名称可以带过来，而给它起个名字恰恰是这次
变更的意义所在。

正因如此，实际的做法是有节奏地迁移 `%`-format 消息——一个模块、一个发布、一种
语言地推进——而不是一次横扫，把所有目录同时变红。

## 新旧调用可以共存 { #old-and-new-calls-coexist }

读取 t-string 的那个 extractor 同样读取普通的 gettext 调用，因此一份 mapping
就能覆盖一个迁移到一半的文件：

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

两条消息都会进入同一个模板，只有 t-string 那条带着开启本库额外检查的 marker
注释：

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

它识别 `_()`、四个标准 gettext 名称、`tr()` / `ntr()` 别名，以及延迟翻译用的
`lazy_gettext()` / `lazy_pgettext()`。你自己的 helper 则必须
[在 mapping 中注册](extraction.md#registering-your-own-function-names)。

在运行时，两种风格同样彼此独立：`gettext.translation()` 返回一个翻译对象，
`_` 和本库的入口点都从它读取。

## 哪些东西不用动 { #what-does-not-move }

- **Template 语言。** Jinja2 的 `{% trans %}`、Django 的 template tag，以及它们
  对应的 Babel extractor 都照常工作，也继续向同一批 PO 目录供料。t-string 是
  Python 语法，只作用于 Python source。
- **你的目录文件。** 格式不变，不新增文件，不需要转换步骤。
- **你的翻译平台。** `.po` 交换格式完全一致，而 t-string 消息带的
  `python-brace-format` 标志与 `.format()` 消息带的是同一个标志——所以占位符 QA
  照常有效。
- **非 Python 代码。** 同一项目中的 JavaScript 或 C 目录不受影响。

## 一份迁移清单 { #a-migration-checklist }

1. 在运行 `pybabel` 的地方装上 `babel` extra，并把 `babel.cfg` 里的 `python`
   mapping 改成 `gettext_tstrings` 方法——此后一份 mapping 覆盖两种风格，而
   `-k` 对普通调用仍然有效。
2. 先改造 `.format()` 调用点。重新提取，运行 `pybabel update`，并把目录与代码
   一起提交；预期不会出现 fuzzy 条目。
3. 按能够被评审的批次改造 `%`-format 调用点，重写带过来的占位符，并清除 `fuzzy`
   与 `python-format` 标志。
4. 修复被限制拒绝的写法：插值必须是简单名称，因此 `t"Hello {user.name}"` 要先
   改成一个局部变量。这是调用点的修改，不是目录的修改。
5. 全部推进完成后，在 extractor mapping 中打开 `strict = true`，这样无法提取的
   消息会让[构建失败](extraction.md#lenient-locally-strict-in-ci)，而不是从模板中
   悄悄消失。
6. 加上[生产实践](workflow.md#what-ci-gates)中的运行时检查：让每种要发布的语言
   各有一条消息通过 strict 的 `Translator` 渲染。

第 2、3 步都是普通的提交。这份清单里没有任何一项需要一次性全量切换。
