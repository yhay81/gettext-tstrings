---
description: "استخراج پیام‌های t-string با pybabel، و این‌که msgfmt و بررسی‌کنندهٔ همراهِ Babel چگونه کاتالوگ‌ها را اعتبارسنجی می‌کنند."
---

# استخراج

استخراج گامی است که همهٔ پیام‌های علامت‌گذاری‌شده را از کد مبدأ شما در
یک الگوی `.pot` برای مترجم‌ها گرد می‌آورد — گام ۳ از چرخهٔ
[آموزش](tutorial.md). این صفحه مرجع همان گام است: پیکربندی، نام‌های
تابع سفارشی، حالت سخت‌گیرانهٔ CI، و بررسی‌هایی که پس از آن از
کاتالوگ‌هایتان پاسداری می‌کنند.

استخراج به افزونهٔ `babel` نیاز دارد:

```console
python -m pip install "gettext-tstrings[babel]"
```

## گردش کار { #the-workflow }

فایل `babel.cfg` را بسازید:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

سپس فرمان‌های معمولی Babel را به کار ببرید:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` برای هر زبان یک بار اجرا می‌شود؛ از آن پس `pybabel update` هر
الگوی تازه را در کاتالوگ‌های موجود ادغام می‌کند. آن چرخهٔ تکرارشونده —
و معنای مدخل‌های `fuzzy`ِ آن برای یک انتشار — در
[در محیط عملیاتی](workflow.md#the-cycle-after-the-first-translation)
پیموده شده است.

استخراج‌کنندهٔ `gettext_tstrings` فراخوانی‌های معمولی `_()` و
`gettext()` و `ngettext()` را هم پوشش می‌دهد؛ پس یک نگاشت برای یک کدبیس
مخلوط بس است. این استخراج‌کننده `_()`، چهار نام استاندارد gettext،
نام‌های دیگر `tr()` / `ntr()` و صورت‌های معوق `lazy_gettext()` /
`lazy_pgettext()` را می‌شناسد.

!!! warning "توضیح‌های مترجم را با `-c` فعال کنید"

    `pybabel extract` تنها وقتی توضیح‌های مترجم را گرد می‌آورد که
    `-c "Translators:"` را پاس دهید؛ دقیقاً همان‌طور که برای
    فراخوانی‌های معمولی gettext چنین می‌کند. اگر آن را نگذارید، استخراج
    باز هم کار می‌کند — فقط توضیح‌ها هرگز به کاتالوگ نمی‌رسند، جایی که
    [ارزان‌ترین اهرم کیفیت](workflow.md#working-with-translators-and-platforms)
    در کل این چرخه‌اند.

## ثبت نام‌های تابع خودتان { #registering-your-own-function-names }

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

فایل ini یک رشته می‌دهد، نگاشت TOML یک فهرست، و درون یک رشته یا
فاصله‌ها نام‌ها را جدا می‌کنند یا ویرگول‌ها. هر چهار املا کار می‌کنند.

گزینه‌ها عبارت‌اند از `tr_functions`، `ntr_functions`،
`gettext_functions`، `ngettext_functions`، `pgettext_functions` و
`npgettext_functions`.

!!! danger "گزینهٔ `-k` به t-string نمی‌رسد"

    یک کمکیِ سفارشی مانند `mytr(t"…")` باید در یکی از گزینه‌های بالا
    نام برده شود. سازوکار `--keyword` در Babel نمی‌تواند یک لیترال
    t-string را بخواند؛ پس `pybabel extract -k mytr` نه چیزی می‌یابد و
    نه چیزی می‌گوید — پیام‌ها به‌سادگی از POT غایب‌اند. `-k` برای
    فراخوانی‌های معمولی gettext که در کنارشان استخراج می‌شوند همچنان
    کار می‌کند.

    تنها ترتیب استاندارد آرگومان‌ها پشتیبانی می‌شود: نخست پیام؛ برای
    `pgettext` بافتار سپس پیام؛ برای `npgettext` بافتار، سپس مفرد، سپس
    جمع.

## سهل‌گیر به‌صورت محلی، سخت‌گیر در CI { #lenient-locally-strict-in-ci }

به‌طور پیش‌فرض یک فایل بد اجرای کار را پایان نمی‌دهد:

- t-string‌ای که استخراج‌کننده رد می‌کند — دسترسی به خصیصه، یک عبارت،
  آرگومانی نابه‌جا — به‌صورت هشدار گزارش و رد می‌شود.
- فایلی که parse نمی‌شود به همان شیوه کنار گذاشته می‌شود.
- و همین‌طور فایلی که فقط `tokenize` نمی‌پذیرد در حالی که `ast`
  می‌پذیرد؛ همان که گذر خود Babel وگرنه بر سرش می‌شکست.

این تا وقتی مشغول ویرایش‌اید راحت است و وقتی نیستید خطرناک: پیامی که رد
شده، به‌سادگی **در POT غایب** است، پس هرگز ترجمه نمی‌شود و هیچ‌چیز هم
این را نمی‌گوید. هر جا که آدمی مراقب استخراج نیست، `strict = true` را در
گزینه‌های نگاشت بگذارید:

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

آنگاه هر هشدار بالا به شکست سخت تبدیل می‌شود. این را تنظیم محیط عملیاتی
بدانید و پیش‌فرض را تنظیم محلی.

## زنجیرهٔ ابزار موجودتان همین کاتالوگ‌ها را اعتبارسنجی می‌کند { #your-existing-toolchain-validates-these-catalogs }

Babel هر پیام استخراج‌شده را با یک پرچم استاندارد نشان می‌گذارد، و همان
یک خط است که بررسی جای‌نگهدارها را در ابزارهایی که همین حالا اجرا
می‌کنید روشن می‌کند:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

آن را `こんにちは {nombre}` ترجمه کنید و اشتباه بدون هیچ پیکربندی گرفته
می‌شود:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate همین بررسی را با نام [Python brace format][weblate-checks]
مستند کرده و پلتفرم‌های تجاری QA جای‌نگهدار خودشان را بر همین پرچم سوار
کرده‌اند. رفتار هر پلتفرم با خودِ اوست؛ دو ابزار پایین همان‌هایی‌اند که
این‌جا راستی‌آزمایی شده‌اند.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

افزون بر آن، این بسته یک **بررسی‌کنندهٔ** Babel هم ثبت می‌کند؛ پس
`pybabel compile` قواعد مشخصات را بر هر پیامی اعمال می‌کند که توضیحِ
نشانهٔ `gettext-tstrings` را دارد:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

برای پیام جمع، اشاره‌گر نامِ صورت را می‌برد؛ چون شمارهٔ خطی که Babel
گزارش می‌کند مال msgid است و یک بلوک روسی سه `msgstr` زیر آن دارد:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "«pybabel compile» باز هم `.mo` را می‌نویسد"

    خطای بالا گزارش می‌شود، وضعیت خروج `1` است — و کاتالوگ خراب به هر
    حال کامپایل می‌شود. تنها همان وضعیت خروج می‌تواند نگذارد یک خط
    لوله آن را روانه کند؛
    [دروازه‌های CI](workflow.md#what-ci-gates) گام ساختی را نشان می‌دهد
    که این اجازه را می‌دهد.

آن دو بررسی زائد بر هم نیستند. بررسی‌کنندهٔ این بسته دست‌کم در دو مورد
سخت‌گیرتر است:

- msgid‌ای که تنها آکولادهایش escape شده‌اند (`Config {{raw}} only`)
  هرگز پرچم `python-brace-format` نمی‌گیرد؛ پس هیچ ابزار بیرونی اصلاً
  اعتبارسنجی‌اش نمی‌کند.
- صورت‌های جمع یک به یک بررسی می‌شوند. `msgfmt --check-format` همان
  فایل بالا را می‌خواند و با `0` خارج می‌شود؛ صورتی که جای‌نگهداری را
  می‌اندازد که خواهرانش نگه داشته‌اند، آن‌جا پذیرفته و این‌جا رد
  می‌شود.

`msgfmt` تنها نام‌های جای‌نگهداری را بررسی می‌کند که بتواند به‌عنوان
قالب آکولادی پایتون parse کند؛ پس نام‌های ASCII همهٔ ابزارهای زنجیره را
قادر به اعتبارسنجی پیام نگه می‌دارند. خود کتابخانه هر نامی را
می‌پذیرد که `str.isidentifier()` بپذیرد.

## قالب‌ها و ابزارهای دیگر { #templates-and-other-tools }

t-string نحو پایتون است؛ پس این کتابخانه کد مبدأ پایتون را پوشش می‌دهد.
زبان‌های قالب همچنان i18n خودشان را به کار می‌برند — `{% trans %}`ِ
Jinja2، تگ‌های قالب Django — و استخراج‌کننده‌های Babel برایشان.
همه‌چیز به همان کاتالوگ PO می‌ریزد؛ پس یک گردش کار ترجمه هنوز یک کدبیس
مخلوط را پوشش می‌دهد.

`pygettext` امروز نمی‌تواند t-string را parse کند؛ برای همین است که
استخراج از راه Babel می‌رود. قرارداد در [مشخصات](spec.md) مکتوب است تا
استخراج‌کنندهٔ دیگری، یا یک `pygettext`ِ آینده، بتواند آن را هدف
بگیرد.
