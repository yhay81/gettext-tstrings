---
description: "API lúc chạy: nên dùng điểm vào nào, gắn một catalog, ngôn ngữ theo từng request, chuỗi trì hoãn, giá trị theo locale, và cách một bản dịch hỏng được báo cáo."
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

## Nên dùng điểm vào nào? { #which-entry-point-should-i-use }

Gói này xuất ra vài cách để dịch một thông điệp, bởi các ứng dụng gắn ngôn ngữ
theo vài cách khác nhau. Hãy chọn theo cách chương trình của bạn quyết định nó
đang ở ngôn ngữ nào:

| Tình huống của bạn | Hãy dùng |
| --- | --- |
| Một ngôn ngữ cho cả tiến trình — một CLI, một ứng dụng desktop, một script | `Translator`, gọi dưới tên `_` |
| Một ngôn ngữ cho mỗi request hoặc mỗi tác vụ async — một ứng dụng web | `use_translations()` bao quanh phần việc, rồi `tr()` |
| Một thông điệp được định nghĩa lúc import — nhãn biểu mẫu, một enum, một hằng số | `lazy_gettext()` hoặc `lazy_pgettext()` |
| Một con số quyết định cách diễn đạt | `ngettext()` / `npgettext()`, ở bất cứ dạng nào bên trên |
| Kết xuất một pattern mà không dính dáng catalog nào | `compile_template()` |

Toàn bộ phần dưới đây là năm mục đó, theo đúng thứ tự ấy.

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
    name = request.user.display_name
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

!!! warning "Một luồng worker có kế thừa binding hay không là tuỳ bản dựng"

    Một `threading.Thread` trần, hay `ThreadPoolExecutor.submit`, khởi đầu
    hoặc từ một bản sao ngữ cảnh của phía gọi, hoặc từ một ngữ cảnh rỗng, và
    bên nào trong hai bên đó chính là `sys.flags.thread_inherit_context` —
    mặc định là đúng trên các bản dựng free-threaded, và sai ở mọi nơi khác.
    Vì thế cùng một đoạn mã sẽ kết xuất ngôn ngữ đã gắn trên 3.14t và catalog
    toàn cục của tiến trình trên 3.14. Hãy truyền ngữ cảnh sang thay vì phụ
    thuộc vào giá trị mặc định:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` đã làm sẵn điều này cho bạn.

## Giá trị theo locale { #locale-aware-values }

Thư viện này quyết định một giá trị xuất hiện *ở đâu* trong thông điệp đã
dịch. Nó không bản địa hóa chính giá trị ấy. `{amount:,.2f}` là một format spec
của Python với hành vi cố định — một dấu phẩy mỗi ba chữ số và một dấu chấm
trước phần thập phân — và nó sinh ra đúng những ký tự đó bất kể thông điệp
đang ở ngôn ngữ nào:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

Tiếng Đức viết con số ấy là `1.234,50`, tiếng Pháp `1 234,50`, còn tiếng Hindi
nhóm `1234567` thành `12,34,567` chứ không phải `1,234,567`. Số, tiền tệ, ngày,
giờ và đơn vị thuộc về [Babel][babel-numbers]. Hãy định dạng giá trị trước, rồi
mới đặt chuỗi đã hoàn chỉnh vào chỗ của nó:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

Với một thông điệp có đếm số, con số làm hai việc — nó chọn dạng số nhiều và
nó xuất hiện trong văn bản — nhưng chỉ việc thứ hai mới được bản địa hóa. Hãy
giữ con số thô cho việc chọn dạng và truyền chuỗi đã định dạng để hiển thị:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

Việc định dạng trước khi gọi cũng chính là thứ giữ cho một format spec nằm
ngoài catalog: cái người dịch nhìn thấy là một mẩu văn bản đã hoàn chỉnh, chứ
không phải một con số kèm chỉ dẫn cách kết xuất nó.

## Điều gì xảy ra khi một catalog bị sai { #what-happens-when-a-catalog-is-wrong }

Nếu các placeholder của một bản dịch không khớp với nguồn — một trường bị
thiếu, không xác định, hoặc bị định dạng lại đã lọt qua khâu kiểm tra, đến từ
một tệp MO sửa tay, một catalog của nhà cung cấp, hay một pipeline bỏ qua bộ
kiểm tra — thì hành vi mặc định là kết xuất thông điệp nguồn thay vì ném ngoại
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

Những thông điệp này được viết cho người có thể hành động dựa trên chúng, mà
với một vấn đề của catalog thì đó thường là người dịch hơn là lập trình viên —
nên ở những chỗ một placeholder trông như có mặt nhưng thực ra không, thông
điệp sẽ giải thích vì sao thay vì chỉ nhắc lại rằng nó bị thiếu. Dấu ngoặc
nhọn toàn độ rộng, một `{{name}}` bị nhân đôi, một dấu cách không ngắt vô
hình, một chữ cái Kirin lọt giữa các chữ Latinh: mỗi trường hợp có cách diễn
đạt riêng, được liệt kê kèm ví dụ ở
[Dành cho người dịch](translators.md#reading-a-failure-message). Trang đó được
viết để đưa thẳng cho người đang sửa tệp `.po`.

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
