---
description: "Ba mươi năm gettext, hai PEP cách nhau mười năm, và cuộc thảo luận về thư viện chuẩn khép lại với kết luận not-planned: vì sao thư viện này tồn tại, kèm liên kết tới các nguồn."
---

# Bối cảnh

Thư viện này nằm ở điểm giao của hai câu chuyện dài — một về cách phần mềm
được dịch, một về cách Python nội suy chuỗi — hai câu chuyện cuối cùng đã gặp
nhau vào năm 2025 rồi khựng lại đúng tại chỗ cần đến một quy ước nhỏ nhưng
được cân nhắc kỹ lưỡng. Trang này kể cả hai câu chuyện, kèm liên kết tới các
nguồn, bởi những quyết định thiết kế trên trang này sẽ dễ đánh giá hơn khi
bạn thấy được các câu hỏi mà chúng trả lời.

## Hệ sinh thái gettext { #the-gettext-ecosystem }

[GNU gettext] là cách phần mềm tự do được dịch kể từ giữa thập niên 1990:
đánh dấu các chuỗi trong mã, trích xuất chúng vào một tệp mẫu, giao cho người
dịch một tệp catalog cho mỗi ngôn ngữ, biên dịch, rồi nạp lúc chạy. Quanh
vòng lặp đó đã mọc lên cả một hệ sinh thái — các trình soạn thảo PO, quy
trình rà soát, và những nền tảng dịch thuật cùng nói chung một định dạng tệp
— còn Python đã đưa mô-đun [`gettext`][stdlib-gettext] vào thư viện chuẩn
của mình hơn hai thập kỷ nay. Nửa lúc chạy của việc dịch chưa bao giờ là vấn
đề.

