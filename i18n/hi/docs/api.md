---
description: "gettext_tstrings का हर एक्सपोर्ट किया गया नाम: फ़ंक्शन, Translator, context binding, lazy strings, और त्रुटियाँ।"
---

# API

नीचे का सब कुछ `gettext_tstrings` से एक्सपोर्ट होता है। इसके सिवा कुछ भी
public नहीं है। यह पेज सिग्नेचर संदर्भ है; हर फ़ंक्शन के सधे हुए उदाहरणों
के लिए [गाइड](guide.md) देखें।

## अनुवाद करना { #translating }

हर फ़ंक्शन अपना t-string positionally लेता है और दो keyword arguments
स्वीकार करता है: `translations` (जो context binding पर, फिर मानक लाइब्रेरी
के वैश्विक फ़ंक्शनों पर फ़ॉलबैक करता है) और `strict`
([गाइड](guide.md#what-happens-when-a-catalog-is-wrong) देखें)।

| फ़ंक्शन | सिग्नेचर |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext` का उपनाम |
| `ntr` | `ngettext` का उपनाम |

### `Translator`

एक frozen dataclass जो एक translation ऑब्जेक्ट बाँधता है, ताकि कॉल स्थल उसे
दोहराएँ नहीं।

```python
Translator(translations, strict=False)
```

यह callable है (`_(t"…")`) और `gettext`, `ngettext`, `pgettext`,
`npgettext` तथा `tr` / `ntr` उपनाम साथ रखता है।

## Context binding { #context-binding }

| नाम | उद्देश्य |
| --- | --- |
| `use_translations(translations)` | `with` ब्लॉक की अवधि के लिए बाँधे, फिर पुनर्स्थापित करे। |
| `set_translations(translations)` | बिना ब्लॉक के बाँधे, फ़्रेमवर्क-प्रबंधित जीवनचक्रों के लिए। |
| `get_translations()` | वर्तमान binding पढ़े, या `None`। |

binding एक `ContextVar` है, इसलिए यह प्रति-context है और concurrency के
अंतर्गत सुरक्षित।

## Deferred strings { #deferred-strings }

| नाम | उद्देश्य |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | अनुवाद को पहले उपयोग तक टाले। |
| `lazy_pgettext(context, template, /, *, strict=False)` | contextual रूप। |
| `LazyString` | दोनों जो लौटाते हैं। `str()` और `format()` से रेंडर होता है, अपने टेक्स्ट के बराबर तुलना करता है, और जान-बूझकर unhashable है। |

## निचला स्तर { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

t-string को compile करे, उसकी कैश की हुई स्थिर योजना का पुन: उपयोग करते
हुए।

### `CompiledTemplate`

| सदस्य | अर्थ |
| --- | --- |
| `.msgid` | स्थिर gettext संदेश पहचानकर्ता। |
| `.placeholders` | placeholder नाम, प्रथम-आगमन क्रम में। |
| `.render(pattern)` | एक pattern सत्यापित करके रेंडर करे। बेमेल पर **हमेशा exception उठाता है**। |

## Types और errors { #types-and-errors }

### `Translations`

चार मानक methods के लिए एक `runtime_checkable` `Protocol`, सभी
positional-only:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` और Babel का
`Translations` — तीनों इसे संतुष्ट करते हैं।

### Exceptions

| Class | कब उठता है |
| --- | --- |
| `TStringError` | नीचे दोनों का base class। |
| `InvalidTemplateError` | **स्रोत** t-string परिपाटी तोड़ता है — कोई जटिल इंटरपोलेशन, या भिन्न फ़ॉर्मैटिंग वाला दोहराया नाम। |
| `InvalidTranslationError` | **अनुवाद** तोड़ता है। डिफ़ॉल्ट उदार मोड में यह लॉग होता है और उसकी जगह स्रोत टेक्स्ट रेंडर होता है। |

## एक्सट्रैक्शन entry points { #extraction-entry-points }

इंस्टॉल पर स्वत: पंजीकृत; आप इन्हें import से नहीं, नाम से संदर्भित करते
हैं।

| Group | नाम | कौन उपयोग करता है |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg` का `method`। |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, स्वत:। |

## प्रदर्शन { #performance }

पूरा विवरण — क्या कैश होता है, कैश किस पर key होते हैं, और मापे हुए आँकड़े
— [हॉट पाथ](internals.md#the-hot-path) है। संक्षेप में: सत्यापन कैश होता
है, कभी छोड़ा नहीं जाता, और पूरा रेंडर माइक्रोसेकंड के एक अंश की लागत रखता
है। benchmark अपने लक्ष्य पर स्वयं चलाएँ:

```console
uv run python benchmarks/runtime.py
```
