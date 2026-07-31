---
description: "Trích xuất thông điệp t-string bằng pybabel, và cách msgfmt cùng trình kiểm tra Babel đi kèm xác thực các catalog."
---

# Trích xuất

Trích xuất là bước gom mọi thông điệp đã đánh dấu từ mã nguồn của bạn vào một
tệp mẫu `.pot` dành cho người dịch — bước 3 trong vòng lặp của
[Hướng dẫn nhập môn](tutorial.md). Trang này là tài liệu tham chiếu cho bước
đó: cấu hình, tên hàm tùy chỉnh, chế độ strict cho CI, và các phép kiểm tra
bảo vệ catalog của bạn về sau.

Trích xuất cần extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Quy trình làm việc { #the-workflow }

Tạo `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Sau đó dùng các lệnh Babel thông thường:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` chỉ chạy một lần cho mỗi ngôn ngữ; sau đó, `pybabel update` gộp từng
tệp mẫu mới vào các catalog hiện có. Chu trình lặp lại đó — và ý nghĩa của các
mục `fuzzy` đối với một bản phát hành — được trình bày từng bước trong
[Vận hành thực tế](workflow.md#the-cycle-after-the-first-translation).

Bộ trích xuất `gettext_tstrings` cũng xử lý các lời gọi `_()`, `gettext()` và
`ngettext()` thông thường, nên một mapping duy nhất bao quát được cả codebase
hỗn hợp. Nó nhận diện `_()`, bốn tên gettext chuẩn, các bí danh `tr()` /
`ntr()`, và các dạng trì hoãn `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Bật chú thích cho người dịch bằng `-c`"

    `pybabel extract` chỉ thu thập chú thích dành cho người dịch khi bạn
    truyền `-c "Translators:"`, đúng như cách nó làm với các lời gọi gettext
    thông thường. Bỏ tùy chọn đó thì việc trích xuất vẫn chạy — chỉ là các
    chú thích không bao giờ tới được catalog, nơi chúng là [đòn bẩy chất lượng
    rẻ nhất](workflow.md#working-with-translators-and-platforms) trong toàn bộ
    quy trình.

## Đăng ký tên hàm của riêng bạn { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Tệp ini nhận một chuỗi, mapping TOML nhận một danh sách, và bên trong một
chuỗi thì khoảng trắng hoặc dấu phẩy đều phân tách được các tên. Cả bốn cách
viết đều hoạt động.

Các tùy chọn gồm `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` và `npgettext_functions`.

!!! danger "`-k` không chạm tới được t-string"

    Một hàm hỗ trợ tùy chỉnh như `mytr(t"…")` phải được khai báo trong một
    trong các tùy chọn ở trên. Cơ chế `--keyword` của Babel không thể đọc một
    literal t-string, nên `pybabel extract -k mytr` không tìm thấy gì và cũng
    không báo gì — các thông điệp đơn giản là vắng mặt trong tệp POT. `-k` vẫn
    hoạt động bình thường với các lời gọi gettext thông thường được trích xuất
    song song.

    Chỉ thứ tự đối số chuẩn được hỗ trợ: thông điệp đứng trước; ngữ cảnh rồi
    đến thông điệp với `pgettext`; ngữ cảnh, rồi số ít, rồi số nhiều với
    `npgettext`.

## Khoan dung tại chỗ, nghiêm ngặt trong CI { #lenient-locally-strict-in-ci }

Theo mặc định, một tệp hỏng không làm chấm dứt cả lượt chạy:

- Một t-string bị bộ trích xuất từ chối — truy cập thuộc tính, một biểu thức,
  một đối số sai — được báo dưới dạng cảnh báo rồi bỏ qua.
- Một tệp không phân tích cú pháp được cũng bị bỏ qua theo cách tương tự.
- Tương tự với tệp mà chỉ `tokenize` từ chối trong khi `ast` chấp nhận —
  trường hợp mà lượt chạy của chính Babel lẽ ra sẽ dừng hẳn.

Điều đó tiện lợi khi bạn đang ngồi sửa mã và nguy hiểm khi bạn không ngồi đó:
một thông điệp bị bỏ qua đơn giản là **vắng mặt trong tệp POT**, nên nó không
bao giờ được dịch mà cũng chẳng có gì báo cho bạn biết. Hãy đặt `strict = true`
trong các tùy chọn của mapping ở bất cứ nơi nào việc trích xuất không có người
theo dõi:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Khi đó mọi cảnh báo bên trên đều trở thành lỗi cứng. Hãy coi đây là thiết lập
cho production, còn mặc định là thiết lập cho máy của bạn.

## Toolchain hiện có của bạn xác thực các catalog này { #your-existing-toolchain-validates-these-catalogs }

Babel đánh dấu mọi thông điệp được trích xuất bằng một cờ chuẩn, và chính
dòng đó là thứ kích hoạt việc kiểm tra placeholder trong các công cụ bạn vốn
đã dùng:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Dịch nó thành `こんにちは {nombre}` và sai sót sẽ bị phát hiện mà không cần
bất kỳ cấu hình nào:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate ghi nhận cùng phép kiểm tra này dưới tên
[Python brace format][weblate-checks], và các nền tảng thương mại có cơ chế
QA placeholder riêng dựa trên cùng cờ đó. Hành vi của mỗi nền tảng là chuyện
riêng của nền tảng đó; hai công cụ dưới đây mới là những công cụ đã được kiểm
chứng tại đây.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Trên hết, gói này còn đăng ký một **checker** cho Babel, nên `pybabel compile`
áp dụng các quy tắc của đặc tả cho mọi thông điệp mang chú thích đánh dấu
`gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Với một thông điệp số nhiều, con trỏ lỗi nêu rõ dạng nào, vì số dòng Babel
báo là của msgid trong khi một khối tiếng Nga có tới ba `msgstr` bên dưới:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` vẫn ghi tệp `.mo`"

    Lỗi ở trên được báo cáo, mã thoát là `1` — nhưng catalog hỏng vẫn cứ được
    biên dịch. Chỉ mã thoát đó mới có thể ngăn một pipeline phát hành nó;
    [Những gì CI chặn lại](workflow.md#what-ci-gates) trình bày bước build
    thực hiện điều này.

Hai phép kiểm tra không hề trùng lặp. Checker của gói này nghiêm ngặt hơn ở ít
nhất hai trường hợp:

- Một msgid mà mọi dấu ngoặc nhọn trong nó đều đã được escape
  (`Config {{raw}} only`) không bao giờ nhận cờ `python-brace-format`, nên
  không công cụ bên ngoài nào xác thực nó cả.
- Các dạng số nhiều được kiểm tra từng dạng một. `msgfmt --check-format` đọc
  đúng tệp ở trên và thoát với mã `0`; một dạng làm rơi mất placeholder mà các
  dạng anh em của nó vẫn giữ sẽ được bên đó chấp nhận nhưng bị bên này từ
  chối.

`msgfmt` chỉ kiểm tra những tên placeholder mà nó phân tích được như Python
brace format, nên tên ASCII giúp mọi công cụ trong chuỗi đều xác thực được
thông điệp. Bản thân thư viện chấp nhận bất kỳ tên nào thỏa
`str.isidentifier()`.

## Template và các công cụ khác { #templates-and-other-tools }

t-string là cú pháp Python, nên thư viện này bao quát mã nguồn Python. Các
ngôn ngữ template vẫn tiếp tục dùng cơ chế i18n riêng của chúng —
`{% trans %}` của Jinja2, các template tag của Django — cùng các bộ trích
xuất Babel dành cho chúng. Tất cả đều đổ về cùng một catalog PO, nên một quy
trình dịch duy nhất vẫn bao quát được codebase hỗn hợp.

`pygettext` hiện chưa thể phân tích t-string, và đó là lý do việc trích xuất
đi qua Babel. Quy ước này đã được ghi lại trong [Đặc tả](spec.md) để một bộ
trích xuất khác, hay một `pygettext` tương lai, có thể nhắm tới nó.
