---
description: "रनटाइम API: कैटलॉग को बाँधना, प्रति-request भाषाएँ, deferred strings, और टूटे हुए अनुवाद की रिपोर्ट कैसे होती है।"
---

# गाइड

यह पेज रनटाइम संदर्भ है: कैटलॉग बन जाने के बाद आपका *एप्लिकेशन कोड* इस
लाइब्रेरी के साथ जो कुछ करता है। यदि आपने अभी पूरा लूप — मार्क, एक्सट्रैक्ट,
अनुवाद, कंपाइल, रन — नहीं देखा है, तो [ट्यूटोरियल](tutorial.md) उसे पाँच
मिनट में एक बार तय कराता है; कैटलॉग बनाना और सत्यापित करना
[एक्सट्रैक्शन](extraction.md) में है, और टीम उस लूप को कैसे चलाती रहती है —
अपडेट चक्र, CI, अनुवाद प्लेटफ़ॉर्म — यह [प्रोडक्शन में](workflow.md) है।

## कैटलॉग को बाँधना { #binding-a-catalog }

अनुशंसित रूप gettext के class-आधारित उपयोग को प्रतिबिंबित करता है: एक मानक
translation ऑब्जेक्ट एक बार बाँधें और callable प्रोसेसर को `_` की तरह उपयोग
करें।

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

