---
description: "APIِ زمان اجرا: این‌که کدام نقطهٔ ورود را به کار ببرید، بستن یک کاتالوگ، زبانِ هر درخواست، رشته‌های معوق، مقدارهای آگاه از محل، و شیوهٔ گزارش‌شدن یک ترجمهٔ خراب."
---

# راهنما

این صفحه مرجعِ زمان اجراست: هر آنچه *کد برنامهٔ* شما پس از موجود شدن
کاتالوگ‌ها با این کتابخانه انجام می‌دهد. اگر هنوز چرخهٔ کامل —
علامت‌گذاری، استخراج، ترجمه، کامپایل، اجرا — را ندیده‌اید،
[آموزش](tutorial.md) آن را یک بار در پنج دقیقه می‌پیماید؛ ساختن و
اعتبارسنجی کاتالوگ‌ها در [استخراج](extraction.md) پوشش داده شده و
این‌که یک تیم چگونه چرخه را در گردش نگه می‌دارد — چرخه‌های به‌روزرسانی،
CI، پلتفرم‌های ترجمه — در [در محیط عملیاتی](workflow.md) آمده است.

## کدام نقطهٔ ورود را به کار ببرم؟ { #which-entry-point-should-i-use }

این بسته چند راه برای ترجمهٔ یک پیام صادر می‌کند، چون برنامه‌ها زبان را
به چند شیوهٔ متفاوت می‌بندند. بر پایهٔ این‌که برنامه‌تان چگونه تصمیم
می‌گیرد در چه زبانی است، انتخاب کنید:

| وضعیت شما | به کار ببرید |
| --- | --- |
| یک زبان برای کل فرایند — یک CLI، یک برنامهٔ رومیزی، یک اسکریپت | `Translator`، فراخوانده به نام `_` |
| یک زبان برای هر درخواست یا هر تسک ناهم‌زمان — یک برنامهٔ وب | `use_translations()` گرد کار، سپس `tr()` |
| پیامی که در زمان import تعریف می‌شود — برچسب یک فرم، یک enum، یک ثابت | `lazy_gettext()` یا `lazy_pgettext()` |
| شماری واژه‌بندی را تعیین می‌کند | `ngettext()` / `npgettext()`، در هر یک از صورت‌های بالا |
| رندر یک الگو بی‌آنکه کاتالوگی در کار باشد | `compile_template()` |

هر چه در ادامه می‌آید همین پنج مورد است، به همین ترتیب.

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
    name = request.user.display_name
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

`strict` همان‌جا که پیام نوشته می‌شود تعیین می‌شود، نه آن‌جا که رندر
می‌شود:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

