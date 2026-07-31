---
description: "Việc dịch một trang nhỏ ra ba mươi lăm ngôn ngữ thực sự làm hỏng những gì, thư viện bắt giúp bạn được cái nào, và cái nào thì không."
---

# Những cái bẫy thường gặp

Trang này được dịch ra ba mươi lăm ngôn ngữ, và mỗi ấn bản trong số đó đều ra
đời bằng cách chạy đúng vòng lặp mà tài liệu này dạy. Theo chuẩn của ngành thì
đó là một kho ngữ liệu nhỏ, vậy mà vẫn đủ để vấp phải hầu hết những cái bẫy
khiến i18n khó hơn vẻ ngoài của nó.

Mỗi mục dưới đây là một chuyện thực sự đã hỏng ở đây, nó trông ra sao vào lúc
đó, và ranh giới nằm ở đâu giữa phần thư viện kiểm tra giúp bạn và phần vẫn
thuộc về phán đoán của bạn.

## Đổi tên một biến là dịch lại cả một câu { #renaming-a-variable-retranslates-a-sentence }

Msgid là khóa của catalog, và một tên được nội suy nằm ngay *bên trong* nó.
Chỉ cần chuyển một hằng số lên phạm vi module rồi viết hoa nó theo đúng quy
ước của Python — `author` thành `AUTHOR` — là `Copyright © 2026 {author} · MIT
License` biến thành một thông điệp chưa catalog nào từng thấy. Mọi bản dịch
của dòng đó sẽ phải quay lại chu trình fuzzy, ở mọi ngôn ngữ, chỉ vì một lần
đổi tên không thay đổi bất cứ điều gì người đọc nhìn thấy.

