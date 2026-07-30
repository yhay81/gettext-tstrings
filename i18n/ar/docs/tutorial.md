---
description: "من مجلد فارغ إلى برنامج يلقي التحية باليابانية، في خمس خطوات — مع عرض كل أمر ومخرجاته الفعلية."
---

# الدرس التعليمي

تنتقل هذه الصفحة من مجلد فارغ إلى برنامج يلقي التحية باليابانية. خمس
خطوات، من دون افتراض أي خبرة في gettext، ومع عرض كل أمر والمخرجات التي
ينتجها فعلاً — فتعرف عند كل خطوة ما إذا كنت على المسار الصحيح.

تحتاج إلى Python 3.14 أو أحدث، لأن t-strings صيغة جديدة في 3.14.

## 1. التثبيت

```console
python -m pip install "gettext-tstrings[babel]"
```

تجلب إضافة `[babel]` مكتبة [Babel]، وهي الأداة التي تجمع رسائلك في ملفات
كتالوج في الخطوة 3. وهي أداة لوقت التطوير: شيفرة الإنتاج تعرض بالمكتبة
القياسية وحدها.

## 2. وسم رسالة في شيفرتك

أنشئ `app.py`:

```python
from gettext_tstrings import tr

name = "Ada"
print(tr(t"Hello {name}"))
```

تبدو `t"Hello {name}"` مثل f-string، لكن البادئة `t` تبقي النص والقيمة
منفصلين بدلاً من دمجهما في الحال. هذا الفصل هو ما يتيح لـ`tr()` البحث عن
ترجمة للجملة الكاملة `Hello {name}` ثم إدراج القيمة بعد ذلك.

شغّله الآن:

```console
$ python app.py
Hello Ada
```

لم تُثبّت أي ترجمات بعد، فيُعرض نص المصدر كما هو. البرنامج الذي يستخدم
هذه المكتبة لا *يتطلب* كتالوجاً كي يعمل أبداً — فالإنجليزية (أو أياً كانت
لغتك المصدرية) هي البديل المدمج.

## 3. استخراج الرسائل

لا يقرأ المترجمون شيفرة مصدرك؛ بل يتنقل بينك وبينهم ملف صغير يسمى
**الكتالوج**. الخطوة الأولى نحوه هي جمع كل رسالة موسومة من الشيفرة.

أخبر Babel كيف يعثر على رسائلك بإنشاء `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

ثم استخرج إلى ملف قالب (`.pot`):

```console
$ mkdir -p locales
$ pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
```

يحتوي `locales/messages.pot` الآن على إدخال واحد لكل رسالة:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

`msgid` هو المفتاح الذي ستبحث عنه شيفرتك. أما `msgstr` الفارغ فهو موضع
الترجمة — لكن ليس في هذا الملف: فملف `.pot` *قالب*، والخطوة التالية تنسخه
مرة واحدة لكل لغة.

## 4. الترجمة والتجميع

أنشئ الكتالوج الياباني من القالب:

```console
$ pybabel init -i locales/messages.pot -d locales -l ja
creating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

افتح `locales/ja/LC_MESSAGES/messages.po` واملأ `msgstr`:

```po
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

أبقِ `{name}` كما هو تماماً — العنصر النائب هو الطريقة التي تجد بها
القيمة موضعها داخل الجملة المترجمة، والترجمة حرة في نقله إلى حيث تحتاجه
اللغة الهدف. في مشروع حقيقي، ملف `.po` هذا هو ما تسلّمه إلى مترجم أو
ترفعه إلى منصة ترجمة؛ والصيغة واحدة في الحالتين.

تُحرر الكتالوجات كنص لكنها تُحمّل بصيغة ثنائية (`.mo`)، فجمّعها:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
```

هذا الأمر شبكة أمان أيضاً. فلو أتلفت الترجمة العنصر النائب — `{nome}`
بدلاً من `{name}` مثلاً — لرفض النجاح:

```console
$ pybabel compile -d locales
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nome} is not in the source message
1 errors encountered.
```

## 5. التشغيل

وجّه `app.py` إلى الكتالوج المجمّع:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales", languages=["ja"]))

name = "Ada"
print(_(t"Hello {name}"))
```

`_` هو الاسم المتعارف عليه في gettext لعبارة «ترجم هذا» — قصير لأنه يظهر
على كل نص موجه للمستخدم. وهو الدالة نفسها `tr`، مربوطة بكتالوج واحد.

```console
$ python app.py
こんにちは Ada
```

هذه هي الحلقة كاملة: **وسم ← استخراج ← ترجمة ← تجميع ← تشغيل**. كل ما
عداها في هذا الموقع تفصيل لإحدى هذه الخطوات الخمس.

## إلى أين بعد ذلك

- [لماذا t-strings؟](comparison.md) — ما الذي يحميك منه هذا التصميم،
  مقارنةً بـ`%(name)s` و`.format()` وسلاسل `$`.
- [الدليل](guide.md) — صيغ الجمع، لغة كل طلب، السلاسل المؤجلة، وما يحدث
  وقت التشغيل عندما يكون الكتالوج خاطئاً رغم كل شيء.
- [الاستخراج](extraction.md) — مرجع `pybabel` الكامل: أسماء الدوال
  المخصصة، والوضع الصارم في CI، والفحوص التي تحرس كتالوجاتك.

  [Babel]: https://babel.pocoo.org/
