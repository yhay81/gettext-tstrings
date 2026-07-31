---
description: "رن ٹائم API: کیٹلاگ باندھنا، فی درخواست زبان، مؤخر سٹرنگز، اور ٹوٹے ہوئے ترجمے کی اطلاع کیسے دی جاتی ہے۔"
---

# رہنما

یہ صفحہ رن ٹائم کا حوالہ ہے: کیٹلاگ موجود ہو جانے کے بعد آپ کا *ایپلی کیشن
کوڈ* اس لائبریری کے ساتھ جو کچھ کرتا ہے، وہ سب۔ اگر آپ نے ابھی تک پورا چکر
نہیں دیکھا — نشان زدگی، استخراج، ترجمہ، کمپائل، چلانا — تو
[ٹیوٹوریل](tutorial.md) اسے پانچ منٹ میں ایک بار طے کرا دیتا ہے؛ کیٹلاگ
بنانا اور ان کی توثیق [استخراج](extraction.md) میں ہے، اور کوئی ٹیم اس چکر
کو کیسے چلاتی رہتی ہے — اپ ڈیٹ کے دور، CI، ترجمے کے پلیٹ فارم — یہ
[پروڈکشن میں](workflow.md) ہے۔

## کیٹلاگ باندھنا { #binding-a-catalog }

تجویز کردہ شکل gettext کے کلاس پر مبنی استعمال کی آئینہ دار ہے: ایک معیاری
ترجمہ آبجیکٹ ایک بار باندھیے اور قابلِ استدعا پروسیسر کو `_` کے طور پر
استعمال کیجیے۔

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

