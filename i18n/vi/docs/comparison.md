---
description: "Cùng một thông điệp cần dịch được viết bằng %-format, .format(), chuỗi $ của flufl.i18n và t-string, kèm cách mỗi kiểu gắn giá trị và xử lý một catalog bị hỏng."
---

# Vì sao chọn t-string

Bốn cách đưa một giá trị vào thông điệp cần dịch, được so sánh trên cùng một
câu. Phiên bản tóm tắt:

- Với **%-format**, người dịch xóa một chữ cái là thành sự cố sập trong
  production.
- Với **str.format**, một bản dịch có thể đọc thuộc tính từ các đối tượng mà
  mã của bạn truyền vào — kể cả bí mật.
- Với **chuỗi $** (flufl.i18n), giá trị được lấy ngầm từ các biến của hàm
  gọi, và placeholder dạng chấm còn với tới được cả thuộc tính.
- Với **t-string**, việc định dạng ở lại trong mã của bạn, bản dịch được kiểm
  tra lúc chạy, và một catalog hỏng sẽ quay về văn bản nguồn thay vì gây sập.

Phần còn lại của trang này là bằng chứng, lần lượt từng phương pháp một.

!!! note "Ba bên chạm vào mỗi thông điệp được dịch"

    **Catalog** là tệp chứa các bản dịch — ở dạng `.po` khi con người chỉnh
    sửa, được biên dịch thành `.mo` để ứng dụng nạp ([Hướng dẫn nhập
    môn](tutorial.md) đi qua cả hai). Ba bên chạm vào mỗi thông điệp: **nhà
    phát triển** viết chuỗi nguồn, **người dịch** chỉnh sửa catalog — thường
    trên một nền tảng bên ngoài, cách xa mọi phiên review mã — và **ứng
    dụng** kết xuất hai thứ đó cùng nhau lúc chạy. Mỗi kiểu định dạng dưới
    đây trả lời cùng một câu hỏi theo cách khác nhau: *catalog được quyền
    kiểm soát bao nhiêu phần của ngôn ngữ định dạng?* Trong các ví dụ, `_` là
    tên quy ước của hàm dịch, còn `tr` là hàm của thư viện này.

## Định dạng % { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Điều có thể hỏng: một chữ cái bị xóa trong bản dịch làm sập quá trình kết
xuất.

Chuỗi trong catalog mang cú pháp printf, bao gồm cả chữ cái kiểu ở cuối —
chữ `s` trong `%(name)s` — thứ dễ bị bỏ sót và dễ bị làm hỏng:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Một chỉnh sửa đúng một ký tự trong trình soạn PO trở thành một traceback
trong production. GNU `msgfmt --check-format` có bắt được lỗi này, nhưng chỉ
với các thông điệp được gắn cờ `python-format`, và chỉ khi catalog thực sự đi
qua msgfmt trên đường đến ứng dụng của bạn.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Nó bỏ được chữ cái kiểu ở cuối trong khi vẫn giữ placeholder có tên, tự do
sắp xếp lại. Điều có thể hỏng chuyển sang phía bên kia của cuộc trao đổi:
bản dịch giành được quyền lực trên các đối tượng của bạn.

`str.format` là một ngôn ngữ biểu thức thu nhỏ, và gọi nó trên một chuỗi
đồng nghĩa với trao cho chuỗi đó quyền sử dụng ngôn ngữ ấy:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Giờ hãy thay những chuỗi literal đó bằng bất cứ thứ gì `_()` trả về. Nếu một
bản dịch của `Hello {name}` quay lại dưới dạng `{conf.api_key}`, việc kết
xuất nó sẽ in ra khóa API của bạn — chính catalog, chứ không phải mã của
bạn, quyết định thứ gì bị đọc. Catalog không phải là mã, nhưng nó di chuyển
như dữ liệu: ra một nền tảng dịch thuật, qua nhiều bàn tay, quay về dưới
dạng `.po`, được biên dịch thành `.mo`, đôi khi còn được vendor từ hoàn toàn
bên ngoài dự án của bạn. `.format()` trao cho mọi chặng của hành trình đó
quyền truy cập thuộc tính trên các đối tượng bạn truyền vào.

