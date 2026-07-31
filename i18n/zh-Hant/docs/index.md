---
description: "透過 gettext 與 Babel 翻譯完整的 t-string 訊息，並把值與格式設定留在目錄之外。"
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# 翻譯完整的訊息，<br>而不是字串片段。

`gettext-tstrings` 把 Python 3.14+ 的 t-string 接上標準的 gettext 目錄與 Babel
工具。值與格式設定留在應用程式的程式碼裡；目錄拿到的是一則完整的訊息，其中只有
單純的 `{name}` 佔位符：

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[開始教學 :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[比較各種做法](comparison.md){ .md-button }

Alpha · Python 3.14+ · 一般的 PO/MO 目錄 · 執行階段零相依
{ .home-facts }

本站身體力行自己所記載的內容：每一個語言版本——導覽、標籤，以及能處理複數的
建置報告——都由
[`gettext-tstrings` 自己](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
從 PO 目錄渲染而成。
{ .home-hero-note }

</div>

## 它適合你嗎？ { #is-this-for-you }

**現在就適合**：你的應用程式跑在 Python 3.14 以上；你已經在用 gettext 與 Babel，
或想採用它們的 PO/MO 工作流程；而且你想要具名佔位符、並且在渲染之前就先被檢查過
的 t-string 語法。

**目前還不適合**：你需要 Python 3.13 或更舊的版本；你需要穩定的 Python
API——本專案還是 alpha，其中已經定案的部分是[規範](spec.md)；或者你幾乎所有可
翻譯的文字都寫在某種樣板語言裡，而不在 Python 原始碼中。

已經有目錄了？它們照樣能用。`_("Hello {name}").format(name=name)` 和
`tr(t"Hello {name}")` 產生同一個 msgid，因此既有的翻譯撐得過這次切換——
[遷移](migration.md)完整說明了整個過程。

## 目錄可以寫什麼 { #what-the-catalog-may-say }

目錄收到的是完整的訊息 `Hello {name}`。翻譯可以調換或重複 `{name}` 的位置，也可以
把它周圍的每一個字都改寫掉。但它不能把佔位符刪掉、憑空造一個新的、藉著它伸手去碰
你的物件，也不能自行加上格式設定。

這就是全部的承諾：**一份譯文改變不了它所翻譯的那則訊息的結構。** 本函式庫會在入口
檢查一次——也就是目錄編譯的時候——渲染時再檢查一次；萬一有壞掉的條目仍然進了正式
環境，它會記錄一則警告並渲染原始訊息，而不是讓程式當掉。

!!! note "第一次接觸 gettext？四句話講完整套流程"

    **gettext** 是軟體翻譯的標準做法，在 Python 內外都通用。你的程式碼標記出
    可翻譯的訊息；*擷取器*把它們收集到樣板檔（`.pot`）；譯者——通常不是
    程式設計師——為每種語言填寫一份目錄檔（`.po`），再編譯成二進位的 `.mo`，
    由應用程式在執行階段載入。翻譯函式的慣用名稱是 `_`，所以
    `_(t"Hello {name}")` 讀起來就是「把這則訊息翻譯出來」。**[教學](tutorial.md)**
    會用大約五分鐘走完整條路徑——標記、擷取、翻譯、編譯、執行。

## 它解決的問題 { #the-problem-it-solves }

f-string 在任何函式庫看到它之前就已經完成插值了——`f"Hello {name}"` 早就變成
`"Hello Ada"`，而把一個值前後的片段拆開來翻譯，會破壞大多數語言的文法。
t-string（[PEP 750]）則把靜態文字、求值後的值、原始運算式、轉換方式與格式規格
分開保留——這正好就是訊息目錄需要的切分方式。
和 `%(name)s`、`.format()` 與 `$`-string 相比，[這帶來了什麼改變](comparison.md)。

不過，gettext 和 Babel 都沒有規定 t-string 該如何變成一則訊息。本函式庫做出了
這個選擇，把它寫成[有版本的規範](spec.md)，並附上[一致性測試套件](spec.md#conformance)
供人驗證。

## 設計原則 { #the-design-rules }

- 永遠翻譯完整的訊息，不翻譯句子片段。
- 只接受 `{name}` 這類單純的變數名稱。
- 讓 `!r` 和 `:.2f` 留在應用程式手上，不進入目錄。
- 允許翻譯調換與重複已知的佔位符，同時擋住它存取屬性或加上格式化行為。
- 沿用一般的 POT、PO 與 MO 檔案，以及既有的相關工具。

與之對應的，是它刻意不碰的那份清單：它不在地化數字、貨幣或日期——請先
[用 Babel 把它們格式化好](guide.md#locale-aware-values)；它不會為了 HTML、shell
或終端機而跳脫渲染結果；它也判斷不了一份譯文是否*正確*，只能判斷其中的佔位符是否
完好。

## 安裝 { #install }

```console
python -m pip install gettext-tstrings
```

需要 Python 3.14 以上。**渲染沒有任何相依套件**——只用到標準函式庫的 `gettext`。

擷取與目錄驗證則透過 [Babel] 進行，因此請在會執行 `pybabel` 的地方安裝該
extra；那通常是開發或 CI 環境，而不是正式環境的映像檔：

```console
python -m pip install "gettext-tstrings[babel]"
```

## 接下來看什麼 { #where-to-go-next }

**從這裡開始**——不預設你有 gettext 經驗：

<div class="grid cards" markdown>

- **[教學](tutorial.md)** — 五個步驟，從一個空資料夾走到一份跑得起來的日文
  翻譯，每道指令都附上輸出。
- **[為什麼選擇 t-string](comparison.md)** — 同一則訊息的四種寫法，以及
  `%(name)s`、`.format()` 和 `$`-string 各自交給目錄什麼東西。

</div>

**實際採用**——日常查閱的參考：

<div class="grid cards" markdown>

- **[指南](guide.md)** — 執行階段 API：該用哪個進入點、複數、依請求切換語言、
  延遲字串，以及目錄出錯時會發生什麼事。
- **[擷取](extraction.md)** — `pybabel` 參考：設定方式、自訂函式名稱，以及既有
  工具如何免費幫你驗證這些目錄。
- **[正式環境實務](workflow.md)** — 團隊實際運作的循環：更新週期、fuzzy 條目、
  CI 關卡、翻譯平台，以及發行出貨。
- **[遷移](migration.md)** — 在一個已經有目錄的專案裡導入本函式庫，一個呼叫點
  一個呼叫點慢慢換。
- **[給譯者](translators.md)** — 可以直接交給編輯 `.po` 檔案那個人的一頁。

</div>

**深入理解**——從歷史到實作：

<div class="grid cards" markdown>

- **[專案背景](background.md)** — 本函式庫為何存在：三十年的 gettext、兩份 PEP，
  以及一場沒有結論就結束的標準函式庫討論。
- **[常見陷阱](pitfalls.md)** — 把本站翻譯成三十五種語言時實際弄壞了什麼，其中
  哪一半是工具攔得住的。
- **[運作原理](internals.md)** — 從 PEP 750 的 template 物件到渲染完成的字串，
  以及讓檢查成本低到可以忽略的那些快取。

</div>

**參考資料**——各項契約：

<div class="grid cards" markdown>

- **[API](api.md)** — 本套件匯出的一切，集中在同一頁。
- **[規範](spec.md)** — 把 t-string ↔ msgid 的約定寫成穩定、有版本的契約，並
  附上機器可讀的一致性測試套件。

</div>

## 專案狀態 { #status }

| | |
| --- | --- |
| 套件版本 | 0.1.0a7 |
| API 穩定性 | alpha——Python API 仍可能變動 |
| [規範](spec.md) | v1，附[一致性測試套件](spec.md#conformance) |
| Python | 3.14 以上；已在 3.14、3.14t（自由執行緒）與 3.15 上測試 |
| Babel | 2.18 以上，且僅在 `pybabel` 跑得動的地方需要 |
| 執行階段相依 | 無——只用標準函式庫的 `gettext` |
| 目錄格式 | 一般的 POT、PO 與 MO |
| 變更紀錄 | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

目前是 alpha。契約刻意做得很小，其中穩定的部分是[規範](spec.md)；Python API
還可能會變動。在正式釋出穩定版之前，還需要更廣的語言 fixture、持續的效能追蹤、
來自實際使用 gettext 與 Babel 的人的 API 審視，以及涵蓋所有受支援 Python 與
Babel 版本的相容性測試。

歡迎提出 [Issue 與 Pull Request](https://github.com/yhay81/gettext-tstrings/issues)——
alpha 階段正是最值得為介面設計爭論的時候。

## 加入社群 { #join-the-community }

- 挑一個範圍明確的
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  來貢獻。
- 使用上的問題請到
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a)
  發問。
- 歡迎把正式環境的 gettext 工作流程與 API 想法帶到
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas)。
- 開 Pull Request 之前，請先讀過
  [貢獻指南](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)。

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
