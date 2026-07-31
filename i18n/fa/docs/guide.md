---
description: "APIِ زمان اجرا: بستن یک کاتالوگ، زبانِ هر درخواست، رشته‌های معوق، و شیوهٔ گزارش‌شدن یک ترجمهٔ خراب."
---

# راهنما

این صفحه مرجعِ زمان اجراست: هر آنچه *کد برنامهٔ* شما پس از موجود شدن
کاتالوگ‌ها با این کتابخانه انجام می‌دهد. اگر هنوز چرخهٔ کامل —
علامت‌گذاری، استخراج، ترجمه، کامپایل، اجرا — را ندیده‌اید،
[آموزش](tutorial.md) آن را یک بار در پنج دقیقه می‌پیماید؛ ساختن و
اعتبارسنجی کاتالوگ‌ها در [استخراج](extraction.md) پوشش داده شده و
این‌که یک تیم چگونه چرخه را در گردش نگه می‌دارد — چرخه‌های به‌روزرسانی،
CI، پلتفرم‌های ترجمه — در [در محیط عملیاتی](workflow.md) آمده است.

## بستن یک کاتالوگ { #binding-a-catalog }

شکل پیشنهادی، آینهٔ کاربرد کلاس‌محور خود gettext است: یک شیء ترجمهٔ
استاندارد را یک بار ببندید و پردازندهٔ فراخوانی‌پذیر را به نام `_` به
کار ببرید.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

