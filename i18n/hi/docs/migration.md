---
description: "जिस प्रोजेक्ट में पहले से gettext कैटलॉग हैं, वहाँ t-strings अपनाना: क्या अछूता बचता है, क्या fuzzy होता है, और एक-एक कॉल स्थल करके कैसे बढ़ें।"
---

# माइग्रेशन

अगर आपका प्रोजेक्ट पहले से gettext उपयोग करता है, तो यह तय करने वाले प्रश्न
कि यह लाइब्रेरी अपनाने योग्य है या नहीं, थोड़े से ही हैं: क्या यह आपके
मौजूदा कैटलॉग बेकार कर देती है, क्या यह उस कोड के साथ रह सकती है जिसे आप
अभी बदलने को तैयार नहीं, और इस क़दम का कितना हिस्सा एक साथ होना ही चाहिए।
उत्तर, सबसे छोटे पहले:

| प्रश्न | उत्तर |
| --- | --- |
| क्या मौजूदा `.po` और `.mo` फ़ाइलें अब भी काम करती हैं? | हाँ। वही फ़ाइलें, वही टूल। |
| क्या पुरानी और नई कॉल एक ही फ़ाइल में रह सकती हैं? | हाँ, और एक ही एक्सट्रैक्टर mapping दोनों को कवर करती है। |
| क्या msgid बदलता है? | `.format()` से नहीं। `%`-format से हाँ। |
| क्या पूरे प्रोजेक्ट को एक साथ बदलना ही होगा? | नहीं। एक कॉल स्थल भी एक वैध बदलाव है। |
| Jinja, Django टेम्पलेट, JavaScript का क्या? | अछूते, वही कैटलॉग। |

इस पेज का बाक़ी हिस्सा इनमें से हर उत्तर के पीछे का विवरण है।

## `.format()` से: msgid नहीं बदलता { #from-format-the-msgid-does-not-change }

यह वह स्थिति है जहाँ माइग्रेशन की क़ीमत लगभग शून्य है। `str.format` संदेश और
t-string संदेश *एक ही* कैटलॉग key निकालते हैं, क्योंकि दोनों ही तरह key वह
टेक्स्ट है जिसमें `{name}` ज्यों का त्यों बचा रहता है:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

इसलिए मौजूदा अनुवाद जुड़ा ही रहता है। ऐसे कैटलॉग से शुरू करें जिसमें है

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

कॉल बदलें, दोबारा एक्सट्रैक्ट करें, और अपडेट करें:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

जो एंट्री वापस आती है वह metadata की दो पंक्तियों में भिन्न है और कहीं नहीं
— एक मार्कर टिप्पणी जो उसे t-string संदेश के रूप में पहचानती है, और एक स्रोत
पंक्ति संख्या:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

न `fuzzy` फ़्लैग, न दोबारा अनुवाद, किसी भी भाषा में। संदेश तुरंत रेंडर होता
है:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` कैटलॉग को पुराना बताएगी"

    वह मार्कर टिप्पणी और खिसकी हुई पंक्ति संख्याएँ ही
    `pybabel update --check` के लिए यह कहने को काफ़ी हैं कि कैटलॉग दोबारा
    बनाना चाहिए, क्योंकि वह पूरी एंट्री की तुलना करती है, केवल अनुवाद की
    नहीं। कोड बदलाव वाले उसी commit में असली `pybabel update` चलाएँ, और
    कैटलॉग उसी के साथ commit करें — यही आदत
    [CI गेट](workflow.md#what-ci-gates) पहले से माँगता है।

## `%`-format से: msgid बदलता है, इसलिए अनुवाद fuzzy हो जाते हैं { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Printf सिंटैक्स संदेश के *भीतर* रहता है, इसलिए उसे बदलना कैटलॉग key को फिर
से लिख देता है। इससे बचने का कोई रास्ता नहीं, और `%(name)s` को पीछे छोड़ने
की यही ईमानदार क़ीमत है:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` नए संदेश को हटाए गए संदेश का निकट सम्बन्धी पहचानता है और
पुराना अनुवाद साथ ले आता है, fuzzy चिह्नित करके:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

उस स्थिति के बारे में तीन बातें जानने योग्य हैं:

