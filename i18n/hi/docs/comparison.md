---
description: "एक ही अनुवाद-योग्य संदेश %-format, .format(), flufl.i18n के $-strings और t-string से लिखा हुआ — हर तरीक़ा values कैसे बाँधता है और क्षतिग्रस्त कैटलॉग के साथ क्या करता है।"
---

# t-strings क्यों

एक अनुवाद-योग्य संदेश में value रखने के चार तरीक़े, एक ही वाक्य पर तुलना
किए हुए। संक्षेप में:

- **%-format** में अनुवादक द्वारा एक अक्षर मिटा देना प्रोडक्शन में क्रैश बन
  जाता है।
- **str.format** में अनुवाद आपके कोड द्वारा पास किए गए ऑब्जेक्ट्स के
  attributes पढ़ सकता है — रहस्यों (secrets) समेत।
- **$-strings** (flufl.i18n) में values कॉल करने वाले फ़ंक्शन के वेरिएबल्स
  से अप्रत्यक्ष रूप से खींची जाती हैं, और dotted placeholders भी attributes
  तक पहुँचते हैं।
- **t-strings** में फ़ॉर्मैटिंग आपके कोड में रहती है, अनुवादों की रनटाइम पर
  जाँच होती है, और टूटा हुआ कैटलॉग क्रैश करने की बजाय स्रोत टेक्स्ट पर
  फ़ॉलबैक करता है।

इस पेज का शेष भाग इसका प्रमाण है, एक-एक तरीक़ा करके।

!!! note "हर अनूदित संदेश को तीन पक्ष छूते हैं"

    **कैटलॉग** अनुवादों की फ़ाइल है — मनुष्य जब उसे संपादित करते हैं तब
    `.po`, और एप्लिकेशन के लोड करने के लिए `.mo` में कंपाइल
    ([ट्यूटोरियल](tutorial.md) दोनों से गुज़रता है)। हर संदेश को तीन पक्ष
    छूते हैं: **डेवलपर** स्रोत स्ट्रिंग लिखता है, **अनुवादक** कैटलॉग
    संपादित करता है — अक्सर किसी बाहरी प्लेटफ़ॉर्म पर, किसी भी कोड समीक्षा
    से दूर — और **एप्लिकेशन** रनटाइम पर दोनों को साथ रेंडर करता है। नीचे की
    हर फ़ॉर्मैटिंग शैली एक ही सवाल का अलग उत्तर देती है: *फ़ॉर्मैट भाषा का
    कितना हिस्सा कैटलॉग के नियंत्रण में जाता है?* उदाहरणों में `_` अनुवाद
    फ़ंक्शन का पारंपरिक नाम है, और `tr` इस लाइब्रेरी का।

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

क्या ग़लत हो सकता है: अनुवाद में एक मिटाया हुआ अक्षर रेंडर को क्रैश कर देता
है।

कैटलॉग स्ट्रिंग printf सिंटैक्स ढोती है, जिसमें अंत में एक type-अक्षर भी है
— `%(name)s` का `s` — जिसे अनदेखा करना आसान है और नुक़सान पहुँचाना भी:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

PO एडिटर में एक-अक्षर का संपादन प्रोडक्शन में traceback बन जाता है। GNU
`msgfmt --check-format` इसे पकड़ तो लेता है, पर केवल `python-format` फ़्लैग
वाले संदेशों के लिए, और तभी जब कैटलॉग आपके एप्लिकेशन तक पहुँचने से पहले
वास्तव में msgfmt से होकर गुज़रे।

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

यह अंतिम type-अक्षर हटा देता है और नामित, स्वतंत्र रूप से पुनर्क्रमित होने
योग्य placeholder रखता है। जो ग़लत हो सकता है, वह लेन-देन के दूसरे छोर पर
चला जाता है: अनुवाद को आपके ऑब्जेक्ट्स पर अधिकार मिल जाता है।

`str.format` एक छोटी एक्सप्रेशन भाषा है, और किसी स्ट्रिंग पर उसे कॉल करने का
अर्थ है उस स्ट्रिंग को उसके उपयोग का अधिकार सौंपना:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

अब उन शाब्दिक स्ट्रिंग्स की जगह वह रखिए जो `_()` लौटाता है। यदि
`Hello {name}` का कोई अनुवाद `{conf.api_key}` बनकर लौटे, तो उसे रेंडर करना
आपकी API key छाप देता है — क्या पढ़ा गया, यह आपके कोड ने नहीं, कैटलॉग ने तय
किया। कैटलॉग कोड नहीं है, पर डेटा की तरह यात्रा करता है: अनुवाद प्लेटफ़ॉर्म
तक बाहर, कई हाथों से होकर, `.po` बनकर वापस, `.mo` में कंपाइल, कभी-कभी पूरी
तरह आपके प्रोजेक्ट से बाहर से vendored। `.format()` उस यात्रा के हर चरण को
आपके पास किए गए ऑब्जेक्ट्स पर attribute पहुँच दे देता है।

