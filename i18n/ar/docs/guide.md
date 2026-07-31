---
description: "API وقت التشغيل: أي مدخل تستخدم، وربط الكتالوج، ولغة كل طلب، والسلاسل المؤجلة، والقيم المرتبطة باللغة، وكيف يُبلَّغ عن الترجمة المعطوبة."
---

# الدليل

هذه الصفحة هي مرجع وقت التشغيل: كل ما تفعله *شيفرة تطبيقك* بهذه المكتبة
بعد أن توجد الكتالوجات. إذا لم ترَ الحلقة الكاملة بعد — وسم، استخراج،
ترجمة، تجميع، تشغيل — فإن [الدرس التعليمي](tutorial.md) يمر بها مرة واحدة
في خمس دقائق؛ ويغطي [الاستخراج](extraction.md) إنشاء الكتالوجات والتحقق
منها، أما كيف يُبقي فريقٌ الحلقةَ دائرة — دورات التحديث وCI ومنصات
الترجمة — فذلك في [في الإنتاج](workflow.md).

## أي مدخل ينبغي أن أستخدم؟ { #which-entry-point-should-i-use }

تصدّر الحزمة عدة طرق لترجمة رسالة لأن التطبيقات تربط اللغة بطرق مختلفة.
اختر بحسب الكيفية التي يقرر بها برنامجك ما اللغة التي هو فيها:

| حالتك | استخدم |
| --- | --- |
| لغة واحدة للعملية كلها — أداة سطر أوامر، تطبيق مكتبي، سكربت | `Translator`، مستدعىً باسم `_` |
| لغة لكل طلب أو لكل مهمة غير متزامنة — تطبيق ويب | `use_translations()` حول العمل، ثم `tr()` |
| رسالة تُعرَّف وقت الاستيراد — عنوان حقل، enum، ثابت | `lazy_gettext()` أو `lazy_pgettext()` |
| عدد يحدد الصياغة | `ngettext()` / `npgettext()`، بأي من الأشكال أعلاه |
| عرض نمط من دون أي كتالوج | `compile_template()` |

وكل ما يلي هو هذه الخمسة، بهذا الترتيب.

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
    name = request.user.display_name
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

يُقرَّر `strict` حيث تُكتب الرسالة، لا حيث تُعرض:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

تُعرض السلسلة المؤجلة حيث تُستخدم في النهاية — داخل قالب أو نموذج أو سطر
سجل — ونادراً ما يعرف ذلك الموضع أهذا تشغيل اختبارات أم إنتاج. وتمرير
`strict=True` عند التعريف هو ما يتيح تطبيق الاختيار نفسه —
[صارم في CI، متساهل في الإنتاج](#what-happens-when-a-catalog-is-wrong) —
على سلسلة لا تُعرض في موضع استدعائها.

تعتمد صيغ الجمع على العدد وقت التشغيل؛ اعرضها فوراً عبر `ngettext`.

## عدة لغات في آن واحد { #several-languages-at-once }

كثيراً ما يحتاج الطلب الواحد إلى أكثر من لغة: صفحة تُعرض للقارئ وتضع في الوقت
نفسه إشعاراً في الطابور لحساب مضبوط على لغة أخرى، أو ملخص يقتبس كل مشارك بلغته.
تتداخل الروابط، والخروج من الكتلة الداخلية يعيد الربط الخارجي.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

ومع قائمة من المستلمين تقوم السلاسل المؤجلة بالمهمة: تُكتب الرسالة مرة واحدة
عند الاستيراد، وتُعرض مرة لكل لغة.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

الربط `ContextVar`، لا مكدس محفوظ على كائن مشترك، فلا تستطيع الطلبات المتداخلة
أن تلتقط لغة بعضها بعضاً — بما في ذلك الحالة التي *تغادر* فيها كتلها بالترتيب
نفسه الذي دخلتها به، وهو التشابك الذي يخطئ فيه المكدس. وتحميل كتالوج لكل لغة
رخيص: تحلل `gettext.translation()` كل ملف `.mo` مرة واحدة وتوزع نسخاً تتشارك
الكتالوج المحلَّل.

!!! warning "وراثة خيط العامل للربط تتوقف على البناء"

    يبدأ `threading.Thread` المجرد، أو `ThreadPoolExecutor.submit`، إما من نسخة
    من سياق المستدعي وإما من سياق فارغ، وأيّهما يحدده
    `sys.flags.thread_inherit_context` — وقيمته الافتراضية صحيحة في بناءات
    الخيوط الحرة، وخاطئة فيما عداها. ولذلك يعرض الكود نفسه اللغة المربوطة على
    3.14t بينما يعرض كتالوج العملية العام على 3.14. مرّر السياق بدل الاعتماد
    على القيمة الافتراضية:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    أما `asyncio.to_thread` فيفعل ذلك عنك بالفعل.

## القيم المرتبطة باللغة { #locale-aware-values }

تقرر هذه المكتبة *أين* تظهر القيمة داخل الرسالة المترجمة، لا كيف تُوطَّن
القيمة نفسها. فـ`{amount:,.2f}` مواصفة تنسيق في Python ذات سلوك ثابت —
فاصلة كل ثلاث خانات ونقطة قبل الكسور — وتنتج المحارف نفسها مهما كانت لغة
الرسالة:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

تكتب الألمانية هذا العدد `1.234,50`، والفرنسية `1 234,50`، وتجمّع الهندية
`1234567` على شكل `12,34,567` لا `1,234,567`. فالأعداد والعملات والتواريخ
والأوقات والوحدات كلها من اختصاص [Babel][babel-numbers]. نسّق القيمة أولاً،
ثم ضع النص الجاهز في موضعه:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

وفي الرسالة المعدودة يؤدي العدد وظيفتين — يختار صيغة الجمع ويظهر في النص —
والثانية وحدها هي التي تُوطَّن. أبقِ العدد الخام للاختيار ومرّر النص المنسّق
للعرض:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

والتنسيق قبل الاستدعاء هو أيضاً ما يُبقي مواصفة التنسيق خارج الكتالوج: فما
يراه المترجم نص جاهز، لا عدد مصحوب بتعليمات عرضه.

## عندما يكون الكتالوج خاطئاً { #what-happens-when-a-catalog-is-wrong }

إذا لم تطابق العناصر النائبة في الترجمة المصدر، يعرض الوضع الافتراضي رسالة
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

وهذه الرسائل مكتوبة لمن يستطيع التصرف حيالها، وهو في مشكلات الكتالوج مترجمٌ
أكثر منه مبرمجاً — فحيث يبدو العنصر النائب حاضراً وهو ليس كذلك، تشرح الرسالة
السبب بدلاً من تكرار أنه مفقود. أقواس معقوفة كاملة العرض، أو `{{name}}`
مضاعفة، أو مسافة غير منقسمة غير مرئية، أو حرف سيريلي بين حروف لاتينية: لكلٍّ
منها صياغته الخاصة، وهي مسرودة بأمثلتها في
[للمترجمين](translators.md#reading-a-failure-message). تلك الصفحة مكتوبة كي
تُسلَّم إلى من يحرر ملف `.po`.

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

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
