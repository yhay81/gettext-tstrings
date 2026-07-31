---
description: "Cyfieithwch negeseuon llinyn-t cyflawn drwy gettext a Babel, gyda'r gwerthoedd a'r fformatio wedi'u cadw allan o'r catalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Cyfieithwch negeseuon cyflawn<br>â llinynnau-t Python

Mae `gettext-tstrings` yn cysylltu llinynnau-t Python 3.14+ â chatalogau
gettext safonol ac offer Babel. Mae gwerthoedd a fformatio'n aros yng nghod y
rhaglen; mae cyfieithwyr yn gweithio â negeseuon cyflawn a dalwyr lle `{name}`
syml:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Mae'r catalog yn cynnwys `Hello {name}`. Caiff cyfieithiad symud neu ailadrodd
`{name}`. Os yw'n ei ddileu, yn ei ailenwi, neu'n ei ailfformatio, mae dilysu'r
catalog yn adrodd y gwall. Os yw cofnod annilys yn cyrraedd cynhyrchu beth
bynnag, mae'r llyfrgell yn cofnodi rhybudd ac yn rendro'r neges ffynhonnell yn
lle chwalu.

[Dechrau'r tiwtorial pum munud :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Cymharwch y dewisiadau eraill](comparison.md){ .md-button }

Alffa · Python 3.14+ · catalogau PO/MO safonol · dim dibyniaethau rhedeg trydydd parti
{ .home-facts }

Mae'r wefan hon yn ymarfer yr hyn y mae'n ei ddogfennu: mae pob argraffiad
iaith — y llywio, y labeli, a'r adroddiad adeiladu sy'n ymwybodol o ffurfiau
lluosog — yn cael ei rendro o gatalogau PO gan
[`gettext-tstrings` ei hun](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Ai ar eich cyfer chi y mae hyn? { #is-this-for-you }

**Yn addas heddiw pan** fo eich rhaglen yn rhedeg ar Python 3.14 neu fwy
newydd; eich bod eisoes yn defnyddio gettext a Babel, neu am fabwysiadu eu llif
gwaith PO/MO; a'ch bod am gystrawen llinyn-t â dalwyr lle wedi'u henwi sy'n cael
eu gwirio cyn iddynt rendro.

**Ddim yn addas eto pan** fo angen Python 3.13 neu hŷn arnoch; pan fo angen API
Python sefydlog arnoch — alffa yw hwn, a'r [fanyleb](spec.md) yw'r rhan
ohono sydd wedi setlo; neu pan fo bron yr holl destun cyfieithadwy sydd gennych
yn byw mewn iaith dempledu yn hytrach nag mewn ffynhonnell Python.

Catalogau gennych eisoes? Maent yn dal i weithio. Mae
`_("Hello {name}").format(name=name)` a `tr(t"Hello {name}")` yn cynhyrchu'r un
msgid, felly mae'r cyfieithiadau sy'n bodoli'n goroesi'r newid — mae
[Mudo](migration.md) yn cerdded y symud cyfan.

## Yr hyn y caiff y catalog ei ddweud { #what-the-catalog-may-say }

**Ni all cyfieithiad newid strwythur y neges y mae'n ei chyfieithu.** Dyna'r
addewid cyfan, ac o hynny y daw gweddill y wefan hon. Caiff cyfieithiad
aildrefnu neu ailadrodd `{name}`, a chaiff ailysgrifennu pob gair arall o'i
amgylch. Ni chaiff ollwng y daliwr lle, dyfeisio un newydd, estyn drwyddo i
mewn i'ch gwrthrychau, na chysylltu fformatio o'i ben a'i bastwn ei hun.

Mae'r llyfrgell yn gwirio hynny ar y ffordd i mewn — pan grynhoir catalogau —
ac eto adeg rendro, sef y gwahaniaeth rhwng camgymeriad a ganfyddir mewn
adolygiad a chamgymeriad a ganfyddir gan ddefnyddiwr.

!!! note "Gettext yn newydd i chi? Y llif gwaith cyfan mewn pedair brawddeg"

    **gettext** yw'r ffordd safonol y caiff meddalwedd ei chyfieithu, yn Python
    a thu hwnt o lawer. Mae eich cod yn nodi'r negeseuon cyfieithadwy; mae
    *echdynnwr* yn eu casglu i ffeil dempled (`.pot`); mae cyfieithydd — nad yw
    fel arfer yn rhaglennydd — yn llenwi un ffeil gatalog (`.po`) fesul iaith,
    sy'n cael ei chrynhoi'n ffeil ddeuaidd `.mo` y mae eich rhaglen yn ei llwytho
    wrth redeg. Yr enw confensiynol ar y ffwythiant cyfieithu yw `_`, felly mae
    `_(t"Hello {name}")` yn darllen fel "cyfieitha'r neges hon". Mae'r
    **[tiwtorial](tutorial.md)** yn cerdded y llwybr cyfan — nodi, echdynnu,
    cyfieithu, crynhoi, rhedeg — mewn tua phum munud.

## Y broblem y mae'n ei datrys { #the-problem-it-solves }

Mae llinyn-f eisoes wedi'i ryngosod erbyn i unrhyw lyfrgell ei weld — mae
`f"Hello {name}"` wedi troi'n `"Hello Ada"`, ac mae cyfieithu'r darnau o
amgylch gwerth yn torri gramadeg y rhan fwyaf o ieithoedd. Mae llinyn-t
([PEP 750]) yn cadw'r testun statig, y gwerthoedd a gyfrifwyd, yr ymadroddion
ffynhonnell, y trawsnewidiadau a'r manylebau fformat ar wahân — sef yn union y
rhaniad y mae catalog negeseuon ei angen.
[Beth mae hynny'n ei newid](comparison.md), o'i gymharu â `%(name)s`,
`.format()` a llinynnau `$`.

Nid oes dim yn gettext nac yn Babel yn dweud sut y daw llinyn-t yn neges,
serch hynny. Mae'r llyfrgell hon yn gwneud y dewis hwnnw, yn ei ysgrifennu
i lawr yn [fanyleb â fersiwn](spec.md), ac yn cludo'r
[gyfres gydymffurfio](spec.md#conformance) i'w wirio.

## Y rheolau cynllunio { #the-design-rules }

- Cyfieithu negeseuon cyflawn, byth darnau o frawddegau.
- Derbyn enwau newidynnau syml yn unig, megis `{name}`.
- Cadw `!r` a `:.2f` dan reolaeth y rhaglen, allan o'r catalog.
- Caniatáu i gyfieithiadau aildrefnu ac ailadrodd dalwyr lle hysbys, gan eu
  hatal rhag cyrraedd priodoleddau neu ychwanegu fformatio.
- Ailddefnyddio ffeiliau POT, PO ac MO cyffredin, a'r offer sydd eisoes yn eu
  darllen.

A'r rhestr gyfatebol o'r hyn y mae'n ei adael llonydd yn fwriadol: nid yw'n
lleoleiddio rhifau, arian, na dyddiadau —
[fformatiwch y rheini'n gyntaf](guide.md#locale-aware-values), gyda Babel; nid
yw'n dianc allbwn wedi'i rendro ar gyfer HTML, cragen, na therfynell; ac ni all
farnu a yw cyfieithiad yn *gywir*, dim ond a yw ei ddalwyr lle'n gyfan.

## Gosod { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 neu fwy newydd. **Nid oes gan y rendro unrhyw ddibyniaethau** —
mae'n defnyddio `gettext` y llyfrgell safonol a dim byd arall.

Mae'r echdynnu a dilysu catalogau'n rhedeg drwy [Babel], felly gosodwch yr
ychwanegyn hwnnw ple bynnag y mae `pybabel` yn rhedeg, sef amgylchedd
datblygu neu CI fel arfer yn hytrach nag delwedd gynhyrchu:

```console
python -m pip install "gettext-tstrings[babel]"
```

## I ble nesaf { #where-to-go-next }

**Dechreuwch yma** — heb dybio unrhyw brofiad o gettext:

<div class="grid cards" markdown>

- **[Tiwtorial](tutorial.md)** — o gyfeiriadur gwag i gyfieithiad Japaneg sy'n
  rhedeg mewn pum cam, pob gorchymyn wedi'i ddangos gyda'i allbwn.
- **[Pam llinynnau-t](comparison.md)** — yr un neges wedi'i hysgrifennu mewn
  pedair ffordd, a'r hyn y mae `%(name)s`, `.format()` a llinynnau `$` yn ei
  drosglwyddo i'r catalog.

</div>

**Ei ddefnyddio** — y cyfeirlyfrau gwaith:

<div class="grid cards" markdown>

- **[Canllaw](guide.md)** — yr API rhedeg: pa bwynt mynediad i'w ddefnyddio,
  ffurfiau lluosog, ieithoedd fesul cais, llinynnau gohiriedig, a beth sy'n
  digwydd pan fo catalog yn anghywir.
- **[Echdynnu](extraction.md)** — y cyfeirlyfr `pybabel`: ffurfweddu, enwau
  ffwythiannau pwrpasol, a sut y mae offer sy'n bodoli eisoes yn dilysu'r
  catalogau hyn am ddim.
- **[Mewn cynhyrchu](workflow.md)** — y ddolen fel y mae tîm yn ei rhedeg: y
  cylch diweddaru, cofnodion fuzzy, gatiau CI, llwyfannau cyfieithu, a chludo.
- **[Mudo](migration.md)** — mabwysiadu hwn mewn prosiect sydd eisoes â
  chatalogau, un safle galw ar y tro.
- **[I gyfieithwyr](translators.md)** — un dudalen i'w rhoi i bwy bynnag sy'n
  golygu'r ffeiliau `.po`.

</div>

**Ei ddeall** — o'r hanes at y gweithredu:

<div class="grid cards" markdown>

- **[Cefndir](background.md)** — pam y mae'r llyfrgell hon yn bodoli: deng
  mlynedd ar hugain o gettext, dau PEP, a'r drafodaeth am y llyfrgell safonol
  a gaeodd heb ateb.
- **[Peryglon](pitfalls.md)** — beth a dorrodd cyfieithu'r wefan hon i
  bymtheg ar hugain o ieithoedd mewn gwirionedd, a pha hanner y gall offeryn
  ei ddal.
- **[Sut mae'n gweithio](internals.md)** — o wrthrych templed PEP 750 at y
  llinyn wedi'i rendro, a'r cachau sy'n gwneud y gwirio'n rhad.

</div>

**Cyfeirlyfr** — y contractau:

<div class="grid cards" markdown>

- **[API](api.md)** — popeth y mae'r pecyn yn ei allforio, ar un dudalen.
- **[Manyleb](spec.md)** — y confensiwn llinyn-t ↔ msgid fel contract sefydlog
  â fersiwn, gyda chyfres gydymffurfio y gall peiriant ei darllen.

</div>

## Statws { #status }

| | |
| --- | --- |
| Fersiwn y pecyn | 0.1.0a7 |
| Sefydlogrwydd yr API | alffa — efallai y bydd yr API Python yn newid eto |
| [Manyleb](spec.md) | v1, gyda [chyfres gydymffurfio](spec.md#conformance) |
| Python | 3.14 a mwy newydd; wedi'i brofi ar 3.14, 3.14t (di-edau) a 3.15 |
| Babel | 2.18 neu fwy newydd, a dim ond ple mae `pybabel` yn rhedeg |
| Dibyniaethau rhedeg | dim — `gettext` y llyfrgell safonol |
| Fformat catalog | POT, PO ac MO cyffredin |
| Newidiadau | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Alffa. Mae'r contract yn fach yn fwriadol a'r [fanyleb](spec.md) yw'r rhan
sefydlog ohono; efallai y bydd yr API Python yn symud eto. Cyn rhyddhad
sefydlog mae angen ffurfweddiadau iaith ehangach, olrhain perfformiad
cyson, adolygiad API gan bobl sy'n defnyddio gettext a Babel o ddifrif, a
phrofi cydnawsedd ar draws pob rhyddhad Python a Babel a gefnogir.

Mae [materion a chynigion tynnu](https://github.com/yhay81/gettext-tstrings/issues)
yn cael croeso — alffa yw'r union adeg y mae'n dal yn werth dadlau am y
rhyngwyneb.

## Ymunwch â'r gymuned { #join-the-community }

- Dewiswch
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  am gyfraniad ag iddo ffiniau clir.
- Gofynnwch gwestiynau defnydd yn
  [Nhrafodaethau Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Dewch â llifau gwaith gettext cynhyrchu a syniadau API i
  [Drafodaethau Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Darllenwch y
  [canllaw cyfrannu](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  cyn agor cynnig tynnu.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
