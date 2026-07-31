---
description: "كل الأسماء العامة في gettext_tstrings: الدوال وTranslator وربط السياق والسلاسل المؤجلة والأخطاء."
---

# API

تصدّر `gettext_tstrings` كل الأسماء التالية. وما عداها ليس API عاماً.
هذه الصفحة مرجع التوقيعات؛ وللاطلاع على أمثلة عملية لكل دالة راجع
[الدليل](guide.md).

## الترجمة { #translating }

تأخذ كل دالة t-string كوسيط موضعي، وتقبل `translations` و`strict` كوسيطين
مسميين ([راجع الدليل](guide.md#what-happens-when-a-catalog-is-wrong)).

| الدالة | التوقيع |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | اسم بديل مطابق لـ`gettext` |
| `ntr` | اسم بديل مطابق لـ`ngettext` |

### `Translator`

dataclass مجمّدة تربط كائن ترجمة:

```python
Translator(translations, strict=False)
```

يمكن استدعاؤها (`_(t"…")`) وتوفر `gettext` و`ngettext` و`pgettext`
و`npgettext` و`tr` و`ntr`.

## ربط السياق { #context-binding }

| الاسم | الدور |
| --- | --- |
| `use_translations(translations)` | يربط خلال كتلة `with` ثم يعيد الحالة السابقة. |
| `set_translations(translations)` | يربط بلا كتلة لدورة حياة يديرها إطار العمل. |
| `get_translations()` | يقرأ الربط الحالي أو يعيد `None`. |

يستخدم الربط `ContextVar` وهو آمن مع التنفيذ المتزامن.

## السلاسل المؤجلة { #deferred-strings }

| الاسم | الدور |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | يؤجل الترجمة حتى الاستخدام. |
| `lazy_pgettext(context, template, /, *, strict=False)` | صيغة مع سياق. |
| `LazyString` | تُعرض عبر `str()` و`format()` وf-strings، وتُقارن بالنص، وهي غير قابلة للتجزئة عمداً. |

## المستوى المنخفض { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

يترجم t-string إلى خطة مع إعادة استخدام الخطة الثابتة المخزنة مؤقتاً.

### `CompiledTemplate`

| العضو | المعنى |
| --- | --- |
| `.msgid` | معرّف gettext مستقر. |
| `.placeholders` | الأسماء بترتيب أول ظهور. |
| `.render(pattern)` | يتحقق ويعرض، و**يثير استثناء دائماً** عند عدم التطابق. |

## الأنواع والأخطاء { #types-and-errors }

### `Translations`

`Protocol` قابل للفحص وقت التشغيل للطرائق القياسية الأربع:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

تطابقه `gettext.NullTranslations` و`gettext.GNUTranslations` و`Translations`
من Babel.

### الاستثناءات

| الصنف | متى |
| --- | --- |
| `TStringError` | الصنف الأساسي. |
| `InvalidTemplateError` | تخالف t-string المصدر الاتفاقية. |
| `InvalidTranslationError` | تخالف الترجمة الاتفاقية؛ يسجل الوضع المرن الخطأ ويعرض المصدر. |

## نقاط دخول الاستخراج { #extraction-entry-points }

| المجموعة | الاسم | الاستخدام |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | قيمة `method` في `babel.cfg` |
| `babel.checkers` | `gettext_tstrings` | يستخدمه `pybabel compile` تلقائياً |

## الأداء { #performance }

الرواية الكاملة — ما يُخزَّن في الذواكر المؤقتة، وما تعتمد عليه مفاتيحها،
والأرقام المقيسة — في [المسار الساخن](internals.md#the-hot-path). والخلاصة:
التحقق يُخزَّن مؤقتاً ولا يُتخطى أبداً، والعرض بأكمله يكلف جزءاً من
الميكروثانية. شغّل القياس على هدفك الخاص:

```console
uv run python benchmarks/runtime.py
```
