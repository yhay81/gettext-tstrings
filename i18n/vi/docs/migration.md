---
description: "Áp dụng t-string trong một dự án đã có sẵn catalog gettext: cái gì còn nguyên, cái gì trở thành fuzzy, và cách chuyển từng điểm gọi một."
---

# Di chuyển

Nếu dự án của bạn đã dùng gettext, những câu hỏi quyết định thư viện này có
áp dụng được hay không là những câu hỏi hẹp: nó có làm hỏng các catalog bạn
đang có không, nó có sống chung được với phần mã bạn chưa sẵn sàng đổi không,
và bao nhiêu phần của bước chuyển phải xảy ra cùng một lúc. Các câu trả lời,
ngắn nhất trước:

| Câu hỏi | Trả lời |
| --- | --- |
| Các tệp `.po` và `.mo` sẵn có còn dùng được không? | Có. Cùng tệp, cùng công cụ. |
| Lời gọi cũ và mới có sống chung trong một tệp được không? | Có, và một ánh xạ trích xuất bao được cả hai. |
| msgid có thay đổi không? | Không, nếu đến từ `.format()`. Có, nếu đến từ `%`-format. |
| Cả dự án có phải chuyển cùng lúc không? | Không. Một điểm gọi cũng là một thay đổi hợp lệ. |
| Còn Jinja, template Django, JavaScript thì sao? | Không đụng tới, vẫn cùng catalog. |

Phần còn lại của trang này là chi tiết đằng sau từng câu trả lời đó.

## Từ `.format()`: msgid không đổi { #from-format-the-msgid-does-not-change }

Đây là trường hợp mà việc di chuyển gần như không tốn gì. Một thông điệp
`str.format` và một thông điệp t-string sinh ra *cùng một* khóa catalog, vì
đằng nào khóa cũng là phần văn bản với `{name}` còn nguyên trong đó:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Nhờ vậy bản dịch sẵn có vẫn dính vào đó. Bắt đầu từ một catalog chứa

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

hãy đổi lời gọi, trích xuất lại, rồi cập nhật:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Mục quay lại chỉ khác ở hai dòng metadata và không gì khác — một chú thích
đánh dấu cho biết đây là thông điệp t-string, và một số dòng nguồn:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Không có cờ `fuzzy`, không phải dịch lại, ở bất kỳ ngôn ngữ nào. Thông điệp
được kết xuất ngay lập tức:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` sẽ báo các catalog là lỗi thời"

    Chú thích đánh dấu đó cùng với các số dòng đã dịch chuyển là đủ để
    `pybabel update --check` nói rằng một catalog cần được sinh lại, vì nó so
    sánh toàn bộ mục chứ không chỉ phần bản dịch. Hãy chạy `pybabel update`
    thật trong cùng commit với thay đổi mã, và commit các catalog kèm theo —
    chính thói quen mà [cổng chặn CI](workflow.md#what-ci-gates) vốn đã yêu
    cầu.

## Từ `%`-format: msgid đổi, nên các bản dịch trở thành fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Cú pháp printf nằm *bên trong* thông điệp, nên thay nó đi là viết lại khóa
catalog. Không có cách nào né được điều đó, và đó là cái giá thành thật của
việc bỏ lại `%(name)s` phía sau:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` nhận ra thông điệp mới là họ hàng gần của thông điệp đã bị
gỡ và mang bản dịch cũ sang, kèm dấu fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Ba điều cần biết về trạng thái đó:

