---
description: "Kuchukua t-string katika mradi ambao tayari una katalogi za gettext: kinachobaki bila kuguswa, kinachokuwa fuzzy, na namna ya kuhama mahali pamoja pa kuita kwa wakati mmoja."
---

# Uhamiaji

Kama mradi wako tayari unatumia gettext, maswali yanayoamua kama maktaba hii
inachukulika ni machache tu: je, inabatilisha katalogi ulizonazo, je, inaweza
kuishi pamoja na msimbo ambao bado hujawa tayari kuubadilisha, na ni kiasi gani
cha uhamiaji lazima kifanyike kwa wakati mmoja. Majibu, mafupi kwanza:

| Swali | Jibu |
| --- | --- |
| Je, mafaili yaliyopo ya `.po` na `.mo` bado yanafanya kazi? | Ndiyo. Mafaili yaleyale, zana zilezile. |
| Je, miito ya zamani na mipya inaweza kukaa katika faili moja? | Ndiyo, na ramani moja ya kitoaji huifunika yote. |
| Je, msgid inabadilika? | Si kutoka `.format()`. Ndiyo kutoka umbizo la `%`. |
| Je, mradi mzima lazima uhame kwa wakati mmoja? | Hapana. Mahali pamoja pa kuita ni badiliko halali. |
| Vipi kuhusu Jinja, violezo vya Django, JavaScript? | Havijaguswa, katalogi zilezile. |

Sehemu iliyobaki ya ukurasa huu ni maelezo yaliyo nyuma ya kila moja kati ya
hayo.

## Kutoka `.format()`: msgid haibadiliki { #from-format-the-msgid-does-not-change }

Hii ndiyo hali ambayo uhamiaji hugharimu karibu chochote. Ujumbe wa `str.format`
na ujumbe wa t-string hutokeza ufunguo *uleule* wa katalogi, kwa sababu ufunguo
ni maandishi yenye `{name}` ndani yake kwa njia yoyote ile:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Kwa hiyo tafsiri iliyopo hubaki imeambatishwa. Ukianza na katalogi yenye

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

