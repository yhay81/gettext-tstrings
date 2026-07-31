---
description: "執行階段 API：繫結目錄、逐請求切換語言、延遲字串，以及損壞的翻譯如何被回報。"
---

# 指南

本頁是執行階段參考：目錄備妥之後，*應用程式碼*透過本函式庫所做的一切都在這裡。
如果你還沒看過完整的循環——標記、擷取、翻譯、編譯、執行——[教學](tutorial.md)
會用五分鐘走過一遍；目錄的建立與驗證請見[擷取](extraction.md)；團隊如何讓這個
循環持續轉動——更新週期、CI、翻譯平台——則在[正式環境實務](workflow.md)。

## 繫結目錄 { #binding-a-catalog }

建議的寫法與 gettext 以類別為基礎的用法一致：把標準翻譯物件繫結一次，再把可呼叫
的處理器當作 `_` 使用。

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

模組層級的函式沿用標準函式庫的名稱，以及僅限位置引數的呼叫慣例：

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` 與 `ntr` 分別是 `gettext` 與 `ngettext` 的完全別名。

## 逐請求切換語言 { #per-request-language }

Web framework 會為每個請求挑選語言。把該請求的翻譯繫結到目前的上下文，之後每一次
模組層級的呼叫都會解析到那個語言，而且在並行的請求之間彼此安全隔離：

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

對於自行管理請求生命週期的 framework，`set_translations(translations)` 不需要
`with` 區塊即可繫結；`get_translations()` 則讀取目前的繫結。明確傳入的
`translations=` 引數一律優先於上下文，而未繫結的上下文會回退到標準函式庫全域
安裝的 gettext 函式。Flask 與 ASGI 中介軟體的完整範例，請見
[正式環境實務](workflow.md#binding-a-language-at-runtime)頁。

## 延遲翻譯 { #deferred-translation }

t-string 會立刻捕捉它的值，但對於在 import 時就定義的字串——表單標籤、列舉值、
模組常數——這並不正確，因為它們必須以*被使用當下*生效的語言渲染。

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` 可透過 `str()`、`format()` 與 f-string 渲染，並與渲染後的文字相等。

!!! note "刻意不可雜湊"

    `LazyString` 的文字取決於當前語言，因此雜湊值會在切換語言時改變，並悄悄
    破壞任何持有它的 set 或 dict。需要當作 key 時，請先呼叫 `str()`。

`strict` 由訊息*被寫下*的地方決定，而不是由它渲染的地方決定：

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

