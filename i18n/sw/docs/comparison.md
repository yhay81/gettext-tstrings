---
description: "Ujumbe uleule unaotafsirika ulioandikwa kwa %-format, .format(), $-strings za flufl.i18n, na t-string, pamoja na jinsi kila mmoja unavyofunga thamani na kushughulikia katalogi mbovu."
---

# Kwa nini t-strings

Njia nne za kuweka thamani ndani ya ujumbe unaotafsirika, zikilinganishwa
kwenye sentensi ileile. Kwa ufupi:

- Kwa **%-format**, mfasiri anayefuta herufi moja husababisha kuanguka kwa
  programu katika uzalishaji.
- Kwa **str.format**, tafsiri inaweza kusoma sifa za vitu ambavyo msimbo wako
  hupitisha — pamoja na siri.
- Kwa **$-strings** (flufl.i18n), thamani huvutwa kimyakimya kutoka vigezo vya
  kitendakazi kinachoita, na vishika nafasi vyenye vitone hufikia sifa pia.
- Kwa **t-strings**, uumbizaji hubaki ndani ya msimbo wako, tafsiri hukaguliwa
  wakati wa utekelezaji, na katalogi mbovu hurejea kwenye maandishi chanzo
  badala ya kuanguka.

Sehemu iliyobaki ya ukurasa huu ni ushahidi, njia moja baada ya nyingine.

!!! note "Pande tatu hugusa kila ujumbe uliotafsiriwa"

    **Katalogi** ni faili la tafsiri — `.po` wakati binadamu wanalihariri,
    likikusanywa kuwa `.mo` ili programu ilipakie ([mafunzo](tutorial.md)
    hupitia zote mbili). Pande tatu hugusa kila ujumbe: **msanidi** huandika
    mfuatano chanzo, **mfasiri** huhariri katalogi — mara nyingi kwenye jukwaa
    la nje, mbali na mapitio yoyote ya msimbo — na **programu** huvionyesha
    vyote viwili pamoja wakati wa utekelezaji. Kila mtindo wa uumbizaji hapa
    chini hujibu swali lilelile kwa njia tofauti: *ni kiasi gani cha lugha ya
    umbizo ambacho katalogi hupewa kudhibiti?* Katika mifano, `_` ni jina la
    kawaida la kitendakazi cha kutafsiri, na `tr` ni la maktaba hii.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Kinachoweza kwenda vibaya: herufi moja iliyofutwa katika tafsiri huvunja
uonyeshaji.

Mfuatano wa katalogi hubeba sintaksia ya printf, ikiwa ni pamoja na herufi ya
aina mwishoni — ile `s` ndani ya `%(name)s` — ambayo ni rahisi kuipuuza na
rahisi kuiharibu:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Uhariri wa herufi moja katika kihariri cha PO huwa traceback katika uzalishaji.
GNU `msgfmt --check-format` huikamata kweli, lakini kwa jumbe zilizowekwa
alama ya `python-format` tu, na tu ikiwa katalogi hupita kwelikweli kwenye
msgfmt njiani kuelekea programu yako.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Huondoa herufi ya aina ya mwishoni huku ikihifadhi kishika nafasi chenye jina
kinachoweza kupangwa upya kwa uhuru. Kinachoweza kwenda vibaya huhamia upande
mwingine wa muamala: tafsiri hupata nguvu juu ya vitu vyako.

`str.format` ni lugha ndogo ya misemo, na kuiita juu ya mfuatano kunamaanisha
kuukabidhi mfuatano huo haki ya kuitumia:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Sasa badilisha mifuatano hiyo halisi na chochote `_()` inachorudisha. Ikiwa
tafsiri ya `Hello {name}` inarudi kama `{conf.api_key}`, kuionyesha huchapisha
ufunguo wako wa API — katalogi, si msimbo wako, ndiyo iliyoamua kilichosomwa.
Katalogi si msimbo, lakini husafiri kama data: nje hadi jukwaa la tafsiri,
kupitia mikono kadhaa, kurudi kama `.po`, ikikusanywa kuwa `.mo`, mara nyingine
ikiletwa kutoka nje ya mradi wako kabisa. `.format()` huipa kila hatua ya safari
hiyo ufikiaji wa sifa za vitu unavyopitisha.

