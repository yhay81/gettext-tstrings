---
description: "三十年的 gettext、相隔十年的两个 PEP，以及以 not-planned 告终的标准库讨论：本库为何存在，并附来源链接。"
---

# 项目背景

本库位于两条漫长故事的交汇处——一条关于软件如何获得翻译，一条关于 Python
如何插值字符串。它们终于在 2025 年相交，却恰好停在需要一个小而谨慎的约定的
地方。本页讲述这两条故事，并附来源链接，因为当你看清设计决策所回答的问题时，
评判本站上的这些决策会容易得多。

## gettext 生态 { #the-gettext-ecosystem }

自 1990 年代中期以来，[GNU gettext] 一直是自由软件获得翻译的方式：在代码中
标记字符串，将它们提取到模板中，为翻译者提供每种语言一份目录文件，编译，
在运行时加载。围绕这个循环生长出了一个完整的生态——PO 编辑器、审校工作流，
以及全都使用同一文件格式的翻译平台——而 Python 的标准库内置
[`gettext` 模块][stdlib-gettext]也已超过二十年。翻译的运行时那一半从来不是
问题。

悬而未决的那一半始终是*目录字符串长什么样*。`%(name)s` 消息把 printf 语法
交到翻译者手中，删掉一个字母就是一次生产环境崩溃；`.format()` 消息则把对
活对象的属性访问交给目录。（[为什么选择 t-string](comparison.md) 逐一演示了
两者，并把失败方式摆在眼前。）而 f-string——如今大多数 Python 代码首选的
语法——根本无法参与：任何库看到它时，它已经是一条完成的字符串。人们仍然
不断尝试，多到 Babel 的 issue 跟踪器收集了这些尝试
（[#594][babel-594]、[#715][babel-715]）；这种失败是结构性的，而不是缺少
某个功能。

## 相隔十年的两个 PEP { #two-peps-ten-years-apart }

2015 年，Alyssa Coghlan 和 Nick Humrich 撰写了 [PEP 501]，提出插值模板，其
陈述的第一动机就是 i18n——用该 PEP 自己的话说，是 "providing a cleaner
syntax for i18n translation"。提案被推迟，部分原因是讨论表明 i18n 场景带有
大量更简单用例所没有的额外考量。

十年之后，[PEP 750]——作者为 Jim Baker、Guido van Rossum、Paul Everitt、
Koudai Aono、Lysandros Nikolaou 和 Dave Peck——以 t-string 的形式复活了这一
想法，于 [2025 年 4 月被接受][sc-resolution]，并于 2025 年 10 月随
[Python 3.14] 发布。PEP 501 随后为其让路而撤回。有一个细节对本页很重要：
i18n *不在* PEP 750 陈述的动机之列。该 PEP 把机制一般化——一种任何库都可以
消费的 template 类型——而把翻译问题留在 PEP 501 十年前搁置它的地方：悬而
未决。

于是，到了 Python 3.14，这门语言恰好拥有了消息目录所需的数据结构，却没有
把它用作消息目录的约定。

## 标准库讨论 { #the-stdlib-discussion }

在 3.14 发布前两个月，Adrian Mönnich（ThiefMaster，Indico 项目的维护者）
提议在标准库内部弥合这一缺口：2025 年 8 月在 discuss.python.org 上开启的
[Support t-strings in gettext][discuss-thread] 帖子，附带一个可用的
[pull request][cpython-pr]，为 `gettext` 和 `pygettext` 同时添加 t-string
支持。

这个帖子值得完整读一遍，因为它浮现出了本库后来必须回答的每一个难题：

- **插值可以是什么？**只允许简单名称，还是允许属性和调用并派生出占位符
  名称？每种答案都在便利性与 msgid 稳定性、目录安全性之间做取舍。
- **复数形式需要什么，**当目标语言的复数体系不同于源语言时？
- **gettext 究竟是不是正确的目标？**Barry Warsaw——他在 PEP 750 的制定过程
  中就主张 t-string 并不适合 i18n——指向自己的 [`flufl.i18n`][flufl-i18n]
  及其 `$`-string 风格作为更友好的工具；也有人主张干脆离开 gettext，转向
  [Fluent] 这样的新系统。
- **还有一个元问题：**标准库一旦发布了什么，就几乎永远无法更改。一个还有
  这么多开放选择的约定，第一次尝试就冻结是件冒险的事。

讨论没有形成共识。CPython issue 被[关闭为 "not planned"][cpython-issue]，
pull request 也在 2025 年 10 月——3.14 发布几天之后——未经合并即被关闭。
能力已经存在于语言之中；约定却无处安放。

## 为什么先做一个包 { #why-a-package-first }

这正是本项目选择从标准库之外填补的缺口，背后是一个深思熟虑的赌注：约定在
能够自由发版、逐个案例赢得采用的地方成熟得更快；而必须第一次就做对的标准库，
应当是约定最终*落脚*的地方，而不是打磨约定的地方。

具体来说，帖子中每一个有争议的问题在这里都有写下来的答案，各自占据一页：

- 插值**只允许简单名称**，让 msgid 保持稳定且有意义——[指南](guide.md#safety-and-scope)
  展示这条规则，[工作原理](internals.md#from-template-to-msgid) 说明其理由。
- **格式完全不进入目录**（[为什么选择 t-string](comparison.md)）。
- **复数**遵循并集/交集规则，允许目标语言的复数体系不同于源语言
  （[规范 §4](spec.md)）。
- 损坏的目录**回退而不是崩溃**，延续 gettext 自身的契约
  （[指南](guide.md#what-happens-when-a-catalog-is-wrong)）。
- 而整个约定是一份[带版本的规范](spec.md)，附有机器可读的一致性测试套件——
  写成任何其他实现（包括未来的标准库实现）都可以原样采用并与之互操作的
  形式。

这场讨论尚未结束，本项目是其中的参与者，而不是对它的裁决。如果你拥有与这些
选择相关的生产 gettext 经验，[同一个帖子][discuss-thread]和本仓库的
[Discussions][gh-discussions] 正是讨论继续进行的地方。

## 时间线 { #timeline }

| 时间 | 发生了什么 |
| --- | --- |
| 1990 年代中期 | GNU gettext 确立了翻译者和平台至今仍在使用的 PO/POT/MO 工作流。 |
| 2015 | [PEP 501] 提出插值模板，i18n 是其第一动机；提案被推迟。 |
| 2016 | f-string 随 Python 3.6 发布——插值有了自己的语法，而翻译无法使用它。 |
| 2024 年 7 月 | [PEP 750] 提出 t-string。 |
| 2025 年 4 月 | PEP 750 [被接受][sc-resolution]；PEP 501 为其让路而撤回。 |
| 2025 年 8 月 | [Support t-strings in gettext][discuss-thread] 帖子开启，并附标准库 [pull request][cpython-pr]。 |
| 2025 年 10 月 | [Python 3.14] 发布 t-string；标准库 issue 以 [not planned][cpython-issue] 关闭。 |
| 2026 | `gettext-tstrings` 以 alpha 版发布，带有[规范 v1](spec.md)及其一致性测试套件。 |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
