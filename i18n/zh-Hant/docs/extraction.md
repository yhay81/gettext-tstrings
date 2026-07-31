---
description: "用 pybabel 擷取 t-string 訊息，以及 msgfmt 與內附的 Babel 檢查器如何驗證這些目錄。"
---

# 擷取

擷取是把你原始碼裡每一則被標記的訊息，收集成一份給譯者的 `.pot` 樣板的那個步驟——
也就是[教學](tutorial.md)循環中的第 3 步。本頁是這個步驟的參考：設定方式、自訂函式
名稱、CI 的 strict 模式，以及事後守護你目錄的那些檢查。

擷取需要 `babel` extra：

```console
python -m pip install "gettext-tstrings[babel]"
```

## 工作流程 { #the-workflow }

建立 `babel.cfg`：

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

接著使用一般的 Babel 指令：

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` 每種語言只跑一次；在那之後，`pybabel update` 會把每一份新的樣板併進既有的
目錄裡。那個週而復始的循環——以及其中的 `fuzzy` 條目對一次發行意味著什麼——在
[正式環境實務](workflow.md#the-cycle-after-the-first-translation)裡走過一遍。

`gettext_tstrings` 擷取器也會處理一般的 `_()`、`gettext()` 與 `ngettext()` 呼叫，
所以單一份 mapping 就能涵蓋混合的程式庫。它認得 `_()`、四個標準 gettext 名稱、
`tr()` / `ntr()` 別名，以及延遲版的 `lazy_gettext()` / `lazy_pgettext()`。

!!! warning "`-c` 不是可有可無的"

    `pybabel extract` 只有在你傳入 `-c "Translators:"` 時才會收集譯者註解，這一點
    與它對待一般 gettext 呼叫的方式完全相同。

## 註冊你自己的函式名稱 { #registering-your-own-function-names }

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

ini 檔給的是一個字串，TOML mapping 給的是一份列表，而在字串裡則以空白或逗號分隔
名稱。這四種寫法都有效。

可用的選項有 `tr_functions`、`ntr_functions`、`gettext_functions`、
`ngettext_functions`、`pgettext_functions` 與 `npgettext_functions`。

!!! danger "`-k` 碰不到 t-string"

    像 `mytr(t"…")` 這樣的自訂輔助函式，必須寫進上面其中一個選項裡。Babel 的
    `--keyword` 機制讀不了 t-string 字面值，所以 `pybabel extract -k mytr` 什麼也
    找不到、也什麼都不會說——那些訊息就這麼從 POT 裡缺席了。對於一併被擷取的一般
    gettext 呼叫，`-k` 依然有效。

    只支援標準的引數順序：訊息在前，`pgettext` 是上下文接訊息，`npgettext` 是
    上下文接單數再接複數。

## 預設就夠穩健 { #robust-by-default }

一個壞掉的檔案不會終結整次執行：

- 被擷取器拒絕的 t-string——屬性存取、運算式、錯誤的引數——會被回報為警告並略過。
- 剖析不了的檔案也以同樣方式略過。
- 只有 `tokenize` 拒絕而 `ast` 接受的檔案同樣如此，而 Babel 自己那一遍原本會在這裡
  中止。

在 mapping 選項裡設定 `strict = true`，就能把上述每一種情況都變成硬性失敗，而那正是
你在 CI 裡想要的。

## 你既有的工具鏈就能驗證這些目錄 { #your-existing-toolchain-validates-these-catalogs }

Babel 會為每一則擷取出來的訊息標上一個標準旗標，而正是那一行，啟動了你早已在跑的
那些工具裡的佔位符檢查：

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

把它翻成 `こんにちは {nombre}`，這個錯誤不需要任何設定就會被抓到：

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate 把同一項檢查記載為 [Python brace format][weblate-checks]，而商用平台也有
各自以同一個旗標為觸發條件的佔位符 QA。它們的行為由它們自己決定；下面那兩個工具，
才是這裡驗證過的。

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

在此之上，本套件還註冊了一個 Babel **檢查器**，所以 `pybabel compile` 會對每一則
帶有 `gettext-tstrings` 標記註解的訊息，套用規範裡的規則：

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

對複數訊息而言，指標會點名是哪一種形式，因為 Babel 回報的行號是 msgid 的行號，而
一個俄文區塊底下有三個 `msgstr`：

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` 還是會把 `.mo` 寫出來"

    上面那個錯誤有被回報，離開狀態碼是 `1`——而壞掉的目錄還是照樣被編譯出來。
    唯有那個離開狀態碼能阻止流水線把它送出去；[CI 把守什麼](workflow.md#what-ci-gates)
    展示了讓它能夠阻止的那個建置步驟。

這兩項檢查並不重複。內附的檢查器至少在兩個地方是比較嚴格的一方：

- 大括號全部都被跳脫掉的 msgid（`Config {{raw}} only`）永遠拿不到
  `python-brace-format` 旗標，所以根本沒有外部工具會驗證它。
- 複數形式是一個一個檢查的。`msgfmt --check-format` 讀上面那個完全相同的檔案會以
  `0` 結束；某個形式漏掉了它的兄弟形式都保留著的佔位符，在那邊會被接受，在這裡則
  會被拒絕。

`msgfmt` 只檢查它能剖析成 Python brace format 的佔位符名稱，所以採用 ASCII 名稱能讓
鏈條上的每個工具都仍然驗證得了這則訊息。至於本函式庫自己，任何
`str.isidentifier()` 的名稱它都接受。

## Template 與其他工具 { #templates-and-other-tools }

t-string 是 Python 語法，所以本函式庫涵蓋的是 Python 原始碼。Template 語言繼續用
它們自己的 i18n——Jinja2 的 `{% trans %}`、Django 的 template tag——以及 Babel 為
它們提供的擷取器。所有東西都匯進同一份 PO 目錄，所以單一套翻譯工作流程照樣涵蓋混合的
程式庫。

`pygettext` 今天還剖析不了 t-string，這就是擷取要走 Babel 的原因。這套約定被寫進了
[規範](spec.md)，好讓另一個擷取器、或未來的 `pygettext` 都能以它為目標。
