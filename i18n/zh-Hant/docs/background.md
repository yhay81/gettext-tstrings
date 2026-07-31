---
description: "三十年的 gettext、相隔十年的兩份 PEP，以及那場以 not-planned 收場的標準函式庫討論：這個函式庫為何存在，並附上出處連結。"
---

# 專案背景

本函式庫坐落在兩條漫長故事的交會處——一條講軟體怎麼被翻譯，一條講 Python 怎麼做
字串插值——它們終於在 2025 年交會，然後恰恰停在最需要一套精簡而謹慎的約定的那個
位置上。本頁把兩條故事都說一遍，並附上出處連結，因為本站上的設計決定，在你看得見
它們所回答的問題之後，會比較容易判斷。

## gettext 生態 { #the-gettext-ecosystem }

自 1990 年代中期以來，[GNU gettext] 就是自由軟體被翻譯的方式：在程式碼裡標記字串、
擷取成樣板、給譯者每種語言一份目錄檔、編譯，然後在執行階段載入。圍繞這個循環長出了
一整套生態——PO 編輯器、審查流程，以及全都講同一種檔案格式的翻譯平台——而 Python
的標準函式庫裡也已經帶著 [`gettext` 模組][stdlib-gettext] 超過二十年。翻譯裡屬於
執行階段的那一半，從來就不是問題。

