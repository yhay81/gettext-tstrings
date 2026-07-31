---
description: "gettext_tstrings যে প্রতিটি নাম এক্সপোর্ট করে: ফাংশন, Translator, context বাঁধা, lazy স্ট্রিং, আর ত্রুটিগুলি।"
---

# API

নিচের সবকিছুই `gettext_tstrings` থেকে এক্সপোর্ট করা। আর কিছুই পাবলিক নয়। এই
পৃষ্ঠা signature-এর রেফারেন্স; প্রতিটি ফাংশনের কাজ-করা উদাহরণের জন্য দেখুন
[গাইড](guide.md)।

## অনুবাদ করা { #translating }

প্রতিটি ফাংশন তার t-string-টি অবস্থানগতভাবে নেয় এবং দুটি কীওয়ার্ড আর্গুমেন্ট
গ্রহণ করে: `translations` (যা context বাঁধাইয়ে, তারপর স্ট্যান্ডার্ড
লাইব্রেরির বিশ্বব্যাপী ফাংশনে ফলব্যাক করে) আর `strict`
(দেখুন [গাইড](guide.md#what-happens-when-a-catalog-is-wrong))।

| ফাংশন | Signature |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext`-এর alias |
| `ntr` | `ngettext`-এর alias |

### `Translator`

একটি frozen dataclass, যা একটি translation অবজেক্ট বেঁধে রাখে, যাতে কল-সাইটে
তা বারবার লিখতে না হয়।

```python
Translator(translations, strict=False)
```

এটি callable (`_(t"…")`) আর বহন করে `gettext`, `ngettext`, `pgettext`,
`npgettext` এবং `tr` / `ntr` alias-গুলি।

## Context বাঁধা { #context-binding }

| নাম | উদ্দেশ্য |
| --- | --- |
| `use_translations(translations)` | একটি `with` ব্লকের সময়কালের জন্য বাঁধে, তারপর আগেরটি ফিরিয়ে আনে। |
| `set_translations(translations)` | ব্লক ছাড়াই বাঁধে, ফ্রেমওয়ার্ক-পরিচালিত জীবনচক্রের জন্য। |
| `get_translations()` | বর্তমান বাঁধাইটি পড়ে, বা `None`। |

বাঁধাইটি একটি `ContextVar`, তাই তা প্রতি-context এবং সমান্তরালতায় নিরাপদ।

## Deferred স্ট্রিং { #deferred-strings }

| নাম | উদ্দেশ্য |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | একটি অনুবাদকে প্রথম ব্যবহার পর্যন্ত পিছিয়ে দেয়। |
| `lazy_pgettext(context, template, /, *, strict=False)` | তার context-যুক্ত রূপ। |
| `LazyString` | দুটিই যা ফেরায়। `str()` ও `format()`-এর মধ্য দিয়ে রেন্ডার হয়, নিজের টেক্সটের সমান হিসেবে তুলনায় ধরা পড়ে, আর ইচ্ছাকৃতভাবেই unhashable। |

## নিচের স্তর { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

একটি t-string কম্পাইল করে, তার ক্যাশ করা স্থির পরিকল্পনাটি পুনর্ব্যবহার করে।

### `CompiledTemplate`

| সদস্য | অর্থ |
| --- | --- |
| `.msgid` | স্থিতিশীল gettext বার্তা-শনাক্তকারী। |
| `.placeholders` | placeholder-এর নাম, প্রথম উপস্থিতির ক্রমে। |
| `.render(pattern)` | একটি প্যাটার্ন যাচাই করে রেন্ডার করে। অমিল হলে **সর্বদা এক্সেপশন তোলে**। |

## টাইপ ও ত্রুটি { #types-and-errors }

### `Translations`

চারটি প্রমিত মেথডের জন্য একটি `runtime_checkable` `Protocol`, সবগুলিই
positional-only:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` এবং Babel-এর
`Translations` — সবগুলিই এটি মেনে চলে।

### এক্সেপশন

| ক্লাস | কখন ওঠে |
| --- | --- |
| `TStringError` | নিচের দুটিরই ভিত্তি ক্লাস। |
| `InvalidTemplateError` | **উৎস** t-string রীতিটি ভাঙে — একটি জটিল ইন্টারপোলেশন, বা ভিন্ন ফরম্যাটিংসহ পুনরাবৃত্ত একটি নাম। |
| `InvalidTranslationError` | **অনুবাদ** তা ভাঙে। ডিফল্ট শিথিল মোডে এটি লগ হয় আর তার বদলে উৎস টেক্সট রেন্ডার হয়। |

## এক্সট্র্যাকশন entry point { #extraction-entry-points }

ইনস্টলের সময় আপনাআপনি নিবন্ধিত হয়; আপনি এদের নাম ধরে উল্লেখ করেন, import
করে নয়।

| গ্রুপ | নাম | কে ব্যবহার করে |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `babel.cfg`-র `method`। |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, আপনাআপনি। |

## পারফরম্যান্স { #performance }

সম্পূর্ণ বিবরণ — কী ক্যাশ হয়, ক্যাশগুলি কীসের উপর কী করে, আর মাপা সংখ্যাগুলি
— আছে [হট পাথ](internals.md#the-hot-path)-এ। সংক্ষেপে: যাচাই ক্যাশ হয়, কখনও
বাদ যায় না, আর গোটা রেন্ডারের খরচ এক মাইক্রোসেকেন্ডেরও ভগ্নাংশ। নিজের
লক্ষ্যে বেঞ্চমার্কটি চালান:

```console
uv run python benchmarks/runtime.py
```
