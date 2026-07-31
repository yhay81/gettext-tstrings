---
description: "同一則可翻譯訊息分別以 %-format、.format()、flufl.i18n 的 $-string 與 t-string 寫成，從譯者的失誤、目錄的權限與整合成本三方面比較。"
---

# 為什麼選擇 t-string

把一個值放進可翻譯訊息的四種做法，以同一則訊息互相比較。四者都替佔位符命名，
也都容許譯者調換順序；它們的差別在於翻譯出錯時會發生什麼、目錄能碰到你程式的
多少部分，以及採用它們要付出什麼代價。

表格擺在最前面，這樣你可以先找到自己在意的那一列，再只讀它背後的那一節。

!!! note "每一則翻譯訊息都經手三方"

    **目錄**就是裝著翻譯的檔案——由人編輯時是 `.po`，編譯成 `.mo` 給應用程式載入
    （[教學](tutorial.md)兩者都走過一遍）。每一則訊息都會經手三方：**開發者**寫下
    來源字串，**譯者**編輯目錄——往往是在外部平台上，離任何一次程式碼審查都很遠——
    然後**應用程式**在執行階段把兩者渲染在一起。以下每一種格式風格，對同一個問題
    給出了不同的答案：*目錄究竟能掌控格式語言的多少部分？* 在這些範例裡，`_` 是
    翻譯函式的慣用名稱，而 `tr` 是本函式庫的。

## 並排比較 { #side-by-side }

