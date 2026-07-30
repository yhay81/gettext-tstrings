---
description: "使用 pybabel 提取 t-string 消息，并通过 msgfmt 和内置 Babel checker 验证目录。"
---

# 提取

提取是把源代码中每一条被标记的消息收集进供翻译者使用的 `.pot` 模板的步骤——
即[教程](tutorial.md)循环中的第 3 步。本页是该步骤的参考：配置、自定义函数名、
CI 的 strict 模式，以及此后守护目录的各项检查。

提取需要 `babel` extra：

```console
python -m pip install "gettext-tstrings[babel]"
```

## 工作流

创建 `babel.cfg`：

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

然后使用普通 Babel 命令：

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`gettext_tstrings` extractor 也处理普通的 `_()`、`gettext()` 和 `ngettext()`
调用，所以一个 mapping 就能覆盖混合 codebase。它识别 `_()`、四个标准 gettext
名称、`tr()` / `ntr()` 别名，以及延迟翻译用的 `lazy_gettext()` /
`lazy_pgettext()`。

!!! warning "`-c` 不能省略"

    与普通 gettext 调用完全一样，只有向 `pybabel extract` 传入
    `-c "Translators:"` 才会收集翻译者注释。

## 注册自定义函数名

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

ini 文件提供一个字符串，TOML mapping 提供一个列表；字符串内可用空格或逗号分隔
名称。四种写法都可使用。

可配置项包括 `tr_functions`、`ntr_functions`、`gettext_functions`、
`ngettext_functions`、`pgettext_functions` 和 `npgettext_functions`。

!!! danger "`-k` 无法到达 t-string"

    `mytr(t"…")` 这样的自定义 helper 必须在上述选项之一中注册。Babel 的
    `--keyword` 机制无法读取 t-string literal，因此
    `pybabel extract -k mytr` 什么也找不到，也不会发出提示——消息只会缺席于 POT。
    对同时提取的普通 gettext 调用，`-k` 仍然有效。

    仅支持标准参数顺序：普通调用先放 message；`pgettext` 依次为 context、message；
    `npgettext` 依次为 context、单数、复数。

## 默认健壮

一个坏文件不会终止整个提取过程：

- extractor 拒绝的 t-string——属性访问、表达式、错误参数——会被报告为警告并跳过。
- 无法 parse 的文件也以同样方式跳过。
- `ast` 接受但只有 `tokenize` 拒绝的文件同样会跳过，否则 Babel 自身的 pass 会
  因此中止。

在 mapping 选项中设置 `strict = true`，可将以上情况全部变成 hard failure；CI
应当使用这一模式。

## 现有 toolchain 会验证这些目录

Babel 为每条提取消息添加一个标准标志，这一行会激活现有工具中的占位符检查：

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

将它翻译为 `こんにちは {nombre}` 后，无需配置就能捕获错误：

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate 将同一检查记录为 [Python brace format][weblate-checks]，商业平台也有基于
同一标志的占位符 QA。它们的行为由各自产品负责；下面两个工具才是本项目明确验证的。

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

此外，本包还注册了一个 Babel **checker**，因此 `pybabel compile` 会把规范规则
应用到每一条带有 `gettext-tstrings` marker 注释的消息：

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

对于复数消息，指针会指出具体形式，因为 Babel 报告的是 msgid 行号，而俄语 block
在它下面有三个 `msgstr`：

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` 仍会写出 `.mo`"

    上面的错误会被报告，退出状态为 `1`，但损坏的目录仍会被编译。先运行
    `pybabel compile`、再复制 `locales/` 的 pipeline 如果不检查退出状态，就会发布
    错误翻译。

    ```yaml
    - run: pybabel compile -d locales   # non-zero exit is the gate
    ```

两种检查并不重复。内置 checker 至少在两处更加严格：

- 如果 msgid 中只有转义花括号（`Config {{raw}} only`），就不会获得
  `python-brace-format` 标志，因此外部工具完全不会验证它。
- 复数形式会逐个检查。`msgfmt --check-format` 读取上面的文件会返回 `0`；某个形式
  删除了兄弟形式保留的占位符，msgfmt 会接受，而本 checker 会拒绝。

`msgfmt` 只检查能按 Python brace format 解析的占位符名称。使用 ASCII 名称，可以
让链中的每个工具都验证消息；本库自身接受所有满足 `str.isidentifier()` 的名称。

## Template 和其他工具

t-string 是 Python 语法，因此本库覆盖 Python source。template 语言继续使用各自的
i18n——Jinja2 的 `{% trans %}`、Django template tag——以及对应的 Babel extractor。
所有内容进入同一个 PO 目录，因此混合 codebase 仍可使用一套翻译工作流。

目前 `pygettext` 无法 parse t-string，所以提取通过 Babel 完成。该约定已写入
[规范](spec.md)，以便其他 extractor 或未来的 `pygettext` 实现同一目标。