一直沒有定案的另一半是*目錄字串長什麼樣子*。`%(name)s` 訊息交給譯者的是 printf
語法，少刪一個字母就在正式環境變成當機；`.format()` 訊息則把對活生生物件的屬性存取
交給了目錄。（[為什麼選擇 t-string](comparison.md) 把兩者連同失敗現場都走過一遍。）
而 f-string——如今大多數 Python 程式碼偏好的語法——則根本無從參與：等到任何函式庫
看到它，它早已是一個成品字串。人們還是照樣嘗試，而且次數多到 Babel 的 issue 追蹤器
收集了這些嘗試（[#594][babel-594]、[#715][babel-715]）；這種失敗是結構性的，不是
少了某個功能。

## 相隔十年的兩份 PEP { #two-peps-ten-years-apart }

2015 年，Alyssa Coghlan 與 Nick Humrich 寫下 [PEP 501]，提出插值 template，其明文
列出的第一項動機正是 i18n——用該 PEP 自己的話說，是「為 i18n 翻譯提供更乾淨的語法」。
這份提案被延後了，部分原因是討論顯示 i18n 這個情境帶著許多較單純的使用情境所沒有的
額外考量。

十年後，[PEP 750]——由 Jim Baker、Guido van Rossum、Paul Everitt、Koudai Aono、
Lysandros Nikolaou 與 Dave Peck 提出——以 t-string 的形式復活了這個想法，
[在 2025 年 4 月獲得接受][sc-resolution]，並隨 2025 年 10 月的
[Python 3.14] 一同推出。PEP 501 隨後為它而撤回。有一個細節對本頁很重要：i18n *不在*
PEP 750 所列的動機之中。這份 PEP 把機制一般化了——一種任何函式庫都能消費的 template
型別——而把翻譯這個問題原封不動地留在 PEP 501 十年前擱下它的地方：懸而未決。

於是到了 Python 3.14，這個語言恰好具備了訊息目錄所需要的資料結構，卻沒有把它當成
訊息目錄來用的任何約定。

## 標準函式庫討論 { #the-stdlib-discussion }

在 3.14 推出的兩個月前，Adrian Mönnich（ThiefMaster，Indico 專案的維護者之一）提議
在標準函式庫本身裡補上這道缺口：discuss.python.org 上的討論串
[Support t-strings in gettext][discuss-thread] 開在 2025 年 8 月，還附上一個可以運作的
[pull request][cpython-pr]，替 `gettext` 與 `pygettext` 都加上 t-string 支援。

那串討論值得整串讀完，因為它把本函式庫後來不得不回答的每一個難題全都攤了出來：

- **插值可以是什麼？** 只能是單純的名稱，還是連屬性與呼叫也行、再從中導出一個佔位符
  名稱？每一種答案都在便利性、msgid 穩定性與目錄安全性之間做取捨。
- **當目標語言的複數系統與來源語言不同時，複數形式要求什麼？**
- **gettext 到底是不是正確的目標？** Barry Warsaw——他在 PEP 750 發展期間就主張
  t-string 並不適合 i18n——指向他的 [`flufl.i18n`][flufl-i18n] 及其 `$`-string 風格，
  認為那才是更友善的工具；也有人主張乾脆離開 gettext，改投 [Fluent] 這類較新的系統。
- **還有那個後設問題：** 不論標準函式庫推出什麼，它基本上永遠不可能再改。一套有這麼多
  未定選項的約定，要在第一次嘗試就凍結下來，是件危險的事。

沒有形成共識。那個 CPython issue 被
[以「not planned」關閉][cpython-issue]，而該 pull request 也在 2025 年 10 月、3.14
發行後沒幾天，未經合併就被關掉。能力已經在語言裡了；約定卻無家可歸。

## 為什麼先做成一個套件 { #why-a-package-first }

那就是本專案選擇從標準函式庫外面來填的缺口，背後是一個刻意的賭注：一套約定在能夠自由
遞增版本、能夠一個案例一個案例地贏得採用的地方會成熟得更快，而標準函式庫——它必須
一次就做對——是一套約定應該*落腳*的地方，而不是應該被推敲出來的地方。

具體來說，那串討論裡每一個有爭議的問題，在這裡都有寫下來的答案，各自佔一頁：

- 插值**只能是單純的名稱**，好讓 msgid 保持穩定而有意義——
  [指南](guide.md#safety-and-scope)寫出這條規則，
  [運作原理](internals.md#from-template-to-msgid)給出理由。
- **格式設定完全不進目錄**（[為什麼選擇 t-string](comparison.md)）。
- **複數**遵循一條聯集／交集規則，讓目標語言的複數系統得以不同於來源語言
  （[spec §4](spec.md)）。
- 壞掉的目錄會**回退而不是當掉**，守住 gettext 自己的契約
  （[指南](guide.md#what-happens-when-a-catalog-is-wrong)）。
- 而整套約定就是一份[有版本的規範](spec.md)，附帶機器可讀的一致性測試套件——寫成
  這樣，是為了讓另一套實作、包括未來標準函式庫裡的那一套，都能原封不動地採用它並且
  互通。

討論還沒結束，而本專案是其中的參與者，不是它的判決。如果你有正式環境的 gettext 經驗
足以左右這些選擇，[那串討論][discuss-thread]與本儲存庫的
[Discussions][gh-discussions] 就是討論持續進行的地方。

## 時間線 { #timeline }

| 時間 | 發生了什麼 |
| --- | --- |
| 1990 年代中期 | GNU gettext 確立了譯者與平台至今仍在講的 PO／POT／MO 工作流程。 |
| 2015 | [PEP 501] 提出插值 template，並以 i18n 為第一動機；遭延後。 |
| 2016 | f-string 隨 Python 3.6 推出——插值有了自己的語法，而翻譯用不上它。 |
| 2024 年 7 月 | [PEP 750] 提出 t-string。 |
| 2025 年 4 月 | PEP 750 [獲得接受][sc-resolution]；PEP 501 為它而撤回。 |
| 2025 年 8 月 | [Support t-strings in gettext][discuss-thread] 討論串開啟，附帶一個標準函式庫的 [pull request][cpython-pr]。 |
| 2025 年 10 月 | [Python 3.14] 推出 t-string；該標準函式庫 issue 以 [not planned][cpython-issue] 關閉。 |
| 2026 | `gettext-tstrings` 以 alpha 發行，帶著 [spec v1](spec.md) 與它的一致性測試套件。 |

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
