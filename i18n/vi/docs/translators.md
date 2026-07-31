---
description: "Hợp đồng về placeholder dành cho người chỉnh sửa tệp .po: bạn được phép đổi gì, phải giữ nguyên gì, và đọc các thông báo lỗi như thế nào."
---

# Dành cho người dịch

Trang này dành cho người chỉnh sửa catalog, không phải người viết mã. Nó ngắn
một cách có chủ ý, và được viết để có thể liên kết hoặc sao chép vào bộ hướng
dẫn dành cho người dịch của chính dự án bạn.

Không có gì ở đây đòi hỏi bạn phải đọc được Python. Mọi thứ ở đây chỉ xoay
quanh một điều: những mảnh của thông điệp nằm trong ngoặc nhọn.

## Placeholder là gì { #what-a-placeholder-is }

Một thông điệp trong catalog có thể chứa các tên nằm trong ngoặc nhọn:

```po
msgid "Hello {name}"
msgstr ""
```

`{name}` là một **placeholder**. Khi chương trình hiển thị thông điệp này, nó
thay `{name}` bằng một giá trị mà nó cung cấp — tên một người, tên một tệp,
một con số. Placeholder không phải là một từ để dịch; nó là một chỗ trống.

Bản dịch của bạn nằm trong `msgstr`, và nó phải giữ lại chỗ trống đó:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

## Bạn được phép đổi gì, và không được đổi gì { #what-you-may-change-and-what-you-may-not }

Bạn **được phép**:

- **Di chuyển một placeholder** tới bất cứ đâu ngữ pháp của ngôn ngữ đích
  muốn, kể cả lên đầu thông điệp.
- **Lặp lại một placeholder** nếu ngôn ngữ cần giá trị đó hai lần.
- **Viết lại mọi từ còn lại**, kể cả dấu câu, khoảng trắng và trật tự câu.

Bạn **không được**:

- **Dịch cái tên bên trong ngoặc nhọn.** `{name}` vẫn là `{name}`, ngay cả
  trong một ngôn ngữ không viết gì khác bằng chữ Latinh.
- **Bỏ ngoặc nhọn**, hay viết cái tên mà không có chúng.
- **Thay ngoặc nhọn ASCII `{` `}` bằng dạng toàn rộng `｛` `｝`.** Nhiều bộ gõ
  sinh ra dạng toàn rộng; chúng trông gần như y hệt và không hoạt động.
- **Thêm phần định dạng**, chẳng hạn `{name!r}` hay `{amount:.2f}`. Việc một
  giá trị được hiển thị ra sao là do chương trình quyết định, không phải
  catalog.
- **Bịa ra một placeholder** không có trong `msgid`.

Nếu một thông điệp cần một giá trị mà bản gốc không cung cấp, thì đó là thông
điệp mà nhà phát triển phải sửa. Hãy nói ra thay vì tìm cách lách.

## Các dạng số nhiều { #plural-forms }

Một thông điệp có đếm sẽ đến với một ô `msgstr` cho mỗi dạng số nhiều của
ngôn ngữ bạn, và chính ngôn ngữ của bạn quyết định có bao nhiêu ô — một cho
tiếng Nhật, hai cho tiếng Đức, ba cho tiếng Nga, sáu cho tiếng Ả Rập. Hãy
điền vào mọi ô mà catalog đưa cho bạn.

Hai quy tắc hay làm người ta vấp:

- **Các ô không phải là "số ít, số nhiều, số nhiều hơn".** Mỗi chỉ số mang
  đúng ý nghĩa mà quy tắc số nhiều của ngôn ngữ bạn quy định. Dạng thứ ba của
  tiếng Latvia chỉ dành cho số không; dạng thứ hai của tiếng Slovenia dành
  cho đúng số hai; tiếng Wales đặt trường hợp chung ở chỉ số 0 và số ít ở chỉ
  số 1.