module-स्तरीय फ़ंक्शन मानक लाइब्रेरी के नामों और उसकी positional-only कॉलिंग
परिपाटी का पालन करते हैं:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` और `ntr`, `gettext` और `ngettext` के सटीक उपनाम (aliases) हैं।

## प्रति-request भाषा { #per-request-language }

वेब फ़्रेमवर्क प्रति request एक भाषा चुनता है। request के translations को
वर्तमान context से बाँध दें, और हर module-स्तरीय कॉल उसी भाषा में हल होती
है, समवर्ती requests के बीच सुरक्षित रूप से:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` बिना `with` ब्लॉक के बाँधता है, उन
फ़्रेमवर्क के लिए जो request का जीवनचक्र स्वयं सँभालते हैं;
`get_translations()` वर्तमान binding पढ़ता है। स्पष्ट `translations=`
argument हमेशा context पर भारी पड़ता है, और अनबाउंड context मानक लाइब्रेरी
के वैश्विक रूप से इंस्टॉल किए गए gettext फ़ंक्शनों पर फ़ॉलबैक करता है।
Flask और ASGI middleware के सधे हुए उदाहरण
[प्रोडक्शन में](workflow.md#binding-a-language-at-runtime) पेज पर हैं।

## विलंबित (deferred) अनुवाद { #deferred-translation }

t-string अपनी values तुरंत कैप्चर करता है, जो import के समय परिभाषित
स्ट्रिंग के लिए ग़लत है — कोई फ़ॉर्म लेबल, कोई enum value, कोई module
स्थिरांक — जिसे उस भाषा में रेंडर होना है जो उसके *उपयोग* के समय सक्रिय हो।

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` `str()`, `format()` और f-strings के ज़रिए रेंडर होता है, और
अपने रेंडर किए हुए टेक्स्ट के बराबर तुलना करता है।

!!! note "जान-बूझकर unhashable"

    `LazyString` का टेक्स्ट सक्रिय भाषा पर निर्भर करता है, इसलिए hash भाषा
    बदलने पर बदल जाता और उसे रखने वाले किसी भी set या dict को चुपचाप भ्रष्ट
    कर देता। key चाहिए तो पहले `str()` कॉल करें।

`strict` वहाँ तय होता है जहाँ संदेश *लिखा* जाता है, वहाँ नहीं जहाँ वह रेंडर
होता है:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

विलंबित स्ट्रिंग वहीं रेंडर होती है जहाँ वह अंतत: उपयोग होती है — किसी
टेम्पलेट के भीतर, किसी फ़ॉर्म में, किसी लॉग लाइन में — और वह जगह शायद ही
जानती है कि यह टेस्ट रन है या प्रोडक्शन। परिभाषा पर `strict=True` देना ही
वह चीज़ है जो [CI में मुखर, प्रोडक्शन में उदार](#what-happens-when-a-catalog-is-wrong)
वाले उसी चुनाव को ऐसी स्ट्रिंग पर भी लागू होने देती है जो अपने call site पर
रेंडर नहीं होती।

बहुवचन रूप रनटाइम की गिनती पर निर्भर करते हैं, इसलिए उन्हें वहीं `ngettext`
से तुरंत रेंडर करें जहाँ गिनती ज्ञात हो।

## एक साथ कई भाषाएँ { #several-languages-at-once }

एक ही request को अक्सर एक से अधिक भाषाएँ चाहिए होती हैं: पाठक के लिए रेंडर
किया गया पेज, जो साथ ही किसी ऐसे खाते के लिए सूचना क़तार में डालता है जो किसी
दूसरी भाषा पर सेट है; या कोई डाइजेस्ट जो हर प्रतिभागी को उसी की भाषा में
उद्धृत करता है। bindings नेस्ट होती हैं, और भीतरी ब्लॉक छोड़ते ही बाहरी वाली
बहाल हो जाती है।

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

प्राप्तकर्ताओं की सूची पर विलंबित स्ट्रिंग्स ही काम कर देती हैं: संदेश एक ही
बार, import पर लिखा जाता है, और हर भाषा के लिए एक बार रेंडर होता है।

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

binding एक `ContextVar` है, किसी साझा ऑब्जेक्ट पर रखा स्टैक नहीं, इसलिए
अतिव्यापी requests एक-दूसरे की भाषा नहीं उठा सकते — उस स्थिति में भी नहीं जब
वे अपने ब्लॉक उसी क्रम में *छोड़ते* हैं जिस क्रम में उनमें घुसे थे, और यही वह
अंतर्ग्रथन है जिसे pushdown स्टैक ग़लत कर देता है। प्रति भाषा कैटलॉग लोड करना
सस्ता है: `gettext.translation()` हर `.mo` को एक बार पार्स करता है और ऐसी
प्रतियाँ देता है जो वही पार्स किया हुआ कैटलॉग साझा करती हैं।

!!! warning "कोई worker thread binding विरासत में लेता है या नहीं, यह build पर निर्भर करता है"

    कोई नंगा `threading.Thread`, या `ThreadPoolExecutor.submit`, या तो कॉल
    करने वाले के context की एक प्रतिलिपि से शुरू होता है या किसी ख़ाली
    context से, और इनमें से कौन-सा — यह `sys.flags.thread_inherit_context`
    है, जो free-threaded builds पर डिफ़ॉल्ट रूप से सत्य और बाक़ी हर जगह
    असत्य रहता है। इसलिए वही कोड 3.14t पर बँधी हुई भाषा रेंडर करता है और
    3.14 पर process-वैश्विक कैटलॉग। डिफ़ॉल्ट पर निर्भर रहने के बजाय context
    पास करें:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` यह आपके लिए पहले से कर देता है।

## कैटलॉग ग़लत होने पर क्या होता है { #what-happens-when-a-catalog-is-wrong }

यदि अनुवाद के placeholders स्रोत से मेल नहीं खाते — कोई ग़ायब, अज्ञात, या
पुन:-फ़ॉर्मैट किया हुआ फ़ील्ड जो सत्यापन से बच निकला, हाथ से संपादित MO से,
किसी vendor कैटलॉग से, या checker छोड़ देने वाली किसी pipeline से — तो
डिफ़ॉल्ट व्यवहार exception उठाने की बजाय स्रोत टेक्स्ट को पुन: प्रस्तुत करना
है। यह gettext के अपने अनुबंध का प्रतिबिंब है कि ख़राब कैटलॉग एप्लिकेशन को
कभी नहीं तोड़ता।

`Hello {name}` का अनुवाद `こんにちは {nombre}` होने पर रेंडर सफल होता है और
एक चेतावनी `gettext_tstrings` logger में जाती है:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

चेतावनी प्रति संदेश और pattern एक बार जारी होती है, प्रति रेंडर नहीं, इसलिए
टूटी हुई कैटलॉग एंट्री लॉग को बाढ़ में नहीं डुबोती।

परीक्षणों और CI के लिए ज़ोर से विफल होना चुनें:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

वही लुकअप तब exception उठाता है, वही वाक्य लिए हुए पर "using source text"
वाले आधे हिस्से के बिना:

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## विफलता का संदेश पढ़ना { #reading-a-failure-message }

ये संदेश उसके लिए लिखे गए हैं जो उन पर कार्रवाई कर सके — और कैटलॉग की समस्या
के लिए वह प्रोग्रामर से अधिक बार अनुवादक होता है। केवल यह बताना कि `{name}`
ग़ायब है, तब बंद गली है जब पढ़ने वाला वे अक्षर अपनी आँखों के सामने देख सकता
है; इसलिए जहाँ placeholder मौजूद दिखता है पर है नहीं, वहाँ संदेश कारण बताता
है। स्रोत `Hello {name}` के विरुद्ध, इनमें से हर एक
`translation does not match the source placeholders:` के अंतर्गत रिपोर्ट
होता है

| अनुवाद कहता है | दिया गया कारण |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

जो अक्षर दिखते ही नहीं, उन्हें अलग बर्ताव मिलता है। braces के भीतर no-break
space कुछ ऐसा है जो input method पैदा करता है और कोई एडिटर नहीं दिखाता,
इसलिए संदेश ऐसे अक्षर का नाम लेने की बजाय — जिसे पाठक ढूँढ ही नहीं सकता —
उसे code point से छाप देता है:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

वह नाम जिसके अक्षर लिपियाँ मिलाते हैं — homoglyph का मामला, जहाँ सिरिलिक
`а` लातिन से अभेद्य है — दो बार दिखाया जाता है, एक बार पठनीय रूप में और एक
बार escaped, जो दोनों को अलग बताने वाला इकलौता रूप है:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

यही असंदिग्धीकरण तब भी लागू होता है जब पूरी तरह एक ही लिपि में लिखा कोई
ग्रीक या सिरिलिक नाम किसी ASCII स्रोत नाम से टकराता है, जिसमें एक-अक्षर
वाला लातिन `a` / सिरिलिक `а` मामला भी शामिल है।

## बिना कैटलॉग के pattern रेंडर करना { #rendering-a-pattern-without-a-catalog }

`compile_template` वही तंत्र एक स्तर नीचे उजागर करता है: यह t-string को
उसके msgid और बँधी हुई values के सेट में बदलता है, और जो भी pattern आप उसे
दें, उसे रेंडर करता है।

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` उन्हीं नियमों से सत्यापित करता है और बेमेल पर **हमेशा exception
उठाता है**। यहाँ कोई उदार मोड नहीं है: उदारता इसलिए है कि *कैटलॉग* लुकअप
स्रोत टेक्स्ट तक degrade हो सके, और जो pattern आपने स्वयं दिया है उसके पास
degrade होने के लिए कुछ नहीं है।

## सुरक्षा और दायरा { #safety-and-scope }

यह वैध है:

```python
tr(t"Hello {name}")
```

ये जान-बूझकर अस्वीकृत हैं:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

पहले एक अर्थपूर्ण value निकालें:

```python
name = user.display_name()
tr(t"Hello {name}")
```

यह प्रतिबंध स्थिर कैटलॉग key देता है, अनुवादकों को उपयोगी नाम देता है, और
अनूदित स्ट्रिंग को एक्सप्रेशन भाषा बनने से रोकता है।

गारंटी *संरचना और फ़ॉर्मैटिंग* तक सीमित है: अनुवाद का कभी मूल्यांकन नहीं
होता, और वह कभी attribute पहुँच, कॉल, कन्वर्ज़न या फ़ॉर्मैट स्पेक नहीं जोड़
सकता। दो चीज़ें कॉलर की ज़िम्मेदारी रहती हैं, ठीक stdlib gettext की तरह —
रेंडर किए गए आउटपुट का उसके गंतव्य (HTML, shell, terminal) के लिए
**escaping**, और **कैटलॉग की अखंडता**, क्योंकि एक शत्रुतापूर्ण कैटलॉग
placeholder दोहराकर आउटपुट का आकार बढ़ा सकता है, जो किसी भी placeholder-आधारित
i18n में अंतर्निहित है।