## Chuỗi `$` và flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

[`string.Template`][stdlib-template] của thư viện chuẩn cung cấp ngôn ngữ
nội suy `$name`, nhưng bản thân nó không phải là một API dịch thuật.
[`flufl.i18n`][flufl-i18n] kết hợp kiểu đó với tra cứu catalog gettext. Hãy
để ý rằng giá trị không bao giờ được truyền vào: flufl.i18n dựng không gian
tên thay thế từ globals và locals của bên gọi — bất kỳ biến nào tồn tại tại
điểm gọi đều sẵn dùng cho thông điệp. Một ánh xạ `extras` tùy chọn có độ ưu
tiên cao hơn cả hai. Cú pháp hướng tới người dịch của nó không có chữ cái
kiểu ở cuối hay chỉ định định dạng, và các placeholder vẫn tự do sắp xếp
lại.

Một phép thay thế không khả dụng sẽ không ném ngoại lệ. Với `name = "Ada"`
và không có `nombre` nào trong không gian tên của bên gọi, một bản dịch
`Hello $nombre` trong catalog được kết xuất thành `Hello $nombre`:
placeholder chưa được phân giải vẫn hiển thị nguyên. [Hành vi được ghi trong
tài liệu][documented behavior] đó giữ lại phần còn lại của thông điệp đã
dịch thay vì làm hỏng lời gọi. Các ngoại lệ ném ra trong lúc phân giải một
thuộc tính hoặc chuyển đổi một giá trị vẫn có thể lan truyền.

`flufl.i18n` mạnh hơn một `string.Template` trần theo một cách đáng nói ở
đây. [Template tùy chỉnh][custom Template] của nó chấp nhận placeholder dạng
chấm như `$settings.api_key`, và [bộ dịch][translator] của nó phân giải các
đường dẫn đó dựa trên giá trị của bên gọi. Một placeholder trong bản dịch có
thể gọi tên bất kỳ biến cục bộ hay toàn cục nào sẵn có của bên gọi và, với
cú pháp chấm, duyệt qua các thuộc tính của biến đó. Điều đó tiện lợi khi một
thông điệp cần một thuộc tính, nhưng đồng thời cũng biến frame của bên gọi
thành một phần trong không gian tên thay thế của catalog. Phần so sánh dưới
đây mô tả `flufl.i18n` 6.0.0, không phải mọi cách dùng có thể của
`string.Template`.

## t-string { #t-strings }

```python
tr(t"Hello {name}")
```

Catalog vẫn thấy `Hello {name}` và vẫn là một catalog PO/MO thông thường.
Khác biệt nằm ở chỗ một bản dịch *được phép nói gì*, và ai kiểm tra điều đó.

Thư viện này xác thực mọi bản dịch so với các placeholder của thông điệp
nguồn trước khi kết xuất, và nó chỉ chấp nhận tên trần, không gì khác. Đối
chiếu với `t"Hello {name}"`:

