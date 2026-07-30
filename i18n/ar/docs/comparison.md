---
description: "الرسالة القابلة للترجمة نفسها بصيغة % و.format() وt-string، وما يتحكم فيه الكتالوج في كل حالة."
---

# لماذا t-strings؟

على كل طريقة لإدخال قيمة في رسالة قابلة للترجمة أن تجيب عن سؤال واحد:
*ما المقدار الذي ينبغي أن يتحكم فيه الكتالوج من لغة التنسيق؟*

## التنسيق بعلامة %

```python
_("Hello %(name)s") % {"name": name}
```

يحمل نص الكتالوج صيغة printf. قد يؤدي حذف حرف واحد إلى خطأ في بيئة الإنتاج:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

يكتشف `msgfmt --check-format` ذلك، لكن فقط للرسائل الموسومة
`python-format` وعندما يمر الكتالوج فعلاً عبر msgfmt.

## str.format

```python
_("Hello {name}").format(name=name)
```

العنصر النائب مسمّى ويمكن نقله بسهولة، لكن `str.format` لغة تعبيرات صغيرة:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

الكتالوج بيانات تمر عبر منصات وأشخاص كثيرين، ومع ذلك تمنحه `.format()` حق
الوصول إلى خصائص الكائنات الممررة.

## t-strings

```python
tr(t"Hello {name}")
```

يبقى msgid هو `Hello {name}`، لكن الترجمة لا تُنفّذ كسلسلة تنسيق؛ بل تُفحص
مقابل عناصر المصدر النائبة، ولا يُقبل إلا الاسم البسيط:

| ما تحتويه الترجمة | سبب الرفض |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

يبقى التنسيق في التطبيق:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

لا تصل `:,.2f` إلى الكتالوج أبداً.

## مقارنة مباشرة

| | `%(name)s` | `.format()` | `t"…"` |
| --- | --- | --- | --- |
| العنصر النائب مسمّى | نعم | نعم | نعم |
| يمكن للمترجم تغيير الترتيب | نعم | نعم | نعم |
| حذف حرف يكسر الرسالة | **نعم** | لا | لا |
| يتحكم الكتالوج في التنسيق | نعم | نعم | **لا** |
| يصل الكتالوج إلى الخصائص | لا | **نعم** | **لا** |
| كتالوج خاطئ يثير خطأ عند العرض | **نعم** | **نعم** | [ليس افتراضياً](guide.md#what-happens-when-a-catalog-is-wrong) |
| يعمل مع PO/MO و`msgfmt` | نعم | نعم | نعم |

## التكلفة

تصل f-string مكتملة إلى الدالة. تتطلب t-strings ([PEP 750]) إصدار Python
3.14 أو أحدث، ويجب أن يكون كل استيفاء اسماً بسيطاً:

```python
tr(t"Hello {user.name}")  # rejected
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

هذا القيد هو ما يمنح ضمان الأمان، كما يمنح المترجم أسماء مفهومة.

  [PEP 750]: https://peps.python.org/pep-0750/
