---
description: "هر نامی که gettext_tstrings صادر می‌کند: توابع، Translator، بستن بافتار، رشته‌های معوق، و خطاها."
---

# API

هر چه در ادامه می‌آید از `gettext_tstrings` صادر می‌شود. هیچ‌چیز دیگری
عمومی نیست. این صفحه مرجعِ امضاهاست؛ برای نمونه‌های کارشده از هر تابع
[راهنما](guide.md) را ببینید.

## ترجمه‌کردن { #translating }

هر تابع t-string خود را به‌صورت موضعی می‌گیرد و دو آرگومان کلیدواژه‌ای
می‌پذیرد: `translations` (که به بستهٔ بافتار و سپس به توابع سراسری
کتابخانهٔ استاندارد بازمی‌گردد) و `strict` (نگاه کنید به
[راهنما](guide.md#what-happens-when-a-catalog-is-wrong)).

| تابع | امضا |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | نام دیگرِ `gettext` |
| `ntr` | نام دیگرِ `ngettext` |

### `Translator`

یک dataclassِ منجمد که یک شیء ترجمه را می‌بندد تا محل‌های فراخوانی
مجبور به تکرارش نباشند.

```python
Translator(translations, strict=False)
```

فراخوانی‌پذیر است (`_(t"…")`) و `gettext` و `ngettext` و `pgettext` و
`npgettext` و نام‌های دیگرِ `tr` / `ntr` را با خود دارد.

## بستن بافتار { #context-binding }

| نام | کارکرد |
| --- | --- |
| `use_translations(translations)` | برای مدت یک بلوک `with` می‌بندد و سپس حالت پیشین را بازمی‌گرداند. |
| `set_translations(translations)` | بدون بلوک می‌بندد، برای چرخه‌های حیاتی که فریم‌ورک مدیریت می‌کند. |
| `get_translations()` | بستهٔ جاری را می‌خواند، یا `None`. |

بسته یک `ContextVar` است؛ پس به‌ازای هر بافتار جداست و زیر هم‌زمانی امن
است.

## رشته‌های معوق { #deferred-strings }

| نام | کارکرد |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | ترجمه را تا هر بار رندر به تعویق می‌اندازد. |
| `lazy_pgettext(context, template, /, *, strict=False)` | صورت بافتاری آن. |
| `LazyString` | آنچه هر دو برمی‌گردانند. از راه `str()` و `format()` به هر زبانی که در آن لحظه مقید است رندر می‌شود، با متنِ رندرشدهٔ خود برابر مقایسه می‌شود، و عمداً hash‌ناپذیر است. |

نمونه‌های کارشده، از جمله اینکه چرا `strict` جایش در محلِ تعریف است، در
[ترجمهٔ معوق](guide.md#deferred-translation) آمده است.

## سطح پایین‌تر { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

یک t-string را کامپایل می‌کند و از نقشهٔ ایستای کش‌شده‌اش دوباره
استفاده می‌کند.

### `CompiledTemplate`

| عضو | معنا |
| --- | --- |
| `.msgid` | شناسهٔ پایدار پیام در gettext. |
| `.placeholders` | نام‌های جای‌نگهدار به ترتیب نخستین ظهور. |
| `.render(pattern)` | یک الگو را اعتبارسنجی و رندر می‌کند. در ناسازگاری **همیشه استثنا پرتاب می‌کند**. |

## نوع‌ها و خطاها { #types-and-errors }

### `Translations`

یک `Protocol`ِ `runtime_checkable` برای چهار متد استاندارد، همه صرفاً
موضعی:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations` و `gettext.GNUTranslations` و `Translations`ِ
Babel هر سه آن را برآورده می‌کنند.

### استثناها

| کلاس | چه وقت پرتاب می‌شود |
| --- | --- |
| `TStringError` | کلاس پایه برای هر دو مورد زیر. |
| `InvalidTemplateError` | t-stringِ **مبدأ** قرارداد را می‌شکند — یک درون‌یابی پیچیده، یا نامی تکراری با قالب‌بندی متفاوت. |
| `InvalidTranslationError` | **ترجمه** آن را می‌شکند. زیر حالت آسان‌گیرِ پیش‌فرض، این در لاگ ثبت می‌شود و به‌جایش متن مبدأ رندر می‌شود. |

## نقطه‌های ورود استخراج { #extraction-entry-points }

هنگام نصب خودکار ثبت می‌شوند؛ با نام به آن‌ها ارجاع می‌دهید، نه با
import.

| گروه | نام | مصرف‌کننده |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | مقدار `method` در `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`، به‌طور خودکار. |

## کارایی { #performance }

روایت کامل — چه چیزی کش می‌شود، کش‌ها بر چه کلید می‌خورند، و اعدادِ
اندازه‌گیری‌شده — در [مسیر داغ](internals.md#the-hot-path) آمده است.
صورت کوتاهش: اعتبارسنجی کش می‌شود و هرگز رد نمی‌شود، و کل رندر کسری از
یک میکروثانیه هزینه دارد. سنجه را روی هدف خودتان اجرا کنید:

```console
uv run python benchmarks/runtime.py
```
