---
description: "রানটাইম API: কোন এন্ট্রি পয়েন্ট ব্যবহার করবেন, ক্যাটালগ বাঁধা, প্রতি-request ভাষা, deferred স্ট্রিং, locale-সচেতন মান, আর ভাঙা অনুবাদ কীভাবে রিপোর্ট হয়।"
---

# গাইড

এই পৃষ্ঠা রানটাইম রেফারেন্স: ক্যাটালগ তৈরি হয়ে যাওয়ার পর আপনার
*অ্যাপ্লিকেশন কোড* এই লাইব্রেরি দিয়ে যা যা করে, সবই। গোটা লুপটি — চিহ্নিত
করা, এক্সট্র্যাক্ট, অনুবাদ, কম্পাইল, রান — এখনও না দেখে থাকলে
[টিউটোরিয়াল](tutorial.md) পাঁচ মিনিটে একবার তার মধ্য দিয়ে হাঁটে; ক্যাটালগ
তৈরি ও যাচাই আছে [এক্সট্র্যাকশন](extraction.md)-এ, আর একটি দল কীভাবে লুপটি
ঘুরিয়ে রাখে — আপডেট চক্র, CI, অনুবাদ প্ল্যাটফর্ম — তা
[প্রোডাকশনে](workflow.md)।

## কোন এন্ট্রি পয়েন্ট ব্যবহার করব? { #which-entry-point-should-i-use }

প্যাকেজটি একটি বার্তা অনুবাদের কয়েকটি উপায় এক্সপোর্ট করে, কারণ অ্যাপ্লিকেশন
কয়েকভাবে ভাষা বাঁধে। আপনার প্রোগ্রাম কীভাবে ঠিক করে সে কোন ভাষায় আছে, সেই
অনুযায়ী বেছে নিন:

| আপনার পরিস্থিতি | যা ব্যবহার করবেন |
| --- | --- |
| গোটা প্রসেসের জন্য একটিই ভাষা — CLI, ডেস্কটপ অ্যাপ, স্ক্রিপ্ট | `Translator`, `_` নামে কল করা |
| প্রতি request বা প্রতি async টাস্কে একটি ভাষা — ওয়েব অ্যাপ্লিকেশন | কাজটির চারপাশে `use_translations()`, তারপর `tr()` |
| import-এর সময়েই সংজ্ঞায়িত বার্তা — ফর্ম লেবেল, enum, ধ্রুবক | `lazy_gettext()` বা `lazy_pgettext()` |
| গণনা ঠিক করে দেয় কোন শব্দরূপ | `ngettext()` / `npgettext()`, উপরের যে রূপেই হোক |
| ক্যাটালগ ছাড়াই একটি প্যাটার্ন রেন্ডার করা | `compile_template()` |

নিচের সবটুকুই ওই পাঁচটি, ঠিক এই ক্রমে।

## ক্যাটালগ বাঁধা { #binding-a-catalog }

সুপারিশ করা আকৃতিটি gettext-এর ক্লাস-ভিত্তিক ব্যবহারের প্রতিফলন: একবার একটি
প্রমিত translation অবজেক্ট বেঁধে নিন, আর callable প্রসেসরটিকে `_` হিসেবে
ব্যবহার করুন।

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

