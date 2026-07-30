---
description: "استخراج رسائل t-string عبر pybabel والتحقق من الكتالوجات باستخدام msgfmt ومدقق Babel المدمج."
---

# الاستخراج

الاستخراج هو الخطوة التي تجمع كل رسالة موسومة من شيفرة المصدر في قالب
`.pot` موجه للمترجمين — وهي الخطوة 3 في حلقة
[الدرس التعليمي](tutorial.md). هذه الصفحة هي مرجع تلك الخطوة: الإعداد،
وأسماء الدوال المخصصة، والوضع الصارم في CI، والفحوص التي تحرس كتالوجاتك
بعد ذلك.

يتطلب الاستخراج إضافة `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## سير العمل

أنشئ `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

ثم استخدم أوامر Babel المعتادة:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

يعالج المستخرج أيضاً `_()` و`gettext()` و`ngettext()`. لذلك يغطي تعيين واحد
الشيفرة المختلطة، بما فيها `tr()` و`ntr()` و`lazy_gettext()` و
`lazy_pgettext()`.

!!! warning "`-c` ليس اختيارياً"

    مرر `-c "Translators:"` لجمع التعليقات الموجهة للمترجمين، كما في gettext
    العادي.

## أسماء دوال مخصصة

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

قيمة INI سلسلة تفصلها المسافات أو الفواصل؛ ويقبل TOML قائمة. تغطي الخيارات
عائلات دوال gettext الست.

!!! danger "`-k` لا يصل إلى t-string"

    يجب إعلان helper مثل `mytr(t"…")` في هذه الخيارات. آلية Babel المسماة
    `--keyword` لا تقرأ قيم t-string الحرفية:
    يحذفها `pybabel extract -k mytr` بلا تحذير.

    لا يُدعم إلا ترتيب الوسائط القياسي.

## متين افتراضياً

- يُحذر من t-string المرفوضة ثم تُتجاوز.
- يُعزل الملف الذي لا يمكن تحليله بالطريقة نفسها.
- يُعزل أيضاً الملف الذي يرفضه `tokenize` وحده.

استخدم `strict = true` لتحويل هذه التحذيرات إلى أخطاء في CI.

## التحقق بسلسلة الأدوات الحالية

يضيف Babel علماً قياسياً:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

تُكتشف ترجمة مثل `こんにちは {nombre}` من دون إعداد إضافي:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

يوثق Weblate هذا الفحص باسم
[Python brace format][weblate-checks]. الأداتان المختبرتان هنا هما msgfmt
ومدقق Babel الذي توفره الحزمة.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

يطبق `pybabel compile` المدقق على كل رسالة موسومة:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

في الجمع، يسمّي الخطأ الصيغة المعنية:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "يكتب `pybabel compile` ملف `.mo` رغم ذلك"

    تكون حالة الخروج `1`، لكن الكتالوج غير الصالح يُترجم أيضاً. يجب أن يعامل
    خط CI هذه الحالة كحاجز.

    ```yaml
    - run: pybabel compile -d locales   # non-zero exit is the gate
    ```

الفحوص ليست مكررة: يتحقق المدقق المرفق من الأقواس المهربة ومن كل صيغة جمع
منفصلة حيث قد يقبل msgfmt الملف. تسمح أسماء ASCII لكل الأدوات بالمشاركة،
بينما تقبل المكتبة نفسها كل اسم يحقق `str.isidentifier()`.

## القوالب والأدوات الأخرى

t-strings صيغة Python. تحتفظ Jinja2 (`{% trans %}`) وDjango والقوالب الأخرى
بمستخرجاتها، ويمكنها الكتابة إلى كتالوج PO نفسه.

لا يستطيع `pygettext` تحليل t-strings بعد. تتيح [المواصفة](spec.md) لأي مستخرج
آخر اتباع الاتفاقية نفسها.
