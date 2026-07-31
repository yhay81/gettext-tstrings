---
description: "Cùng một thông điệp cần dịch được viết bằng %-format, .format(), chuỗi $ của flufl.i18n và t-string, so sánh trên lỗi của người dịch, quyền hạn của catalog và chi phí tích hợp."
---

# Vì sao chọn t-string

Bốn cách đưa một giá trị vào thông điệp cần dịch, được so sánh trên cùng một
thông điệp. Cả bốn đều đặt tên cho placeholder và cho phép người dịch sắp xếp
lại chúng; chúng khác nhau ở điều xảy ra khi một bản dịch bị sai, ở mức độ
catalog với tới được bao nhiêu phần chương trình của bạn, và ở cái giá phải
trả khi áp dụng.

Các bảng được đặt lên trước, để bạn tìm được hàng mình quan tâm rồi chỉ đọc
phần nằm sau nó.

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

## So sánh cạnh nhau { #side-by-side }

**Khi người dịch mắc lỗi.** Một catalog đi qua rất nhiều bàn tay, và phần lớn
những gì hỏng trong đó đều là vô tình:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Một bản dịch *bỏ rơi* một placeholder — cái gì được kết xuất? | giá trị lặng lẽ biến mất | giá trị lặng lẽ biến mất | giá trị lặng lẽ biến mất | thông điệp nguồn, kèm một cảnh báo ([theo mặc định](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Một bản dịch *thêm* một placeholder lạ — cái gì được kết xuất? | một ngoại lệ | một ngoại lệ | placeholder vẫn hiển thị dưới dạng văn bản | thông điệp nguồn, kèm một cảnh báo ([theo mặc định](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Một bản dịch *đổi định dạng* một placeholder — cái gì được kết xuất? | thứ mà catalog yêu cầu, hoặc một ngoại lệ nếu chữ cái kiểu không còn hợp với giá trị | thứ mà catalog yêu cầu | không diễn đạt được trong chuỗi `$` | thông điệp nguồn, kèm một cảnh báo |
| Placeholder có được kiểm tra lúc kết xuất không? | không | không | không | có (xem bên dưới) |

**Catalog có quyền hạn gì.** Một bản dịch là dữ liệu đến từ bên ngoài kho mã
của bạn, và mỗi kiểu trao cho nó một mức quyền lực khác nhau:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Giá trị đến từ đâu? | một ánh xạ tường minh | các đối số tường minh | biến cục bộ và toàn cục của bên gọi, cộng thêm `extras` tùy chọn | các giá trị được bắt giữ bên trong t-string |
| Catalog có thể thay đổi cách định dạng một giá trị không? | có | có | không | không |
| Catalog có thể với vào đối tượng (truy cập thuộc tính) không? | không | có | có, với tên dạng chấm | không |
| "Ngôn ngữ hiện tại" nằm ở đâu? | ở bất cứ đâu ứng dụng đặt nó | ở bất cứ đâu ứng dụng đặt nó | một ngăn xếp các mã ngôn ngữ trên đối tượng ứng dụng dùng chung | một `ContextVar`, theo từng task hoặc request |

**Cái giá của việc tích hợp.** Mọi thứ ở trên đều miễn phí nếu công cụ vừa
vặn; đây là chỗ có thể không vừa:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Python tối thiểu | bất kỳ | bất kỳ | 3.10 | **3.14** |
| Độ trưởng thành | thư viện chuẩn | thư viện chuẩn | bản phát hành ổn định | **alpha** |
| Dùng catalog PO/MO thông thường? | có | có | có | có |
| Cần bộ trích xuất nguồn tùy chỉnh? | không | không | không | có, hiện tại |
| Babel suy ra cờ PO nào, để các công cụ hiện có xác thực? | `python-format` | `python-brace-format` | không có | `python-brace-format` |

Về bước kiểm tra lúc kết xuất: thông điệp số ít được kiểm tra khớp
placeholder một cách chính xác. Thông điệp số nhiều cũng được kiểm tra, theo
[quy tắc hợp/giao](spec.md) cho phép các dạng số nhiều của ngôn ngữ đích
khác với ngôn ngữ nguồn; bước kiểm tra chặt hơn theo từng dạng chạy khi
catalog được biên dịch ([Trích xuất](extraction.md)).

Hàng về cờ định dạng nói về việc xác thực có hiểu placeholder, không phải về
tính tương thích của catalog. "Không có" nghĩa là các công cụ gettext chuẩn
vẫn đọc và biên dịch được thông điệp, nhưng `msgfmt --check-format` không có
ngữ pháp placeholder `$` nào để áp dụng.

## Tương thích và độ trưởng thành { #compatibility-and-maturity }

Hai hàng đầu của bảng cuối cùng là những hàng quyết định việc áp dụng, nên
chúng đáng được nói thẳng ra thay vì nằm trong ô bảng.

`%`-format và `.format()` được dựng sẵn trong Python và không cần phụ thuộc
nào cả. [`flufl.i18n`][flufl-i18n] là một gói trưởng thành, đã phát hành và
đang được dùng trong production, chạy trên Python 3.10 trở lên.
`gettext-tstrings` đang ở giai đoạn **alpha** và yêu cầu **Python 3.14 trở
lên**, vì t-string là cú pháp mới trong 3.14 — không có bản back-port và cũng
không thể có. [Đặc tả](spec.md) của nó là phần ổn định; API Python có thể còn
thay đổi trước 1.0.

Thứ mà không cái nào trong số chúng bắt bạn trả giá là tính tương thích của
catalog. Cả bốn đều sinh ra các tệp POT/PO/MO thông thường mà mọi trình soạn
PO, mọi nền tảng dịch thuật và mọi công cụ GNU gettext đều đã đọc được, nên
lựa chọn dưới đây là đảo ngược được, theo cách mà việc đổi *định dạng*
catalog thì không. [Di chuyển](migration.md) nói về việc chuyển một dự án sẵn
có.

Các phần dưới đây trình bày chi tiết từng đánh đổi, lần lượt từng phương pháp
một.

## Định dạng % { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Điều có thể hỏng: một placeholder bị hỏng sẽ trở thành ngoại lệ lúc chạy, trừ
khi việc kiểm tra catalog bắt được nó trước.

Chuỗi trong catalog mang cú pháp printf, bao gồm cả chữ cái kiểu ở cuối —
chữ `s` trong `%(name)s` — thứ dễ bị bỏ sót và dễ bị làm hỏng:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Một chỉnh sửa đúng một ký tự trong trình soạn PO trở thành một ngoại lệ lúc
chạy, trừ khi bước xác thực catalog bắt được nó trước. GNU
`msgfmt --check-format` có bắt được lỗi này, nhưng chỉ với các thông điệp
được gắn cờ `python-format`, và chỉ khi catalog thực sự đi qua msgfmt trên
đường đến ứng dụng của bạn.

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
thành một phần trong không gian tên thay thế của catalog. Phần so sánh ở đây
mô tả `flufl.i18n` 6.0.0, không phải mọi cách dùng có thể của
`string.Template`.

Nó còn trả lời một câu hỏi mà hai kiểu định dạng kia phó mặc hoàn toàn cho
ứng dụng: ngôn ngữ *nào* đang là ngôn ngữ hiện tại, và đổi nó bằng cách nào.
Một [đối tượng ứng dụng][application object] giữ một ngăn xếp các ngôn ngữ,
`_.push(code)` và `_.pop()` dịch chuyển nó, `with _.using(code):` cho phép
lồng nhau, còn một [chiến lược][strategy] tìm catalog ứng với một mã ngôn
ngữ để ứng dụng không bao giờ phải tự tay xử lý các đối tượng catalog. Một
máy chủ phải sinh ra văn bản bằng nhiều hơn một ngôn ngữ trong cùng một đơn
vị công việc — một trang cho người đọc, một thông báo cho người có tài khoản
đặt ngôn ngữ khác — chính là trường hợp mà cơ chế này sinh ra để phục vụ.

Ngăn xếp ấy nằm trên chính đối tượng ứng dụng đó, thứ mà cả tiến trình cùng
dùng chung. Vì vậy hai request chồng lấn nhau sẽ dùng chung một ngăn xếp, và
những khối lệnh không lồng nhau chặt chẽ *về mặt thời gian* sẽ trao nhầm
ngôn ngữ cho nhau:

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

Thư viện này giữ nguyên khả năng đó — các binding vẫn lồng vào nhau và gỡ ra
theo đúng cách ấy — nhưng đặt nó trong một `ContextVar` thay vì một ngăn xếp
dùng chung, nên kiểu đan xen ở trên được phân giải theo từng task. Các cách
viết tương đương nằm ở
[Nhiều ngôn ngữ cùng lúc](guide.md#several-languages-at-once). Thứ mà nó
không cung cấp là phép tra cứu từ mã ngôn ngữ ra catalog: bạn truyền vào một
đối tượng bản dịch, mà trong trường hợp thông thường chỉ là một lời gọi
`gettext.translation()`, và thư viện chuẩn lưu đệm catalog đã phân tích.

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
và kết xuất thông điệp nguồn, nên một catalog hỏng không bao giờ kéo sập ứng
dụng — [chính hợp đồng mà bản thân gettext vẫn
giữ](guide.md#what-happens-when-a-catalog-is-wrong).

Việc định dạng ở nguyên nơi nó được viết ra, trong mã:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` không bao giờ tới được catalog, nên không bản dịch nào thay đổi được
nó, và không người dịch nào phải nhìn thấy nó. Tuy vậy đó là một định dạng
*cố định*, không phải một định dạng bản địa hóa — việc chọn chữ số và dấu
phân cách theo từng ngôn ngữ là
[việc của Babel, trước lời gọi](guide.md#locale-aware-values).

Một khác biệt nữa là công cụ: t-string là cú pháp mới, nên việc trích xuất
chúng vào một tệp `.pot` hiện cần một bộ trích xuất hiểu t-string, chẳng hạn
bộ mà gói này [cung cấp cho Babel](extraction.md).

## Cái giá của ràng buộc { #the-cost-of-the-restriction }

Ngoài yêu cầu về phiên bản Python, cái giá của tất cả những điều trên là một
quy tắc duy nhất: một phép nội suy phải là một tên trần.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Đó là một ràng buộc thực sự, và nó chính là ràng buộc sinh ra những bảo đảm ở
trên. Cùng với việc gắn giá trị ở phía nguồn và kiểm tra placeholder lúc
chạy, nó ngăn các chuỗi trong catalog thực thi biểu thức và giữ cho tên
placeholder luôn có ý nghĩa với người đang dịch chúng.

Một f-string hoàn toàn không thể dùng theo cách này — đến lúc bất kỳ thư viện
nào nhìn thấy nó thì nó đã là một chuỗi hoàn chỉnh, nên dịch nó đồng nghĩa
với dịch một mảnh rời. t-string ([PEP 750]) giữ phần văn bản tĩnh và các giá
trị tách rời nhau trong khi vẫn giữ cú pháp giống f-string và cách gắn giá
trị tường minh.

Python đã đi đến đây như thế nào — hai bản PEP cách nhau mười năm, và
cuộc thảo luận về thư viện chuẩn khép lại mà không có câu trả lời — được kể
kèm nguồn dẫn tại [Bối cảnh](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