## `$`-strings और flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

मानक लाइब्रेरी का [`string.Template`][stdlib-template] `$name` इंटरपोलेशन
भाषा देता है, पर स्वयं कोई अनुवाद API नहीं है। [`flufl.i18n`][flufl-i18n]
उस शैली को gettext कैटलॉग लुकअप से जोड़ता है। ध्यान दें कि value कभी पास
नहीं की जाती: flufl.i18n प्रतिस्थापन namespace को कॉलर के globals और locals
से बनाता है — कॉल स्थल पर जो भी वेरिएबल मौजूद हैं, वे संदेश को उपलब्ध हैं।
एक वैकल्पिक `extras` mapping दोनों पर वरीयता पाती है। इसकी अनुवादक-सम्मुख
सिंटैक्स में कोई अंतिम type-अक्षर या फ़ॉर्मैट स्पेसिफ़ायर नहीं है, और
placeholders स्वतंत्र रूप से पुनर्क्रमित किए जा सकते हैं।

अनुपलब्ध प्रतिस्थापन कोई exception नहीं उठाता। `name = "Ada"` के साथ और
कॉलर के namespace में कोई `nombre` न होने पर, कैटलॉग का अनुवाद
`Hello $nombre` `Hello $nombre` के रूप में ही रेंडर होता है: अनसुलझा
placeholder दिखता रहता है। यह [प्रलेखित व्यवहार][documented behavior] कॉल को
विफल करने की बजाय अनूदित संदेश के शेष भाग को बचा लेता है। किसी attribute को
सुलझाते या value बदलते समय उठे exceptions फिर भी आगे बढ़ सकते हैं।

एक प्रासंगिक अर्थ में `flufl.i18n` नंगे `string.Template` से अधिक सक्षम है।
इसका [custom Template] `$settings.api_key` जैसे dotted placeholders स्वीकार
करता है, और इसका [translator] उन पथों को कॉलर की values के विरुद्ध सुलझाता
है। अनूदित placeholder कॉलर के किसी भी उपलब्ध local या global का नाम ले
सकता है और dotted सिंटैक्स से उसके attributes में उतर सकता है। जब किसी
संदेश को attribute चाहिए तो यह सुविधाजनक है, पर साथ ही कॉलर का frame कैटलॉग
के प्रतिस्थापन namespace का हिस्सा बन जाता है। नीचे की तुलना `flufl.i18n`
6.0.0 का वर्णन करती है, `string.Template` के हर संभव उपयोग का नहीं।

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

कैटलॉग को अब भी `Hello {name}` ही दिखता है और वह एक साधारण PO/MO कैटलॉग
बना रहता है। फ़र्क़ इसमें है कि अनुवाद को *क्या कहने की अनुमति है*, और उसकी
जाँच कौन करता है।

यह लाइब्रेरी रेंडर करने से पहले हर अनुवाद की स्रोत संदेश के placeholders के
विरुद्ध जाँच करती है, और सिर्फ़ नंगे नाम स्वीकार करती है, और कुछ नहीं।
`t"Hello {name}"` के विरुद्ध:

| अनुवाद में यह होने पर | इस संदेश के साथ अस्वीकृत होता है |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