## `$`-strings na flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

[`string.Template`][stdlib-template] ya maktaba sanifu hutoa lugha ya uingizaji
ya `$name`, lakini yenyewe si API ya kutafsiri. [`flufl.i18n`][flufl-i18n]
huunganisha mtindo huo na utafutaji wa katalogi ya gettext. Zingatia kwamba
thamani haipitishwi kamwe: flufl.i18n hujenga nafasi ya majina ya ubadilishaji
kutoka vigezo vya jumla na vya ndani vya kinachoita — vigezo vyovyote
vilivyopo mahali pa wito vinapatikana kwa ujumbe. Ramani ya hiari ya `extras`
hutangulia vyote viwili. Sintaksia yake inayomkabili mfasiri haina herufi ya
aina ya mwishoni wala kiainishi cha umbizo, na vishika nafasi hubaki
vinapangika upya kwa uhuru.

Ubadilishaji usiopatikana hauinui hitilafu. Kwa `name = "Ada"` na bila
`nombre` katika nafasi ya majina ya kinachoita, tafsiri ya katalogi ya
`Hello $nombre` huonyeshwa kama `Hello $nombre`: kishika nafasi kisichotatuliwa
hubaki kikionekana. [Tabia hiyo iliyoandikwa][documented behavior] huhifadhi
sehemu iliyobaki ya ujumbe uliotafsiriwa badala ya kuufanya wito ushindwe.
Hitilafu zinazoinuliwa wakati wa kutatua sifa au kubadilisha thamani bado
zinaweza kuenea.

`flufl.i18n` ina uwezo zaidi kuliko `string.Template` tupu kwa njia moja
inayohusika. [Template yake maalum][custom Template] hukubali vishika nafasi
vyenye vitone kama `$settings.api_key`, na [mfasiri wake][translator] hutatua
njia hizo dhidi ya thamani za kinachoita. Kishika nafasi kilichotafsiriwa
kinaweza kutaja kigezo chochote cha ndani au cha jumla kinachopatikana kwa
kinachoita na, kwa sintaksia ya vitone, kupitia sifa zake. Hilo ni jambo la
urahisi wakati ujumbe unahitaji sifa, huku pia likifanya fremu ya kinachoita
kuwa sehemu ya nafasi ya majina ya ubadilishaji ya katalogi. Ulinganisho hapa
chini unaelezea `flufl.i18n` 6.0.0, si kila matumizi yanayowezekana ya
`string.Template`.

## t-strings { #t-strings }

```python
tr(t"Hello {name}")
```

Katalogi bado huona `Hello {name}` na hubaki katalogi ya kawaida ya PO/MO.
Tofauti ni kile ambacho tafsiri *inaruhusiwa kusema*, na nani anayekikagua.

Maktaba hii huthibitisha kila tafsiri dhidi ya vishika nafasi vya ujumbe chanzo
kabla ya kuonyesha, nayo hukubali majina matupu na hakuna kingine. Dhidi ya
`t"Hello {name}"`:

| Tafsiri iliyo na | hukataliwa kwa |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Kukataliwa hakumaanishi kuanguka: kwa chaguo-msingi maktaba huandika onyo na
kuonyesha maandishi chanzo, hivyo katalogi mbaya kamwe haiiangushi programu —
[mkataba uleule ambao gettext yenyewe huutunza](guide.md#what-happens-when-a-catalog-is-wrong).

Uumbizaji hubaki pale ulipoandikwa, ndani ya msimbo:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` haifiki kamwe kwenye katalogi, hivyo hakuna tafsiri inayoweza kuibadili,
na hakuna mfasiri anayelazimika kuiangalia.

Tofauti nyingine ni zana: t-strings ni sintaksia mpya, hivyo kuzitoa ndani ya
`.pot` kwa sasa kunahitaji kitoaji kinachotambua t-string, kama kile ambacho
kifurushi hiki [hukitoa kwa Babel](extraction.md).

## Ubavu kwa ubavu { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Je, kishika nafasi kina jina? | ndiyo | ndiyo | ndiyo | ndiyo |
| Je, mfasiri anaweza kupanga upya vishika nafasi? | ndiyo | ndiyo | ndiyo | ndiyo |
| Thamani hutoka wapi? | ramani iliyo wazi | hoja zilizo wazi | vigezo vya ndani na vya jumla vya kinachoita, pamoja na `extras` ya hiari | thamani zilizonaswa ndani ya t-string |
| Je, katalogi inaweza kubadilisha jinsi thamani inavyoumbizwa? | ndiyo | ndiyo | hapana | hapana |
| Je, katalogi inaweza kufikia ndani ya vitu (ufikiaji wa sifa)? | hapana | ndiyo | ndiyo, kwa majina yenye vitone | hapana |
| Tafsiri *huondoa* kishika nafasi — nini huonyeshwa? | thamani hutoweka kimyakimya | thamani hutoweka kimyakimya | thamani hutoweka kimyakimya | maandishi chanzo, pamoja na onyo ([kwa chaguo-msingi](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Tafsiri *huongeza* kishika nafasi kisichojulikana — nini huonyeshwa? | hitilafu | hitilafu | kishika nafasi hubaki kikionekana kama maandishi | maandishi chanzo, pamoja na onyo ([kwa chaguo-msingi](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Je, vishika nafasi hukaguliwa wakati wa kuonyesha? | hapana | hapana | hapana | ndiyo (ona hapa chini) |
| Ni bendera gani ya PO ambayo Babel huidokeza, ili zana zilizopo zithibitishe? | `python-format` | `python-brace-format` | hakuna | `python-brace-format` |
| Je, hutumia katalogi za kawaida za PO/MO? | ndiyo | ndiyo | ndiyo | ndiyo |
| Je, huhitaji kitoaji maalum cha chanzo? | hapana | hapana | hapana | ndiyo, kwa sasa |

Kuhusu ukaguzi wa wakati wa kuonyesha: jumbe za umoja hukaguliwa kwa
ulinganifu kamili wa vishika nafasi. Jumbe za wingi hukaguliwa pia, dhidi ya
[kanuni ya muungano/mwingiliano](spec.md) inayoruhusu maumbo ya wingi ya lugha
lengwa kutofautiana na ya chanzo; ukaguzi mkali zaidi wa kila umbo huendeshwa
katalogi zinapokusanywa ([Utoaji](extraction.md)).

Safu ya bendera ya umbizo inahusu uthibitishaji unaotambua vishika nafasi, si
uoanifu wa katalogi. `hakuna` humaanisha zana sanifu za gettext bado husoma na
kukusanya ujumbe, lakini `msgfmt --check-format` haina sarufi ya kishika nafasi
cha `$` ya kuitumia.

## Gharama yake { #what-it-costs }

f-string haiwezi kutumika hivi hata kidogo — kufikia wakati maktaba yoyote
inaiona tayari ni mfuatano uliokamilika, hivyo kuitafsiri kunamaanisha
kutafsiri kipande. t-strings ([PEP 750]) hutenganisha maandishi tuli na
thamani huku zikihifadhi sintaksia inayofanana na ya f-string na ufungaji wa
thamani ulio wazi. `$`-strings tayari hutoa mbadala mfupi wenye mfumo tofauti
wa kufunga na wa kushindwa. `flufl.i18n` ni kifurushi kilichokomaa
kinachoendeshwa kwenye Python 3.10 na baadaye; `gettext-tstrings` kwa sasa ni
alpha, na kwa kuwa t-strings ni sintaksia mpya inahitaji Python 3.14 au mpya
zaidi.

Gharama nyingine ni kizuizi chenyewe: uingizaji lazima uwe jina tupu.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

Hilo ni kizuizi halisi. Pamoja na ufungaji wa thamani upande wa chanzo na
ukaguzi wa vishika nafasi wakati wa utekelezaji, huzuia mifuatano ya katalogi
kutathmini misemo na huyafanya majina ya vishika nafasi yaendelee kuwa na maana.

Jinsi Python ilivyofika kwenye njia panda hii — PEP mbili zenye tofauti ya
miaka kumi, na mjadala wa stdlib uliofungwa bila jibu — imesimuliwa pamoja na
vyanzo katika [Usuli](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