ماڈیول کی سطح کے فنکشن معیاری لائبریری کے ناموں اور اس کے صرف موضعی کال کے
اسلوب کی پیروی کرتے ہیں:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` اور `ntr` بالکل `gettext` اور `ngettext` کے دوسرے نام ہیں۔

## فی درخواست زبان { #per-request-language }

ویب فریم ورک ہر درخواست کے لیے ایک زبان چنتا ہے۔ درخواست کے ترجمے موجودہ سیاق
سے باندھ دیجیے اور ماڈیول کی سطح کی ہر کال اُسی زبان پر حل ہو گی، ہم وقت
درخواستوں کے درمیان بحفاظت:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` `with` بلاک کے بغیر باندھتا ہے، اُن
فریم ورکس کے لیے جو درخواست کا دورانِ حیات خود سنبھالتے ہیں؛
`get_translations()` موجودہ بندش پڑھتا ہے۔ صریح `translations=` آرگیومنٹ
ہمیشہ سیاق پر بھاری رہتا ہے، اور غیر بندھا ہوا سیاق معیاری لائبریری کے عالمی
طور پر نصب gettext فنکشنوں پر واپس آ جاتا ہے۔ Flask اور ASGI مڈل ویئر کی عملی
مثالیں [پروڈکشن میں](workflow.md#binding-a-language-at-runtime) والے صفحے پر
ہیں۔

## مؤخر ترجمہ { #deferred-translation }

t-string اپنی قدریں فوراً پکڑ لیتی ہے، جو اُس سٹرنگ کے لیے غلط ہے جو import
کے وقت متعین ہو — کوئی فارم لیبل، کوئی enum قدر، کوئی ماڈیول مستقل — اور جسے
اُس زبان میں رینڈر ہونا ہے جو اس کے *استعمال* کے وقت فعال ہو۔

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` `str()`، `format()` اور f-string کے ذریعے رینڈر ہوتی ہے، اور
اپنے رینڈر شدہ متن کے برابر موازنہ کرتی ہے۔

!!! note "جان بوجھ کر ناقابلِ ہیش"

    `LazyString` کا متن فعال زبان پر منحصر ہے، لہٰذا زبان بدلنے پر ہیش بھی
    بدل جاتی اور اسے تھامے ہوئے کسی بھی set یا dict کو خاموشی سے خراب کر
    دیتی۔ اگر آپ کو کلید درکار ہو تو پہلے `str()` پکاریے۔

`strict` کا فیصلہ وہاں ہوتا ہے جہاں پیغام *لکھا* جاتا ہے، وہاں نہیں جہاں وہ
رینڈر ہوتا ہے:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

مؤخر سٹرنگ وہیں رینڈر ہوتی ہے جہاں وہ آخرکار استعمال ہوتی ہے — کسی ٹیمپلیٹ
کے اندر، کسی فارم میں، کسی لاگ لائن میں — اور اُس جگہ کو شاذ ہی معلوم ہوتا
ہے کہ یہ ٹیسٹ کا چکر ہے یا پروڈکشن۔ تعریف کے مقام پر `strict=True` دینا ہی
وہ چیز ہے جو [CI میں بلند آواز، پروڈکشن میں نرم](#what-happens-when-a-catalog-is-wrong)
والے اسی انتخاب کو ایسی سٹرنگ پر بھی لاگو ہونے دیتی ہے جو اپنے کال سائٹ پر
رینڈر نہیں ہوتی۔

جمع کی صورتیں رن ٹائم کی گنتی پر منحصر ہیں، لہٰذا انہیں `ngettext` کے ساتھ
وہیں فوراً رینڈر کیجیے جہاں گنتی معلوم ہو۔

## ایک ساتھ کئی زبانیں { #several-languages-at-once }

اکثر ایک ہی درخواست کو ایک سے زیادہ زبانیں درکار ہوتی ہیں: ایک صفحہ جو قاری کے
لیے رینڈر ہو اور ساتھ ہی کسی ایسے کھاتے کے لیے اطلاع قطار میں لگا دے جو کسی اور
زبان پر مقرر ہو، یا ایسا خلاصہ جو ہر شریک کو اُسی کی زبان میں نقل کرے۔ بندشیں
نیسٹ ہوتی ہیں، اور اندرونی بلاک سے نکلتے ہی بیرونی بندش بحال ہو جاتی ہے۔

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

وصول کنندگان کی فہرست پر مؤخر سٹرنگز کام سنبھال لیتی ہیں: پیغام ایک ہی بار،
import کے وقت لکھا جاتا ہے، اور فی زبان ایک بار رینڈر ہوتا ہے۔

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

بندش ایک `ContextVar` ہے، کسی مشترک آبجیکٹ پر رکھا ہوا سٹیک نہیں، لہٰذا باہم
متداخل درخواستیں ایک دوسرے کی زبان نہیں اٹھا سکتیں — بشمول اُس صورت کے جہاں وہ
اپنے بلاک اُسی ترتیب سے *چھوڑتی* ہیں جس ترتیب سے ان میں داخل ہوئی تھیں، اور یہی
وہ تداخل ہے جسے پُش ڈاؤن سٹیک غلط سنبھالتا ہے۔ فی زبان کیٹلاگ لوڈ کرنا سستا
ہے: `gettext.translation()` ہر `.mo` کا تجزیہ ایک بار کرتا ہے اور ایسی نقول
دیتا ہے جو تجزیہ شدہ کیٹلاگ آپس میں مشترک رکھتی ہیں۔

!!! warning "کارکن تھریڈ بغیر بندش کے شروع ہوتا ہے"

    سادہ `threading.Thread`، یا `ThreadPoolExecutor.submit`، ایک تازہ سیاق سے
    شروع ہوتا ہے اور بندش وراثت میں نہیں لیتا — کال پروسیس کے عالمی gettext
    کیٹلاگ پر واپس آ جاتی ہے۔ سیاق کو صراحتاً ساتھ لے جائیے:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` یہ کام آپ کے لیے پہلے ہی کر دیتا ہے۔

## کیٹلاگ غلط ہو تو کیا ہوتا ہے { #what-happens-when-a-catalog-is-wrong }

اگر ترجمے کے پلیس ہولڈر ماخذ سے میل نہ کھائیں — کوئی غائب، نامعلوم یا دوبارہ
فارمیٹ شدہ فیلڈ جو توثیق سے بچ نکلا ہو، کسی ہاتھ سے مرتب کیے گئے MO سے،
بیرونی کیٹلاگ سے، یا ایسی پائپ لائن سے جو چیکر چھوڑ دیتی ہے — تو طے شدہ رویہ
یہ ہے کہ استثنا اٹھانے کے بجائے ماخذ متن دہرا دیا جائے۔ یہ خود gettext کے اُس
معاہدے کی آئینہ داری ہے کہ خراب کیٹلاگ ایپلی کیشن کو کبھی نہیں توڑتا۔

اگر `Hello {name}` کا ترجمہ `こんにちは {nombre}` ہو، تو رینڈر کامیاب رہتا ہے
اور `gettext_tstrings` لاگر کو ایک وارننگ جاتی ہے:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

وارننگ فی پیغام اور فی پیٹرن ایک بار چلتی ہے، ہر رینڈر پر ایک بار نہیں،
چنانچہ ٹوٹا ہوا کیٹلاگ اندراج لاگ کو بھر نہیں دیتا۔

ٹیسٹ اور CI کے لیے بلند آواز میں ناکام ہونے کا انتخاب یوں کیجیے:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

تب وہی تلاش استثنا اٹھاتی ہے، اور وہی جملہ اٹھائے ہوئے، بس "using source
text" والا نصف اس میں نہیں ہوتا:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## ناکامی کا پیغام پڑھنا { #reading-a-failure-message }

یہ پیغامات اُس کے لیے لکھے گئے ہیں جو ان پر عمل کر سکے، اور کیٹلاگ کے مسئلے
میں وہ پروگرامر سے زیادہ اکثر کوئی مترجم ہوتا ہے۔ صرف یہ بتا دینا کہ
`{name}` غائب ہے، ایک بند گلی ہے جب پڑھنے والے کو وہی حروف اپنے سامنے نظر آ
رہے ہوں، لہٰذا جہاں کوئی پلیس ہولڈر موجود لگتا ہو مگر ہو نہ، وہاں پیغام وجہ
بھی بتاتا ہے۔ ماخذ `Hello {name}` کے مقابل، ان میں سے ہر ایک کی اطلاع
`translation does not match the source placeholders:` کے تحت دی جاتی ہے۔

| ترجمہ کیا کہتا ہے | جو وجہ وہ بتاتا ہے |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` غائب ہے (اس کے گرد کے بریسز ASCII کے `{` اور `}` نہیں ہیں) |
| `こんにちは {{name}}` | `{name}` غائب ہے (وہ `{{name}}` لکھا ہے، جو ثابت بریس کو ایسکیپ کرنے کا طریقہ ہے) |
| `こんにちは name` | `{name}` غائب ہے (نام تو آیا ہے، مگر بریسز کے اندر نہیں) |
| `こんにちは {名前}` | `{name}` غائب ہے؛ `{名前}` ماخذ پیغام میں نہیں ہے |

جو حروف دیکھے نہیں جا سکتے، ان کا الگ سلوک ہے۔ بریسز کے اندر بغیر توڑ والی
خالی جگہ (no-break space) وہ چیز ہے جو کوئی ان پٹ میتھڈ پیدا کرتا ہے اور
کوئی ایڈیٹر دکھاتا نہیں، لہٰذا پیغام اسے ایسے حرف کا نام لینے کے بجائے —
جسے پڑھنے والا ڈھونڈ ہی نہیں سکتا — اس کے کوڈ پوائنٹ سے چھاپ دیتا ہے:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

جس نام کے حروف مختلف رسم الخط ملا دیں — یعنی ہم شکل حروف والا معاملہ، جہاں
سریلک `а` لاطینی `a` سے الگ پہچانا ہی نہیں جا سکتا — اسے دو بار دکھایا جاتا
ہے، ایک بار پڑھنے کے قابل صورت میں اور ایک بار ایسکیپ شدہ، اور یہی وہ واحد
صورت ہے جو دونوں میں فرق بتاتی ہے:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

یہی تفریق اُس وقت بھی لاگو ہوتی ہے جب پورا کا پورا ایک ہی رسم الخط میں لکھا
ہوا یونانی یا سریلک نام کسی ASCII ماخذ نام سے ٹکرائے، بشمول ایک حرفی لاطینی
`a` / سریلک `а` والے معاملے کے۔

## بغیر کیٹلاگ کے پیٹرن رینڈر کرنا { #rendering-a-pattern-without-a-catalog }

`compile_template` وہی سازوسامان ایک درجہ نیچے کھول دیتا ہے: یہ ایک t-string
کو اس کے msgid اور بندھی ہوئی قدروں کے مجموعے میں بدلتا ہے، اور جو بھی پیٹرن
آپ اسے تھمائیں، اسے رینڈر کر دیتا ہے۔

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` انہی اصولوں سے توثیق کرتا ہے اور عدم مطابقت پر **ہمیشہ استثنا اٹھاتا
ہے**۔ یہاں کوئی نرم موڈ نہیں: نرمی اس لیے موجود ہے کہ *کیٹلاگ* کی تلاش ماخذ
متن تک اتر سکے، اور جو پیٹرن آپ نے خود دیا ہو، اس کے پاس اترنے کے لیے کچھ
ہوتا ہی نہیں۔

## حفاظت اور دائرہ { #safety-and-scope }

یہ درست ہے:

```python
tr(t"Hello {name}")
```

یہ جان بوجھ کر مسترد ہیں:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

پہلے کوئی بامعنی قدر نکال لیجیے:

```python
name = user.display_name()
tr(t"Hello {name}")
```

یہ پابندی مستحکم کیٹلاگ کلیدیں پیدا کرتی ہے، مترجموں کو کام کے نام دیتی ہے،
اور ترجمہ شدہ سٹرنگ کو اظہاری زبان بننے سے روکتی ہے۔

ضمانت *ساخت اور فارمیٹنگ* تک محدود ہے: کسی ترجمے کو کبھی چلایا نہیں جاتا،
اور وہ کبھی خصوصیات تک رسائی، کالیں، کنورژن یا فارمیٹ اسپیک نہیں جوڑ سکتا۔
دو چیزیں کال کرنے والے کی ذمہ داری رہتی ہیں، بالکل جیسے معیاری لائبریری کے
gettext کے ساتھ — رینڈر شدہ آؤٹ پٹ کو اس کی منزل (HTML، شیل، ٹرمینل) کے لیے
**ایسکیپ کرنا**، اور **کیٹلاگ کی سالمیت**، کیونکہ کوئی دشمن کیٹلاگ آؤٹ پٹ کا
حجم بڑھانے کے لیے کسی پلیس ہولڈر کو دہرا سکتا ہے، اور یہ پلیس ہولڈر پر مبنی
ہر i18n میں موجود ہے۔
