---
description: "‏pybabel کے ساتھ t-string پیغامات نکالنا، اور یہ کہ msgfmt اور ہمراہ آنے والا Babel چیکر کیٹلاگوں کی توثیق کیسے کرتے ہیں۔"
---

# استخراج

استخراج وہ مرحلہ ہے جو آپ کے ماخذ کوڈ میں سے ہر نشان زد پیغام جمع کر کے
مترجموں کے لیے ایک `.pot` ٹیمپلیٹ میں ڈالتا ہے — [ٹیوٹوریل](tutorial.md) کے
چکر کا تیسرا مرحلہ۔ یہ صفحہ اسی مرحلے کا حوالہ ہے: تشکیل، اپنے فنکشن نام، CI
کا سخت موڈ، اور وہ جانچیں جو بعد میں آپ کے کیٹلاگوں کی حفاظت کرتی ہیں۔

استخراج کو `babel` اضافی جزو درکار ہے:

```console
python -m pip install "gettext-tstrings[babel]"
```

## ورک فلو { #the-workflow }

`babel.cfg` بنائیے:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

پھر عام Babel کمانڈز استعمال کیجیے:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` ہر زبان کے لیے ایک بار چلتا ہے؛ اس کے بعد `pybabel update` ہر تازہ
ٹیمپلیٹ کو موجودہ کیٹلاگوں میں سمو دیتا ہے۔ وہ بار بار آنے والا دور — اور
اس کے `fuzzy` اندراج کسی ریلیز کے لیے کیا معنی رکھتے ہیں — یہ
[پروڈکشن میں](workflow.md#the-cycle-after-the-first-translation) بیان ہوا ہے۔

`gettext_tstrings` استخراج کار عام `_()`، `gettext()` اور `ngettext()` کالیں
بھی سنبھالتا ہے، لہٰذا ایک ہی نقشہ ملے جلے کوڈ بیس کو ڈھانپ لیتا ہے۔ یہ
`_()` کو، gettext کے چار معیاری ناموں کو، `tr()` / `ntr()` کے دوسرے ناموں
کو، اور مؤخر `lazy_gettext()` / `lazy_pgettext()` کو پہچانتا ہے۔

!!! warning "`-c` سے مترجموں کے تبصرے فعال کیجیے"

    `pybabel extract` مترجموں کے تبصرے صرف اُس وقت جمع کرتا ہے جب آپ
    `-c "Translators:"` دیں، بالکل ویسے ہی جیسے عام gettext کالوں کے لیے
    کرتا ہے۔ اسے چھوڑ دیجیے تو استخراج پھر بھی چلتا ہے — تبصرے بس کیٹلاگ تک
    کبھی نہیں پہنچتے، جہاں وہ پورے ورک فلو کا
    [سب سے سستا معیاری لیور](workflow.md#working-with-translators-and-platforms)
    ہوتے ہیں۔

## اپنے فنکشن نام رجسٹر کرنا { #registering-your-own-function-names }

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

ini فائل ایک سٹرنگ دیتی ہے، TOML نقشہ ایک فہرست دیتا ہے، اور سٹرنگ کے اندر
نام خالی جگہ یا کوما سے جدا ہوتے ہیں۔ چاروں املا کام کرتے ہیں۔

اختیارات یہ ہیں: `tr_functions`، `ntr_functions`، `gettext_functions`،
`ngettext_functions`، `pgettext_functions` اور `npgettext_functions`۔

!!! danger "`-k` کسی t-string تک نہیں پہنچتا"

    `mytr(t"…")` جیسے اپنے مددگار کا نام اوپر دیے گئے اختیارات میں سے کسی
    ایک میں دینا لازم ہے۔ Babel کا `--keyword` سازوسامان کسی t-string لٹریل
    کو پڑھ ہی نہیں سکتا، لہٰذا `pybabel extract -k mytr` کو کچھ نہیں ملتا
    اور وہ کہتا بھی کچھ نہیں — پیغامات بس POT میں سے غائب رہتے ہیں۔ ساتھ
    نکلنے والی عام gettext کالوں کے لیے `-k` بدستور کام کرتا ہے۔

    صرف معیاری آرگیومنٹ ترتیب کی حمایت ہے: پہلے پیغام؛ `pgettext` کے لیے
    پہلے سیاق پھر پیغام؛ `npgettext` کے لیے سیاق، پھر واحد، پھر جمع۔

## مقامی طور پر نرم، CI میں سخت { #lenient-locally-strict-in-ci }

طے شدہ طور پر ایک خراب فائل پورا چکر ختم نہیں کرتی:

- جس t-string کو استخراج کار مسترد کرے — خصوصیات تک رسائی، کوئی اظہاریہ،
  کوئی غلط آرگیومنٹ — اس کی اطلاع وارننگ کے طور پر دی جاتی ہے اور اسے چھوڑ
  دیا جاتا ہے۔
- جو فائل پارس نہ ہو، اسے بھی اسی طرح چھوڑ دیا جاتا ہے۔
- اور وہ فائل بھی جسے صرف `tokenize` مسترد کرے جبکہ `ast` قبول کر لے، اور
  جس پر خود Babel کا اپنا دور ورنہ رک جاتا۔

جب آپ ترمیم کر رہے ہوں تو یہ سہولت ہے، اور جب نہ کر رہے ہوں تو خطرہ:
چھوڑا گیا پیغام سیدھا **POT میں سے غائب** ہوتا ہے، لہٰذا اس کا ترجمہ کبھی نہیں
ہوتا اور کوئی یہ بتاتا بھی نہیں۔ جہاں کہیں استخراج کو کوئی انسان نہ دیکھ رہا
ہو، وہاں نقشے کے اختیارات میں `strict = true` رکھ دیجیے:

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

اوپر کی ہر وارننگ تب سخت ناکامی بن جاتی ہے۔ اسے پروڈکشن کی ترتیب سمجھیے اور
طے شدہ کو مقامی ترتیب۔

## آپ کا موجودہ اوزار سلسلہ ان کیٹلاگوں کی توثیق کرتا ہے { #your-existing-toolchain-validates-these-catalogs }

Babel ہر نکالے گئے پیغام پر ایک معیاری نشان لگاتا ہے، اور وہی ایک سطر اُن
اوزاروں میں پلیس ہولڈر کی جانچ کو فعال کر دیتی ہے جو آپ پہلے ہی چلا رہے ہیں:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

اس کا ترجمہ `こんにちは {nombre}` کر دیجیے تو غلطی بغیر کسی تشکیل کے پکڑی
جاتی ہے:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate اسی جانچ کو [Python brace format][weblate-checks] کے نام سے دستاویز
کرتا ہے، اور تجارتی پلیٹ فارموں کی اپنی پلیس ہولڈر QA اسی نشان پر مبنی ہے۔
ہر پلیٹ فارم کا رویہ اس کا اپنا ہے؛ نیچے دیے گئے دو اوزار وہ ہیں جن کی یہاں
تصدیق کی گئی ہے۔

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

اس کے علاوہ، پیکیج ایک Babel **چیکر** رجسٹر کرتا ہے، لہٰذا `pybabel compile`
تصریح کے اصول ہر اُس پیغام پر لاگو کرتا ہے جو `gettext-tstrings` کا نشان
تبصرہ اٹھائے ہو:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

جمع والے پیغام کے لیے اشارہ صورت کا نام لیتا ہے، کیونکہ Babel جو سطر نمبر
بتاتا ہے وہ msgid کا ہوتا ہے اور روسی بلاک کے نیچے تین `msgstr` ہوتے ہیں:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` پھر بھی `.mo` لکھ دیتا ہے"

    اوپر والی غلطی کی اطلاع دی جاتی ہے، خارجی حالت `1` ہوتی ہے — اور خراب
    کیٹلاگ پھر بھی کمپائل ہو جاتا ہے۔ صرف وہی خارجی حالت کسی پائپ لائن کو اسے
    بھیجنے سے روک سکتی ہے؛ [CI کیا روکتی ہے](workflow.md#what-ci-gates) وہ
    بلڈ مرحلہ دکھاتا ہے جو یہ کر دیتا ہے۔

دونوں جانچیں فالتو نہیں ہیں۔ پیکیج کا چیکر کم از کم دو صورتوں میں زیادہ سخت
ہے:

- جس msgid میں بریسز صرف ایسکیپ شدہ ہوں (`Config {{raw}} only`)، اسے
  `python-brace-format` نشان ملتا ہی نہیں، لہٰذا کوئی بیرونی اوزار اس کی
  توثیق سرے سے نہیں کرتا۔
- جمع کی صورتیں ایک ایک کر کے جانچی جاتی ہیں۔ `msgfmt --check-format` اوپر
  والی وہی فائل پڑھ کر `0` پر نکل جاتا ہے؛ جو صورت کوئی ایسا پلیس ہولڈر گرا
  دے جو اس کی بہنیں رکھتی ہوں، وہ وہاں قبول ہوتی ہے اور یہاں مسترد۔

`msgfmt` صرف اُنہی پلیس ہولڈر ناموں کو جانچتا ہے جنہیں وہ Python brace format
کے طور پر پارس کر سکے، لہٰذا ASCII نام سلسلے کے ہر اوزار کو پیغام کی توثیق
کے قابل رکھتے ہیں۔ لائبریری خود ہر ایسا نام قبول کرتی ہے جس پر
`str.isidentifier()` صادق ہو۔

## ٹیمپلیٹ اور دوسرے اوزار { #templates-and-other-tools }

t-string Python کی نحو ہیں، لہٰذا یہ لائبریری Python ماخذ کو ڈھانپتی ہے۔
ٹیمپلیٹ زبانیں اپنا i18n استعمال کرتی رہتی ہیں — Jinja2 کا `{% trans %}`،
Django کے ٹیمپلیٹ ٹیگ — اور Babel کے ان کے لیے استخراج کار۔ سب کچھ اسی ایک PO
کیٹلاگ میں جاتا ہے، لہٰذا ایک ہی ترجمے کا ورک فلو ملے جلے کوڈ بیس کو اب بھی
ڈھانپ لیتا ہے۔

`pygettext` آج t-string پارس نہیں کر سکتا، اسی لیے استخراج Babel سے ہو کر
گزرتا ہے۔ اصول [تصریح](spec.md) میں لکھ دیا گیا ہے تاکہ کوئی دوسرا استخراج
کار، یا مستقبل کا `pygettext`، اسے ہدف بنا سکے۔