رشتهٔ معوق هر جا که سرانجام به کار رود رندر می‌شود — درون یک قالب، یک
فرم، یک خط لاگ — و آن‌جا به‌ندرت می‌داند که این اجرا آزمون است یا محیط
عملیاتی. دادنِ `strict=True` هنگام تعریف است که می‌گذارد همان انتخابِ
[باصدا در CI، سهل‌گیر در محیط عملیاتی](#what-happens-when-a-catalog-is-wrong)
بر رشته‌ای هم اعمال شود که در محل فراخوانی‌اش رندر نمی‌شود.

صورت‌های جمع به شمارشی در زمان اجرا وابسته‌اند؛ پس آن‌ها را همان جایی
که شمارش معلوم است، مشتاقانه با `ngettext` رندر کنید.

## چند زبان به‌طور هم‌زمان { #several-languages-at-once }

یک درخواست اغلب به بیش از یک زبان نیاز دارد: صفحه‌ای که برای خواننده
رندر می‌شود و در همان حال اعلانی را برای حسابی با زبانی دیگر در صف
می‌گذارد، یا خلاصه‌ای که هر مشارکت‌کننده را به زبان خودش نقل می‌کند.
بسته‌ها تودرتو می‌شوند، و بیرون آمدن از بلوک درونی بلوک بیرونی را
بازمی‌گرداند.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

روی فهرستی از گیرندگان، این رشته‌های معوق‌اند که کار را انجام می‌دهند:
پیام یک بار، هنگام import، نوشته می‌شود و به‌ازای هر زبان یک بار رندر
می‌شود.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

بسته یک `ContextVar` است، نه پشته‌ای که روی یک شیء مشترک نگه داشته شود؛
پس درخواست‌هایی که هم‌پوشانی دارند نمی‌توانند زبان یکدیگر را بردارند —
از جمله در حالتی که بلوک‌هایشان را به همان ترتیبی که وارد شده‌اند *ترک
کنند*، که همان درهم‌بافتگی‌ای است که یک پشتهٔ push-down اشتباه می‌گیرد.
بارگذاری یک کاتالوگ به‌ازای هر زبان ارزان است: `gettext.translation()`
هر `.mo` را یک بار تجزیه می‌کند و کپی‌هایی می‌دهد که در کاتالوگِ
تجزیه‌شده شریک‌اند.

!!! warning "اینکه نخ کارگر بسته را به ارث ببرد یا نه، به ساخت بستگی دارد"

    یک `threading.Thread` ساده، یا `ThreadPoolExecutor.submit`، یا از
    رونوشتِ بافتارِ فراخواننده آغاز می‌شود یا از بافتاری تهی، و اینکه
    کدام‌یک باشد را `sys.flags.thread_inherit_context` تعیین می‌کند — که
    در ساخت‌های free-threaded به‌طور پیش‌فرض درست است و در همه‌جای دیگر
    نادرست. پس یک کد یکسان روی 3.14t زبانِ بسته‌شده را می‌نمایاند و روی
    3.14 کاتالوگ سراسریِ gettext در سطح فرایند را. بافتار را به‌جای تکیه
    بر مقدار پیش‌فرض، صریحاً با خود ببرید:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` این کار را از پیش برایتان انجام می‌دهد.

## مقدارهای آگاه از محل { #locale-aware-values }

این کتابخانه تصمیم می‌گیرد که یک مقدار *کجا* در پیام ترجمه‌شده ظاهر
شود. خودِ مقدار را بومی‌سازی نمی‌کند. `{amount:,.2f}` یک مشخصهٔ
قالب‌بندی پایتون با رفتار ثابت است — یک ویرگول هر سه رقم و یک نقطه پیش
از اعشار — و هر زبانی که پیام در آن باشد، همان نویسه‌ها را تولید
می‌کند:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

آلمانی همان عدد را `1.234,50` می‌نویسد، فرانسوی `1 234,50`، و هندی
`1234567` را به‌صورت `12,34,567` گروه‌بندی می‌کند نه `1,234,567`.
عددها، ارزها، تاریخ‌ها، زمان‌ها و یکاها به [Babel][babel-numbers] تعلق
دارند. نخست مقدار را قالب‌بندی کنید، سپس رشتهٔ آماده را جای‌گذاری کنید:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

در یک پیام شمارشی، عدد دو کار می‌کند — صورت جمع را برمی‌گزیند و در متن
هم ظاهر می‌شود — و تنها دومی بومی‌سازی می‌شود. شمارِ خام را برای گزینش
نگه دارید و رشتهٔ قالب‌بندی‌شده را برای نمایش پاس دهید:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

قالب‌بندی پیش از فراخوانی همان چیزی است که مشخصهٔ قالب‌بندی را هم بیرون
از کاتالوگ نگه می‌دارد: آنچه مترجم می‌بیند تکه‌ای متنِ آماده است، نه یک
عدد به‌علاوهٔ دستورهای رندرکردنش.

## وقتی کاتالوگ خراب است چه می‌شود { #what-happens-when-a-catalog-is-wrong }

اگر جای‌نگهدارهای یک ترجمه با مبدأ نخوانند — فیلدی غایب، ناشناخته یا
دوباره‌قالب‌بندی‌شده که از اعتبارسنجی گذشته است؛ از یک MOِ دستی‌ویرایش‌شده،
یک کاتالوگ عرضه‌کننده، یا خطِ لوله‌ای که بررسی‌کننده را رد می‌کند —
رفتار پیش‌فرض رندرِ پیام مبدأ است، نه پرتاب استثنا. این آینهٔ پیمان
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

این پیام‌ها برای کسی نوشته شده‌اند که می‌تواند کاری برایشان بکند، که
برای مشکل کاتالوگ بیشتر مترجم است تا برنامه‌نویس — پس هر جا جای‌نگهداری
حاضر به نظر می‌رسد اما نیست، پیام به‌جای تکرار این‌که غایب است، توضیح
می‌دهد چرا. آکولادهای تمام‌عرض، `{{name}}`ِ دوبرابرشده، فاصلهٔ نشکنِ
نامرئی، حرفی سیریلی میان حروف لاتین: هر یک واژه‌بندی خود را دارد و
همراه با نمونه در
[برای مترجمان](translators.md#reading-a-failure-message) فهرست شده است.
آن صفحه چنان نوشته شده که به دست کسی داده شود که `.po` را ویرایش می‌کند.

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
