---
description: "将 t-string 到 msgid 的约定定义为精简、带版本并拥有机器可读一致性测试套件的契约。"
---

# 规范

本库实现的约定被写成一份精简而稳定的契约，使其他实现——提取器、IDE、类型检查器或
未来的 `pygettext`——也能采用它并实现互操作。

[阅读规范 v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## 一屏内的规则

**msgid** 按源代码顺序连接所有字面量片段，并为每个插值加入一个 `{name}` token。
字面量花括号会被转义（`{` 变成 `{{`）。名称必须是简单占位符名，即
`str.isidentifier()` 为真且不是 Python 关键字。转换和格式说明**不属于** msgid，
而由应用程序控制。

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *拒绝——不是简单名称* |

当一条**翻译**只包含裸 `{name}` 占位符、每个必需名称至少出现一次，且没有允许集合
之外的名称时，它就是有效的。我们刻意不限制调整顺序和重复，因为目标语言的语法可能
需要二者。

对于复数，*允许*集合是两个分支名称的并集，*必需*集合是交集。因此
`t"One file"` 与 `t"{n} files"` 允许任一翻译形式使用 `n`，但都不强制要求它。
目标语言的复数规则可以与源语言不同。

**空 msgid** 不会被查询，因为 gettext 将它保留给目录元数据头。

## 一致性 { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
是同一文档的机器可读版本：其中包含从 t-string 静态结构到 msgid 的案例，以及从
msgid 和目录 pattern 到渲染结果或拒绝结果的案例。

能够复现所有案例的实现即**符合规范 v1**。案例只描述规范定义的内容——派生 msgid、
接受或拒绝的 pattern、渲染输出——而不绑定错误消息或异常类型，因此其他语言的实现
也可原样运行。

插值以结构描述，而不是 Python 源代码：

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

参考实现会在自身测试套件中运行这些案例，因此文档和代码不会在无人察觉的情况下
逐渐偏离。

## 版本管理

当前是规范 v1。若 msgid 派生或翻译验证发生不向后兼容的变化，就提高版本，并在现有
文件旁提供新的 `conformance/vN.json`。如果补充说明既不改变派生 msgid，也不改变
接受的 pattern，则不提高版本。