মডিউল-স্তরের ফাংশনগুলি স্ট্যান্ডার্ড লাইব্রেরির নাম আর তার
positional-only কলিং রীতি মেনে চলে:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` ও `ntr` হল `gettext` ও `ngettext`-এর হুবহু alias।

## প্রতি-request ভাষা { #per-request-language }

একটি ওয়েব ফ্রেমওয়ার্ক প্রতি request-এ একটি ভাষা বাছে। request-এর
translations বর্তমান কনটেক্সটে বেঁধে দিন, তাহলে প্রতিটি মডিউল-স্তরের কল সেই
ভাষাতেই মীমাংসিত হয়, একই সঙ্গে চলা request-গুলির মধ্যেও নিরাপদে:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    name = request.user.display_name
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` `with` ব্লক ছাড়াই বেঁধে দেয়, সেইসব
ফ্রেমওয়ার্কের জন্য যারা request-এর জীবনচক্র নিজেরাই সামলায়;
`get_translations()` বর্তমান বাঁধাইটি পড়ে। স্পষ্ট `translations=` আর্গুমেন্ট
সর্বদা কনটেক্সটের উপরে জেতে, আর কনটেক্সট না বাঁধা থাকলে স্ট্যান্ডার্ড
লাইব্রেরির বিশ্বব্যাপী ইনস্টল করা gettext ফাংশনে ফলব্যাক হয়। Flask ও ASGI
মিডলওয়্যারের কাজ-করা উদাহরণ আছে
[প্রোডাকশনে](workflow.md#binding-a-language-at-runtime) পৃষ্ঠায়।

## বিলম্বিত (deferred) অনুবাদ { #deferred-translation }

একটি t-string তার মান তৎক্ষণাৎ ধরে ফেলে, যা import-সময়ে সংজ্ঞায়িত কোনও
স্ট্রিংয়ের জন্য ভুল — একটি ফর্ম লেবেল, একটি enum মান, একটি মডিউল ধ্রুবক —
যাকে *ব্যবহারের* সময় যে ভাষা সক্রিয় সেই ভাষাতেই রেন্ডার হতে হবে।

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

একটি `LazyString` রেন্ডার হয় `str()`, `format()` ও f-strings-এর মধ্য দিয়ে,
আর তার রেন্ডার করা টেক্সটের সমান হিসেবে তুলনায় ধরা পড়ে।

!!! note "ইচ্ছাকৃতভাবেই unhashable"

    একটি `LazyString`-এর টেক্সট সক্রিয় ভাষার উপর নির্ভর করে, তাই ভাষা বদলালে
    hash বদলে যেত এবং তাকে ধরে রাখা যেকোনও set বা dict নীরবে নষ্ট করত। কী
    দরকার হলে আগে `str()` ডাকুন।

`strict` ঠিক হয় যেখানে বার্তাটি লেখা হয়, যেখানে সে রেন্ডার হয় সেখানে নয়:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

একটি deferred স্ট্রিং রেন্ডার হয় শেষমেশ যেখানে তাকে ব্যবহার করা হয় সেখানে —
কোনও টেমপ্লেটের ভিতরে, কোনও ফর্মে, কোনও লগ লাইনে — আর সেই জায়গাটি খুব কমই
জানে এটি কোনও টেস্ট রান না প্রোডাকশন। সংজ্ঞার জায়গায় `strict=True` পাঠানোই
সেই জিনিস, যা এমন একটি স্ট্রিংয়ের জন্যও ওই
[CI-তে সশব্দ, প্রোডাকশনে শিথিল](#what-happens-when-a-catalog-is-wrong)
পছন্দটিকে খাটতে দেয়, যে স্ট্রিংটি তার কল-সাইটে রেন্ডার হয় না।

বহুবচন রূপ রানটাইমের গণনার উপর নির্ভর করে, তাই যেখানে গণনাটি জানা সেখানেই
`ngettext` দিয়ে সেগুলি তৎক্ষণাৎ রেন্ডার করুন।

## একসঙ্গে একাধিক ভাষা { #several-languages-at-once }

একটিমাত্র request-এরও প্রায়ই একাধিক ভাষা দরকার হয়: পাঠকের জন্য রেন্ডার করা
একটি পৃষ্ঠা, যা আবার অন্য ভাষায় সেট করা কোনও অ্যাকাউন্টের জন্য একটি
বিজ্ঞপ্তিও সারিতে তুলে দেয়; কিংবা এমন একটি সারসংক্ষেপ, যা প্রত্যেক
অংশগ্রহণকারীকে তাঁর নিজের ভাষাতেই উদ্ধৃত করে। বাঁধাই নেস্ট করে, আর ভিতরের
ব্লক ছেড়ে বেরোলেই বাইরেরটি ফিরে আসে।

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

প্রাপকদের একটি তালিকার উপর কাজটি করে deferred স্ট্রিং: বার্তাটি একবারই লেখা
হয়, import-সময়ে, আর রেন্ডার হয় ভাষা-পিছু একবার করে।

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

বাঁধাইটি একটি `ContextVar`, কোনও ভাগ-করা অবজেক্টে রাখা স্ট্যাক নয়, তাই
পরস্পর-ওভারল্যাপ করা request-গুলি একে অপরের ভাষা তুলে নিতে পারে না — এর মধ্যে
সেই ক্ষেত্রটিও পড়ে যেখানে তারা নিজেদের ব্লক থেকে *বেরোয়* ঠিক সেই ক্রমেই যে
ক্রমে তারা ঢুকেছিল, আর এই ইন্টারলিভিংটিই একটি পুশডাউন স্ট্যাক ভুল করে।
ভাষা-পিছু একটি ক্যাটালগ লোড করা সস্তা: `gettext.translation()` প্রতিটি `.mo`
একবারই পার্স করে আর এমন অনুলিপি বিলি করে যারা পার্স করা ক্যাটালগটি ভাগ করে
নেয়।

!!! warning "worker thread বাঁধাইটি উত্তরাধিকারে পায় কি না, তা বিল্ডের উপর নির্ভর করে"

    খালি একটি `threading.Thread`, কিংবা `ThreadPoolExecutor.submit`, শুরু হয় হয়
    কলারের কনটেক্সটের একটি অনুলিপি থেকে, নয়তো একেবারে খালি একটি কনটেক্সট থেকে;
    কোনটি, তা ঠিক করে `sys.flags.thread_inherit_context` — ফ্রি-থ্রেডেড বিল্ডে
    ডিফল্টে সত্য, আর অন্য সব জায়গায় মিথ্যা। তাই একই কোড 3.14t-তে বাঁধাই করা
    ভাষাটি রেন্ডার করে, আর 3.14-তে প্রসেস-ব্যাপী বিশ্বব্যাপী ক্যাটালগটি।
    ডিফল্টের উপর নির্ভর না করে কনটেক্সটটি পাস করে দিন:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` এটি আগে থেকেই আপনার হয়ে করে দেয়।

## Locale-সচেতন মান { #locale-aware-values }

এই লাইব্রেরি ঠিক করে দেয় অনুবাদ করা বার্তার *কোথায়* একটি মান বসবে। মানটিকে
নিজে সে স্থানীয়করণ করে না। `{amount:,.2f}` হল একটি Python ফরম্যাট স্পেক, যার
আচরণ নির্দিষ্ট — প্রতি তিন অঙ্কে একটি কমা আর দশমিকের আগে একটি বিন্দু — আর
বার্তাটি যে ভাষাতেই থাকুক, সে একই অক্ষরই তৈরি করে:

```pycon
>>> f"{1234.5:,.2f}"  # the same in every locale
'1,234.50'
```

জার্মান ওই সংখ্যাটি লেখে `1.234,50`, ফরাসি `1 234,50`, আর হিন্দি `1234567`-কে
`1,234,567` নয়, `12,34,567` হিসেবে দল বাঁধে। সংখ্যা, মুদ্রা, তারিখ, সময় ও একক
[Babel][babel-numbers]-এর এলাকা। আগে মানটি ফরম্যাট করুন, তারপর তৈরি হওয়া
স্ট্রিংটি বসান:

```python
from babel.numbers import format_currency

total = format_currency(amount, "EUR", locale=locale)
tr(t"Your order comes to {total}")
```

গণনা-নির্ভর বার্তায় সংখ্যাটি দুটি কাজ করে — সে বহুবচনের রূপ বেছে দেয়, আর সে
টেক্সটেও দেখা যায় — আর কেবল দ্বিতীয়টিই স্থানীয়কৃত হয়। বাছাইয়ের জন্য কাঁচা
গণনাটি রাখুন, আর দেখানোর জন্য ফরম্যাট করা স্ট্রিংটি পাঠান:

```python
from babel.numbers import format_decimal

shown = format_decimal(n, locale=locale)
_.ngettext(t"One file", t"{shown} files", n)
```

কল করার আগেই ফরম্যাট করাটিই ফরম্যাট স্পেককে ক্যাটালগের বাইরে রাখে: অনুবাদক যা
দেখেন তা তৈরি হয়ে যাওয়া এক টুকরো টেক্সট, কোনও সংখ্যা আর তাকে রেন্ডার করার
নির্দেশ নয়।

## ক্যাটালগ ভুল হলে কী ঘটে { #what-happens-when-a-catalog-is-wrong }

কোনও অনুবাদের placeholder উৎসের সঙ্গে না মিললে — অনুপস্থিত, অজানা বা
নতুনভাবে ফরম্যাট করা কোনও ফিল্ড, যা যাচাই এড়িয়ে গেছে, হাতে সম্পাদনা করা কোনও
MO থেকে, কোনও vendor ক্যাটালগ থেকে, বা যে পাইপলাইন চেকারকে বাদ দেয় তার থেকে —
ডিফল্ট আচরণ হল এক্সেপশন না তুলে উৎস বার্তাটিই রেন্ডার করা। এটি gettext-এর
নিজের চুক্তিরই প্রতিফলন: খারাপ ক্যাটালগ কখনও অ্যাপ্লিকেশন ভাঙে না।

`Hello {name}`-এর অনুবাদ `こんにちは {nombre}` হলে রেন্ডার সফল হয় আর
`gettext_tstrings` লগারে একটি সতর্কবার্তা যায়:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

সতর্কবার্তাটি প্রতি বার্তা ও প্যাটার্ন-পিছু একবারই ওঠে, প্রতি রেন্ডারে নয়,
তাই একটি ভাঙা ক্যাটালগ এন্ট্রি লগ ভাসিয়ে দেয় না।

টেস্ট ও CI-এর জন্য সশব্দে ব্যর্থ হওয়া বেছে নিন:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

তখন একই লুকআপ এক্সেপশন তোলে, "using source text" অংশটুকু বাদ দিয়ে একই বাক্য
বয়ে এনে:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

এই বার্তাগুলি লেখা হয়েছে তাঁদের জন্য যাঁরা এ নিয়ে কিছু করতে পারেন, আর
ক্যাটালগ-সমস্যার ক্ষেত্রে তিনি প্রোগ্রামারের চেয়ে বেশিবার একজন অনুবাদক — তাই
যেখানে placeholder উপস্থিত বলে মনে হয় অথচ নয়, সেখানে বার্তাটি "অনুপস্থিত"
কথাটি ফের না বলে কারণটাই ব্যাখ্যা করে। পূর্ণ-প্রস্থ বন্ধনী, দ্বিগুণ হয়ে যাওয়া
`{{name}}`, অদৃশ্য একটি no-break space, লাতিন অক্ষরের মাঝে একটি সিরিলিক অক্ষর:
প্রতিটির নিজস্ব ভাষ্য আছে, উদাহরণসহ তালিকাভুক্ত
[অনুবাদকদের জন্য](translators.md#reading-a-failure-message) পৃষ্ঠায়। ওই পৃষ্ঠাটি
লেখাই হয়েছে যিনি `.po` সম্পাদনা করছেন তাঁর হাতে তুলে দেওয়ার জন্য।

## ক্যাটালগ ছাড়াই একটি প্যাটার্ন রেন্ডার করা { #rendering-a-pattern-without-a-catalog }

`compile_template` একই যন্ত্রপাতিকে এক স্তর নিচে খুলে দেখায়: সে একটি
t-string-কে তার msgid ও বাঁধা মানের সেটে পরিণত করে, আর আপনি যে প্যাটার্নই
হাতে দিন তা রেন্ডার করে।

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` একই নিয়মে যাচাই করে আর অমিল হলে **সর্বদা এক্সেপশন তোলে**। এখানে কোনও
শিথিল মোড নেই: শিথিলতা আছে যাতে একটি *ক্যাটালগ* লুকআপ উৎস টেক্সটে নেমে আসতে
পারে, আর আপনি নিজে যে প্যাটার্ন পাঠিয়েছেন তার নেমে আসার মতো কিছু নেই।

## নিরাপত্তা ও পরিধি { #safety-and-scope }

এটি বৈধ:

```python
tr(t"Hello {name}")
```

এগুলি ইচ্ছাকৃতভাবেই প্রত্যাখ্যাত:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

আগে একটি অর্থবহ মান হিসেব করে নিন:

```python
name = user.display_name()
tr(t"Hello {name}")
```

এই সীমাবদ্ধতা স্থিতিশীল ক্যাটালগ কী তৈরি করে, অনুবাদকদের কাজে লাগার মতো নাম
দেয়, আর একটি অনূদিত স্ট্রিংকে এক্সপ্রেশন ভাষা হয়ে ওঠা থেকে আটকায়।

নিশ্চয়তাটির পরিধি *কাঠামো ও ফরম্যাটিং* পর্যন্ত: একটি অনুবাদ কখনও মূল্যায়িত
হয় না, আর সে কখনও অ্যাট্রিবিউট অ্যাক্সেস, কল, কনভার্শন বা ফরম্যাট স্পেক যোগ
করতে পারে না। দুটি জিনিস কলারেরই দায়িত্বে থাকে, ঠিক যেমন stdlib gettext-এ —
রেন্ডার করা আউটপুটকে তার গন্তব্যের (HTML, shell, terminal) জন্য **escape
করা**, আর **ক্যাটালগের অখণ্ডতা**, যেহেতু বিদ্বেষী কোনও ক্যাটালগ আউটপুটের
আকার বাড়াতে একটি placeholder পুনরাবৃত্তি করতে পারে, যা placeholder-ভিত্তিক
যেকোনও i18n-এরই সহজাত।

  [babel-numbers]: https://babel.pocoo.org/en/latest/api/numbers.html