Nửa còn bỏ ngỏ luôn luôn là *chuỗi trong catalog trông như thế nào*. Một
thông điệp `%(name)s` trao vào tay người dịch cú pháp printf mà chỉ một chữ
cái bị xóa nhầm cũng biến thành sự cố sập trong production; một thông điệp
`.format()` trao cho catalog quyền truy cập thuộc tính trên các đối tượng
đang hoạt động. ([Vì sao chọn t-string](comparison.md) phân tích cả hai,
trưng ra rõ ràng các cách chúng thất bại.) Còn f-string — cú pháp mà phần
lớn mã Python ngày nay ưa chuộng — hoàn toàn không thể tham gia: đến lúc bất
kỳ thư viện nào nhìn thấy nó, nó đã là một chuỗi hoàn chỉnh. Người ta vẫn cứ
thử, thường xuyên tới mức trình theo dõi lỗi của Babel gom lại được các nỗ
lực đó ([#594][babel-594], [#715][babel-715]); thất bại nằm ở cấu trúc, chứ
không phải một tính năng còn thiếu.

## Hai PEP, cách nhau mười năm { #two-peps-ten-years-apart }

Năm 2015, Alyssa Coghlan và Nick Humrich viết [PEP 501], đề xuất các template
nội suy với động lực đầu tiên được nêu rõ là i18n — "providing a cleaner
syntax for i18n translation" (cung cấp một cú pháp gọn gàng hơn cho việc dịch
i18n), theo đúng lời của chính PEP. Đề xuất bị hoãn lại, một phần vì cuộc
thảo luận cho thấy trường hợp i18n kéo theo những cân nhắc phụ đáng kể mà các
trường hợp sử dụng đơn giản hơn không gặp phải.

Một thập kỷ sau, [PEP 750] — của Jim Baker, Guido van Rossum, Paul Everitt,
Koudai Aono, Lysandros Nikolaou và Dave Peck — hồi sinh ý tưởng đó dưới dạng
t-string, được [chấp nhận vào tháng 4 năm 2025][sc-resolution], và ra mắt
trong [Python 3.14] vào tháng 10 năm 2025. PEP 501 sau đó được rút lại để
nhường chỗ cho nó. Có một chi tiết quan trọng với trang này: i18n *không*
nằm trong các động lực mà PEP 750 nêu ra. PEP này tổng quát hóa cơ chế — một
kiểu template mà bất kỳ thư viện nào cũng có thể tiêu thụ — và để câu hỏi về
dịch thuật lại đúng nơi PEP 501 đã gác nó mười năm trước: bỏ ngỏ.

Vậy nên tính đến Python 3.14, ngôn ngữ này có chính xác cấu trúc dữ liệu mà
một catalog thông điệp cần, nhưng lại không có quy ước nào để dùng nó theo
cách đó.

## Cuộc thảo luận về thư viện chuẩn { #the-stdlib-discussion }

Hai tháng trước khi 3.14 phát hành, Adrian Mönnich (ThiefMaster, một
maintainer của dự án Indico) đề xuất lấp khoảng trống đó ngay trong thư viện
chuẩn: chủ đề [Support t-strings in gettext][discuss-thread] trên
discuss.python.org, mở vào tháng 8 năm 2025, đi kèm một
[pull request][cpython-pr] chạy được, bổ sung hỗ trợ t-string cho cả
`gettext` lẫn `pygettext`.

Chủ đề đó đáng để đọc trọn vẹn, vì nó làm nổi lên mọi câu hỏi khó mà thư
viện này về sau phải trả lời:

- **Một phép nội suy được phép là gì?** Chỉ một tên đơn giản, hay cả truy
  cập thuộc tính và lời gọi hàm với tên placeholder được suy ra? Mỗi câu trả
  lời đều đánh đổi sự tiện lợi lấy độ ổn định của msgid và độ an toàn của
  catalog.
- **Các dạng số nhiều đòi hỏi gì,** khi hệ thống số nhiều của ngôn ngữ đích
  khác với hệ thống của ngôn ngữ nguồn?
- **Liệu gettext có phải là mục tiêu đúng?** Barry Warsaw — người từng lập
  luận trong quá trình phát triển PEP 750 rằng t-string không phù hợp cho
  i18n — chỉ tới [`flufl.i18n`][flufl-i18n] của ông và phong cách chuỗi `$`
  của nó như một công cụ thân thiện hơn; những người khác đề nghị bỏ hẳn
  gettext để chuyển sang các hệ thống mới hơn như [Fluent].
- **Và câu hỏi ở tầng meta:** bất kể thư viện chuẩn phát hành thứ gì, về cơ
  bản nó không bao giờ thay đổi được nữa. Một quy ước với nhiều lựa chọn còn
  bỏ ngỏ đến vậy là thứ đầy rủi ro nếu đóng băng ngay ở lần thử đầu tiên.

Không có đồng thuận nào hình thành. Issue trên CPython bị
[đóng với trạng thái "not planned"][cpython-issue] và pull request bị đóng
mà không được merge vào tháng 10 năm 2025, chỉ vài ngày sau khi 3.14 phát
hành. Năng lực đã có sẵn trong ngôn ngữ; quy ước thì chưa có mái nhà.

## Vì sao lại là một gói trước { #why-a-package-first }

Đó là khoảng trống mà dự án này chọn lấp từ bên ngoài thư viện chuẩn, dựa
trên một sự đặt cược có chủ đích: một quy ước sẽ trưởng thành nhanh hơn ở
nơi nó có thể tự do đánh phiên bản và giành lấy sự chấp nhận qua từng trường
hợp một, còn thư viện chuẩn — nơi buộc phải đúng ngay từ lần đầu — là nơi
một quy ước nên *kết thúc hành trình*, chứ không phải nơi nó được mài giũa.

Cụ thể, mọi câu hỏi gây tranh cãi trong chủ đề đó đều có câu trả lời được
ghi thành văn tại đây, mỗi câu trên một trang riêng:

- Phép nội suy chỉ nhận **tên đơn giản**, để msgid luôn ổn định và có ý
  nghĩa — [Cẩm nang](guide.md#safety-and-scope) trình bày quy tắc,
  [Cách hoạt động](internals.md#from-template-to-msgid) trình bày lý do.
- **Việc định dạng hoàn toàn nằm ngoài catalog**
  ([Vì sao chọn t-string](comparison.md)).
- **Số nhiều** tuân theo một quy tắc hợp/giao cho phép hệ thống số nhiều của
  ngôn ngữ đích khác với hệ thống của ngôn ngữ nguồn ([spec §4](spec.md)).
- Một catalog hỏng sẽ **quay về dự phòng thay vì sập**, giữ đúng hợp đồng
  vốn có của gettext
  ([Cẩm nang](guide.md#what-happens-when-a-catalog-is-wrong)).
- Và toàn bộ quy ước là một [đặc tả có phiên bản](spec.md) với bộ kiểm thử
  tuân thủ máy đọc được — viết sao cho một hiện thực khác, kể cả một hiện
  thực trong thư viện chuẩn tương lai, có thể áp dụng nguyên vẹn và tương
  tác được.

Cuộc thảo luận vẫn chưa kết thúc, và dự án này là một bên tham gia trong đó,
chứ không phải phán quyết dành cho nó. Nếu bạn có kinh nghiệm vận hành
gettext trong production liên quan tới các lựa chọn này, thì
[chính chủ đề đó][discuss-thread] và mục [Discussions][gh-discussions] của
kho mã này là nơi cuộc thảo luận vẫn đang tiếp diễn.

## Dòng thời gian { #timeline }

| Thời điểm | Điều gì đã xảy ra |
| --- | --- |
| Giữa thập niên 1990 | GNU gettext thiết lập quy trình PO/POT/MO mà người dịch và các nền tảng vẫn dùng chung tới nay. |
| 2015 | [PEP 501] đề xuất các template nội suy, với i18n là động lực đầu tiên; bị hoãn lại. |
| 2016 | f-string ra mắt trong Python 3.6 — phép nội suy có được cú pháp của mình, còn việc dịch thì không thể dùng nó. |
| Tháng 7 2024 | [PEP 750] đề xuất t-string. |
| Tháng 4 2025 | PEP 750 được [chấp nhận][sc-resolution]; PEP 501 được rút lại để nhường chỗ. |
| Tháng 8 2025 | Chủ đề [Support t-strings in gettext][discuss-thread] được mở, kèm một [pull request][cpython-pr] cho thư viện chuẩn. |
| Tháng 10 2025 | [Python 3.14] phát hành với t-string; issue trên thư viện chuẩn đóng lại với trạng thái [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` ra mắt bản alpha, với [spec v1](spec.md) và bộ kiểm thử tuân thủ của nó. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
