---
description: "API ya wakati wa utekelezaji: kufunga katalogi, lugha kwa kila ombi, mifuatano iliyoahirishwa, na jinsi tafsiri mbovu inavyoripotiwa."
---

# Mwongozo

Ukurasa huu ni marejeo ya wakati wa utekelezaji: kila kitu ambacho *msimbo wa
programu yako* hufanya na maktaba hii mara katalogi zinapokuwepo. Ikiwa
hujaona bado mzunguko mzima — weka alama, toa, tafsiri, kusanya, endesha —
[mafunzo](tutorial.md) huupitia mara moja kwa dakika tano; kutengeneza na
kuthibitisha katalogi kumeelezwa katika [Utoaji](extraction.md), na jinsi timu
inavyouzungusha mzunguko — mizunguko ya masasisho, CI, majukwaa ya tafsiri —
imeelezwa katika [Katika uzalishaji](workflow.md).

## Kufunga katalogi { #binding-a-catalog }

Umbo linalopendekezwa huakisi matumizi ya gettext yanayotegemea klasi: funga
kitu sanifu cha tafsiri mara moja na utumie kichakataji kinachoitwa kama `_`.

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

Vitendakazi vya ngazi ya moduli hufuata majina ya maktaba sanifu na mkataba
wake wa kuita kwa nafasi pekee:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` na `ntr` ni visawe kamili vya `gettext` na `ngettext`.

## Lugha kwa kila ombi { #per-request-language }

Mfumo wa wavuti huchagua lugha kwa kila ombi. Funga tafsiri za ombi kwenye
muktadha wa sasa nao kila wito wa ngazi ya moduli hutatuliwa kwenye lugha hiyo,
kwa usalama katika maombi yanayoendeshwa sambamba:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` hufunga bila kizuizi cha `with`, kwa mifumo
inayosimamia mzunguko wa maisha ya ombi yenyewe; `get_translations()` husoma
ufungaji wa sasa. Hoja iliyo wazi ya `translations=` daima hushinda muktadha,
na muktadha usiofungwa hurejea kwenye vitendakazi vya gettext vilivyosakinishwa
kimataifa na maktaba sanifu. Mifano iliyofanyiwa kazi ya Flask na kiungo cha
kati cha ASGI iko kwenye ukurasa wa
[Katika uzalishaji](workflow.md#binding-a-language-at-runtime).

## Tafsiri iliyoahirishwa { #deferred-translation }

t-string hunasa thamani zake papo hapo, jambo ambalo si sahihi kwa mfuatano
unaobainishwa wakati wa kuingiza moduli — lebo ya fomu, thamani ya enum,
kigezo tuli cha moduli — ambao unapaswa kuonyeshwa kwa lugha yoyote iliyo hai
wakati *unapotumika*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` huonyeshwa kupitia `str()`, `format()`, na f-strings, nayo
hulingana sawa na maandishi yake yaliyoonyeshwa.

!!! note "Haihifadhiki kwa makusudi"

    Maandishi ya `LazyString` hutegemea lugha iliyo hai, hivyo hashi yake
    ingebadilika lugha inapobadilishwa na kuharibu kimyakimya seti au kamusi
    yoyote inayoishikilia. Ita `str()` kwanza ikiwa unahitaji ufunguo.

`strict` huamuliwa mahali ujumbe unapoandikwa, si mahali unapoonyeshwa:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Mfuatano ulioahirishwa huonyeshwa popote unapotumika hatimaye — ndani ya
kiolezo, fomu, au mstari wa kumbukumbu — na mahali hapo mara chache hujua kama
huu ni mzunguko wa majaribio au ni uzalishaji. Kupitisha `strict=True` pale
mfuatano unapobainishwa ndiko kunakoruhusu chaguo lilelile la
[kelele katika CI, upole katika uzalishaji](#what-happens-when-a-catalog-is-wrong)
litumike kwa mfuatano ambao hauonyeshwi mahali unapoitwa.

Maumbo ya wingi hutegemea idadi ya wakati wa utekelezaji, hivyo yaonyeshe hayo
papo hapo kwa `ngettext` mahali idadi inapojulikana.

## Lugha kadhaa kwa wakati mmoja { #several-languages-at-once }

Ombi moja mara nyingi huhitaji lugha zaidi ya moja: ukurasa unaoonyeshwa kwa
msomaji ambao pia hupanga foleni arifa kwenda akaunti iliyowekwa lugha nyingine,
au muhtasari unaomnukuu kila mshiriki kwa lugha yake mwenyewe. Ufungaji huwekwa
ndani kwa ndani, na kutoka kwenye kizuizi cha ndani hurejesha kile cha nje.

```python
with use_translations(reader):
    page = tr(t"Hello {name}")
    with use_translations(recipient):
        notice = tr(t"Hello {name}")  # the recipient's language
    footer = tr(t"Hello {name}")  # the reader's again
```

Kwenye orodha ya wapokeaji, mifuatano iliyoahirishwa ndiyo hufanya kazi: ujumbe
huandikwa mara moja tu, wakati wa kuingiza moduli, nao huonyeshwa mara moja kwa
kila lugha.

```python
SUBJECT = lazy_gettext(t"Your order shipped")

for user in users:
    with use_translations(load_translations(user.locale)):
        send(user.email, str(SUBJECT))
```

Ufungaji ni `ContextVar`, si rundo lililoshikiliwa kwenye kitu
kinachoshirikiwa, hivyo maombi yanayopishana hayawezi kuchukua lugha ya
mwenzake — ikiwa ni pamoja na hali ambapo *yanatoka* kwenye vizuizi vyake kwa
mpangilio uleule yalioingia, ambao ndio mpishano ambao rundo la kusukuma
huukosea. Kupakia katalogi kwa kila lugha ni jambo rahisi:
`gettext.translation()` huchanganua kila `.mo` mara moja na hutoa nakala
zinazoshiriki katalogi iliyochanganuliwa.

!!! warning "Iwapo uzi wa kufanyia kazi hurithi ufungaji hutegemea jenzi"

    `threading.Thread` ya kawaida, au `ThreadPoolExecutor.submit`, huanza ama
    kwa nakala ya muktadha wa mwitaji ama kwa muktadha mtupu, na kipi kati ya
    hivyo huamuliwa na `sys.flags.thread_inherit_context` — ni kweli kwa
    chaguo-msingi kwenye jenzi za nyuzi huru, na si kweli kwingineko kote.
    Hivyo msimbo uleule huonyesha lugha iliyofungwa kwenye 3.14t na katalogi
    ya jumla ya mchakato kwenye 3.14. Pitisha muktadha badala ya kutegemea
    chaguo-msingi:

    ```python
    pool.submit(contextvars.copy_context().run, render)
    ```

    `asyncio.to_thread` tayari hufanya hivi kwa niaba yako.

## Kinachotokea katalogi inapokuwa na kasoro { #what-happens-when-a-catalog-is-wrong }

Ikiwa vishika nafasi vya tafsiri havilingani na vya chanzo — uga uliokosekana,
usiojulikana, au ulioumbizwa upya uliopita uthibitishaji, kutoka MO
iliyohaririwa kwa mkono, katalogi ya muuzaji, au mkondo unaoruka kikaguzi —
chaguo-msingi ni kuzalisha tena maandishi chanzo badala ya kuinua hitilafu.
Hili huakisi mkataba wa gettext wenyewe kwamba katalogi mbaya kamwe haivunji
programu.

Kwa `Hello {name}` iliyotafsiriwa kama `こんにちは {nombre}`, uonyeshaji hufanikiwa
na onyo moja huenda kwenye kiandikaji kumbukumbu cha `gettext_tstrings`:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Onyo hupigwa mara moja kwa kila ujumbe na muundo, si mara moja kwa kila
uonyeshaji, hivyo ingizo bovu la katalogi halifuriki kumbukumbu.

Chagua kushindwa kwa kelele kwa ajili ya majaribio na CI:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

Utafutaji uleule kisha huinua hitilafu, ukibeba sentensi ileile bila nusu ya
"using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Kusoma ujumbe wa kushindwa { #reading-a-failure-message }

Jumbe hizi zimeandikwa kwa yeyote anayeweza kuchukua hatua juu yake, ambaye kwa
tatizo la katalogi mara nyingi ni mfasiri kuliko mtayarishaji programu.
Kuripoti tu kwamba `{name}` imekosekana ni njia isiyo na mwisho wakati msomaji
anaweza kuona herufi hizo mbele yake, hivyo pale kishika nafasi kinapoonekana
kipo lakini hakipo, ujumbe husema kwa nini. Dhidi ya chanzo `Hello {name}`,
kila mojawapo ya haya huripotiwa chini ya
`translation does not match the source placeholders:`

| Tafsiri inasema | Sababu inayotolewa |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` imekosekana (mabano yanayokizunguka si `{` na `}` za ASCII) |
| `こんにちは {{name}}` | `{name}` imekosekana (imeandikwa `{{name}}`, ambayo ndiyo namna bano halisi hukwepwa) |
| `こんにちは name` | `{name}` imekosekana (jina linaonekana, lakini si ndani ya mabano) |
| `こんにちは {名前}` | `{name}` imekosekana; `{名前}` haipo ndani ya ujumbe chanzo |

Herufi zisizoweza kuonekana hupata utaratibu wake. Nafasi isiyokatika ndani ya
mabano ni kitu ambacho mbinu ya kuingiza maandishi huzalisha na hakuna kihariri
kinachokionyesha, hivyo ujumbe hukichapisha kwa nukta ya msimbo badala ya
kutaja herufi ambayo msomaji hawezi kuipata:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Jina ambalo herufi zake huchanganya mifumo ya uandishi — kesi ya homoglifu,
ambapo `а` ya Kisirili haitofautiani na ile ya Kilatini — huonyeshwa mara
mbili, mara moja kwa namna inayosomeka na mara moja kwa namna iliyokwepwa,
ambayo ndiyo namna pekee inayozitofautisha:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

Utofautishaji uleule hutumika pale jina la Kigiriki au la Kisirili
lililoandikwa kabisa kwa mfumo mmoja linapogongana na jina chanzo la ASCII,
ikiwemo kesi ya herufi moja ya `a` ya Kilatini dhidi ya `а` ya Kisirili.

## Kuonyesha muundo bila katalogi { #rendering-a-pattern-without-a-catalog }

`compile_template` hufunua mfumo uleule ngazi moja chini: hugeuza t-string kuwa
msgid yake pamoja na seti ya thamani zilizofungwa, na huonyesha muundo wowote
unaompa.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` huthibitisha kwa kanuni zilezile na **daima huinua hitilafu**
zinapotofautiana. Hakuna hali ya kuvumilia hapa: uvumilivu upo ili utafutaji wa
*katalogi* uweze kushuka hadi maandishi chanzo, na muundo uliouipa wewe
mwenyewe hauna cha kushukia.

## Usalama na wigo { #safety-and-scope }

Hii ni halali:

```python
tr(t"Hello {name}")
```

Hizi zinakataliwa kwa makusudi:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Kokotoa thamani yenye maana kwanza:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Kizuizi hiki huzalisha funguo thabiti za katalogi, huwapa wafasiri majina yenye
manufaa, na huzuia mfuatano uliotafsiriwa kuwa lugha ya misemo.

Dhamana imefungwa kwenye *muundo na uumbizaji*: tafsiri haitathminiwi kamwe,
nayo haiwezi kamwe kuongeza ufikiaji wa sifa, miito, ubadilishaji, au maainisho
ya umbizo. Mambo mawili hubaki jukumu la anayeita, sawasawa na ilivyo kwa
gettext ya maktaba sanifu — **kukwepesha** matokeo yaliyoonyeshwa kwa ajili ya
mahali yanapoenda (HTML, ganda, kituo), na **uadilifu wa katalogi**, kwa kuwa
katalogi hasidi inaweza kurudia kishika nafasi ili kukuza ukubwa wa matokeo,
jambo ambalo ni asili ya i18n yoyote inayotegemea vishika nafasi.