- **Hai ô có thể mang cùng một văn bản một cách hợp lệ.** Trong tiếng Thổ Nhĩ
  Kỳ, tiếng Hungary, tiếng Ba Tư và tiếng Bengal, danh từ vẫn ở dạng số ít
  sau một số đếm, nên cả hai dạng của một thông điệp có đếm đều là cùng một
  chuỗi. Điều đó là đúng, không phải lỗi sao chép.

Các quy tắc về placeholder ở trên áp dụng cho từng dạng một cách độc lập.

## Các mục fuzzy { #fuzzy-entries }

Một mục được đánh dấu `fuzzy` là phỏng đoán của máy: nhà phát triển đã đổi
thông điệp gốc, và công cụ ghép văn bản mới với bản dịch cũ của bạn để bạn có
chỗ mà bắt đầu.

```po
#, fuzzy
msgid "Welcome back, {name}"
msgstr "こんにちは {name}"
```

Một mục fuzzy **không được chương trình dùng** — nó hiển thị bản gốc chưa
dịch thay vào đó — cho tới khi ai đó sửa lại văn bản và gỡ dấu `fuzzy`. Phần
lớn trình soạn PO có sẵn một nút cho đúng việc đó.

## Đọc một thông báo lỗi { #reading-a-failure-message }

Công cụ kiểm tra placeholder khi catalog được biên dịch, và thông báo được
viết cho bạn chứ không phải cho một lập trình viên. Chỉ báo rằng `{name}` bị
thiếu là một ngõ cụt khi bạn đang nhìn thấy đúng những ký tự đó trước mắt,
nên ở chỗ một placeholder trông có vẻ hiện diện mà thực ra không, thông báo
sẽ nói vì sao. Đối chiếu với bản gốc `Hello {name}`, mỗi trường hợp dưới đây
được báo dưới dạng `translation does not match the source placeholders:`

| Bản dịch của bạn viết | Lý do được đưa ra |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Những ký tự không nhìn thấy được có cách xử lý riêng. Một khoảng trắng không
ngắt nằm trong ngoặc nhọn là thứ do bộ gõ sinh ra và không trình soạn nào
hiển thị, nên thông báo in nó ra theo điểm mã thay vì gọi tên một ký tự mà
bạn không bao giờ tìm thấy:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Một cái tên có các chữ cái trộn lẫn hệ chữ viết — trường hợp đồng hình, khi
chữ `а` Kirin không thể phân biệt với chữ `a` Latinh — được hiển thị hai lần,
một lần đọc được và một lần đã escape, đó là dạng duy nhất phân biệt được hai
thứ:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Cách khử nhập nhằng ấy cũng áp dụng khi một cái tên Hy Lạp hoặc Kirin viết
hoàn toàn bằng một hệ chữ xung đột với một tên nguồn ASCII, bao gồm cả trường
hợp một chữ cái `a` Latinh / `а` Kirin.

Nếu bạn gặp một trong những trường hợp này mà cách sửa không rõ ràng, nước đi
an toàn là xóa placeholder bạn đã gõ và sao chép placeholder từ `msgid`.

## Những gì các bước kiểm tra không làm được { #what-the-checks-cannot-do }

Công cụ xác minh rằng các placeholder của bạn còn nguyên vẹn. Nó không thể
biết bản dịch có chính xác, có tự nhiên, hay có đúng với ngữ cảnh hay không —
điều đó hoàn toàn thuộc về bạn.

Hai thứ giúp ích hơn mọi bước kiểm tra:

- **Đọc chú thích dành cho người dịch.** Một dòng bắt đầu bằng `#.` phía trên
  thông điệp là lời nhà phát triển nói cho bạn biết nó xuất hiện ở đâu và có
  nghĩa gì.
- **Hỏi về `msgctxt`.** Khi cùng một từ xuất hiện hai lần với ngữ cảnh khác
  nhau, đó là vì hai chỗ ấy cần được dịch khác nhau — chẳng hạn "Open" là cái
  nút và "Open" là trạng thái.
