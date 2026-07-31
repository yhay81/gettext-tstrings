---
description: "Tafsiri jumbe kamili za t-string kupitia gettext na Babel, huku thamani na uumbizaji vikibaki nje ya katalogi."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Tafsiri jumbe kamili<br>kwa t-strings za Python

`gettext-tstrings` huunganisha t-strings za Python 3.14+ na katalogi sanifu za
gettext na zana za Babel. Thamani na uumbizaji hubaki ndani ya msimbo wa
programu; watafsiri hushughulika na jumbe kamili na vishika nafasi rahisi vya
`{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Katalogi hushikilia `Hello {name}`. Tafsiri inaweza kuhamisha au kurudia
`{name}`. Ikiwa itakiondoa kishika nafasi, kukipa jina jingine, au kukiumbiza
upya, uthibitishaji wa katalogi huripoti hitilafu. Ikiwa ingizo batili
litafikia uzalishaji hata hivyo, maktaba huandika onyo na huonyesha ujumbe
chanzo badala ya kuanguka.

[Anza mafunzo ya dakika tano :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Linganisha mbadala](comparison.md){ .md-button }

Alpha · Python 3.14+ · katalogi sanifu za PO/MO · hakuna vitegemezi vya wakati wa utekelezaji kutoka kwa watu wa tatu
{ .home-facts }

Tovuti hii hutekeleza kile inachoandika: kila toleo la lugha — urambazaji,
lebo, na ripoti ya ujenzi inayotambua wingi — huonyeshwa kutoka katalogi za PO
na
[`gettext-tstrings` yenyewe](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Je, hii ni kwa ajili yako? { #is-this-for-you }

**Inafaa leo ikiwa** programu yako huendeshwa kwenye Python 3.14 au mpya zaidi;
tayari unatumia gettext na Babel, au unataka kuanza kutumia mtiririko wao wa
PO/MO; nawe unataka sintaksia ya t-string yenye vishika nafasi vyenye majina
vinavyokaguliwa kabla ya kuonyeshwa.

**Bado haifai ikiwa** unahitaji Python 3.13 au ya zamani zaidi; unahitaji API
thabiti ya Python — hii ni alpha, na [ainisho](spec.md) ndiyo sehemu yake
iliyotulia; au takribani maandishi yako yote yanayotafsirika hukaa ndani ya
lugha ya violezo badala ya msimbo chanzo wa Python.

Tayari una katalogi? Zitaendelea kufanya kazi.
`_("Hello {name}").format(name=name)` na `tr(t"Hello {name}")` huzalisha msgid
ileile, hivyo tafsiri zilizopo hunusurika mabadiliko —
[Uhamiaji](migration.md) hupitia hatua nzima.

## Kile katalogi inachoruhusiwa kusema { #what-the-catalog-may-say }

**Tafsiri haiwezi kubadilisha muundo wa ujumbe inaoutafsiri.** Hiyo ndiyo
ahadi nzima, na kila kitu kingine kwenye tovuti hii hufuata kutoka hapo.
Tafsiri inaweza kupanga upya au kurudia `{name}`, nayo inaweza kuandika upya
kila neno jingine linalokizunguka. Haiwezi kukiondoa kishika nafasi, kubuni
kipya, kufikia vitu vyako kupitia kishika nafasi, wala kuambatisha umbizo lake
yenyewe.

Maktaba hukagua hilo wakati wa kuingia — katalogi zinapokusanywa — na tena
wakati wa kuonyesha, na hapo ndipo tofauti ilipo kati ya kosa linalogunduliwa
kwenye mapitio na kosa linalogunduliwa na mtumiaji.

!!! note "Mgeni kwa gettext? Mtiririko mzima wa kazi kwa sentensi nne"

    **gettext** ndiyo njia ya kawaida ambayo programu hutafsiriwa, ndani ya
    Python na mbali zaidi. Msimbo wako huweka alama kwenye jumbe
    zinazotafsirika; *kitoaji* huzikusanya katika faili la kiolezo (`.pot`);
    mfasiri — mara nyingi si mtayarishaji programu — hujaza faili moja la
    katalogi (`.po`) kwa kila lugha, ambalo hukusanywa kuwa `.mo` ya mfumo-jozi
    ambayo programu yako hupakia wakati wa utekelezaji. Jina la kawaida la
    kitendakazi cha kutafsiri ni `_`, hivyo `_(t"Hello {name}")` husomeka kama
    "tafsiri ujumbe huu". **[Mafunzo](tutorial.md)** hupitia njia nzima —
    weka alama, toa, tafsiri, kusanya, endesha — kwa takribani dakika tano.

## Tatizo linalotatuliwa { #the-problem-it-solves }

f-string huwa tayari imeingizwa thamani kabla maktaba yoyote haijaiona —
`f"Hello {name}"` tayari imekuwa `"Hello Ada"`, na kutafsiri vipande
vinavyozunguka thamani huvunja sarufi ya lugha nyingi. t-string ([PEP 750])
hutunza maandishi tuli, thamani zilizokokotolewa, misemo chanzo, ubadilishaji,
na maainisho ya umbizo kila kimoja peke yake — nayo ndiyo hasa mgawanyo
ambao katalogi ya jumbe inauhitaji.
[Kinachobadilika](comparison.md), ikilinganishwa na `%(name)s`, `.format()`, na
`$`-strings.

Hata hivyo, hakuna chochote ndani ya gettext au Babel kinachosema jinsi
t-string inavyokuwa ujumbe. Maktaba hii hufanya uamuzi huo, huuandika kama
[ainisho lenye matoleo](spec.md), na husambaza
[seti ya utiifu](spec.md#conformance) ya kuukagua.

## Kanuni za muundo { #the-design-rules }

- Tafsiri jumbe kamili, kamwe si vipande vya sentensi.
- Kubali majina rahisi tu ya vigezo kama `{name}`.
- Weka `!r` na `:.2f` chini ya udhibiti wa programu, nje ya katalogi.
- Ruhusu tafsiri kupanga upya na kurudia vishika nafasi vinavyojulikana, huku
  ukizizuia kufikia sifa za vitu au kuongeza uumbizaji.
- Tumia tena mafaili ya kawaida ya POT, PO, na MO, pamoja na zana ambazo
  tayari huyasoma.

Na orodha inayolingana ya kile inachokiacha kwa makusudi: haitafsirii nambari,
sarafu, wala tarehe kwa eneo — [ziumbize kwanza](guide.md#locale-aware-values),
kwa Babel; haikwepeshi matokeo yaliyoonyeshwa kwa ajili ya HTML, ganda, au
kituo; nayo haiwezi kuhukumu kama tafsiri ni *sahihi*, bali tu kama vishika
nafasi vyake vipo kamili.

## Usakinishaji { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 au mpya zaidi. **Uonyeshaji hauna vitegemezi** — hutumia `gettext`
ya maktaba sanifu na hakuna kingine.

Utoaji na uthibitishaji wa katalogi hupitia [Babel], hivyo sakinisha nyongeza
hiyo popote `pybabel` inapoendeshwa, ambako mara nyingi ni mazingira ya
usanidi au CI badala ya taswira ya uzalishaji:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Wapi pa kwenda { #where-to-go-next }

**Anza hapa** — hakuna uzoefu wa gettext unaohitajika:

<div class="grid cards" markdown>

- **[Mafunzo](tutorial.md)** — kutoka saraka tupu hadi tafsiri ya Kijapani
  inayofanya kazi kwa hatua tano, kila amri ikionyeshwa na matokeo yake.
- **[Kwa nini t-strings](comparison.md)** — ujumbe uleule ulioandikwa kwa njia
  nne, na kile ambacho `%(name)s`, `.format()`, na `$`-strings kila kimoja
  hukikabidhi katalogi.

</div>

**Itumie** — marejeo ya kazi:

<div class="grid cards" markdown>

- **[Mwongozo](guide.md)** — API ya wakati wa utekelezaji: sehemu ipi ya
  kuingilia kutumia, wingi, lugha kwa kila ombi, mifuatano iliyoahirishwa, na
  kinachotokea katalogi inapokuwa na kasoro.
- **[Utoaji](extraction.md)** — marejeo ya `pybabel`: usanidi, majina maalum ya
  vitendakazi, na jinsi zana zilizopo zinavyothibitisha katalogi hizi bure.
- **[Katika uzalishaji](workflow.md)** — mzunguko kama timu inavyouendesha:
  mzunguko wa masasisho, maingizo ya fuzzy, vizuizi vya CI, majukwaa ya
  tafsiri, na usafirishaji.
- **[Uhamiaji](migration.md)** — kuanza kutumia hii katika mradi ambao tayari
  una katalogi, sehemu moja ya wito baada ya nyingine.
- **[Kwa watafsiri](translators.md)** — ukurasa mmoja wa kumkabidhi yeyote
  anayehariri mafaili ya `.po`.

</div>

**Ielewe** — kutoka historia hadi utekelezaji:

<div class="grid cards" markdown>

- **[Usuli](background.md)** — kwa nini maktaba hii ipo: miaka thelathini ya
  gettext, PEP mbili, na mjadala wa stdlib uliofungwa bila jibu.
- **[Mitego](pitfalls.md)** — kile ambacho kutafsiri tovuti hii katika lugha
  thelathini na tano kulivunja kwelikweli, na ni nusu ipi ambayo zana inaweza
  kuinasa.
- **[Jinsi inavyofanya kazi](internals.md)** — kutoka kwenye kitu cha kiolezo
  cha PEP 750 hadi mfuatano ulioonyeshwa, na akiba zinazofanya ukaguzi kuwa wa
  bei rahisi.

</div>

**Marejeleo** — mikataba:

<div class="grid cards" markdown>

- **[API](api.md)** — kila kitu ambacho kifurushi hukitoa nje, kwenye ukurasa
  mmoja.
- **[Ainisho](spec.md)** — makubaliano ya t-string ↔ msgid kama mkataba thabiti
  wenye matoleo, pamoja na seti ya utiifu inayosomeka na mashine.

</div>

## Hali { #status }

| | |
| --- | --- |
| Toleo la kifurushi | 0.1.0a7 |
| Uthabiti wa API | alpha — API ya Python bado inaweza kubadilika |
| [Ainisho](spec.md) | v1, pamoja na [seti ya utiifu](spec.md#conformance) |
| Python | 3.14 na mpya zaidi; imejaribiwa kwenye 3.14, 3.14t (nyuzi huru), na 3.15 |
| Babel | 2.18 au mpya zaidi, na pale tu ambapo `pybabel` huendeshwa |
| Vitegemezi vya wakati wa utekelezaji | hakuna — `gettext` ya maktaba sanifu |
| Muundo wa katalogi | POT, PO, na MO za kawaida |
| Mabadiliko | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Ni alpha. Mkataba ni mdogo kwa makusudi na [ainisho](spec.md) ndilo sehemu yake
thabiti; API ya Python bado inaweza kubadilika. Kabla ya toleo thabiti, hii
inahitaji vifaa vya majaribio vya lugha nyingi zaidi, ufuatiliaji endelevu wa
utendaji, mapitio ya API kutoka kwa watu wanaotumia gettext na Babel kwa dhati,
na majaribio ya uoanifu katika kila toleo linalotegemezwa la Python na Babel.

[Masuala na maombi ya kuunganisha](https://github.com/yhay81/gettext-tstrings/issues)
yanakaribishwa — alpha ndiyo wakati hasa ambapo kiolesura bado kinastahili
kujadiliwa.

## Jiunge na jumuiya { #join-the-community }

- Chagua
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  kwa mchango wenye mipaka.
- Uliza maswali ya matumizi katika
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Leta mitiririko halisi ya kazi ya gettext na mawazo kuhusu API katika
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Soma
  [mwongozo wa kuchangia](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  kabla ya kufungua ombi la kuunganisha.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
