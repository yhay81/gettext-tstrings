---
description: "ترجمة رسائل t-string الكاملة بأمان عبر gettext وBabel مع إبقاء التنسيق خارج الكتالوج."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# اكتب الجملة مرة واحدة.<br>وترجمها كاملة.

تكامل آمن بين t-strings في Python 3.14+ وبين gettext وBabel — تبقى القيمة
في موضعها، ويرى الكتالوج الرسالة كاملة:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[ابدأ الدرس التعليمي :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[لماذا t-strings؟](comparison.md){ .md-button }

هذا الموقع يطبّق ما يوثّقه: فكل طبعة لغوية — التنقل والتسميات
وتقرير البناء المعتمد على صيغ الجمع — تُعرض من كتالوجات PO بواسطة
[`gettext-tstrings` نفسها](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

يستقبل الكتالوج الجملة الكاملة `Hello {name}`. يمكن للترجمة تغيير موضع
`{name}` أو تكراره، لكنها لا تستطيع حذفه أو اختراع عنصر نائب جديد أو إضافة
تنسيق من عندها — تتحقق هذه المكتبة من ذلك، والكتالوج المعطوب يتراجع إلى نص
المصدر بدلاً من إيقاف التطبيق.

!!! note "جديد على gettext؟ سير العمل كله في أربع جمل"

    **gettext** هو الطريقة القياسية لترجمة البرمجيات، في Python وخارجها.
    توسم شيفرتك النصوص القابلة للترجمة؛ ويجمعها *مستخرج* في ملف قالب
    (`.pot`)؛ ويملأ مترجم — ليس مبرمجاً في الغالب — ملف كتالوج واحداً
    (`.po`) لكل لغة، يُجمّع إلى ملف `.mo` ثنائي يحمّله تطبيقك وقت التشغيل.
    الاسم المتعارف عليه لدالة الترجمة هو `_`، فتُقرأ `_(t"Hello {name}")`
    على أنها «ترجم هذه الجملة». يمر **[الدرس التعليمي](tutorial.md)**
    بالمسار كاملاً — وسم، استخراج، ترجمة، تجميع، تشغيل — في نحو خمس دقائق.

## المشكلة التي يحلها { #the-problem-it-solves }

تكون f-string قد أُجري عليها الاستيفاء قبل أن تراها أي مكتبة — فتكون
`f"Hello {name}"` قد صارت `"Hello Ada"`، وترجمة الأجزاء المحيطة بالقيمة
تكسر قواعد معظم اللغات. أما t-string ([PEP 750]) فتحفظ النص الثابت والقيم
المقيّمة وتعبيرات المصدر والتحويلات ومواصفات التنسيق منفصلة، وهذا هو الفصل
الذي يحتاجه كتالوج الرسائل. توضّح [صفحة المقارنة](comparison.md) الفرق عن
`%(name)s` و`.format()` وسلاسل `$`.

لا يحدد gettext أو Babel كيفية تحويل t-string إلى رسالة. تختار هذه المكتبة
قاعدة واضحة، وتوثقها في [مواصفة ذات إصدارات](spec.md)، وتوفر
[حزمة اختبارات توافق](spec.md#conformance).

## القرارات الأساسية { #the-choice-it-makes }

- ترجمة الرسائل الكاملة لا أجزاء الجمل.
- قبول أسماء متغيرات بسيطة فقط مثل `{name}`.
- إبقاء `!r` و`:.2f` تحت سيطرة التطبيق وخارج الكتالوج.
- السماح بإعادة ترتيب العناصر النائبة المعروفة وتكرارها، دون الوصول إلى
  الخصائص أو إضافة سلوك تنسيق.
- إعادة استخدام ملفات POT وPO وMO والأدوات الحالية.

## التثبيت { #install }

```console
python -m pip install gettext-tstrings
```

يتطلب Python 3.14 أو أحدث. العرض **بلا تبعيات خارجية** ويستخدم `gettext` من
المكتبة القياسية فقط.

يعمل الاستخراج والتحقق من الكتالوج عبر [Babel]. ثبّت الإضافة التالية في بيئة
التطوير أو CI:

```console
python -m pip install "gettext-tstrings[babel]"
```

## الخطوة التالية { #where-to-go-next }

يصل إلى هنا ثلاثة أنواع من القراء: من يترجم برنامجه الأول، ومن يربط
الترجمة بمشروع حقيقي، ومن يريد أن يعرف بالضبط لماذا اتخذت الآلية هذا
الشكل. ولكل منهم مسار.

**تعلّمها** — من دون افتراض أي خبرة في gettext:

<div class="grid cards" markdown>

- **[الدرس التعليمي](tutorial.md)** — ابدأ هنا: من مجلد فارغ إلى ترجمة
  يابانية عاملة في خمس خطوات، مع عرض كل أمر ومخرجاته.
- **[لماذا t-strings؟](comparison.md)** — الرسالة نفسها بأربع طرق، وما
  يسلّمه كل من `%(name)s` و`.format()` وسلاسل `$` إلى الكتالوج.
- **[الخلفية](background.md)** — لماذا توجد هذه المكتبة: ثلاثون عاماً من
  gettext، ومقترحا PEP، ونقاش المكتبة القياسية الذي أُغلق دون إجابة.

</div>

**استخدامها بجدية** — المراجع العملية:

<div class="grid cards" markdown>

- **[الدليل](guide.md)** — API وقت التشغيل: صيغ الجمع، لغة كل طلب، السلاسل
  المؤجلة، والتعامل مع الكتالوج الخاطئ.
- **[الاستخراج](extraction.md)** — مرجع `pybabel`: الإعداد وأسماء الدوال
  المخصصة وكيف تتحقق الأدوات الحالية من هذه الكتالوجات مجاناً.
- **[في الإنتاج](workflow.md)** — الحلقة كما يديرها فريق: دورة التحديث،
  وإدخالات fuzzy، وبوابات CI، ومنصات الترجمة، ولغة كل طلب في تطبيق ويب.
- **[API](api.md)** — كل ما تصدّره الحزمة، في صفحة واحدة.

</div>

**فهمها** — من المبادئ إلى التنفيذ:

<div class="grid cards" markdown>

- **[كيف تعمل](internals.md)** — من كائن القالب في PEP 750 إلى السلسلة
  المعروضة، والذواكر المؤقتة التي تجعل الفحص رخيصاً.
- **[المواصفة](spec.md)** — اتفاقية t-string ↔ msgid كعقد مستقر ذي إصدارات
  مع حزمة توافق قابلة للقراءة آلياً.

</div>

## الحالة { #status }

المشروع في مرحلة alpha. العقد الصغير والمواصفة هما الجزء المستقر، أما Python
API فقد يتغير قبل الإصدار المستقر. نحتاج إلى حالات لغوية أوسع وقياس أداء
مستمر وخبرة من مشاريع تستخدم gettext وBabel فعلياً.

نرحب بـ[المشكلات وطلبات السحب](https://github.com/yhay81/gettext-tstrings/issues).

## شارك في المجتمع { #join-the-community }

- اختر
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  واضحة النطاق.
- اطرح أسئلة الاستخدام في
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- ناقش أفكار API في
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- اقرأ
  [دليل المساهمة](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  قبل فتح طلب سحب.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