- **Không có gì hỏng lúc chạy.** Các mục fuzzy bị loại khỏi tệp `.mo` đã
  biên dịch, nên ứng dụng kết xuất thông điệp nguồn cho tới khi có con người
  xác nhận cặp đó —
  [chính kiểu suy giảm mềm](workflow.md#the-cycle-after-the-first-translation)
  mà mọi thông điệp được viết lại đều đi qua.
- **CI vẫn xanh trong lúc chúng còn fuzzy.** Bộ kiểm tra placeholder bỏ qua
  các mục fuzzy, đúng như `msgfmt --check-format` làm, vì một mục không
  thể tới được lúc chạy thì không nên làm hỏng bản dựng. Ngay khi người dịch
  gỡ cờ đó, mục đó được kiểm tra như mọi mục khác — nên một `%(name)s` còn
  sót trong một bản dịch đã xác nhận sẽ bị bắt ngay lúc ấy, đúng thời điểm mà
  nếu không thì nó sẽ bắt đầu được kết xuất.
- **Cờ `python-format` cũ đi theo cùng** và nên được xóa cùng với cờ `fuzzy`,
  nếu không `msgfmt --check-format` sẽ tiếp tục áp các quy tắc printf lên một
  thông điệp dạng brace-format.

Với các placeholder printf có tên, việc chỉnh sửa là máy móc — `%(name)s`
thành `{name}` và không gì khác dịch chuyển — nên một catalog lớn là một lượt
chạy script rồi tới một vòng review của người dịch, chứ không phải một cuộc
dịch lại. `%s` theo vị trí thì không máy móc được: nó không có tên nào để
mang sang, và việc chọn một cái tên chính là mục đích của thay đổi này.

Vì vậy quá trình di chuyển có thể tiến với bất kỳ nhịp nào mà việc review cho
phép: một mục fuzzy chưa chuyển đổi là một phần việc nhìn thấy được trong
catalog, không phải một bản dựng hỏng.

## Lời gọi cũ và mới sống chung { #old-and-new-calls-coexist }

Bộ trích xuất đọc được t-string cũng đọc được các lời gọi gettext thông
thường, nên một ánh xạ bao được một tệp đang giữa chừng di chuyển:

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

Cả hai thông điệp đều rơi vào cùng một template, và chỉ thông điệp t-string
mang chú thích đánh dấu bật thêm phần kiểm tra bổ sung của thư viện này:

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

Nó nhận ra `_()`, bốn tên gettext chuẩn, các bí danh `tr()` / `ntr()`, cùng
các hàm hoãn `lazy_gettext()` / `lazy_pgettext()`. Một hàm phụ trợ của riêng
bạn thì phải được
[nêu tên trong ánh xạ](extraction.md#registering-your-own-function-names).

Lúc chạy, hai kiểu này độc lập ngang nhau: `gettext.translation()` trả về một
đối tượng bản dịch, và cả `_` lẫn các điểm vào của thư viện này đều đọc từ
đó.

## Những gì không phải chuyển { #what-does-not-move }

- **Các ngôn ngữ template.** `{% trans %}` của Jinja2, các thẻ template của
  Django cùng các bộ trích xuất Babel của chúng vẫn hoạt động y nguyên và vẫn
  nạp vào cùng các catalog PO. t-string là cú pháp Python; chúng chỉ áp dụng
  cho mã nguồn Python.
- **Các tệp catalog của bạn.** Không đổi định dạng, không thêm tệp mới, không
  có bước chuyển đổi nào.
- **Nền tảng dịch thuật của bạn.** Việc trao đổi qua `.po` là y hệt, và cờ
  `python-brace-format` mà một thông điệp t-string mang theo chính là cờ mà
  một thông điệp `.format()` vẫn mang — nên phần QA placeholder vẫn chạy như
  cũ.
- **Mã không phải Python.** Một catalog JavaScript hay C trong cùng dự án
  không bị ảnh hưởng.

## Một danh sách kiểm tra khi di chuyển { #a-migration-checklist }

1. Thêm extra `babel` ở nơi `pybabel` chạy, và đổi ánh xạ `python` trong
   `babel.cfg` sang phương thức `gettext_tstrings` — khi đó một ánh xạ bao
   được cả hai kiểu, và `-k` vẫn hoạt động cho các lời gọi thông thường.
2. Chuyển đổi các điểm gọi `.format()` trước. Trích xuất lại, chạy
   `pybabel update`, và commit các catalog kèm mã; sẽ không có mục fuzzy nào.
3. Chuyển đổi các điểm gọi `%`-format theo từng đợt mà bạn review được, viết
   lại các placeholder được mang sang và gỡ các cờ `fuzzy` cùng
   `python-format`.
4. Sửa những gì bị ràng buộc từ chối: một phép nội suy phải là một tên trần,
   nên `t"Hello {user.name}"` phải thành một biến cục bộ trước. Đây là một
   chỉnh sửa ở điểm gọi, không phải ở catalog.
5. Bật `strict = true` trong ánh xạ của bộ trích xuất một khi lượt quét đã
   xong, để một thông điệp không trích xuất được sẽ làm hỏng
   [bản dựng](extraction.md#lenient-locally-strict-in-ci) thay vì lặng lẽ
   biến mất khỏi template.
6. Thêm bước kiểm tra lúc chạy từ
   [Vận hành thực tế](workflow.md#what-ci-gates):
   kết xuất một thông điệp cho mỗi ngôn ngữ được phát hành qua một
   `Translator` ở chế độ strict.

Bước 2 và 3 là những commit bình thường. Không có mục nào trong danh sách này
cần một ngày "chuyển hết một lượt".