अस्वीकृत का अर्थ क्रैश नहीं: डिफ़ॉल्ट रूप से लाइब्रेरी एक चेतावनी लॉग करती
है और स्रोत टेक्स्ट रेंडर करती है, इसलिए ख़राब कैटलॉग एप्लिकेशन को कभी नहीं
गिराता —
[वही अनुबंध जो gettext स्वयं निभाता है](guide.md#what-happens-when-a-catalog-is-wrong)।

फ़ॉर्मैटिंग वहीं रहती है जहाँ वह लिखी गई थी — कोड में:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` कैटलॉग तक कभी नहीं पहुँचता, इसलिए कोई अनुवाद उसे बदल नहीं सकता, और
किसी अनुवादक को उसे देखना नहीं पड़ता।

एक और फ़र्क़ टूलिंग का है: t-strings नया सिंटैक्स हैं, इसलिए उन्हें `.pot`
में एक्सट्रैक्ट करने के लिए फ़िलहाल t-string-सचेत एक्सट्रैक्टर चाहिए, जैसे
वह जो यह पैकेज [Babel के लिए देता है](extraction.md)।

## आमने-सामने { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| क्या placeholder नामित है? | हाँ | हाँ | हाँ | हाँ |
| क्या अनुवादक placeholders का क्रम बदल सकता है? | हाँ | हाँ | हाँ | हाँ |
| values कहाँ से आती हैं? | एक स्पष्ट mapping | स्पष्ट arguments | कॉलर के local और global वेरिएबल, साथ में वैकल्पिक `extras` | t-string के भीतर कैप्चर की गई values |
| क्या कैटलॉग value की फ़ॉर्मैटिंग बदल सकता है? | हाँ | हाँ | नहीं | नहीं |
| क्या कैटलॉग ऑब्जेक्ट्स के भीतर पहुँच सकता है (attribute access)? | नहीं | हाँ | हाँ, dotted नामों से | नहीं |
| अनुवाद कोई placeholder *छोड़ दे* — क्या रेंडर होता है? | value चुपचाप ग़ायब हो जाती है | value चुपचाप ग़ायब हो जाती है | value चुपचाप ग़ायब हो जाती है | स्रोत टेक्स्ट, एक चेतावनी के साथ ([डिफ़ॉल्ट रूप से](guide.md#what-happens-when-a-catalog-is-wrong)) |
| अनुवाद कोई अज्ञात placeholder *जोड़ दे* — क्या रेंडर होता है? | एक exception | एक exception | placeholder टेक्स्ट के रूप में दिखता रहता है | स्रोत टेक्स्ट, एक चेतावनी के साथ ([डिफ़ॉल्ट रूप से](guide.md#what-happens-when-a-catalog-is-wrong)) |
| क्या रेंडर के समय placeholders की जाँच होती है? | नहीं | नहीं | नहीं | हाँ (नीचे देखें) |
| Babel कौन-सा PO फ़्लैग अनुमानित करता है, जिससे मौजूदा टूल सत्यापन करें? | `python-format` | `python-brace-format` | कोई नहीं | `python-brace-format` |
| क्या साधारण PO/MO कैटलॉग उपयोग होते हैं? | हाँ | हाँ | हाँ | हाँ |
| क्या custom सोर्स एक्सट्रैक्टर चाहिए? | नहीं | नहीं | नहीं | हाँ, फ़िलहाल |

रेंडर-समय जाँच के बारे में: एकवचन संदेशों की placeholder की सटीक बराबरी की
जाँच होती है। बहुवचन संदेशों की भी होती है, उस
[union/intersection नियम](spec.md) के विरुद्ध जो लक्ष्य भाषा के बहुवचन रूपों
को स्रोत से भिन्न होने देता है; प्रति-रूप सख़्त जाँच कैटलॉग कंपाइल होते समय
चलती है ([एक्सट्रैक्शन](extraction.md))।

format-flag वाली पंक्ति placeholder-सचेत सत्यापन के बारे में है, कैटलॉग
संगतता के बारे में नहीं। `कोई नहीं` का अर्थ है कि मानक gettext टूल संदेश को
पढ़ते और कंपाइल तो करते हैं, पर `msgfmt --check-format` के पास लागू करने के
लिए कोई `$`-placeholder व्याकरण नहीं है।

## इसकी क़ीमत क्या है { #what-it-costs }

कोई f-string इस तरह बिलकुल उपयोग नहीं हो सकता — किसी भी लाइब्रेरी तक
पहुँचते-पहुँचते वह एक पूर्ण स्ट्रिंग बन चुका होता है, इसलिए उसका अनुवाद
टुकड़े का अनुवाद है। t-strings ([PEP 750]) स्थिर टेक्स्ट और values को अलग
रखते हुए f-string-जैसा सिंटैक्स और स्पष्ट value binding बनाए रखते हैं।
`$`-strings पहले से एक संक्षिप्त विकल्प देते हैं, पर binding और विफलता का
मॉडल अलग है। `flufl.i18n` एक परिपक्व पैकेज है जो Python 3.10 और बाद में
चलता है; `gettext-tstrings` फ़िलहाल alpha है, और चूँकि t-strings नया
सिंटैक्स हैं, इसे Python 3.14 या नया चाहिए।

दूसरी क़ीमत स्वयं यह प्रतिबंध है: इंटरपोलेशन को सादा नाम होना ही होगा।

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

यह एक वास्तविक बाधा है। स्रोत-पक्ष value binding और रनटाइम placeholder जाँच
के साथ मिलकर यह कैटलॉग स्ट्रिंग्स को एक्सप्रेशन का मूल्यांकन करने से रोकती
है और placeholder नामों को अर्थपूर्ण रखती है।

Python इस चौराहे तक कैसे पहुँचा — दस साल के अंतराल पर दो PEP, और stdlib की
वह चर्चा जो बिना उत्तर के बंद हुई — यह स्रोतों सहित
[पृष्ठभूमि](background.md) पर बताया गया है।

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
