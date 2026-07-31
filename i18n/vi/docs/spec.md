---
description: "Quy ước từ t-string sang msgid như một hợp đồng nhỏ có phiên bản, kèm một bộ kiểm thử tuân thủ máy đọc được."
---

# Đặc tả

Bạn có thể dùng thư viện này mà không cần đọc trang này —
[Hướng dẫn nhập môn](tutorial.md) và [Cẩm nang](guide.md) đã bao quát việc sử
dụng thường ngày. Trang này dành cho các tác giả công cụ: quy ước mà thư viện
hiện thực được viết thành một hợp đồng nhỏ và ổn định, để một hiện thực
khác — một bộ trích xuất, một IDE, một trình kiểm tra kiểu, hay một
`pygettext` tương lai — có thể nhắm tới nó và tương tác được với nhau. Để
hiểu chính các quy tắc ấy cùng lý do của chúng, và cách hiện thực tham chiếu
thực thi chúng, hãy đọc [Cách hoạt động](internals.md) trước.

[Đọc đặc tả v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Các quy tắc trong một màn hình { #the-rules-in-one-screen }

**Một msgid** là kết quả nối, theo thứ tự trong mã nguồn, của các đoạn văn
bản literal và một token `{name}` cho mỗi phép nội suy. Ngoặc nhọn literal
được thoát chuỗi (`{` trở thành `{{`). Một tên phải là một tên placeholder
đơn giản — `str.isidentifier()` trả về true và nó không phải một từ khóa
Python. Phép chuyển đổi và format spec **không** thuộc về msgid; chúng nằm
dưới quyền kiểm soát của ứng dụng.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *bị từ chối — không phải một tên đơn giản* |

**Một bản dịch** hợp lệ khi nó chỉ chứa các placeholder `{name}` trần, mọi
tên bắt buộc xuất hiện ít nhất một lần, và không tên nào ngoài tập được phép
xuất hiện. Việc đảo thứ tự và lặp lại được cố ý để không ràng buộc: cả hai
đều có thể là điều ngữ pháp của một ngôn ngữ đích đòi hỏi.

Với số nhiều, tập *được phép* là hợp của các tên trong những nhánh và tập
*bắt buộc* là giao của chúng — vì vậy `t"One file"` đối chiếu với
`t"{n} files"` để `n` sẵn dùng cho người dịch của cả hai dạng nhưng không bắt
buộc ở dạng nào, và quy tắc số nhiều của ngôn ngữ đích có thể khác với ngôn
ngữ nguồn.

**Một msgid rỗng** không bao giờ được tra cứu, vì gettext dành riêng nó cho
header siêu dữ liệu của catalog.

## Tuân thủ { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
là chính tài liệu này ở dạng máy đọc được: các trường hợp ánh xạ cấu trúc
tĩnh của một t-string sang một msgid, và một msgid cùng một pattern trong
catalog sang một chuỗi đã kết xuất hoặc một sự từ chối.

Một hiện thực **tuân thủ đặc tả v1** khi nó tái tạo được mọi trường hợp. Các
trường hợp chỉ gọi tên những gì đặc tả định nghĩa — msgid dẫn xuất, các
pattern được chấp nhận và bị từ chối, đầu ra kết xuất — và không bao giờ là
một thông điệp lỗi hay một kiểu ngoại lệ, nhờ đó một hiện thực bằng ngôn ngữ
khác có thể chạy chúng nguyên vẹn.

Các phép nội suy được mô tả theo cấu trúc, không bao giờ dưới dạng mã nguồn
Python:

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

Trường `"spec"` **không phải** là phiên bản đặc tả — mọi trường hợp trong
`v1.json` đều thuộc đặc tả v1. Nó gọi tên mục nào của `SPEC.md` mà trường hợp
đó thử thách, nên `"2.2"` đọc là §2.2, quy tắc dẫn xuất một token placeholder.

Hiện thực tham chiếu chạy bộ kiểm thử này như một phần trong bộ kiểm thử của
chính nó, nên phần văn xuôi và phần mã không thể lặng lẽ trôi dạt xa nhau.

## Đánh phiên bản { #versioning }

Đây là đặc tả v1. Một thay đổi không tương thích ngược đối với cách dẫn xuất
msgid hay cách kiểm tra tính hợp lệ của bản dịch sẽ tăng số phiên bản và phát
hành một `conformance/vN.json` mới bên cạnh tệp hiện có. Những làm rõ mang
tính bổ sung không thay đổi msgid dẫn xuất lẫn các pattern được chấp nhận thì
không.