- **रनटाइम पर कुछ नहीं टूटता।** fuzzy एंट्रियाँ कंपाइल की गई `.mo` से बाहर
  रहती हैं, इसलिए जब तक कोई मनुष्य जोड़ी की पुष्टि नहीं करता, एप्लिकेशन स्रोत
  संदेश रेंडर करता है — [वही degradation](workflow.md#the-cycle-after-the-first-translation)
  जिससे कोई भी दोबारा लिखा गया संदेश गुज़रता है।
- **जब तक वे fuzzy हैं, CI हरी रहती है।** placeholder checker fuzzy एंट्रियाँ
  छोड़ देता है, ठीक वैसे ही जैसे `msgfmt --check-format` करता है, क्योंकि जो
  एंट्री रनटाइम तक पहुँच ही नहीं सकती उसे बिल्ड विफल नहीं करना चाहिए। जिस
  क्षण अनुवादक फ़्लैग हटाता है, एंट्री बाक़ी सबकी तरह जाँची जाती है — इसलिए
  पुष्ट अनुवाद में छूटा हुआ `%(name)s` तभी पकड़ा जाता है, यानी ठीक उसी बिंदु
  पर जहाँ वह अन्यथा रेंडर होना शुरू करता।
- **पुराना `python-format` फ़्लैग साथ चला आता है** और उसे `fuzzy` फ़्लैग के
  साथ ही हटा देना चाहिए, वरना `msgfmt --check-format` brace-format संदेश पर
  printf नियम लगाता रहेगा।

नामित printf placeholders के लिए संपादन यांत्रिक है — `%(name)s` `{name}` बन
जाता है और कुछ नहीं हिलता — इसलिए बड़ा कैटलॉग दोबारा अनुवाद नहीं, बल्कि एक
स्क्रिप्टेड पास और उसके बाद अनुवादक की समीक्षा है। स्थानिक `%s` यांत्रिक नहीं
है: उसका कोई नाम नहीं जिसे आगे ले जाया जा सके, और नाम चुनना ही इस बदलाव का
मक़सद है।

इसलिए माइग्रेशन उतनी ही गति से बढ़ सकता है जितनी समीक्षा अनुमति दे: बिना बदली
हुई fuzzy एंट्री कैटलॉग में दिखता हुआ बचा काम है, टूटा हुआ बिल्ड नहीं।

## पुरानी और नई कॉल साथ रहती हैं { #old-and-new-calls-coexist }

जो एक्सट्रैक्टर t-strings पढ़ता है वही साधारण gettext कॉल भी पढ़ता है, इसलिए
एक mapping माइग्रेशन के बीच वाली फ़ाइल को कवर कर लेती है:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

दोनों संदेश एक ही टेम्पलेट में पहुँचते हैं, और केवल t-string वाला वह मार्कर
टिप्पणी लिए होता है जो इस लाइब्रेरी की अतिरिक्त जाँच चालू करती है:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

यह `_()`, चार मानक gettext नाम, `tr()` / `ntr()` उपनाम, और deferred
`lazy_gettext()` / `lazy_pgettext()` को पहचानता है। अपना कोई helper हो तो
उसे [mapping में नाम देना](extraction.md#registering-your-own-function-names)
होगा।

रनटाइम पर दोनों शैलियाँ बराबर स्वतंत्र हैं: `gettext.translation()` एक
translations object लौटाता है, और `_` तथा इस लाइब्रेरी के entry points दोनों
उसी से पढ़ते हैं।

## जो नहीं बदलता { #what-does-not-move }

- **टेम्पलेट भाषाएँ।** Jinja2 का `{% trans %}`, Django के टेम्पलेट टैग, और
  उनके Babel एक्सट्रैक्टर बिना बदले काम करते रहते हैं और उन्हीं PO कैटलॉग को
  भरते रहते हैं। t-strings Python सिंटैक्स हैं; वे Python सोर्स पर लागू होते
  हैं।
- **आपकी कैटलॉग फ़ाइलें।** न फ़ॉर्मैट बदलता है, न कोई नई फ़ाइल, न कोई रूपांतरण
  चरण।
- **आपका अनुवाद प्लेटफ़ॉर्म।** `.po` का आदान-प्रदान वैसा ही है, और t-string
  संदेश जो `python-brace-format` फ़्लैग लिए चलता है वही फ़्लैग `.format()`
  संदेश भी लिए चलता है — इसलिए placeholder QA काम करती रहती है।
- **ग़ैर-Python कोड।** उसी प्रोजेक्ट का JavaScript या C कैटलॉग अप्रभावित है।

## माइग्रेशन की चेकलिस्ट { #a-migration-checklist }

1. जहाँ `pybabel` चलता है वहाँ `babel` extra जोड़ें, और `babel.cfg` की
   `python` mapping को `gettext_tstrings` method में बदल दें — तब एक ही
   mapping दोनों शैलियों को कवर करती है, और साधारण कॉलों के लिए `-k` काम
   करता रहता है।
2. पहले `.format()` कॉल स्थल बदलें। दोबारा एक्सट्रैक्ट करें, `pybabel update`
   चलाएँ, और कैटलॉग कोड के साथ commit करें; कोई fuzzy एंट्री अपेक्षित नहीं।
3. `%`-format कॉल स्थल उतने-उतने बैचों में बदलें जितनों की समीक्षा करा सकें,
   साथ आए placeholders को फिर से लिखते हुए और `fuzzy` तथा `python-format`
   फ़्लैग हटाते हुए।
4. जिसे प्रतिबंध अस्वीकार करता है उसे ठीक करें: interpolation सादा नाम ही
   होना चाहिए, इसलिए `t"Hello {user.name}"` पहले एक स्थानीय वेरिएबल बनता है।
   यह कॉल स्थल का संपादन है, कैटलॉग का नहीं।
5. सफ़ाई पूरी हो जाने पर एक्सट्रैक्टर mapping में `strict = true` चालू करें,
   ताकि जो संदेश एक्सट्रैक्ट न हो सके वह टेम्पलेट से ग़ायब होने की बजाय
   [बिल्ड](extraction.md#lenient-locally-strict-in-ci) विफल करे।
6. [प्रोडक्शन में](workflow.md#what-ci-gates) दी गई रनटाइम जाँच जोड़ें: हर
   शिप होने वाली भाषा में एक संदेश सख़्त `Translator` से रेंडर करें।

चरण 2 और 3 साधारण commits हैं। इस सूची में किसी चीज़ के लिए flag day नहीं
चाहिए।
