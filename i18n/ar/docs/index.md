---
description: "ترجمة رسائل t-string الكاملة بأمان عبر gettext وBabel مع إبقاء التنسيق خارج الكتالوج."
---

# gettext-tstrings

تكامل آمن بين t-strings في Python 3.14+ وبين gettext وBabel.

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))
```

يستقبل الكتالوج الجملة الكاملة `Hello {name}`. يمكن للترجمة تغيير موضع
`{name}` أو تكراره، لكنها لا تستطيع حذفه أو اختراع عنصر نائب جديد أو إضافة
تنسيق من عندها.

## المشكلة التي يحلها

تكون f-string قد أُجري عليها الاستيفاء قبل أن تراها أي مكتبة، ولذلك لا يبقى
للترجمة إلا جزء من الجملة. أما t-string ([PEP 750]) فتحفظ النص الثابت والقيم
المقيّمة وتعبيرات المصدر والتحويلات ومواصفات التنسيق منفصلة، وهذا هو الفصل
الذي يحتاجه كتالوج الرسائل. توضّح [صفحة المقارنة](comparison.md) الفرق عن
`%(name)s` و`.format()`.

لا يحدد gettext أو Babel كيفية تحويل t-string إلى رسالة. تختار هذه المكتبة
قاعدة واضحة، وتوثقها في [مواصفة ذات إصدارات](spec.md)، وتوفر
[حزمة اختبارات توافق](spec.md#conformance).

## القرارات الأساسية

- ترجمة الرسائل الكاملة لا أجزاء الجمل.
- قبول أسماء متغيرات بسيطة فقط مثل `{name}`.
- إبقاء `!r` و`:.2f` تحت سيطرة التطبيق وخارج الكتالوج.
- السماح بإعادة ترتيب العناصر النائبة المعروفة وتكرارها، دون الوصول إلى
  الخصائص أو إضافة سلوك تنسيق.
- إعادة استخدام ملفات POT وPO وMO والأدوات الحالية.

## هذا الموقع يستخدم المكتبة فعلياً

هذه الوثائق ليست مجرد عرض مترجم. فالتنقل وتسميات السمة وسطر حقوق النشر وتقرير
البناء المعتمد على صيغ الجمع كلها تُعرض من كتالوجات PO بواسطة
`gettext-tstrings` نفسها. يشغّل
[الباني متعدد اللغات](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py)
الرسائل ذات السياق والعناصر النائبة المسماة وقواعد الجمع للغات العشر في كل
بناء صارم.

## التثبيت

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

## الخطوة التالية

<div class="grid cards" markdown>

- **[لماذا t-strings؟](comparison.md)** — الرسالة نفسها بثلاث طرق.
- **[الدليل](guide.md)** — API وقت التشغيل، لغة كل طلب، الترجمة المؤجلة،
  والتعامل مع الكتالوج الخاطئ.
- **[الاستخراج](extraction.md)** — سير عمل `pybabel` والإعداد والتحقق.
- **[المواصفة](spec.md)** — العقد المستقر وحزمة التوافق.
- **[API](api.md)** — كل ما تصدّره الحزمة.

</div>

## الحالة

المشروع في مرحلة alpha. العقد الصغير والمواصفة هما الجزء المستقر، أما Python
API فقد يتغير قبل الإصدار المستقر. نحتاج إلى حالات لغوية أوسع وقياس أداء
مستمر وخبرة من مشاريع تستخدم gettext وBabel فعلياً.

نرحب بـ[المشكلات وطلبات السحب](https://github.com/yhay81/gettext-tstrings/issues).

## شارك في المجتمع

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
