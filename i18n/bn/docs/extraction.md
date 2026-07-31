---
description: "pybabel দিয়ে t-string বার্তা এক্সট্র্যাক্ট করা, আর msgfmt ও সঙ্গে দেওয়া Babel চেকার কীভাবে ক্যাটালগ যাচাই করে।"
---

# এক্সট্র্যাকশন

এক্সট্র্যাকশন হল সেই ধাপ, যা আপনার সোর্স কোড থেকে চিহ্নিত প্রতিটি বার্তা
অনুবাদকদের জন্য একটি `.pot` টেমপ্লেটে জড়ো করে —
[টিউটোরিয়াল](tutorial.md)-এর লুপের ৩ নম্বর ধাপ। এই পৃষ্ঠা সেই ধাপের
রেফারেন্স: কনফিগারেশন, নিজস্ব ফাংশন নাম, কড়া CI মোড, আর তার পরে যে যাচাইগুলি
আপনার ক্যাটালগ পাহারা দেয়।

এক্সট্র্যাকশনের জন্য `babel` extra দরকার:

```console
python -m pip install "gettext-tstrings[babel]"
```

## ওয়ার্কফ্লো { #the-workflow }

`babel.cfg` তৈরি করুন:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

তারপর সাধারণ Babel কমান্ডগুলিই ব্যবহার করুন:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` প্রতি ভাষায় একবারই চলে; তারপর থেকে `pybabel update` প্রতিটি নতুন
টেমপ্লেটকে বিদ্যমান ক্যাটালগে ভাঁজ করে নেয়। সেই পুনরাবৃত্ত চক্র — আর তার
`fuzzy` এন্ট্রিগুলি একটি রিলিজের জন্য কী অর্থ বহন করে — নিয়ে হাঁটা হয়েছে
[প্রোডাকশনে](workflow.md#the-cycle-after-the-first-translation) পৃষ্ঠায়।

`gettext_tstrings` এক্সট্র্যাক্টর সাধারণ `_()`, `gettext()` ও `ngettext()`
কলও সামলায়, তাই একটি ম্যাপিংই মিশ্র কোডবেস ঢেকে দেয়। সে চেনে `_()`, চারটি
প্রমিত gettext নাম, `tr()` / `ntr()` alias, আর deferred
`lazy_gettext()` / `lazy_pgettext()`।

!!! warning "`-c` দিয়ে অনুবাদকদের মন্তব্য চালু করুন"

    `pybabel extract` অনুবাদকদের জন্য লেখা মন্তব্য কেবল তখনই জড়ো করে যখন আপনি
    `-c "Translators:"` পাঠান, ঠিক যেমনটি সে সাধারণ gettext কলের ক্ষেত্রে
    করে। এটি বাদ দিলেও এক্সট্র্যাকশন চলে — কেবল মন্তব্যগুলি ক্যাটালগ পর্যন্ত
    কখনও পৌঁছায় না, যেখানে সেগুলিই গোটা ওয়ার্কফ্লোর
    [সবচেয়ে সস্তা মান-উন্নয়নের হাতল](workflow.md#working-with-translators-and-platforms)।

## নিজের ফাংশন নাম নিবন্ধন করা { #registering-your-own-function-names }

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

একটি ini ফাইল একটি স্ট্রিং দেয়, একটি TOML ম্যাপিং দেয় একটি তালিকা, আর
স্ট্রিংয়ের ভিতরে নামগুলিকে আলাদা করে হোয়াইটস্পেস বা কমা। চারটি বানানই কাজ
করে।

অপশনগুলি হল `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` ও `npgettext_functions`।

!!! danger "`-k` কোনও t-string পর্যন্ত পৌঁছয় না"

    `mytr(t"…")`-এর মতো নিজস্ব কোনও helper-এর নাম উপরের অপশনগুলির একটিতে বলে
    দিতেই হবে। Babel-এর `--keyword` যন্ত্রপাতি t-string লিটারেল পড়তে পারে
    না, তাই `pybabel extract -k mytr` কিছুই খুঁজে পায় না, কিছু বলেও না —
    বার্তাগুলি POT থেকে নিছক অনুপস্থিত থাকে। পাশাপাশি এক্সট্র্যাক্ট হওয়া
    সাধারণ gettext কলের জন্য `-k` কাজ করেই যায়।

    কেবল প্রমিত আর্গুমেন্ট-ক্রম সমর্থিত: প্রথমে বার্তা, `pgettext`-এর জন্য
    আগে context তারপর বার্তা, আর `npgettext`-এর জন্য context, তারপর একবচন,
    তারপর বহুবচন।

## স্থানীয়ভাবে শিথিল, CI-তে কড়া { #lenient-locally-strict-in-ci }

ডিফল্টে একটি খারাপ ফাইল গোটা রানটাকে শেষ করে দেয় না:

- এক্সট্র্যাক্টর যে t-string প্রত্যাখ্যান করে — অ্যাট্রিবিউট অ্যাক্সেস,
  একটি এক্সপ্রেশন, একটি ভুল আর্গুমেন্ট — তা সতর্কবার্তা হিসেবে জানিয়ে বাদ
  দেওয়া হয়।
- যে ফাইল parse হবে না, তাকেও একইভাবে বাদ দেওয়া হয়।
- সেই ফাইলটিকেও, যাকে কেবল `tokenize` প্রত্যাখ্যান করে অথচ `ast` মেনে নেয়,
  আর যেটিতে Babel-এর নিজের পাস নাহলে থেমে যেত।

আপনি যখন সম্পাদনা করছেন তখন এটি সুবিধাজনক, আর যখন করছেন না তখন বিপজ্জনক:
বাদ পড়া বার্তা **POT-এ থাকেই না**, তাই তা কখনও অনুবাদ হয় না আর কিছুই সে কথা
জানায় না। যেখানেই এক্সট্র্যাকশনের দিকে কোনও মানুষ তাকিয়ে নেই, সেখানে ম্যাপিং
অপশনে `strict = true` বসান:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

উপরের প্রতিটি সতর্কবার্তা তখন কড়া ব্যর্থতায় পরিণত হয়। একে প্রোডাকশন সেটিং
আর ডিফল্টটিকে স্থানীয় সেটিং হিসেবে ধরুন।

## আপনার বর্তমান toolchain এই ক্যাটালগগুলি যাচাই করে { #your-existing-toolchain-validates-these-catalogs }

Babel এক্সট্র্যাক্ট করা প্রতিটি বার্তায় একটি প্রমিত ফ্ল্যাগ বসায়, আর ওই একটি
লাইনই আপনার আগে থেকে চালানো টুলগুলিতে placeholder যাচাই চালু করে দেয়:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

একে `こんにちは {nombre}` হিসেবে অনুবাদ করুন, আর কোনও কনফিগারেশন ছাড়াই ভুলটি
ধরা পড়বে:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate একই যাচাইকে [Python brace format][weblate-checks] হিসেবে নথিভুক্ত
করে, আর বাণিজ্যিক প্ল্যাটফর্মগুলির নিজস্ব placeholder QA-ও ওই একই ফ্ল্যাগে
বাঁধা। প্রতিটি প্ল্যাটফর্মের আচরণ তার নিজের; নিচের দুটি টুল সেগুলিই যা এখানে
যাচাই করা হয়েছে।

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

তার উপরে, প্যাকেজটি একটি Babel **চেকার** নিবন্ধন করে, তাই `pybabel compile`
`gettext-tstrings` মার্কার-মন্তব্য বহন করা প্রতিটি বার্তায় স্পেসিফিকেশনের
নিয়মগুলি প্রয়োগ করে:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

বহুবচন বার্তার ক্ষেত্রে নির্দেশকটি রূপের নামও বলে, কারণ Babel যে লাইন নম্বর
জানায় তা msgid-এর, আর একটি রুশ ব্লকের নিচে তিনটি `msgstr` থাকে:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` তবু `.mo` লিখেই ফেলে"

    উপরের ত্রুটিটি জানানো হয়, exit status হয় `1` — আর ভাঙা ক্যাটালগটি তবু
    কম্পাইল হয়ে যায়। কেবল ওই exit status-ই কোনও পাইপলাইনকে সেটি পাঠিয়ে দেওয়া
    থেকে থামাতে পারে; [CI কী গেট করে](workflow.md#what-ci-gates) সেই বিল্ড
    ধাপটি দেখায় যা তা করতে দেয়।

দুটি যাচাই অপ্রয়োজনীয় পুনরাবৃত্তি নয়। প্যাকেজের চেকারটি অন্তত দুটি ক্ষেত্রে
বেশি কড়া:

- যে msgid-এর একমাত্র বন্ধনীগুলিই escape করা (`Config {{raw}} only`), সে
  কখনও `python-brace-format` ফ্ল্যাগ পায় না, তাই বাইরের কোনও টুলই তাকে
  যাচাই করে না।
- বহুবচন রূপগুলি একে একে যাচাই হয়। `msgfmt --check-format` উপরের ওই ফাইলটিই
  পড়ে আর `0` দিয়ে বেরিয়ে যায়; যে রূপটি তার সহোদরদের রাখা একটি placeholder
  ফেলে দেয়, সেটি সেখানে গৃহীত আর এখানে প্রত্যাখ্যাত।

`msgfmt` কেবল সেইসব placeholder নাম যাচাই করে যাদের সে Python brace format
হিসেবে parse করতে পারে, তাই ASCII নাম রাখলে শৃঙ্খলের প্রতিটি টুলই বার্তাটি
যাচাই করতে পারে। লাইব্রেরি নিজে `str.isidentifier()` সত্য হয় এমন যেকোনও নাম
গ্রহণ করে।

## টেমপ্লেট ও অন্যান্য টুল { #templates-and-other-tools }

t-strings হল Python সিনট্যাক্স, তাই এই লাইব্রেরি Python সোর্স ঢাকে। টেমপ্লেট
ভাষাগুলি নিজেদের i18n-ই ব্যবহার করে যায় — Jinja2-র `{% trans %}`, Django-র
টেমপ্লেট ট্যাগ — আর তাদের জন্য Babel-এর এক্সট্র্যাক্টরগুলি। সবই একই PO
ক্যাটালগে গিয়ে জমা হয়, তাই একটিই অনুবাদ ওয়ার্কফ্লো এখনও মিশ্র কোডবেস ঢেকে
রাখে।

`pygettext` আজ t-strings parse করতে পারে না, আর সেই কারণেই এক্সট্র্যাকশন
Babel-এর মধ্য দিয়ে চলে। রীতিটি [স্পেসিফিকেশনে](spec.md) লিখে রাখা হয়েছে,
যাতে অন্য কোনও এক্সট্র্যাক্টর, বা ভবিষ্যতের কোনও `pygettext` তাকে লক্ষ্য
করতে পারে।