Thư viện sẽ không ngăn bạn: cả hai cách viết đều là tên placeholder hợp lệ.
Thứ nó làm được là khiến cái tên ấy *đáng* được bảo vệ — một phép nội suy bắt
buộc phải là một [tên trần](internals.md#from-template-to-msgid), nên thứ nằm
trong khóa của catalog là một từ mà người dịch đọc được, chứ không phải một
biểu thức.

Trường hợp phản chiếu thì an toàn ngay từ thiết kế. Các phép chuyển đổi và
format spec không thuộc msgid, nên siết `{amount:,.2f}` thành `{amount:,.0f}`
không đổi khóa nào và không làm mất hiệu lực bản dịch nào ở bất cứ đâu.

## `nplurals=2` không có nghĩa là hai chuỗi khác nhau { #nplurals-2-does-not-mean-two-different-strings }

Tiếng Thổ Nhĩ Kỳ, tiếng Hungary, tiếng Ba Tư và tiếng Bengal đều khai báo hai
dạng số nhiều, và ở cả bốn ngôn ngữ, hai dạng của một thông điệp có đếm hoàn
toàn chính đáng khi là *cùng một chuỗi* — danh từ giữ nguyên số ít sau một số
từ, nên `{n} sayfa` đúng cho một trang cũng như cho mười trang. Người rà soát
nào "sửa" chỗ trùng lặp đó là làm hỏng bản dịch.

Sai lầm ngược lại cũng dễ mắc y như vậy. Dạng thứ ba của tiếng Latvia tồn tại
**chỉ dành cho số không**; dạng thứ hai của tiếng Slovenia là một dạng **số
đôi**, dành cho đúng hai; dạng cuối của tiếng Romania đòi hỏi từ `de` mà hai
dạng đầu không được phép có. Nhét vào những ô đó một dạng số ít và một dạng số
nhiều sẽ cho ra một catalog chỉ sai ở những số đếm không ai kiểm thử.

Tệ hơn, *thứ tự* của các ô không mang nghĩa. Tiếng Wales đánh chỉ số năm dạng
của nó sao cho `msgstr[0]` là trường hợp chung còn `msgstr[1]` mới là dạng số
ít. Điền chúng theo trình tự hiển nhiên sẽ đặt dạng số ít vào đúng chỗ mà mọi
thông điệp không đếm sẽ tìm tới.

Thư viện không ôm lấy bất kỳ điều nào trong số đó, và đó chính là chủ ý: quy
tắc số nhiều của ngôn ngữ đích nằm trong header của chính catalog ấy, còn
[quy tắc hợp/giao](spec.md) cho phép một bản dịch có nhiều dạng hơn, hoặc ít
dạng hơn, so với nguồn. Thứ nó kiểm tra là thứ duy nhất có thể kiểm mà không
cần biết ngôn ngữ — rằng mọi dạng đều giữ đủ những placeholder mà nó cần.

## Hai dạng giống hệt nhau là có lý do { #two-forms-can-be-identical-for-a-reason }

Tiếng Ireland có năm dạng số nhiều, và trong báo cáo build của trang này, vài
dạng trong số đó được viết giống hệt nhau. Đó không phải là một cú sao chép
nhầm: *leathanach* bắt đầu bằng `l`, và không phép biến âm đầu từ nào mà số từ
tiếng Ireland kích hoạt được thể hiện trên `l`. Các dạng ấy vẫn làm việc thật
— thân từ luân phiên giữa *leathanach* và *leathanaigh*, và các số đếm trên
mười thì quay về dạng số ít — nhưng không danh từ nào mang nghĩa "trang" cho
thấy được sự tương phản đó.

Bất kỳ phép kiểm nào đánh dấu các dạng trùng nhau là đáng ngờ đều sẽ đánh dấu
cả tiếng Ireland đúng đắn. Người rà soát duy nhất cho chuyện này là một con
người biết ngôn ngữ đó.

## Một thông điệp chỉ có thể hòa hợp với một số đếm { #a-message-can-only-agree-with-one-count }

Báo cáo build của trang này cho biết đã kết xuất bao nhiêu trang và mất bao
lâu. Viết nó thành "Rendered {n} pages in {seconds} seconds" thì trông vô hại
mà lại không dịch được: gettext chọn một dạng từ một số đếm, và số đếm đó là
`n`. Từ *seconds* sẽ phải hòa hợp với một con số mà bộ máy số nhiều không bao
giờ nhìn thấy.

Cách sửa là biến đại lượng thứ hai thành một ký hiệu đơn vị thay vì một từ, và
bản thân các ký hiệu đơn vị cũng được bản địa hóa: các catalog của trang này
mang `s`, `с`, `ث`, `שנ׳` và `mp`, còn quy ước chữ nghĩa của tiếng Pháp, tiếng
Tây Ban Nha và tiếng Thụy Điển đòi một dấu cách trước ký hiệu ở chỗ tiếng Anh
thì không. Chẳng điều nào trong đó là việc của thư viện — nhưng nhận ra rằng
một thông điệp cần tới *hai* sự hòa hợp thì đúng là việc của bạn, và công cụ
duy nhất cho nó là viết thông điệp theo cách khác.

## Sửa một câu tiếng Anh là sửa ngữ pháp của tiếng nước ngoài { #editing-an-english-sentence-edits-foreign-grammar }

Trang chủ từng ghi "all ten language editions". Bỏ con số đi — một sửa đổi
tiếng Anh gọn trong một từ, làm vì con số cứ liên tục lỗi thời — đã biến một
chủ ngữ số nhiều thành số ít. Tiếng Tây Ban Nha, tiếng Ý, tiếng Bồ Đào Nha,
tiếng Nga, tiếng Ukraina, tiếng Hy Lạp, tiếng Hà Lan và tiếng Do Thái đều phải
hòa hợp lại động từ; vài ngôn ngữ còn phải đổi cả phân từ.

Một sửa đổi ở nguồn đọc lên có vẻ tầm thường trong tiếng Anh thì không hề tầm
thường ở phía hạ nguồn. Việc đánh dấu nó là fuzzy, đúng như `pybabel update`
vẫn làm, chính là cơ chế trao cho mỗi người dịch cơ hội nhận ra điều đó.

## Những khác biệt vô hình sống sót qua mọi lần sao chép { #invisible-differences-survive-every-copy-paste }

Trang cẩm nang trích một thông điệp chẩn đoán có chứa `(nаme)` — một dạng
thoát chuỗi có chủ ý, bởi ký tự mà nó gọi tên là một chữ `а` Kirin mà không
người đọc nào phân biệt được với chữ Latinh. Người dịch của trang này đã đổi
dạng thoát ấy thành chính ký tự thật **năm lần riêng biệt**, ở năm ngôn ngữ
khác nhau, lần nào cũng cho ra một trang trông thì đúng mà thực ra là sai.

Chuyện này thì thư viện có bắt được, và đó cũng là lý do các thông điệp chẩn
đoán mang hình hài như hiện nay: một placeholder có các chữ cái pha trộn nhiều
hệ chữ viết sẽ được [báo cáo hai lần](internals.md#diagnostics-are-part-of-the-design),
một lần ở dạng dễ đọc và một lần ở dạng thoát chuỗi, vì dạng thoát chuỗi là
cách viết duy nhất phân biệt được chúng. Một dấu cách không ngắt nằm trong cặp
ngoặc nhọn cũng được in ra theo điểm mã vì đúng lý do ấy. Bộ kiểm tra catalog
từ chối thông điệp đó trước khi nó kịp phát hành.

## Không rỗng không có nghĩa là đã dịch { #non-empty-is-not-translated }

Một catalog được dựng khung bằng cách chép msgid của nó vào msgstr sẽ qua được
mọi phép kiểm ngây thơ: không có gì rỗng, không có gì fuzzy, tập thông điệp
khớp chính xác. Một ấn bản của trang này đã phát hành như thế trong vài giờ.
Tám trang của một ấn bản khác cũng vậy — chúng là bản sao giống hệt từng byte
của nguồn tiếng Anh, và điều đó qua được cả phép kiểm đối chiếu các khối mã
giữa hai bên, bởi chúng vốn là cùng một tệp.

Không trường hợp nào là thứ một thư viện dịch thuật có thể thấy. Cả hai đều rẻ
để kiểm thử một khi bạn biết là phải kiểm: hãy đối chiếu với nguồn và đòi hỏi
phải có khác biệt.

## Catalog không phải là thứ duy nhất được dịch { #the-catalog-is-not-the-only-translated-thing }

Hai sự cố ở đây chẳng liên quan gì tới gettext.

Dịch một tiêu đề sẽ làm đổi cái neo được sinh ra từ nó, nên mọi liên kết từ
trang khác trỏ vào mục đó đều gãy — một cách âm thầm, và chỉ trong ngôn ngữ
ấy. Trang này ghim neo tiếng Anh trên mọi tiêu đề, và một bài kiểm thử suy ra
danh sách neo mong đợi từ trang tiếng Anh.

Còn bộ sinh trang thì đi kèm bản dịch giao diện cho sáu mươi tám ngôn ngữ,
trong đó không có tiếng Swahili lẫn tiếng Ireland. Thiếu một bản dịch như vậy,
bản dựng không hạ cấp về tiếng Anh; lệnh include của template thất bại và ấn
bản đó hoàn toàn không dựng được. Hai tệp của chính kho mã này tồn tại để lấp
khoảng trống đó.

## Công cụ của bạn cũng có lỗi { #your-tools-have-bugs-too }

Bước CI mà tài liệu này khuyến nghị để bắt các catalog lỗi thời, `pybabel
update --check`, không làm nổi việc đó với bất kỳ dự án nào dùng `pgettext`
hay `npgettext` — nó báo mọi catalog có `msgctxt` là đã lỗi thời, ở mọi lần
chạy, vì một lỗi trong cách phép so sánh tra cứu thông điệp. Lỗi này được phát
hiện ngay tại đây khi thử dùng nó, đã được báo lên thượng nguồn, và được
[trình bày đầy đủ kèm cách đi vòng](workflow.md#what-ci-gates).

Bài học chung là bài học khó chịu: một cổng chặn lúc nào cũng đỏ còn tệ hơn là
không có cổng nào, vì rồi cả đội sẽ tắt nó đi. Hãy kiểm chứng rằng phép kiểm
CI của bạn thực sự có thể qua, trước khi tin tưởng giao cho nó việc báo hỏng.

## Thư viện này để làm gì, gói trong một câu { #what-the-library-is-for-in-one-line }

Phần lớn trang này là chuyện phán đoán mà không công cụ nào gánh thay được.
Thứ một công cụ *có thể* làm là bảo đảm rằng một bản dịch không thể thay đổi
cấu trúc của chính câu mà nó dịch — không thể bỏ rơi một giá trị, bịa ra một
giá trị, định dạng lại một giá trị, hay thò tay vào các đối tượng của bạn — và
có thể nói ra điều đó bằng một câu mà người phải đi sửa có thể hành động theo.
Đó là toàn bộ những gì thư viện này hứa hẹn, và phần còn lại của trang này là
cách nó giữ lời.