**當譯者出錯的時候。** 一份目錄會經過許多人的手，而其中出的差錯多半是無心的：

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 翻譯*漏掉*一個佔位符——會渲染出什麼？ | 值無聲無息地消失 | 值無聲無息地消失 | 值無聲無息地消失 | 來源訊息，外加一則警告（[預設](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻譯*多加*一個未知佔位符——會渲染出什麼？ | 一個例外 | 一個例外 | 佔位符以文字形式留著可見 | 來源訊息，外加一則警告（[預設](guide.md#what-happens-when-a-catalog-is-wrong)） |
| 翻譯*改寫*了某個佔位符的格式——會渲染出什麼？ | 目錄要求的格式，或者在型別字母不再配得上那個值時拋出例外 | 目錄要求的格式 | `$`-string 表達不出來 | 來源訊息，外加一則警告 |
| 佔位符會在渲染時被檢查嗎？ | 不會 | 不會 | 不會 | 會（見下文） |

**目錄握有多大的權限。** 一則翻譯是來自你儲存庫之外的資料，而每一種風格交到
它手上的權力並不一樣：

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 值從哪裡來？ | 一份明確的對應表 | 明確傳入的引數 | 呼叫端的 local 與 global 變數，外加選用的 `extras` | t-string 內部捕捉到的值 |
| 目錄能改變值被格式化的方式嗎？ | 能 | 能 | 不能 | 不能 |
| 目錄能伸進物件裡（屬性存取）嗎？ | 不能 | 能 | 能，透過帶點號的名稱 | 不能 |
| 「目前的語言」放在哪裡？ | 應用程式放到哪就在哪 | 應用程式放到哪就在哪 | 共用應用程式物件上的一疊語言代碼 | 一個 `ContextVar`，逐任務或逐請求 |

**整合起來要付出什麼。** 只要工具鏈合得來，上面這一切都不用花錢；下面才是可能
合不來的地方：

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| 最低 Python 版本 | 不限 | 不限 | 3.10 | **3.14** |
| 成熟度 | 標準函式庫 | 標準函式庫 | 穩定發行版 | **alpha** |
| 使用一般的 PO／MO 目錄嗎？ | 是 | 是 | 是 | 是 |
| 需要自訂的原始碼擷取器嗎？ | 不用 | 不用 | 不用 | 目前需要 |
| Babel 會推斷出哪個 PO 旗標，好讓既有工具驗證？ | `python-format` | `python-brace-format` | 無 | `python-brace-format` |

關於渲染時的檢查：單數訊息會被檢查佔位符是否完全相符。複數訊息同樣會被檢查，依據
的是那條讓目標語言的複數形式得以不同於來源語言的[聯集／交集規則](spec.md)；更嚴格
的逐形式檢查則在目錄編譯時執行（[擷取](extraction.md)）。

格式旗標那一列談的是「能否做佔位符感知的驗證」，而不是目錄相容性。`無`的意思是
標準的 gettext 工具照樣讀得懂也編譯得了這則訊息，只是 `msgfmt --check-format`
沒有可套用的 `$` 佔位符文法。

## 相容性與成熟度 { #compatibility-and-maturity }

上一張表的前兩列才是真正決定要不要採用的關鍵，所以值得直接說清楚，而不是塞在
格子裡。

`%`-format 與 `.format()` 內建於 Python，完全不需要任何相依套件。
[`flufl.i18n`][flufl-i18n] 是一個成熟的套件，已正式發行且用於正式環境，在
Python 3.10 以上都能跑。`gettext-tstrings` 還是 **alpha**，而且需要
**Python 3.14 以上**，因為 t-string 是 3.14 才有的新語法——它沒有回移版本，
也不可能有。它的[規範](spec.md)是其中穩定的那一部分；Python API 在 1.0 之前
仍有可能改動。

四者都不必付出的代價則是目錄相容性。它們全都產出普通的 POT／PO／MO 檔案，任何 PO
編輯器、翻譯平台與 GNU gettext 工具都早已讀得懂，所以底下這個選擇是可逆的，換掉
目錄*格式*可就不是。[遷移](migration.md)談的是如何搬動一個既有專案。

以下各節會逐一展開每一種做法的取捨細節。

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

會出什麼錯：翻譯裡少了一個字母，渲染就當場當掉。

目錄字串攜帶著 printf 語法，包括結尾那個型別字母——`%(name)s` 裡的 `s`——它既容易
被忽略，也容易被弄壞：

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

在 PO 編輯器裡改一個字元，除非目錄驗證先攔下來，否則就成了執行階段的例外。GNU
`msgfmt --check-format` 確實抓得到這一個，但僅限於被標上 `python-format` 的訊息，
而且還要目錄在送進你的應用程式的路上真的經過 msgfmt 才行。

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

它拿掉了結尾的型別字母，同時保留具名、可自由調換順序的佔位符。會出錯的地方換到了
交換的另一端：翻譯取得了對你物件的權力。

`str.format` 是一種小型的運算式語言，而對某個字串呼叫它，就等於把使用這種語言的
權利交給那個字串：

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

現在把那些字面字串換成 `_()` 回傳的任何東西。如果 `Hello {name}` 的某個翻譯回來
變成 `{conf.api_key}`，渲染它就會印出你的 API key——決定讀了什麼的是目錄，不是你的
程式碼。目錄不是程式碼，但它像資料一樣流動：送出去到翻譯平台、經過好幾雙手、以
`.po` 回來、編譯成 `.mo`，有時甚至整份是從專案外部取得的。`.format()` 讓這趟旅程
的每一站，都對你傳進去的物件擁有屬性存取權。

## `$`-string 與 flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

標準函式庫的 [`string.Template`][stdlib-template] 提供了 `$name` 這套插值語言，
但它本身並不是翻譯 API。[`flufl.i18n`][flufl-i18n] 把這種風格與 gettext 的目錄
查詢結合起來。請注意值從來不是傳進去的：flufl.i18n 是從呼叫端的 globals 與 locals
建出替換用的命名空間——呼叫點存在的任何變數，訊息都拿得到。另有一個選用的 `extras`
對應表，優先權高於前兩者。它面向譯者的語法沒有結尾的型別字母，也沒有格式規格，
而佔位符仍可自由調換順序。

替換不到值時並不會拋出例外。在 `name = "Ada"` 而呼叫端命名空間裡沒有 `nombre` 的
情況下，目錄裡 `Hello $nombre` 這則翻譯會渲染成 `Hello $nombre`：無法解析的佔位符
就這麼留著可見。那份[有明文記載的行為][documented behavior]保住了翻譯訊息的其餘
部分，而不是讓這次呼叫失敗。至於解析屬性或轉換值時拋出的例外，仍然可能往外傳。

`flufl.i18n` 在一個切題的面向上比裸的 `string.Template` 更有能耐。它的
[自訂 Template][custom Template] 接受 `$settings.api_key` 這類帶點號的佔位符，而它的
[translator] 會沿著這些路徑對呼叫端的值求解。一個被翻譯出來的佔位符，可以指名任何
取得得到的呼叫端 local 或 global，並且透過點號語法穿行它的屬性。當一則訊息需要某個
屬性時，這很方便，同時也把呼叫端的 frame 納入了目錄的替換命名空間。這裡的比較描述
的是 `flufl.i18n` 6.0.0，而不是 `string.Template` 的所有可能用法。

它同時也回答了另外兩種格式化風格完全丟給應用程式的一個問題：目前是*哪一個*語言，
以及要怎麼換掉它。一個[應用程式物件][application object]持有一疊語言，`_.push(code)`
與 `_.pop()` 推動它，`with _.using(code):` 可以巢狀，而一套[策略][strategy]負責依語言
代碼找出目錄，於是應用程式自己從不必碰目錄物件。那種在單一個工作單位之內就得產出
一種以上語言文字的伺服器——給讀者的一個頁面，加上給某個帳號設定成別種語言的人的一則
通知——正是這套機制存在的理由。

那疊語言就掛在那個應用程式物件上，而整個行程共用它。因此兩個彼此重疊的請求會共用
同一疊，於是那些在*時間上*並非嚴格巢狀的區塊，就會把錯的語言交到對方手上：

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

本函式庫保留了同樣的能力——繫結一樣會巢狀、一樣會層層退回——只是放在 `ContextVar`
裡，而不是一個共用的堆疊，所以上面那種交錯會逐任務各自解出正確答案。對應的寫法在
[同時處理多種語言](guide.md#several-languages-at-once)。它沒有提供的是「語言代碼到
目錄」的查詢：你要傳入一個 translations 物件，常見情況下就是一次
`gettext.translation()` 呼叫，而解析後的目錄由標準函式庫快取起來。

## t-string { #t-strings }

```python
tr(t"Hello {name}")
```

目錄看到的仍然是 `Hello {name}`，而且它依舊是一份普通的 PO／MO 目錄。差別在於一則
翻譯*被允許說些什麼*，以及由誰來檢查。

本函式庫在渲染之前，會拿每一則翻譯去對照來源訊息的佔位符做驗證，而且只接受裸的
名稱，別無其他。對照 `t"Hello {name}"`：

| 含有這種內容的翻譯 | 會被拒絕，理由是 |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

被拒絕不等於當掉：預設情況下本函式庫會記錄一則警告並渲染來源訊息，所以壞掉的目錄
絕不會把應用程式拖垮——[這正是 gettext 自己所守的契約](guide.md#what-happens-when-a-catalog-is-wrong)。

格式設定留在它原本被寫下的地方，也就是程式碼裡：

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` 從不會抵達目錄，所以沒有任何翻譯能改動它，也沒有任何譯者需要看到它。不過
它是一種*固定*的格式，而不是在地化的格式——要依語言選擇位數與分隔符號，那是
[Babel 的工作，在呼叫之前做](guide.md#locale-aware-values)。

還有一項差別在於工具：t-string 是新語法，所以要把它們擷取進 `.pot`，目前需要一個
懂 t-string 的擷取器，例如本套件[為 Babel 提供的那一個](extraction.md)。

## 這項限制的代價 { #the-cost-of-the-restriction }

除了 Python 版本要求之外，上述這一切的代價就是一條規則：插值必須是一個單純的
名稱。

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

那是一項實實在在的約束，而它正是造就上述那些保證的同一項約束。它與來源端的值繫結、
執行階段的佔位符檢查合在一起，阻止了目錄字串去求值運算式，也讓佔位符名稱對翻譯它的
那個人保持有意義。

f-string 根本無法這樣用——等到任何函式庫看到它的時候，它早已是一個成品字串，所以
翻譯它就等於在翻譯一個片段。t-string（[PEP 750]）把靜態文字與值分開保留，同時保有
近似 f-string 的語法以及明確的值繫結。

至於 Python 是怎麼走到這個十字路口的——相隔十年的兩份 PEP，以及那場沒有答案就結束的
標準函式庫討論——[專案背景](background.md)有連同出處的完整敘述。

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
