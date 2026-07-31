---
description: "Dịch trọn vẹn thông điệp t-string qua gettext và Babel, với giá trị và phần định dạng được giữ ngoài catalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Dịch trọn cả thông điệp<br>bằng t-string của Python

`gettext-tstrings` nối t-string của Python 3.14+ với các catalog gettext tiêu
chuẩn và bộ công cụ Babel. Giá trị và định dạng ở nguyên trong mã ứng dụng;
người dịch làm việc với những thông điệp trọn vẹn và các placeholder `{name}`
giản dị:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Catalog chứa `Hello {name}`. Một bản dịch có thể chuyển chỗ hoặc lặp lại
`{name}`. Nếu nó bỏ mất, đổi tên hay thêm định dạng cho placeholder, khâu kiểm
tra catalog sẽ báo lỗi. Nếu một mục sai vẫn lọt tới production, thư viện ghi một
cảnh báo và kết xuất thông điệp nguồn thay vì làm chương trình đổ vỡ.

[Bắt đầu hướng dẫn nhập môn năm phút :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[So sánh các lựa chọn khác](comparison.md){ .md-button }

Alpha · Python 3.14+ · catalog PO/MO tiêu chuẩn · không phụ thuộc bên thứ ba lúc chạy
{ .home-facts }

Trang này thực hành đúng điều nó viết: mọi phiên bản ngôn ngữ —
thanh điều hướng, nhãn, và báo cáo build có xử lý số nhiều — đều được kết xuất
từ các catalog PO bởi chính
[`gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Thư viện này có hợp với bạn không? { #is-this-for-you }

**Hợp ngay hôm nay khi** ứng dụng của bạn chạy trên Python 3.14 trở lên; bạn đã
dùng gettext và Babel, hoặc muốn áp dụng quy trình PO/MO của chúng; và bạn muốn
cú pháp t-string với các placeholder có tên được kiểm tra trước khi kết xuất.

**Chưa hợp khi** bạn cần Python 3.13 hoặc cũ hơn; bạn đòi hỏi một API Python ổn
định — đây là bản alpha, và [đặc tả](spec.md) mới là phần đã ổn định của nó;
hoặc gần như toàn bộ văn bản cần dịch của bạn nằm trong một ngôn ngữ template
chứ không phải trong mã nguồn Python.

Đã có sẵn catalog? Chúng vẫn chạy tốt. `_("Hello {name}").format(name=name)` và
`tr(t"Hello {name}")` sinh ra cùng một msgid, nên các bản dịch hiện có sống sót
qua lần chuyển đổi — [Chuyển đổi](migration.md) đi hết cả chặng đường ấy.

## Catalog được phép nói gì { #what-the-catalog-may-say }

**Một bản dịch không thể thay đổi cấu trúc của thông điệp mà nó dịch.** Đó là
toàn bộ lời hứa, và mọi phần còn lại của trang này đều theo sau nó. Một bản dịch
có thể đảo thứ tự hoặc lặp lại `{name}`, và có thể viết lại mọi từ khác quanh
nó. Nó không được phép bỏ mất placeholder, bịa ra một cái mới, thò qua nó để với
vào đối tượng của bạn, hay gắn định dạng của riêng mình.

Thư viện kiểm tra điều đó ở đầu vào — khi catalog được biên dịch — và kiểm tra
lại lúc kết xuất, và đó chính là khác biệt giữa một sai sót được tìm thấy trong
lúc rà soát và một sai sót được người dùng tìm thấy.

!!! note "Mới biết đến gettext? Toàn bộ quy trình trong bốn câu"

    **gettext** là cách chuẩn để phần mềm được dịch, trong Python và xa hơn
    thế nữa. Mã của bạn đánh dấu các chuỗi cần dịch; một *trình trích xuất*
    thu thập chúng vào một tệp mẫu (`.pot`); người dịch — thường không phải
    lập trình viên — điền vào một tệp catalog (`.po`) cho mỗi ngôn ngữ, rồi
    tệp đó được biên dịch thành tệp nhị phân `.mo` mà ứng dụng của bạn nạp
    lúc chạy. Tên quy ước của hàm dịch là `_`, nên `_(t"Hello {name}")`
    đọc như "dịch câu này". **[Hướng dẫn nhập môn](tutorial.md)** đi hết
    con đường — đánh dấu, trích xuất, dịch, biên dịch, chạy — trong khoảng
    năm phút.

## Vấn đề nó giải quyết { #the-problem-it-solves }

Một f-string đã bị nội suy trước khi bất kỳ thư viện nào nhìn thấy nó —
`f"Hello {name}"` đã trở thành `"Hello Ada"`, và việc dịch từng mảnh văn bản
quanh một giá trị sẽ phá vỡ ngữ pháp của hầu hết các ngôn ngữ. Một t-string
([PEP 750]) giữ tách bạch phần văn bản tĩnh, các giá trị đã được tính, các
biểu thức nguồn, các phép chuyển đổi và các format spec — đúng là cách phân
tách mà một catalog thông điệp cần.
[Điều đó thay đổi những gì](comparison.md), so với `%(name)s`, `.format()` và
chuỗi `$`.

Tuy nhiên, không có gì trong gettext hay Babel quy định một t-string trở
thành thông điệp như thế nào. Thư viện này đưa ra lựa chọn đó, ghi nó thành
một [đặc tả có phiên bản](spec.md), và kèm theo [bộ kiểm thử tuân
thủ](spec.md#conformance) để kiểm chứng.

## Các nguyên tắc thiết kế { #the-design-rules }

- Dịch thông điệp trọn vẹn, không bao giờ dịch mảnh câu.
- Chỉ chấp nhận tên biến đơn giản như `{name}`.
- Giữ `!r` và `:.2f` dưới quyền kiểm soát của ứng dụng, ngoài catalog.
- Cho phép người dịch đảo thứ tự và lặp lại các placeholder đã biết, đồng thời
  ngăn họ với tới thuộc tính hay thêm định dạng.
- Tái sử dụng các tệp POT, PO, MO thông thường, cùng những công cụ vốn đã
  đọc được chúng.

Và đây là danh sách tương ứng của những gì nó cố tình không đụng tới: nó không
bản địa hóa số, tiền tệ hay ngày tháng — [hãy định dạng chúng
trước](guide.md#locale-aware-values), bằng Babel; nó không escape kết quả kết
xuất cho HTML, shell hay terminal; và nó không thể phán xét một bản dịch có
*đúng* hay không, chỉ biết các placeholder của bản dịch ấy còn nguyên vẹn hay
không.

## Cài đặt { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 trở lên. **Phần kết xuất không có phụ thuộc nào** — nó chỉ dùng
`gettext` của thư viện chuẩn và không gì khác.

Trích xuất và kiểm tra catalog chạy qua [Babel], nên hãy cài extra đó ở nơi
`pybabel` chạy, thường là môi trường phát triển hoặc CI chứ không phải image
production:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Đi tiếp đến đâu { #where-to-go-next }

**Bắt đầu ở đây** — không đòi hỏi kinh nghiệm gettext:

<div class="grid cards" markdown>

- **[Hướng dẫn nhập môn](tutorial.md)** — từ một thư mục trống đến một bản dịch
  tiếng Nhật chạy được trong năm bước, mọi lệnh đều kèm kết quả thật.
- **[Vì sao chọn t-string](comparison.md)** — cùng một thông điệp viết theo
  bốn cách, và những gì `%(name)s`, `.format()` và chuỗi `$` mỗi loại trao
  cho catalog.

</div>

**Bắt tay vào dùng** — các tài liệu tham chiếu khi làm việc:

<div class="grid cards" markdown>

- **[Cẩm nang](guide.md)** — API lúc chạy: chọn điểm vào nào, số nhiều, ngôn
  ngữ theo từng request, chuỗi trì hoãn, và điều gì xảy ra khi một catalog sai.
- **[Trích xuất](extraction.md)** — tài liệu tham chiếu `pybabel`: cấu hình,
  tên hàm tùy biến, và cách các công cụ sẵn có kiểm tra những catalog này
  miễn phí.
- **[Vận hành thực tế](workflow.md)** — vòng lặp như một đội ngũ vận hành
  nó: chu kỳ cập nhật, các mục fuzzy, cổng chặn CI, nền tảng dịch thuật, và
  chuyện đưa bản dịch lên sản phẩm.
- **[Chuyển đổi](migration.md)** — áp dụng thư viện này vào một dự án đã có sẵn
  catalog, mỗi lần một điểm gọi.
- **[Dành cho người dịch](translators.md)** — một trang duy nhất để đưa cho ai
  đó sẽ sửa các tệp `.po`.

</div>

**Hiểu nó** — từ lịch sử đến hiện thực:

<div class="grid cards" markdown>

- **[Bối cảnh](background.md)** — vì sao thư viện này tồn tại: ba mươi năm
  gettext, hai PEP, và cuộc thảo luận về thư viện chuẩn khép lại mà không có
  câu trả lời.
- **[Cạm bẫy](pitfalls.md)** — việc dịch trang này ra ba mươi lăm ngôn ngữ đã
  thực sự làm hỏng những gì, và công cụ bắt được phân nửa nào.
- **[Cách hoạt động](internals.md)** — từ đối tượng template của PEP 750 đến
  chuỗi được kết xuất, và các cache khiến việc kiểm tra trở nên rẻ.

</div>

**Tra cứu** — các bản hợp đồng:

<div class="grid cards" markdown>

- **[API](api.md)** — mọi thứ gói này xuất ra, trên một trang.
- **[Đặc tả](spec.md)** — quy ước t-string ↔ msgid như một hợp đồng ổn định,
  có phiên bản, kèm bộ kiểm thử tuân thủ máy đọc được.

</div>

## Trạng thái { #status }

| | |
| --- | --- |
| Phiên bản gói | 0.1.0a7 |
| Độ ổn định API | alpha — API Python vẫn có thể thay đổi |
| [Đặc tả](spec.md) | v1, kèm [bộ kiểm thử tuân thủ](spec.md#conformance) |
| Python | 3.14 trở lên; đã kiểm thử trên 3.14, 3.14t (free-threaded) và 3.15 |
| Babel | 2.18 trở lên, và chỉ ở nơi `pybabel` chạy |
| Phụ thuộc lúc chạy | không có — chỉ `gettext` của thư viện chuẩn |
| Định dạng catalog | POT, PO và MO thông thường |
| Thay đổi | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Một bản alpha. Hợp đồng được giữ nhỏ một cách có chủ đích và [đặc tả](spec.md)
là phần ổn định của nó; API Python vẫn có thể thay đổi. Trước một bản phát
hành ổn định, dự án cần thêm fixture cho nhiều ngôn ngữ hơn, theo dõi hiệu
năng bền bỉ, đánh giá API từ những người dùng gettext và Babel nghiêm túc, và
kiểm thử tương thích trên mọi bản Python và Babel được hỗ trợ.

[Issue và pull request](https://github.com/yhay81/gettext-tstrings/issues)
đều được chào đón — bản alpha chính là lúc giao diện còn đáng để tranh luận.

## Tham gia cộng đồng { #join-the-community }

- Chọn một
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  cho một đóng góp có phạm vi gọn.
- Đặt câu hỏi sử dụng tại
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Mang quy trình gettext trong production và ý tưởng API đến
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Đọc
  [hướng dẫn đóng góp](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  trước khi mở pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
