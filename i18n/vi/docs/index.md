---
description: "Dịch trọn vẹn thông điệp t-string qua gettext và Babel, với phần định dạng được giữ ngoài catalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Viết câu một lần.<br>Dịch trọn cả câu.

Tích hợp gettext và Babel an toàn cho t-string của Python 3.14+ — giá trị
ở nguyên vị trí, còn catalog nhìn thấy toàn bộ thông điệp:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Bắt đầu hướng dẫn nhập môn :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Vì sao chọn t-string](comparison.md){ .md-button }

Trang này thực hành đúng điều nó viết: mọi phiên bản ngôn ngữ —
thanh điều hướng, nhãn, và báo cáo build có xử lý số nhiều — đều được kết xuất
từ các catalog PO bởi chính
[`gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Catalog nhận được trọn vẹn câu `Hello {name}`. Một bản dịch có thể đảo thứ tự
hoặc lặp lại `{name}`; nó không được phép bỏ mất, tự bịa thêm, hay gắn định
dạng của riêng mình — thư viện này kiểm tra điều đó, và một catalog hỏng sẽ
quay về văn bản nguồn thay vì làm chương trình đổ vỡ.

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

## Lựa chọn nó đưa ra { #the-choice-it-makes }

- Dịch thông điệp trọn vẹn, không bao giờ dịch mảnh câu.
- Chỉ chấp nhận tên biến đơn giản như `{name}`.
- Giữ `!r` và `:.2f` dưới quyền kiểm soát của ứng dụng, ngoài catalog.
- Cho phép người dịch đảo thứ tự và lặp lại các placeholder đã biết — nhưng
  không được gọi thuộc tính, và không được thêm hành vi định dạng.
- Tái sử dụng các tệp POT, PO, MO thông thường, cùng những công cụ vốn đã
  đọc được chúng.

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

Ba kiểu độc giả đến trang này: người đang dịch chương trình đầu tiên của
mình, người đang nối phần dịch vào một dự án thực, và người muốn biết chính
xác vì sao bộ máy lại có hình hài như vậy. Mỗi người có một lộ trình.

**Học nó** — không đòi hỏi kinh nghiệm gettext:

<div class="grid cards" markdown>

- **[Hướng dẫn nhập môn](tutorial.md)** — bắt đầu tại đây: từ một thư mục
  trống đến một bản dịch tiếng Nhật chạy được trong năm bước, mọi lệnh đều
  kèm kết quả thật.
- **[Vì sao chọn t-string](comparison.md)** — cùng một thông điệp viết theo
  bốn cách, và những gì `%(name)s`, `.format()` và chuỗi `$` mỗi loại trao
  cho catalog.
- **[Bối cảnh](background.md)** — vì sao thư viện này tồn tại: ba mươi năm
  gettext, hai PEP, và cuộc thảo luận về thư viện chuẩn khép lại mà không có
  câu trả lời.

</div>

**Dùng nó nghiêm túc** — các tài liệu tham chiếu khi làm việc:

<div class="grid cards" markdown>

- **[Cẩm nang](guide.md)** — API lúc chạy: số nhiều, ngôn ngữ theo từng
  request, chuỗi trì hoãn, và điều gì xảy ra khi một catalog sai.
- **[Trích xuất](extraction.md)** — tài liệu tham chiếu `pybabel`: cấu hình,
  tên hàm tùy biến, và cách các công cụ sẵn có kiểm tra những catalog này
  miễn phí.
- **[Vận hành thực tế](workflow.md)** — vòng lặp như một đội ngũ vận hành
  nó: chu kỳ cập nhật, các mục fuzzy, cổng chặn CI, nền tảng dịch thuật, và
  ngôn ngữ theo từng request trong một ứng dụng web.
- **[API](api.md)** — mọi thứ gói này xuất ra, trên một trang.

</div>

**Hiểu nó** — từ nguyên tắc đến hiện thực:

<div class="grid cards" markdown>

- **[Cách hoạt động](internals.md)** — từ đối tượng template của PEP 750 đến
  chuỗi được kết xuất, và các cache khiến việc kiểm tra trở nên rẻ.
- **[Đặc tả](spec.md)** — quy ước t-string ↔ msgid như một hợp đồng ổn định,
  có phiên bản, kèm bộ kiểm thử tuân thủ máy đọc được.

</div>

## Trạng thái { #status }

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
