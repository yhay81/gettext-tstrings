---
description: "Mọi tên mà gettext_tstrings xuất ra: các hàm, Translator, gắn ngữ cảnh, chuỗi lazy, và các lỗi."
---

# API

Mọi thứ bên dưới đều được xuất ra từ `gettext_tstrings`. Ngoài chúng ra không
có gì là công khai. Trang này là tài liệu tham chiếu chữ ký hàm; để xem ví dụ
hoàn chỉnh của từng hàm, hãy xem [Cẩm nang](guide.md).

## Dịch { #translating }

Mỗi hàm nhận t-string của nó theo vị trí và chấp nhận hai đối số từ khóa:
`translations` (quay về binding của ngữ cảnh, rồi đến các hàm toàn cục của
thư viện chuẩn) và `strict` (xem
[Cẩm nang](guide.md#what-happens-when-a-catalog-is-wrong)).

| Hàm | Chữ ký |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | bí danh của `gettext` |
| `ntr` | bí danh của `ngettext` |

### `Translator`

Một dataclass đóng băng gắn với một đối tượng bản dịch duy nhất, để các vị
trí gọi không phải lặp lại nó.

```python
Translator(translations, strict=False)
```

Nó có thể gọi được (`_(t"…")`) và mang theo `gettext`, `ngettext`,
`pgettext`, `npgettext`, cùng các bí danh `tr` / `ntr`.

## Gắn ngữ cảnh { #context-binding }

| Tên | Mục đích |
| --- | --- |
| `use_translations(translations)` | Gắn trong phạm vi một khối `with`, sau đó khôi phục. |
| `set_translations(translations)` | Gắn mà không cần khối, dành cho vòng đời do framework quản lý. |
| `get_translations()` | Đọc ra binding hiện tại, hoặc `None`. |

Binding này là một `ContextVar`, nên nó thuộc về từng ngữ cảnh và an toàn khi
chạy đồng thời.

## Chuỗi trì hoãn { #deferred-strings }

| Tên | Mục đích |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Hoãn việc dịch cho tới từng lần kết xuất. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Dạng có ngữ cảnh. |
| `LazyString` | Kiểu mà cả hai hàm trả về. Kết xuất qua `str()` và `format()` bằng ngôn ngữ đang được gắn tại đúng khoảnh khắc đó, so sánh bằng với văn bản đã kết xuất của nó, và cố ý không thể băm. |

Các ví dụ đầy đủ, kể cả lý do `strict` thuộc về nơi định nghĩa, nằm ở
[Bản dịch trì hoãn](guide.md#deferred-translation).

## Tầng thấp hơn { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Biên dịch một t-string, tái sử dụng kế hoạch tĩnh đã được cache của nó.

### `CompiledTemplate`

| Thành viên | Ý nghĩa |
| --- | --- |
| `.msgid` | Định danh thông điệp gettext ổn định. |
| `.placeholders` | Tên các placeholder theo thứ tự xuất hiện lần đầu. |
| `.render(pattern)` | Kiểm tra tính hợp lệ của một pattern và kết xuất nó. **Luôn ném ngoại lệ** khi không khớp. |

## Kiểu và lỗi { #types-and-errors }

### `Translations`

Một `Protocol` `runtime_checkable` cho bốn phương thức tiêu chuẩn, tất cả đều
chỉ-theo-vị-trí:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` và `Translations` của
Babel đều thỏa mãn nó.

### Ngoại lệ

| Lớp | Được ném khi |
| --- | --- |
| `TStringError` | Lớp cơ sở của cả hai lớp bên dưới. |
| `InvalidTemplateError` | T-string **nguồn** phá vỡ quy ước — một phép nội suy phức tạp, hoặc một tên lặp lại với định dạng khác nhau. |
| `InvalidTranslationError` | **Bản dịch** phá vỡ quy ước. Ở chế độ khoan dung mặc định, lỗi này được ghi log và văn bản nguồn được kết xuất thay thế. |

## Các điểm vào trích xuất { #extraction-entry-points }

Được đăng ký tự động khi cài đặt; bạn tham chiếu đến chúng bằng tên, không
phải bằng import.

| Nhóm | Tên | Được dùng bởi |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` trong `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, một cách tự động. |

## Hiệu năng { #performance }

Bản tường thuật đầy đủ — cái gì được cache, các cache khóa theo gì, và những
con số đo được — nằm trong [Cách hoạt động](internals.md#the-hot-path). Phiên
bản ngắn gọn: việc kiểm tra tính hợp lệ được cache, không bao giờ bị bỏ qua,
và toàn bộ phép kết xuất chỉ tốn một phần nhỏ của micro giây. Hãy tự chạy
benchmark trên máy đích của bạn:

```console
uv run python benchmarks/runtime.py
```
