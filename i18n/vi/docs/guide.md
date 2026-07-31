---
description: "API lúc chạy: gắn một catalog, ngôn ngữ theo từng request, chuỗi trì hoãn, và cách một bản dịch hỏng được báo cáo."
---

# Cẩm nang

Trang này là tài liệu tham chiếu lúc chạy: tất cả những gì *mã ứng dụng* của
bạn làm với thư viện này một khi các catalog đã tồn tại. Nếu bạn chưa từng
thấy trọn vòng lặp — đánh dấu, trích xuất, dịch, biên dịch, chạy — thì
[Hướng dẫn nhập môn](tutorial.md) sẽ dẫn bạn đi hết một lượt trong năm phút;
việc tạo và kiểm tra tính hợp lệ của catalog được trình bày trong
[Trích xuất](extraction.md), còn cách một đội ngũ giữ cho vòng lặp tiếp tục
quay — chu kỳ cập nhật, CI, nền tảng dịch thuật — nằm ở
[Vận hành thực tế](workflow.md).

## Gắn một catalog { #binding-a-catalog }

Hình thức được khuyến nghị phỏng theo cách dùng dựa trên lớp của gettext: gắn
một đối tượng bản dịch tiêu chuẩn một lần rồi dùng bộ xử lý có thể gọi được
như `_`.

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