badilisha mwito, toa upya, na usasishe:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Ingizo linalorudi hutofautiana katika mistari miwili ya metadata na si kingine —
maoni ya alama yanayolitambulisha kuwa ni ujumbe wa t-string, na nambari ya
mstari wa chanzo:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Hakuna bendera ya `fuzzy`, hakuna kutafsiri upya, katika lugha yoyote. Ujumbe
huonyeshwa papo hapo:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` itaripoti katalogi kuwa zimepitwa na wakati"

    Maoni hayo ya alama na nambari za mistari zilizohama zinatosha kwa
    `pybabel update --check` kusema katalogi inahitaji kuzalishwa upya, kwa
    sababu hulinganisha ingizo zima na si tafsiri peke yake. Endesha
    `pybabel update` halisi katika commit ileile ya badiliko la msimbo, na
    commit katalogi pamoja nayo — ni tabia ileile ambayo
    [kizuizi cha CI](workflow.md#what-ci-gates) tayari huiomba.

## Kutoka umbizo la `%`: msgid inabadilika, hivyo tafsiri huwa fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Sintaksia ya printf hukaa *ndani* ya ujumbe, hivyo kuiondoa huandika upya
ufunguo wa katalogi. Hakuna njia ya kuikwepa, nayo ni gharama ya kweli ya
kuachana na `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` huutambua ujumbe mpya kama ndugu wa karibu wa ule
ulioondolewa nayo huibeba tafsiri ya zamani hadi humo, ikiwa na alama ya fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

Mambo matatu ya kujua kuhusu hali hiyo:

- **Hakuna kinachovunjika wakati wa utekelezaji.** Maingizo ya fuzzy huachwa nje
  ya `.mo` iliyokusanywa, hivyo programu huonyesha ujumbe chanzo hadi binadamu
  athibitishe jozi hiyo — [kushuka kulekule](workflow.md#the-cycle-after-the-first-translation)
  ambako ujumbe wowote ulioandikwa upya hupitia.
- **CI hubaki kijani wakati yakiwa fuzzy.** Kikaguzi cha vishika nafasi huruka
  maingizo ya fuzzy, sawasawa na `msgfmt --check-format` inavyofanya, kwa sababu
  ingizo lisiloweza kufika wakati wa utekelezaji halipaswi kuangusha ujenzi.
  Mara tu mfasiri anapofuta bendera hiyo, ingizo hukaguliwa kama lingine lolote
  — hivyo `%(name)s` iliyoachwa katika tafsiri iliyothibitishwa hukamatwa hapo,
  ambapo ndipo vinginevyo ingeanza kuonyeshwa.
- **Bendera ya zamani ya `python-format` husafiri pamoja** nayo inapaswa kufutwa
  pamoja na bendera ya `fuzzy`, la sivyo `msgfmt --check-format` itaendelea
  kutumia kanuni za printf kwa ujumbe wa umbizo la mabano.

Kwa vishika nafasi vya printf vyenye majina badiliko ni la kimitambo —
`%(name)s` huwa `{name}` na hakuna kingine kinachohama — hivyo katalogi kubwa ni
kupitia kwa hati moja kunakofuatiwa na mapitio ya mfasiri, badala ya kutafsiri
upya. `%s` ya nafasi si ya kimitambo: haina jina la kubeba, na kuchagua moja
ndilo lengo la badiliko lenyewe.

Kwa hiyo uhamiaji unaweza kwenda kwa mwendo wowote ambao mapitio yanaruhusu:
ingizo la fuzzy ambalo halijabadilishwa ni kazi inayoonekana ndani ya katalogi,
si ujenzi uliovunjika.

## Miito ya zamani na mipya huishi pamoja { #old-and-new-calls-coexist }

Kitoaji kinachosoma t-string husoma pia miito ya kawaida ya gettext, hivyo
ramani moja huifunika faili iliyo katikati ya uhamiaji:

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

Jumbe zote mbili hutua katika kiolezo kimoja, na ile ya t-string peke yake ndiyo
hubeba maoni ya alama yanayowasha ukaguzi wa ziada wa maktaba hii:

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

Hutambua `_()`, majina manne sanifu ya gettext, majina mbadala ya `tr()` /
`ntr()`, na `lazy_gettext()` / `lazy_pgettext()` zilizoahirishwa. Msaidizi wako
mwenyewe lazima [atajwe katika ramani](extraction.md#registering-your-own-function-names).

Wakati wa utekelezaji mitindo hiyo miwili hujitegemea sawasawa:
`gettext.translation()` hurudisha kitu kimoja cha tafsiri, na `_` pamoja na
sehemu za kuingilia za maktaba hii husoma kutoka humo.

## Kisichohama { #what-does-not-move }

- **Lugha za violezo.** `{% trans %}` ya Jinja2, lebo za violezo za Django, na
  vitoaji vyao vya Babel huendelea kufanya kazi bila mabadiliko na huendelea
  kulisha katalogi zilezile za PO. t-string ni sintaksia ya Python; zinahusu
  msimbo chanzo wa Python.
- **Mafaili yako ya katalogi.** Hakuna badiliko la umbizo, hakuna faili jipya,
  hakuna hatua ya kubadilisha.
- **Jukwaa lako la tafsiri.** Ubadilishanaji wa `.po` ni uleule, na bendera ya
  `python-brace-format` ambayo ujumbe wa t-string hubeba ni bendera ileile
  ambayo ujumbe wa `.format()` hubeba — hivyo QA ya vishika nafasi huendelea
  kufanya kazi.
- **Msimbo usio wa Python.** Katalogi ya JavaScript au ya C katika mradi uleule
  haiguswi.

## Orodha hakiki ya uhamiaji { #a-migration-checklist }

1. Ongeza nyongeza ya `babel` mahali `pybabel` inapoendeshwa, na ubadilishe
   ramani ya `python` ndani ya `babel.cfg` kuwa mbinu ya `gettext_tstrings` —
   kisha ramani moja huifunika mitindo yote miwili, na `-k` huendelea kufanya
   kazi kwa miito ya kawaida.
2. Badilisha mahali pa kuita pa `.format()` kwanza. Toa upya, endesha
   `pybabel update`, na commit katalogi pamoja na msimbo; usitegemee maingizo ya
   fuzzy.
3. Badilisha mahali pa kuita pa umbizo la `%` katika makundi unayoweza
   kuyapitisha kwenye mapitio, ukiandika upya vishika nafasi vilivyobebwa na
   kufuta bendera za `fuzzy` na `python-format`.
4. Rekebisha kile ambacho kizuizi hukikataa: uingizaji lazima uwe jina tupu,
   hivyo `t"Hello {user.name}"` huwa kigezo cha ndani kwanza. Hili ni badiliko
   la mahali pa kuita, si la katalogi.
5. Washa `strict = true` ndani ya ramani ya kitoaji mara tu upitiaji
   utakapokamilika, ili ujumbe usioweza kutolewa uangushe
   [ujenzi](extraction.md#lenient-locally-strict-in-ci) badala ya kutoweka
   kimyakimya kutoka kiolezoni.
6. Ongeza ukaguzi wa wakati wa utekelezaji kutoka
   [Katika uzalishaji](workflow.md#what-ci-gates): onyesha ujumbe mmoja kwa kila
   lugha inayosafirishwa kupitia `Translator` mkali.

Hatua za 2 na 3 ni commit za kawaida. Hakuna kitu katika orodha hii
kinachohitaji siku ya kubadili yote kwa mpigo.
