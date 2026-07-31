---
description: "রানটাইম API: ক্যাটালগ বাঁধা, প্রতি-request ভাষা, deferred স্ট্রিং, আর ভাঙা অনুবাদ কীভাবে রিপোর্ট হয়।"
---

# গাইড

এই পৃষ্ঠা রানটাইম রেফারেন্স: ক্যাটালগ তৈরি হয়ে যাওয়ার পর আপনার
*অ্যাপ্লিকেশন কোড* এই লাইব্রেরি দিয়ে যা যা করে, সবই। গোটা লুপটি — চিহ্নিত
করা, এক্সট্র্যাক্ট, অনুবাদ, কম্পাইল, রান — এখনও না দেখে থাকলে
[টিউটোরিয়াল](tutorial.md) পাঁচ মিনিটে একবার তার মধ্য দিয়ে হাঁটে; ক্যাটালগ
তৈরি ও যাচাই আছে [এক্সট্র্যাকশন](extraction.md)-এ, আর একটি দল কীভাবে লুপটি
ঘুরিয়ে রাখে — আপডেট চক্র, CI, অনুবাদ প্ল্যাটফর্ম — তা
[প্রোডাকশনে](workflow.md)।

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

!!! warning "worker thread শুরু হয় বাঁধাই ছাড়াই"

    খালি একটি `threading.Thread`, কিংবা `ThreadPoolExecutor.submit`, একেবারে
    নতুন একটি কনটেক্সট নিয়ে শুরু হয় আর বাঁধাইটি উত্তরাধিকারে পায় না — কলটি
    তখন প্রসেস-ব্যাপী বিশ্বব্যাপী gettext ক্যাটালগে ফলব্যাক করে। কনটেক্সটটি
    স্পষ্টভাবে বয়ে নিয়ে যান:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` এটি আগে থেকেই আপনার হয়ে করে দেয়।

## ক্যাটালগ ভুল হলে কী ঘটে { #what-happens-when-a-catalog-is-wrong }

কোনও অনুবাদের placeholder উৎসের সঙ্গে না মিললে — অনুপস্থিত, অজানা বা
নতুনভাবে ফরম্যাট করা কোনও ফিল্ড, যা যাচাই এড়িয়ে গেছে, হাতে সম্পাদনা করা কোনও
MO থেকে, কোনও vendor ক্যাটালগ থেকে, বা যে পাইপলাইন চেকারকে বাদ দেয় তার থেকে —
ডিফল্ট আচরণ হল এক্সেপশন না তুলে উৎস টেক্সটটিই ফিরিয়ে দেওয়া। এটি gettext-এর
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

## একটি ব্যর্থতা-বার্তা পড়া { #reading-a-failure-message }

এই বার্তাগুলি লেখা হয়েছে তাঁদের জন্য যাঁরা এ নিয়ে কিছু করতে পারেন, আর
ক্যাটালগ-সমস্যার ক্ষেত্রে তিনি প্রোগ্রামারের চেয়ে বেশিবার একজন অনুবাদক।
পাঠক যখন ওই অক্ষরগুলি নিজের চোখের সামনেই দেখতে পাচ্ছেন, তখন কেবল `{name}`
অনুপস্থিত বলাটা অন্ধগলি, তাই যেখানে placeholder উপস্থিত বলে মনে হয় অথচ নয়,
সেখানে বার্তাটি কারণটাও বলে। উৎস `Hello {name}`-এর বিপরীতে এদের প্রতিটি
রিপোর্ট হয় `translation does not match the source placeholders:`-এর অধীনে

| অনুবাদে যা আছে | সে যে কারণ দেয় |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` অনুপস্থিত (তাকে ঘিরে থাকা বন্ধনী ASCII `{` ও `}` নয়) |
| `こんにちは {{name}}` | `{name}` অনুপস্থিত (লেখা হয়েছে `{{name}}`, যেভাবে আক্ষরিক বন্ধনী escape করা হয়) |
| `こんにちは name` | `{name}` অনুপস্থিত (নামটি আছে, কিন্তু বন্ধনীর ভিতরে নয়) |
| `こんにちは {名前}` | `{name}` অনুপস্থিত; `{名前}` উৎস বার্তায় নেই |

যেসব অক্ষর দেখা যায় না, তারা আলাদা ব্যবহার পায়। বন্ধনীর ভিতরে একটি no-break
space হল এমন জিনিস যা কোনও input method তৈরি করে আর কোনও এডিটর দেখায় না, তাই
বার্তাটি পাঠক খুঁজে পাবেন না এমন একটি অক্ষরের নাম বলার বদলে তাকে code point
হিসেবে ছাপে:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

যে নামের অক্ষরগুলি একাধিক লিখনপদ্ধতি মিশিয়ে ফেলে — homoglyph-এর ক্ষেত্র,
যেখানে একটি সিরিলিক `а` লাতিন `a` থেকে আলাদা করা যায় না — তাকে দুবার দেখানো
হয়, একবার পাঠযোগ্যভাবে আর একবার escape করে, কারণ কেবল সেই রূপটিই দুটিকে
আলাদা করে চেনায়:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

একটি গ্রিক বা সিরিলিক নাম পুরোপুরি এক লিপিতে লেখা হয়েও কোনও ASCII উৎস-নামের
সঙ্গে সংঘাতে এলে একই অস্পষ্টতা-নিরসন প্রযোজ্য, এক-অক্ষরের লাতিন `a` /
সিরিলিক `а`-র ক্ষেত্রটিসহ।

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
