---
description: "在已經有 gettext 目錄的專案裡採用 t-string：什麼原封不動、什麼會變成 fuzzy，以及如何一次只搬一個呼叫點。"
---

# 遷移

如果你的專案已經在用 gettext，那麼決定本函式庫能不能採用的問題就那麼幾個：它會不會
讓你手上的目錄作廢、它能不能和你還不打算改的程式碼共存，以及這趟搬遷有多少必須一次
做完。答案如下，最短的先講：

| 問題 | 答案 |
| --- | --- |
| 現有的 `.po` 與 `.mo` 檔還能用嗎？ | 能。同樣的檔案，同樣的工具。 |
| 新舊呼叫能寫在同一個檔案裡嗎？ | 能，而且一份擷取器 mapping 就涵蓋兩者。 |
| msgid 會變嗎？ | 從 `.format()` 過來不會變；從 `%`-format 過來會變。 |
| 整個專案必須一次搬完嗎？ | 不必。只改一個呼叫點也是一次成立的變更。 |
| Jinja、Django template、JavaScript 怎麼辦？ | 不受影響，目錄照舊。 |

本頁接下來就是上面每一條背後的細節。

## 從 `.format()` 過來：msgid 不會變 { #from-format-the-msgid-does-not-change }

這是遷移幾乎不花成本的情況。一則 `str.format` 訊息和一則 t-string 訊息推導出的是
*同一個*目錄 key，因為不論哪一種寫法，那個 key 都是把 `{name}` 原樣留在裡面的文字：

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

所以既有的翻譯仍然掛在上面。假設目錄裡原本是

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

改掉呼叫、重新擷取，然後更新：

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

回來的那筆條目只差在兩行後設資料上，其餘一模一樣——一則標明它是 t-string 訊息的
marker 註解，以及一個原始碼行號：

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

沒有 `fuzzy` 旗標，任何語言都不必重譯。訊息立刻就渲染得出來：

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` 會把這些目錄報成過期"

    那則 marker 註解和挪動過的行號，就足以讓 `pybabel update --check` 說某份目錄需要
    重新產生，因為它比較的是整筆條目，而不只是譯文。請在改動程式碼的同一次 commit 裡
    跑真正的 `pybabel update`，並把目錄一起提交——這正是
    [CI 關卡](workflow.md#what-ci-gates)本來就要求的習慣。

## 從 `%`-format 過來：msgid 會變，所以翻譯會變成 fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

printf 語法住在訊息*裡面*，所以換掉它就等於改寫目錄 key。這一點沒有辦法繞過去，而它
就是揮別 `%(name)s` 所要誠實付出的代價：

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` 會認出這則新訊息是被移除那則的近親，把舊翻譯帶過來，並標上 fuzzy：

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

關於這個狀態，有三件事要知道：

- **執行階段不會壞掉。** fuzzy 條目會被排除在編譯出來的 `.mo` 之外，所以在有人確認
  這一對之前，應用程式渲染的是原文訊息——這和任何被改寫過的訊息所經歷的
  [降級方式一樣](workflow.md#the-cycle-after-the-first-translation)。
- **它們還是 fuzzy 的期間，CI 維持綠燈。** 佔位符檢查器會跳過 fuzzy 條目，和
  `msgfmt --check-format` 的做法完全相同，因為一筆根本到不了執行階段的條目不該弄垮
  建置。譯者一清掉那個旗標，這筆條目就會像其他條目一樣受檢——所以一則被確認的翻譯裡
  還留著 `%(name)s`，會正好在它即將開始渲染的那一刻被抓出來。
- **舊的 `python-format` 旗標會一起被帶過來**，應該和 `fuzzy` 旗標一併刪掉，否則
  `msgfmt --check-format` 會繼續拿 printf 規則去套一則 brace-format 訊息。

對於具名的 printf 佔位符，這項編輯是機械性的——`%(name)s` 變成 `{name}`，其餘一動
不動——所以一份大目錄只需要一次腳本化的掃過，再加上譯者複核，而不是重新翻譯。位置式
的 `%s` 就不是機械性的：它沒有名稱可以帶過來，而替它取一個名字，正是這次變更的重點。

因此這趟遷移可以照審查所允許的節奏推進：一筆還沒轉換的 fuzzy 條目，是目錄裡一件看得
見的待辦工作，而不是一次壞掉的建置。

## 新舊呼叫可以共存 { #old-and-new-calls-coexist }

讀得懂 t-string 的那個擷取器同樣讀得懂一般的 gettext 呼叫，所以一份 mapping 就能涵蓋
一個遷移到一半的檔案：

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

兩則訊息都會落進同一份樣板，而只有 t-string 那則帶著那道會打開本函式庫額外檢查的
marker 註解：

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

它認得 `_()`、四個標準 gettext 名稱、`tr()` / `ntr()` 別名，以及延遲版的
`lazy_gettext()` / `lazy_pgettext()`。你自己的 helper 則必須
[在 mapping 裡指名](extraction.md#registering-your-own-function-names)。

在執行階段，這兩種寫法同樣彼此獨立：`gettext.translation()` 回傳一個 translations
物件，而 `_` 和本函式庫的進入點都從它讀取。

## 什麼東西不用動 { #what-does-not-move }

- **樣板語言。** Jinja2 的 `{% trans %}`、Django 的 template tag，以及它們各自的
  Babel 擷取器都照常運作，也繼續餵給同一批 PO 目錄。t-string 是 Python 語法，只作用在
  Python 原始碼上。
- **你的目錄檔。** 格式不變、不多出檔案、不需要轉換步驟。
- **你的翻譯平台。** `.po` 這個交換格式完全相同，而 t-string 訊息帶的
  `python-brace-format` 旗標，和 `.format()` 訊息帶的是同一個旗標——所以佔位符 QA
  照樣有效。
- **非 Python 的程式碼。** 同一專案裡的 JavaScript 或 C 目錄不受影響。

## 一份遷移檢查清單 { #a-migration-checklist }

1. 在會跑 `pybabel` 的地方裝上 `babel` extra，並把 `babel.cfg` 裡的 `python` mapping
   改成 `gettext_tstrings` 方法——之後一份 mapping 就涵蓋兩種寫法，而 `-k` 對一般呼叫
   依然有效。
2. 先改造 `.format()` 呼叫點。重新擷取、跑 `pybabel update`，並把目錄和程式碼一起
   提交；預期不會出現 fuzzy 條目。
3. 以你有辦法讓人審查得完的批次去改造 `%`-format 呼叫點，重寫被帶過來的佔位符，並
   清掉 `fuzzy` 與 `python-format` 旗標。
4. 修掉那項限制所拒絕的寫法：插值必須是單純的名稱，所以 `t"Hello {user.name}"` 要先
   改成一個區域變數。這是呼叫點的修改，不是目錄的修改。
5. 掃過一遍之後，就在擷取器 mapping 裡打開 `strict = true`，這樣一則擷取不出來的訊息
   會讓[建置失敗](extraction.md#lenient-locally-strict-in-ci)，而不是從樣板裡消失。
6. 加上[正式環境實務](workflow.md#what-ci-gates)裡的執行階段檢查：讓每一種出貨語言各
   有一則訊息通過一個 strict 的 `Translator` 渲染。

第 2 步和第 3 步都是再普通不過的 commit。這份清單裡沒有任何一項需要挑個大日子一次
切換。