توابع سطح ماژول از نام‌های کتابخانهٔ استاندارد و قرارداد فراخوانیِ
صرفاً-موضعیِ آن پیروی می‌کنند:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` و `ntr` نام‌های دیگرِ دقیقاً همان `gettext` و `ngettext` هستند.

## زبانِ هر درخواست { #per-request-language }

یک فریم‌ورک وب برای هر درخواست یک زبان برمی‌گزیند. ترجمه‌های آن درخواست
را به بافتار جاری ببندید تا هر فراخوانی سطح ماژول به همان زبان حل شود،
به‌طور امن در میان درخواست‌های هم‌زمان:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` بدون بلوک `with` می‌بندد، برای
فریم‌ورک‌هایی که چرخهٔ حیات درخواست را خودشان مدیریت می‌کنند؛
`get_translations()` بستهٔ جاری را می‌خواند. آرگومان صریح
`translations=` همیشه بر بافتار مقدم است، و بافتارِ بسته‌نشده به توابع
سراسریِ نصب‌شدهٔ gettext در کتابخانهٔ استاندارد بازمی‌گردد. نمونه‌های
کامل برای Flask و میان‌افزار ASGI در صفحهٔ
[در محیط عملیاتی](workflow.md#binding-a-language-at-runtime) آمده‌اند.

## ترجمهٔ معوق { #deferred-translation }

یک t-string مقدارهایش را مشتاقانه ثبت می‌کند، و این برای رشته‌ای که در
زمان import تعریف می‌شود نادرست است — برچسب یک فرم، مقدار یک enum، یک
ثابت ماژول — که باید در هر زبانی رندر شود که هنگام *استفاده* فعال است.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

یک `LazyString` از راه `str()` و `format()` و f-string‌ها رندر می‌شود و
با متن رندرشده‌اش برابر مقایسه می‌شود.

!!! note "عمداً hash‌ناپذیر"

    متن یک `LazyString` به زبان فعال بسته است؛ پس hash آن با هر تعویض
    زبان تغییر می‌کرد و هر set یا dict نگه‌دارنده‌اش را بی‌سروصدا خراب
    می‌کرد. اگر به کلید نیاز دارید، اول `str()` بگیرید.

صورت‌های جمع به شمارشی در زمان اجرا وابسته‌اند؛ پس آن‌ها را همان جایی
که شمارش معلوم است، مشتاقانه با `ngettext` رندر کنید.

## وقتی کاتالوگ خراب است چه می‌شود { #what-happens-when-a-catalog-is-wrong }

اگر جای‌نگهدارهای یک ترجمه با مبدأ نخوانند — فیلدی غایب، ناشناخته یا
دوباره‌قالب‌بندی‌شده که از اعتبارسنجی گذشته است؛ از یک MOِ دستی‌ویرایش‌شده،
یک کاتالوگ عرضه‌کننده، یا خطِ لوله‌ای که بررسی‌کننده را رد می‌کند —
رفتار پیش‌فرض بازتولید متن مبدأ است، نه پرتاب استثنا. این آینهٔ پیمان
خود gettext است که کاتالوگ بد هرگز برنامه را نمی‌شکند.

با ترجمه‌شدن `Hello {name}` به `こんにちは {nombre}`، رندر موفق می‌شود
و یک هشدار به لاگر `gettext_tstrings` می‌رود:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

هشدار برای هر پیام و الگو یک بار شلیک می‌شود، نه برای هر رندر؛ پس یک
مدخل خراب کاتالوگ، لاگ را سیل‌آسا پر نمی‌کند.

برای آزمون‌ها و CI، شکستِ باصدا را انتخاب کنید:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

آن‌گاه همان جست‌وجو استثنا پرتاب می‌کند و همان جمله را — بدون نیمهٔ
«using source text» — با خود می‌برد:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## خواندن پیام یک شکست { #reading-a-failure-message }

این پیام‌ها برای کسی نوشته شده‌اند که می‌تواند کاری برایشان بکند، که
برای مشکل کاتالوگ بیشتر مترجم است تا برنامه‌نویس. گزارشِ صرف این‌که
`{name}` غایب است بن‌بست است وقتی خواننده همان نویسه‌ها را جلوی چشمش
می‌بیند؛ پس هر جا جای‌نگهداری حاضر به نظر می‌رسد اما نیست، پیام می‌گوید
چرا. در برابر مبدأ `Hello {name}`، هر یک از این‌ها زیر
`translation does not match the source placeholders:` گزارش می‌شود

| ترجمه می‌گوید | دلیلی که می‌دهد |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

نویسه‌هایی که دیده نمی‌شوند برخورد ویژهٔ خود را دارند. فاصلهٔ نشکن درون
آکولادها چیزی است که یک روش ورودی تولید می‌کند و هیچ ویرایشگری نشان
نمی‌دهد؛ پس پیام آن را با کدنقطه چاپ می‌کند، نه با نام بردن از
نویسه‌ای که خواننده نمی‌تواند بیابد:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

نامی که حروفش نظام‌های نوشتاری را می‌آمیزد — حالت هم‌نگاره، آن‌جا که
`а`ِ سیریلی از لاتین بازشناختنی نیست — دو بار نشان داده می‌شود، یک بار
خوانا و یک بار escape‌شده، که تنها صورتی است که آن دو را از هم جدا
می‌کند:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

همین ابهام‌زدایی وقتی هم به کار می‌آید که نامی یونانی یا سیریلی که
یک‌سره در یک خط نوشته شده با نام مبدأ ASCII تعارض کند، از جمله حالت
تک‌حرفیِ `a`ِ لاتین / `а`ِ سیریلی.

## رندر یک الگو بدون کاتالوگ { #rendering-a-pattern-without-a-catalog }

`compile_template` همان سازوکار را یک سطح پایین‌تر عرضه می‌کند: یک
t-string را به msgid آن به‌علاوهٔ مجموعه‌ای بسته از مقدارها تبدیل
می‌کند و هر الگویی را که به آن بدهید رندر می‌کند.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` با همان قواعد اعتبارسنجی می‌کند و در ناسازگاری **همیشه استثنا
پرتاب می‌کند**. این‌جا حالت آسان‌گیر وجود ندارد: آسان‌گیری برای آن هست
که جست‌وجوی *کاتالوگ* بتواند به متن مبدأ فرو بنشیند، و الگویی که خودتان
پاس داده‌اید چیزی ندارد که به آن فرو بنشیند.

## امنیت و دامنه { #safety-and-scope }

این معتبر است:

```python
tr(t"Hello {name}")
```

این‌ها عمداً رد می‌شوند:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

اول یک مقدار معنادار محاسبه کنید:

```python
name = user.display_name()
tr(t"Hello {name}")
```

این محدودیت کلیدهای پایدار کاتالوگ می‌سازد، به مترجم‌ها نام‌های سودمند
می‌دهد، و نمی‌گذارد رشتهٔ ترجمه‌شده به یک زبان عبارت بدل شود.

تضمین به *ساختار و قالب‌بندی* محدود است: ترجمه هرگز ارزیابی نمی‌شود و
هرگز نمی‌تواند دسترسی به خصیصه، فراخوانی، تبدیل یا مشخصهٔ قالب‌بندی
اضافه کند. دو چیز بر عهدهٔ فراخواننده می‌ماند، درست مانند gettext در
کتابخانهٔ استاندارد — **escape کردن** خروجی رندرشده برای مقصدش (HTML،
شل، پایانه) و **سلامت کاتالوگ**؛ چرا که کاتالوگ متخاصم می‌تواند با
تکرار یک جای‌نگهدار اندازهٔ خروجی را چند برابر کند، و این در ذات هر
i18nِ جای‌نگهدارمحور است.
