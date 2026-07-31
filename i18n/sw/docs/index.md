---
description: "Tafsiri jumbe kamili za t-string kupitia gettext na Babel, huku uumbizaji ukibaki nje ya katalogi."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Andika sentensi mara moja.<br>Itafsiri nzima.

Muunganisho salama wa gettext na Babel kwa t-strings za Python 3.14+ — thamani
hubaki mahali pake, na katalogi huona ujumbe mzima:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Anza mafunzo :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Kwa nini t-strings](comparison.md){ .md-button }

Tovuti hii hutekeleza kile inachoandika: kila toleo la lugha — urambazaji,
lebo, na ripoti ya ujenzi inayotambua wingi — huonyeshwa kutoka katalogi za PO
na
[`gettext-tstrings` yenyewe](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalogi hupokea sentensi kamili `Hello {name}`. Tafsiri inaweza kupanga upya
au kurudia `{name}`; haiwezi kukiondoa, kubuni kipya, wala kuambatisha umbizo
lake yenyewe — maktaba hii hukagua hilo, na katalogi mbovu hurejea kwenye
maandishi chanzo badala ya kuanguka.

!!! note "Mgeni kwa gettext? Mtiririko mzima wa kazi kwa sentensi nne"

    **gettext** ndiyo njia ya kawaida ambayo programu hutafsiriwa, ndani ya
    Python na mbali zaidi. Msimbo wako huweka alama kwenye mifuatano
    inayotafsirika; *kitoaji* huzikusanya katika faili la kiolezo (`.pot`);
    mfasiri — mara nyingi si mtayarishaji programu — hujaza faili moja la
    katalogi (`.po`) kwa kila lugha, ambalo hukusanywa kuwa `.mo` ya mfumo-jozi
    ambayo programu yako hupakia wakati wa utekelezaji. Jina la kawaida la
    kitendakazi cha kutafsiri ni `_`, hivyo `_(t"Hello {name}")` husomeka kama
    "tafsiri sentensi hii". **[Mafunzo](tutorial.md)** hupitia njia nzima —
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

## Uamuzi unaofanywa { #the-choice-it-makes }

- Tafsiri jumbe kamili, kamwe si vipande vya sentensi.
- Kubali majina rahisi tu ya vigezo kama `{name}`.
- Weka `!r` na `:.2f` chini ya udhibiti wa programu, nje ya katalogi.
- Waache wafasiri wapange upya na warudie vishika nafasi vinavyojulikana —
  lakini si kufikia sifa za vitu, wala kuongeza tabia ya uumbizaji.
- Tumia tena mafaili ya kawaida ya POT, PO, na MO, pamoja na zana ambazo
  tayari huyasoma.

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

Aina tatu za wasomaji hufika hapa: yule anayetafsiri programu yake ya kwanza,
yule anayeunganisha tafsiri katika mradi halisi, na yule anayetaka kujua hasa
kwa nini mfumo umeundwa hivi. Kila mmoja ana njia yake.

**Kujifunza** — hakuna uzoefu wa gettext unaohitajika:

<div class="grid cards" markdown>

- **[Mafunzo](tutorial.md)** — anza hapa: kutoka saraka tupu hadi tafsiri ya
  Kijapani inayofanya kazi kwa hatua tano, kila amri ikionyeshwa na matokeo
  yake.
- **[Kwa nini t-strings](comparison.md)** — ujumbe uleule ulioandikwa kwa njia
  nne, na kile ambacho `%(name)s`, `.format()`, na `$`-strings kila kimoja
  hukikabidhi katalogi.
- **[Usuli](background.md)** — kwa nini maktaba hii ipo: miaka thelathini ya
  gettext, PEP mbili, na mjadala wa stdlib uliofungwa bila jibu.

</div>

**Kuitumia kwa dhati** — marejeo ya kazi:

<div class="grid cards" markdown>

- **[Mwongozo](guide.md)** — API ya wakati wa utekelezaji: wingi, lugha kwa
  kila ombi, mifuatano iliyoahirishwa, na kinachotokea katalogi inapokuwa na
  kasoro.
- **[Utoaji](extraction.md)** — marejeo ya `pybabel`: usanidi, majina maalum ya
  vitendakazi, na jinsi zana zilizopo zinavyothibitisha katalogi hizi bure.
- **[Katika uzalishaji](workflow.md)** — mzunguko kama timu inavyouendesha:
  mzunguko wa masasisho, maingizo ya fuzzy, vizuizi vya CI, majukwaa ya
  tafsiri, na lugha kwa kila ombi katika programu ya wavuti.
- **[API](api.md)** — kila kitu ambacho kifurushi hukitoa nje, kwenye ukurasa
  mmoja.

</div>

**Kuielewa** — kutoka misingi hadi utekelezaji:

<div class="grid cards" markdown>

- **[Jinsi inavyofanya kazi](internals.md)** — kutoka kwenye kitu cha kiolezo
  cha PEP 750 hadi mfuatano ulioonyeshwa, na akiba zinazofanya ukaguzi kuwa wa
  bei rahisi.
- **[Ainisho](spec.md)** — makubaliano ya t-string ↔ msgid kama mkataba thabiti
  wenye matoleo, pamoja na seti ya utiifu inayosomeka na mashine.

</div>

## Hali { #status }

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