一個延遲字串會在它最終被使用的任何地方渲染——在模板裡、在表單裡、在某行日誌
裡——而那個地方很少知道這次究竟是測試執行還是正式環境。在定義處傳入
`strict=True`，正是讓同一套[在 CI 大聲、在正式環境寬容](#what-happens-when-a-catalog-is-wrong)
的取捨，也能套用到一個並非在其呼叫點渲染的字串上。

複數形式取決於執行階段的數量，所以請在已知數量之處以 `ngettext` 立即渲染。

## 同時處理多種語言 { #several-languages-at-once }

一個請求常常需要不只一種語言：為讀者渲染的頁面，同時又要為某個設定成另一種語言的
帳號排入一則通知；或是一份摘要，要以每位參與者自己的語言引述他們。繫結可以巢狀，
而離開內層區塊就會回復外層那一個。

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

面對一整份收件者清單，延遲字串就把事情做完了：訊息只在 import 時寫一次，然後每種
語言各渲染一次。

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

這個繫結是一個 `ContextVar`，而不是掛在共用物件上的一個堆疊，所以彼此重疊的請求
不可能撿到對方的語言——包括它們以進入的順序*離開*各自區塊的那種情況，而那正是下推
堆疊會弄錯的交錯。逐語言載入目錄的成本很低：`gettext.translation()` 只解析每個
`.mo` 一次，並交出共用同一份已解析目錄的副本。

!!! warning "工作執行緒會不會繼承繫結，取決於建置版本"

    一個裸的 `threading.Thread`，或 `ThreadPoolExecutor.submit`，起步時用的要嘛是
    呼叫端上下文的一份副本，要嘛是一個空的上下文；決定是哪一種的是
    `sys.flags.thread_inherit_context`——在自由執行緒建置上預設為真，在其他任何地方
    都為假。因此同一份程式碼在 3.14t 上渲染出被繫結的語言，在 3.14 上卻渲染出行程
    層級的全域目錄。請把上下文傳過去，而不要依賴預設值：

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` 已經替你做好這件事了。

## 目錄出錯時會發生什麼事 { #what-happens-when-a-catalog-is-wrong }

如果翻譯的佔位符與原文不符——缺漏、未知，或被改寫格式的欄位躲過了驗證，來自手動
編輯的 MO、外部廠商的目錄，或是略過檢查器的流程——預設行為是重現原文，而不是拋出
例外。這與 gettext 自身的契約一致：損壞的目錄絕不該弄壞應用程式。

當 `Hello {name}` 被翻譯成 `こんにちは {nombre}`，渲染仍會成功，並向
`gettext_tstrings` logger 送出一則警告：

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

警告只會就每一組訊息與 pattern 觸發一次，而不是每次渲染都觸發，因此一筆損壞的
目錄項目不會灌爆日誌。

測試與 CI 可以選擇讓它大聲失敗：

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

同一次查詢屆時會拋出例外，帶著同樣那句話，但少了「using source text」那一半：

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## 讀懂錯誤訊息 { #reading-a-failure-message }

這些訊息是寫給有能力處理它們的人看的，而目錄的問題落在譯者身上的機會，遠多於
程式設計師。當那幾個字就明明白白攤在讀者眼前時，只回報 `{name}` 不見了等於死路
一條；因此只要佔位符看起來存在、實際上卻不是，訊息就會說明原因。對照原文
`Hello {name}`，下列每一種情況都會在
`translation does not match the source placeholders:` 之後回報：

| 翻譯寫成 | 訊息給出的原因 |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

看不見的字元有專屬的處理方式。花括號裡的 no-break space 是輸入法的產物，任何編輯器
都不會顯示它，所以訊息會以碼位印出它，而不是要讀者去找一個根本找不到的字元：

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

字母混用了不同書寫系統的名稱——也就是 homoglyph 的情況，西里爾字母 `а` 和拉丁
字母根本無從分辨——會被顯示兩次，一次可讀、一次跳脫，而後者是唯一能分辨兩者的
形式：

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

當一個完全以希臘字母或西里爾字母寫成的名稱與 ASCII 原始名稱衝突時，也會做同樣的
消歧，包括只有單一字母的拉丁 `a` 與西里爾 `а` 那種情況。

## 不透過目錄渲染 pattern { #rendering-a-pattern-without-a-catalog }

`compile_template` 把同一套機制往下暴露一層：它把 t-string 轉成 msgid 加上一組
繫結好的值，並渲染你交給它的任何 pattern。

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` 以相同的規則驗證，而且只要不相符就**一律拋出例外**。這裡沒有寬鬆模式：
寬鬆存在的用意，是讓*目錄*查詢能夠退回原文，而你自己傳進來的 pattern 沒有可退回
的對象。

## 安全性與適用範圍 { #safety-and-scope }

這樣寫是有效的：

```python
tr(t"Hello {name}")
```

這些則是刻意被拒絕的：

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

請先算出一個有意義的值：

```python
name = user.display_name()
tr(t"Hello {name}")
```

這項限制帶來穩定的目錄 key，讓譯者拿到有意義的名稱，也讓被翻譯的字串不至於變成
一種運算式語言。

這項保證的範圍限於*結構與格式*：翻譯永遠不會被求值，也永遠無法加入屬性存取、
呼叫、轉換或格式規格。有兩件事仍屬於呼叫端的責任，和標準函式庫的 gettext 一模
一樣——依輸出去向（HTML、shell、終端機）對渲染結果進行**跳脫**，以及維護**目錄
完整性**，因為惡意的目錄可以重複佔位符來放大輸出量，而這是任何以佔位符為基礎的
i18n 都固有的性質。