Các hàm ở cấp module tuân theo tên gọi của thư viện chuẩn cùng quy ước gọi
chỉ-theo-vị-trí của nó:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` và `ntr` là bí danh chính xác của `gettext` và `ngettext`.

## Ngôn ngữ theo từng request { #per-request-language }

Một framework web chọn ngôn ngữ theo từng request. Hãy gắn bản dịch của
request vào ngữ cảnh hiện tại, và mọi lời gọi cấp module sẽ phân giải về đúng
ngôn ngữ đó, an toàn giữa các request chạy đồng thời:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` gắn mà không cần khối `with`, dành cho những
framework tự quản lý vòng đời request; `get_translations()` đọc ra binding
hiện tại. Một đối số `translations=` tường minh luôn thắng ngữ cảnh, và một
ngữ cảnh chưa được gắn sẽ quay về các hàm gettext được cài đặt toàn cục của
thư viện chuẩn. Các ví dụ hoàn chỉnh cho Flask và middleware ASGI nằm ở trang
[Vận hành thực tế](workflow.md#binding-a-language-at-runtime).

## Dịch trì hoãn { #deferred-translation }

Một t-string bắt giữ giá trị của nó ngay lập tức, điều này là sai đối với một
chuỗi được định nghĩa lúc import — nhãn của form, giá trị enum, hằng số cấp
module — vốn phải kết xuất bằng bất kỳ ngôn ngữ nào đang hoạt động tại thời
điểm nó *được dùng*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

Một `LazyString` kết xuất qua `str()`, `format()` và f-string, và so sánh
bằng với văn bản đã kết xuất của nó.

!!! note "Cố ý không thể băm"

    Văn bản của một `LazyString` phụ thuộc vào ngôn ngữ đang hoạt động, nên
    giá trị băm sẽ thay đổi khi chuyển ngôn ngữ và âm thầm làm hỏng bất kỳ
    set hay dict nào đang chứa nó. Hãy gọi `str()` trước nếu bạn cần một
    khóa.

`strict` được quyết định tại nơi thông điệp được viết ra, chứ không phải tại
nơi nó được kết xuất:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Một chuỗi trì hoãn được kết xuất tại bất cứ đâu nó thực sự được dùng — bên
trong một template, một form, một dòng log — và nơi đó hiếm khi biết được đây
là một lần chạy kiểm thử hay là môi trường sản xuất. Truyền `strict=True` ngay
tại chỗ định nghĩa chính là điều cho phép áp dụng cùng một lựa chọn
[ồn ào trong CI, khoan dung khi vận hành](#what-happens-when-a-catalog-is-wrong)
cho một chuỗi không được kết xuất tại nơi gọi nó.

Các dạng số nhiều phụ thuộc vào một số đếm lúc chạy, nên hãy kết xuất chúng
ngay bằng `ngettext` tại nơi đã biết số đếm.

## Nhiều ngôn ngữ cùng lúc { #several-languages-at-once }

Một request thường cần nhiều hơn một ngôn ngữ: một trang được kết xuất cho
người đọc đồng thời xếp hàng một thông báo gửi tới tài khoản đang đặt ngôn ngữ
khác, hoặc một bản tổng hợp trích lời mỗi người tham gia bằng đúng ngôn ngữ của
họ. Các binding lồng vào nhau, và khi rời khối bên trong thì binding bên ngoài
được khôi phục.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Trên cả một danh sách người nhận, các chuỗi trì hoãn gánh phần việc này: thông
điệp được viết một lần, lúc import, rồi kết xuất một lần cho mỗi ngôn ngữ.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Binding là một `ContextVar`, chứ không phải một ngăn xếp giữ trên một đối tượng
dùng chung, nên các request chồng lấn nhau không thể nhặt phải ngôn ngữ của
nhau — kể cả trường hợp chúng *rời* khối lệnh của mình theo đúng thứ tự đã bước
vào, vốn là kiểu đan xen mà một ngăn xếp đẩy-xuống làm sai. Nạp một catalog cho
mỗi ngôn ngữ là việc rẻ: `gettext.translation()` phân tích mỗi tệp `.mo` đúng
một lần rồi trao ra những bản sao dùng chung catalog đã phân tích.

!!! warning "Một luồng worker khởi đầu ở trạng thái chưa gắn"

    Một `threading.Thread` trần, hay `ThreadPoolExecutor.submit`, khởi đầu
    với một ngữ cảnh mới tinh và không kế thừa binding — lời gọi sẽ quay về
    catalog gettext toàn cục của tiến trình. Hãy mang ngữ cảnh sang một cách
    tường minh:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` đã làm sẵn điều này cho bạn.

## Điều gì xảy ra khi một catalog bị sai { #what-happens-when-a-catalog-is-wrong }

Nếu các placeholder của một bản dịch không khớp với nguồn — một trường bị
thiếu, không xác định, hoặc bị định dạng lại đã lọt qua khâu kiểm tra, đến từ
một tệp MO sửa tay, một catalog của nhà cung cấp, hay một pipeline bỏ qua bộ
kiểm tra — thì hành vi mặc định là tái tạo văn bản nguồn thay vì ném ngoại
lệ. Điều này phản chiếu đúng cam kết của chính gettext rằng một catalog hỏng
không bao giờ làm đổ vỡ ứng dụng.

Với `Hello {name}` được dịch thành `こんにちは {nombre}`, việc kết xuất vẫn
thành công và một cảnh báo được ghi vào logger `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Cảnh báo chỉ phát một lần cho mỗi thông điệp và pattern, chứ không phải mỗi
lần kết xuất, nên một mục catalog hỏng sẽ không làm ngập log.

Bạn có thể chủ động chọn chế độ báo lỗi lớn tiếng cho kiểm thử và CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Cùng phép tra cứu đó khi ấy sẽ ném ngoại lệ, mang đúng câu thông báo ấy nhưng
không còn nửa "using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Đọc một thông điệp lỗi { #reading-a-failure-message }

Những thông điệp này được viết cho người có thể hành động dựa trên chúng, mà
với một vấn đề của catalog thì đó thường là người dịch hơn là lập trình viên.
Chỉ báo rằng `{name}` bị thiếu là một ngõ cụt khi người đọc có thể thấy rõ
những ký tự ấy ngay trước mắt, vì vậy ở những chỗ một placeholder trông như
có mặt nhưng thực ra không, thông điệp sẽ nói rõ vì sao. Đối chiếu với nguồn
`Hello {name}`, mỗi trường hợp dưới đây được báo cáo dưới dòng
`translation does not match the source placeholders:`

| Bản dịch viết | Lý do được đưa ra |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Những ký tự không thể nhìn thấy được đối xử theo cách riêng. Một dấu cách
không ngắt bên trong cặp ngoặc nhọn là thứ mà một bộ gõ có thể sinh ra còn
không trình soạn thảo nào hiển thị, nên thông điệp in nó ra theo code point
thay vì gọi tên một ký tự mà người đọc không thể tìm thấy:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Một tên có các chữ cái pha trộn nhiều hệ chữ viết — trường hợp homoglyph, nơi
chữ `а` Kirin không thể phân biệt được với chữ Latinh — được hiển thị hai
lần, một lần ở dạng dễ đọc và một lần ở dạng thoát chuỗi, vốn là dạng duy
nhất phân biệt được hai chữ đó:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Cách khử nhập nhằng tương tự cũng áp dụng khi một tên viết hoàn toàn bằng chữ
Hy Lạp hay Kirin xung đột với một tên nguồn ASCII, kể cả trường hợp một chữ
cái `a` Latinh / `а` Kirin.

## Kết xuất một pattern không cần catalog { #rendering-a-pattern-without-a-catalog }

`compile_template` phơi bày cùng bộ máy đó ở một tầng thấp hơn: nó biến một
t-string thành msgid của nó cùng một tập giá trị đã gắn kèm, và kết xuất bất
kỳ pattern nào bạn đưa vào.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` kiểm tra tính hợp lệ theo đúng các quy tắc đó và **luôn ném ngoại
lệ** khi không khớp. Ở đây không có chế độ khoan dung: sự khoan dung tồn tại
để một phép tra cứu *catalog* có thể xuống cấp êm về văn bản nguồn, còn một
pattern do chính bạn truyền vào thì chẳng có gì để xuống cấp về.

## An toàn và phạm vi { #safety-and-scope }

Cách viết này hợp lệ:

```python
tr(t"Hello {name}")
```

Những cách viết này bị từ chối một cách có chủ đích:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Hãy tính trước một giá trị có ý nghĩa:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Hạn chế này tạo ra các khóa catalog ổn định, cho người dịch những cái tên hữu
ích, và giữ cho một chuỗi được dịch không biến thành một ngôn ngữ biểu thức.

Sự bảo đảm được giới hạn trong phạm vi *cấu trúc và định dạng*: một bản dịch
không bao giờ được thực thi, và không bao giờ có thể thêm truy cập thuộc
tính, lời gọi hàm, phép chuyển đổi hay format spec. Hai điều vẫn thuộc trách
nhiệm của bên gọi, hệt như với gettext của thư viện chuẩn — **escape** đầu ra
đã kết xuất cho đích đến của nó (HTML, shell, terminal), và **tính toàn vẹn
của catalog**, vì một catalog ác ý có thể lặp lại một placeholder để khuếch
đại kích thước đầu ra, điều vốn cố hữu ở mọi cơ chế i18n dựa trên
placeholder.
