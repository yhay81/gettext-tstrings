---
description: "pybabel से t-string संदेशों का एक्सट्रैक्शन, और msgfmt तथा बंडल किया हुआ Babel checker कैटलॉग को कैसे सत्यापित करते हैं।"
---

# एक्सट्रैक्शन

एक्सट्रैक्शन वह चरण है जो आपके सोर्स कोड में मार्क किए गए हर संदेश को
अनुवादकों के लिए एक `.pot` टेम्पलेट में इकट्ठा करता है —
[ट्यूटोरियल](tutorial.md) के लूप का चरण 3। यह पेज उस चरण का संदर्भ है:
कॉन्फ़िगरेशन, अपने फ़ंक्शन नाम, सख़्त CI मोड, और वे जाँचें जो उसके बाद आपके
कैटलॉग की रखवाली करती हैं।

एक्सट्रैक्शन को `babel` extra चाहिए:

```console
python -m pip install "gettext-tstrings[babel]"
```

## वर्कफ़्लो { #the-workflow }

`babel.cfg` बनाएँ:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

फिर साधारण Babel कमांड चलाएँ:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` प्रति भाषा एक बार चलता है; उसके बाद `pybabel update` हर ताज़ा
टेम्पलेट को मौजूदा कैटलॉग में समाहित कर देता है। वह आवर्ती चक्र — और उसकी
`fuzzy` एंट्रियाँ किसी रिलीज़ के लिए क्या अर्थ रखती हैं — इसकी सैर
[प्रोडक्शन में](workflow.md#the-cycle-after-the-first-translation) कराई गई
है।

`gettext_tstrings` एक्सट्रैक्टर साधारण `_()`, `gettext()` और `ngettext()`
कॉल भी सँभालता है, इसलिए एक mapping मिश्रित codebase को कवर करती है। यह
`_()`, चार मानक gettext नाम, `tr()` / `ntr()` उपनाम, और deferred
`lazy_gettext()` / `lazy_pgettext()` को पहचानता है।

!!! warning "`-c` वैकल्पिक नहीं है"

    `pybabel extract` अनुवादक टिप्पणियाँ तभी इकट्ठा करता है जब आप
    `-c "Translators:"` पास करें — ठीक वैसे ही जैसे वह साधारण gettext कॉलों
    के लिए करता है।

## अपने फ़ंक्शन नाम पंजीकृत करना { #registering-your-own-function-names }

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

ini फ़ाइल एक स्ट्रिंग देती है, TOML mapping एक सूची, और स्ट्रिंग के भीतर
नामों को whitespace या अल्पविराम अलग करते हैं। चारों वर्तनियाँ काम करती
हैं।

विकल्प हैं: `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` और `npgettext_functions`।

!!! danger "`-k` किसी t-string तक नहीं पहुँचता"

    `mytr(t"…")` जैसे custom helper का नाम ऊपर के किसी विकल्प में देना ही
    होगा। Babel की `--keyword` मशीनरी t-string literal नहीं पढ़ सकती,
    इसलिए `pybabel extract -k mytr` कुछ नहीं पाता और कुछ नहीं कहता — संदेश
    POT से बस अनुपस्थित रहते हैं। साथ-साथ एक्सट्रैक्ट होने वाली साधारण
    gettext कॉलों के लिए `-k` काम करता रहता है।

    केवल मानक argument क्रम समर्थित है: पहले संदेश, `pgettext` के लिए
    context फिर संदेश, `npgettext` के लिए context फिर एकवचन फिर बहुवचन।

## डिफ़ॉल्ट रूप से मज़बूत { #robust-by-default }

एक ख़राब फ़ाइल पूरे रन का अंत नहीं करती:

- जिस t-string को एक्सट्रैक्टर अस्वीकार करता है — attribute पहुँच, कोई
  एक्सप्रेशन, ग़लत argument — वह चेतावनी के रूप में रिपोर्ट होकर छोड़ दिया
  जाता है।
- जो फ़ाइल parse नहीं होती, वह उसी तरह छोड़ दी जाती है।
- वैसी फ़ाइल भी, जिसे केवल `tokenize` नकारता है जबकि `ast` स्वीकार करता है —
  जिस पर Babel का अपना pass अन्यथा रुक जाता।

mapping विकल्पों में `strict = true` रखने पर इनमें से हर एक कठोर विफलता बन
जाता है — CI में आप यही चाहते हैं।

## आपका मौजूदा toolchain इन कैटलॉग को सत्यापित करता है { #your-existing-toolchain-validates-these-catalogs }

Babel हर एक्सट्रैक्ट किए गए संदेश पर एक मानक फ़्लैग लगाता है, और वही एक
पंक्ति उन टूलों में placeholder जाँच सक्रिय करती है जिन्हें आप पहले से चलाते
हैं:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

इसका अनुवाद `こんにちは {nombre}` कर दें, और ग़लती बिना किसी कॉन्फ़िगरेशन
के पकड़ी जाती है:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate इसी जाँच को [Python brace format][weblate-checks] के रूप में
प्रलेखित करता है, और व्यावसायिक प्लेटफ़ॉर्मों की अपनी placeholder QA इसी
फ़्लैग पर आधारित है। उनका व्यवहार उनका है; नीचे के दो टूल ही यहाँ सत्यापित
हैं।

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

उसके ऊपर, यह पैकेज एक Babel **checker** पंजीकृत करता है, जिससे
`pybabel compile` `gettext-tstrings` मार्कर टिप्पणी वाले हर संदेश पर
विनिर्देश के नियम लागू करता है:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

बहुवचन संदेश के लिए संकेतक रूप का नाम लेता है, क्योंकि Babel जो पंक्ति
संख्या रिपोर्ट करता है वह msgid की है और रूसी ब्लॉक में उसके नीचे तीन
`msgstr` होते हैं:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` फिर भी `.mo` लिख देता है"

    ऊपर की त्रुटि रिपोर्ट होती है, exit status `1` होता है — और टूटा हुआ
    कैटलॉग फिर भी कंपाइल हो जाता है। उसे शिप होने से केवल वही exit status
    रोक सकता है; [CI क्या गेट करता है](workflow.md#what-ci-gates) वह बिल्ड
    चरण दिखाता है जो उसे रोकने देता है।

दोनों जाँचें अनावश्यक दोहराव नहीं हैं। बंडल किया हुआ checker कम से कम दो
जगहों पर अधिक सख़्त पक्ष है:

- जिस msgid में केवल escaped braces हों (`Config {{raw}} only`), उसे
  `python-brace-format` फ़्लैग कभी नहीं मिलता, इसलिए कोई बाहरी टूल उसे
  सत्यापित ही नहीं करता।
- बहुवचन रूप एक-एक करके जाँचे जाते हैं। `msgfmt --check-format` ठीक ऊपर वाली
  फ़ाइल पढ़कर `0` से बाहर निकलता है; जो रूप वह placeholder गिरा देता है जिसे
  उसके साथी रूप रखते हैं, वह वहाँ स्वीकार और यहाँ अस्वीकार होता है।

`msgfmt` केवल वही placeholder नाम जाँचता है जिन्हें वह Python brace format
के रूप में parse कर सके, इसलिए ASCII नाम श्रृंखला के हर टूल को संदेश
सत्यापित करने योग्य बनाए रखते हैं। लाइब्रेरी स्वयं कोई भी
`str.isidentifier()` नाम स्वीकार करती है।

## टेम्पलेट और अन्य टूल { #templates-and-other-tools }

t-strings Python सिंटैक्स हैं, इसलिए यह लाइब्रेरी Python सोर्स को कवर करती
है। टेम्पलेट भाषाएँ अपनी i18n का उपयोग करती रहती हैं — Jinja2 का
`{% trans %}`, Django के टेम्पलेट टैग — और उनके लिए Babel के एक्सट्रैक्टर।
सब कुछ उसी PO कैटलॉग में जाता है, इसलिए एक अनुवाद वर्कफ़्लो मिश्रित codebase
को अब भी कवर करता है।

`pygettext` आज t-strings parse नहीं कर सकता, इसीलिए एक्सट्रैक्शन Babel से
होकर जाता है। परिपाटी [विनिर्देश](spec.md) में लिखी हुई है ताकि कोई और
एक्सट्रैक्टर, या भविष्य का `pygettext`, उसे लक्ष्य बना सके।
