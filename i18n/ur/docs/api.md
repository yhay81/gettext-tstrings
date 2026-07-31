---
description: "gettext_tstrings جو بھی نام برآمد کرتی ہے: فنکشن، Translator، سیاق کی بندش، مؤخر سٹرنگز، اور غلطیاں۔"
---

# API

نیچے جو کچھ ہے، سب `gettext_tstrings` سے برآمد ہوتا ہے۔ اس کے سوا کچھ عوامی
نہیں۔ یہ صفحہ دستخطوں کا حوالہ ہے؛ ہر فنکشن کی عملی مثالوں کے لیے
[رہنما](guide.md) دیکھیے۔

## ترجمہ کرنا { #translating }

ہر فنکشن اپنی t-string کو موضعی طور پر لیتا ہے اور دو کلیدی لفظی آرگیومنٹ
قبول کرتا ہے: `translations` (جو سیاق کی بندش پر، اور پھر معیاری لائبریری کے
عالمی فنکشنوں پر واپس آ جاتا ہے) اور `strict` (دیکھیے
[رہنما](guide.md#what-happens-when-a-catalog-is-wrong))۔

| فنکشن | دستخط |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext` کا دوسرا نام |
| `ntr` | `ngettext` کا دوسرا نام |

### `Translator`

ایک منجمد ڈیٹا کلاس جو ایک ترجمہ آبجیکٹ کو باندھ لیتی ہے، تاکہ کال کرنے
والی جگہوں کو اسے بار بار نہ لکھنا پڑے۔

```python
Translator(translations, strict=False)
```

یہ قابلِ استدعا ہے (`_(t"…")`) اور اپنے ساتھ `gettext`، `ngettext`،
`pgettext`، `npgettext` اور `tr` / `ntr` کے دوسرے نام رکھتی ہے۔

## سیاق کی بندش { #context-binding }

| نام | مقصد |
| --- | --- |
| `use_translations(translations)` | ایک `with` بلاک کے دورانیے کے لیے باندھتا ہے، پھر پہلی حالت بحال کر دیتا ہے۔ |
| `set_translations(translations)` | بلاک کے بغیر باندھتا ہے، ان فریم ورکس کے لیے جو خود دورانِ حیات سنبھالتے ہیں۔ |
| `get_translations()` | موجودہ بندش پڑھتا ہے، یا `None`۔ |

بندش ایک `ContextVar` ہے، لہٰذا وہ فی سیاق الگ ہے اور ہم وقتی کے تحت محفوظ
ہے۔

## مؤخر سٹرنگز { #deferred-strings }

| نام | مقصد |
| --- | --- |
| `lazy_gettext(template, /)` | ترجمے کو پہلے استعمال تک مؤخر کر دیتا ہے۔ |
| `lazy_pgettext(context, template, /)` | اس کی سیاقی صورت۔ |
| `LazyString` | جو دونوں لوٹاتے ہیں۔ `str()` اور `format()` کے ذریعے رینڈر ہوتی ہے، اپنے متن کے برابر موازنہ کرتی ہے، اور جان بوجھ کر ناقابلِ ہیش ہے۔ |

## نچلی سطح { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

ایک t-string کو کمپائل کرتا ہے، اس کے کیش شدہ ساکن منصوبے کو دوبارہ استعمال
کرتے ہوئے۔

### `CompiledTemplate`

| رکن | مطلب |
| --- | --- |
| `.msgid` | gettext کا مستحکم پیغام شناخت کنندہ۔ |
| `.placeholders` | پلیس ہولڈر نام، پہلی بار ظاہر ہونے کی ترتیب میں۔ |
| `.render(pattern)` | ایک پیٹرن کی توثیق کرتا اور اسے رینڈر کرتا ہے۔ عدم مطابقت پر **ہمیشہ استثنا اٹھاتا ہے**۔ |

## قسمیں اور غلطیاں { #types-and-errors }

### `Translations`

چار معیاری میتھڈز کے لیے ایک `runtime_checkable` `Protocol`، سب صرف موضعی:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`، `gettext.GNUTranslations` اور Babel کا
`Translations` — تینوں اس پر پورے اترتے ہیں۔

### استثناءات

| کلاس | کب اٹھتی ہے |
| --- | --- |
| `TStringError` | نیچے دونوں کی بنیادی کلاس۔ |
| `InvalidTemplateError` | **ماخذ** t-string اصول توڑتی ہے — کوئی پیچیدہ انٹرپولیشن، یا مختلف فارمیٹنگ کے ساتھ دہرایا گیا نام۔ |
| `InvalidTranslationError` | **ترجمہ** اسے توڑتا ہے۔ طے شدہ نرم موڈ میں یہ لاگ ہوتی ہے اور اس کی جگہ ماخذ متن رینڈر ہوتا ہے۔ |

## استخراج کے داخلی نقطے { #extraction-entry-points }

تنصیب پر خودکار طور پر رجسٹر ہو جاتے ہیں؛ آپ ان کا حوالہ نام سے دیتے ہیں،
import سے نہیں۔

| گروہ | نام | استعمال کنندہ |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg` میں `method`۔ |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`، خودکار طور پر۔ |

## کارکردگی { #performance }

پوری تفصیل — کیا کیش ہوتا ہے، کیش کس چیز پر کلید بناتے ہیں، اور ناپے گئے
اعداد — [گرم راستہ](internals.md#the-hot-path) میں ہے۔ مختصر یہ کہ: توثیق
کیش ہوتی ہے، چھوڑی کبھی نہیں جاتی، اور پورا رینڈر ایک مائیکرو سیکنڈ کے
معمولی حصے پر پڑتا ہے۔ بینچ مارک اپنے ہدف پر خود چلائیے:

```console
uv run python benchmarks/runtime.py
```