| Bản dịch chứa | bị từ chối với |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Bị từ chối không có nghĩa là sập: theo mặc định, thư viện ghi một cảnh báo
và kết xuất văn bản nguồn, nên một catalog hỏng không bao giờ kéo sập ứng
dụng — [chính hợp đồng mà bản thân gettext vẫn
giữ](guide.md#what-happens-when-a-catalog-is-wrong).

Việc định dạng ở nguyên nơi nó được viết ra, trong mã:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` không bao giờ tới được catalog, nên không bản dịch nào thay đổi được
nó, và không người dịch nào phải nhìn thấy nó.

Một khác biệt nữa là công cụ: t-string là cú pháp mới, nên việc trích xuất
chúng vào một tệp `.pot` hiện cần một bộ trích xuất hiểu t-string, chẳng hạn
bộ mà gói này [cung cấp cho Babel](extraction.md).

## So sánh cạnh nhau { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Placeholder có tên không? | có | có | có | có |
| Người dịch có thể sắp xếp lại placeholder không? | có | có | có | có |
| Giá trị đến từ đâu? | một ánh xạ tường minh | các đối số tường minh | biến cục bộ và toàn cục của bên gọi, cộng thêm `extras` tùy chọn | các giá trị được bắt giữ bên trong t-string |
| Catalog có thể thay đổi cách định dạng một giá trị không? | có | có | không | không |
| Catalog có thể với vào đối tượng (truy cập thuộc tính) không? | không | có | có, với tên dạng chấm | không |
| Một bản dịch *bỏ rơi* một placeholder — cái gì được kết xuất? | giá trị lặng lẽ biến mất | giá trị lặng lẽ biến mất | giá trị lặng lẽ biến mất | văn bản nguồn, kèm một cảnh báo ([theo mặc định](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Một bản dịch *thêm* một placeholder lạ — cái gì được kết xuất? | một ngoại lệ | một ngoại lệ | placeholder vẫn hiển thị dưới dạng văn bản | văn bản nguồn, kèm một cảnh báo ([theo mặc định](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Placeholder có được kiểm tra lúc kết xuất không? | không | không | không | có (xem bên dưới) |
| Babel suy ra cờ PO nào, để các công cụ hiện có xác thực? | `python-format` | `python-brace-format` | không có | `python-brace-format` |
| Dùng catalog PO/MO thông thường? | có | có | có | có |
| Cần bộ trích xuất nguồn tùy chỉnh? | không | không | không | có, hiện tại |

Về bước kiểm tra lúc kết xuất: thông điệp số ít được kiểm tra khớp
placeholder một cách chính xác. Thông điệp số nhiều cũng được kiểm tra, theo
[quy tắc hợp/giao](spec.md) cho phép các dạng số nhiều của ngôn ngữ đích
khác với ngôn ngữ nguồn; bước kiểm tra chặt hơn theo từng dạng chạy khi
catalog được biên dịch ([Trích xuất](extraction.md)).

Hàng về cờ định dạng nói về việc xác thực có hiểu placeholder, không phải về
tính tương thích của catalog. "Không có" nghĩa là các công cụ gettext chuẩn
vẫn đọc và biên dịch được thông điệp, nhưng `msgfmt --check-format` không có
ngữ pháp placeholder `$` nào để áp dụng.

## Cái giá phải trả { #what-it-costs }

Một f-string hoàn toàn không thể dùng theo cách này — đến lúc bất kỳ thư
viện nào nhìn thấy nó thì nó đã là một chuỗi hoàn chỉnh, nên dịch nó đồng
nghĩa với dịch một mảnh rời. t-string ([PEP 750]) giữ phần văn bản tĩnh và
các giá trị tách rời nhau trong khi vẫn giữ cú pháp giống f-string và cách
gắn giá trị tường minh. Chuỗi `$` vốn đã cung cấp một lựa chọn gọn gàng với
mô hình gắn giá trị và mô hình lỗi khác. `flufl.i18n` là một gói trưởng
thành chạy trên Python 3.10 trở lên; `gettext-tstrings` hiện đang ở giai
đoạn alpha, và vì t-string là cú pháp mới nên nó yêu cầu Python 3.14 trở
lên.

Cái giá còn lại là chính sự ràng buộc: một phép nội suy phải là một tên
trần.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Đó là một ràng buộc thực sự. Cùng với việc gắn giá trị ở phía nguồn và kiểm
tra placeholder lúc chạy, nó ngăn các chuỗi trong catalog thực thi biểu thức
và giữ cho tên placeholder luôn có ý nghĩa.

Python đã đi đến ngã rẽ này như thế nào — hai bản PEP cách nhau mười năm, và
cuộc thảo luận về thư viện chuẩn khép lại mà không có câu trả lời — được kể
kèm nguồn dẫn tại [Bối cảnh](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
