---
description: "API وقت التشغيل: ربط الكتالوج، لغة كل طلب، السلاسل المؤجلة، والتعامل مع الترجمات الخاطئة."
---

# الدليل

هذه الصفحة هي مرجع وقت التشغيل: كل ما تفعله *شيفرة تطبيقك* بهذه المكتبة
بعد أن توجد الكتالوجات. إذا لم ترَ الحلقة الكاملة بعد — وسم، استخراج،
ترجمة، تجميع، تشغيل — فإن [الدرس التعليمي](tutorial.md) يمر بها مرة واحدة
في خمس دقائق؛ ويغطي [الاستخراج](extraction.md) إنشاء الكتالوجات والتحقق
منها، أما كيف يُبقي فريقٌ الحلقةَ دائرة — دورات التحديث وCI ومنصات
الترجمة — فذلك في [في الإنتاج](workflow.md).

## ربط كتالوج { #binding-a-catalog }

يتبع الأسلوب الموصى به واجهة gettext الكائنية: اربط كائن ترجمة قياسياً مرة
واحدة واستخدم المعالج القابل للاستدعاء باسم `_`.

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

تتبع دوال الوحدة أسماء المكتبة القياسية ووسائطها الموضعية:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` و`ntr` اسمان بديلان مطابقان لـ`gettext` و`ngettext`.

## لغة لكل طلب { #per-request-language }

يختار إطار الويب لغة لكل طلب. اربط الترجمة بالسياق الحالي فتستخدم كل استدعاءات
الوحدة تلك اللغة، حتى بين الطلبات المتزامنة.

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

يربط `set_translations()` بلا كتلة عندما يدير إطار العمل دورة الحياة،
ويقرأ `get_translations()` الربط. يأخذ `translations=` الصريح الأولوية. عند
غياب الربط تكون دوال gettext العامة في المكتبة القياسية هي البديل. وتجد
أمثلة عملية لـFlask ولوسيط ASGI على صفحة
[في الإنتاج](workflow.md#binding-a-language-at-runtime).

## الترجمة المؤجلة { #deferred-translation }

تلتقط t-string قيمها فوراً. لعنوان أو enum أو ثابت يُعرّف عند الاستيراد لكنه
يُعرض باللغة الفعالة وقت *الاستخدام*، استخدم سلسلة مؤجلة.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

تُعرض `LazyString` بواسطة `str()` و`format()` وf-strings، وتُقارن بنصها.

!!! note "غير قابلة للتجزئة عمداً"

    يتغير النص باختلاف اللغة. لو تغيّرت قيمة التجزئة لأفسدت set أو dict بصمت.
    استدعِ `str()` أولاً إذا أردت مفتاحاً.

تعتمد صيغ الجمع على العدد وقت التشغيل؛ اعرضها فوراً عبر `ngettext`.

## عندما يكون الكتالوج خاطئاً { #what-happens-when-a-catalog-is-wrong }

إذا لم تطابق العناصر النائبة في الترجمة المصدر، يعرض الوضع الافتراضي نص
المصدر بدلاً من إثارة استثناء. يتبع ذلك عقد gettext: لا ينبغي لكتالوج سيئ أن
يوقف التطبيق.

إذا تُرجمت `Hello {name}` إلى `こんにちは {nombre}` ينجح العرض ويُرسل تحذير
إلى logger باسم `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

يصدر التحذير مرة واحدة لكل رسالة ونمط، لا عند كل عرض، فلا يُغرق إدخال
الكتالوج المعطوب السجل. فعّل الوضع الصارم في الاختبارات وCI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

عندئذ تثير عملية البحث نفسها استثناء:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## قراءة رسالة الخطأ { #reading-a-failure-message }

تشرح الرسائل أيضاً لماذا لا يكون العنصر النائب الظاهر صالحاً:

| ما تحتويه الترجمة | السبب |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

تُعرض المسافة غير المنقسمة غير المرئية بنقطة الترميز:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

ويُعرض الحرف الشبيه من أبجدية أخرى بصورته المقروءة والمهربة:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

يغطي ذلك أيضاً التعارض بين أسماء يونانية أو سيريليّة بالكامل ونظائرها ASCII.

## عرض نمط من دون كتالوج { #rendering-a-pattern-without-a-catalog }

ينتج `compile_template` قيمة msgid والقيم المرتبطة ثم يعرض نمطاً:

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

يتحقق `render` بالقواعد نفسها و**يثير استثناء دائماً** عند الاختلاف. لا يوجد
بديل لأن العملية لا تبحث في كتالوج.

## الأمان والنطاق { #safety-and-scope }

صالح:

```python
tr(t"Hello {name}")
```

مرفوض عمداً:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

احسب قيمة صريحة أولاً:

```python
name = user.display_name()
tr(t"Hello {name}")
```

لا تُقيّم الترجمة أبداً، ولا تستطيع إضافة وصول إلى خاصية أو استدعاء أو تحويل
أو تنسيق. كما في gettext العادي، يبقى التطبيق مسؤولاً عن **التهريب الملائم
لوجهة الإخراج** و**سلامة الكتالوج**.
