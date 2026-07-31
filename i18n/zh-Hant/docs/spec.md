---
description: "把 t-string 到 msgid 的約定寫成一份精簡、有版本的契約，並附上機器可讀的一致性測試套件。"
---

# 規範

不看本頁也能使用本函式庫——日常用法在[教學](tutorial.md)與[指南](guide.md)
裡都有。本頁是寫給工具作者的：本函式庫實作的這套約定被寫成一份精簡而穩定的
契約，讓另一套實作——擷取器、IDE、型別檢查器，或未來的 `pygettext`——都能
以它為目標並彼此互通。若想看到同樣這些規則連同背後的理由，以及參考實作如何
落實它們，請先讀[運作原理](internals.md)。

[閱讀 spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## 一個畫面看完的規則 { #the-rules-in-one-screen }

**msgid** 是依原始碼順序，把各段字面片段與每個插值各一個 `{name}` token 串接
起來的結果。字面的大括號會被跳脫（`{` 變成 `{{`）。名稱必須是單純的佔位符
名稱——`str.isidentifier()` 為真，且不是 Python 關鍵字。轉換與格式規格**不是**
msgid 的一部分，它們仍由應用程式掌控。

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *拒絕——不是單純的名稱* |

當一則**翻譯**只含有裸的 `{name}` 佔位符、每個必要名稱至少出現一次，且沒有
出現允許集合之外的名稱時，它就是有效的。調換順序與重複使用是刻意不加限制
的：這兩者在目標語言中都可能是文法上的必要。

至於複數，*允許*集合是兩個分支名稱的聯集，*必要*集合是它們的交集——因此
`t"One file"` 對上 `t"{n} files"`，會讓 `n` 對任一形式的譯者都可用，卻對哪一
形式都不強制，而目標語言的複數規則也就得以不同於來源語言。

**空的 msgid** 永遠不會被查詢，因為 gettext 把它保留給目錄的中繼資料標頭。

## 一致性 { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
是同一份文件的機器可讀版本：其中的案例把 t-string 的靜態結構對應到 msgid，
也把 msgid 加上目錄 pattern 對應到渲染後的字串或一次拒絕。

當一套實作能重現每一個案例，它就**符合 spec v1**。這些案例只點名規範所定義
的東西——導出的 msgid、被接受與被拒絕的 pattern、渲染輸出——而從不涉及錯誤
訊息或例外型別，因此以另一種語言寫成的實作也能原封不動地跑它們。

插值是以結構描述的，而不是寫成 Python 原始碼：

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

參考實作會把這套測試套件當成自身測試的一部分來執行，所以文字敘述與程式碼
不可能在無聲無息中各自漂移。

## 版本管理 { #versioning }

目前是 spec v1。若 msgid 推導或翻譯驗證出現不向後相容的變更，版本號就會遞增，
並在既有檔案旁附上新的 `conformance/vN.json`。至於既不改變導出的 msgid、也不
改變被接受的 pattern 的補充說明，則不會遞增版本。
