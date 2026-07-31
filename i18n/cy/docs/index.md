---
description: "Cyfieithwch negeseuon llinyn-t cyflawn drwy gettext a Babel, gyda'r fformatio wedi'i gadw allan o'r catalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Ysgrifennwch y frawddeg unwaith.<br>Cyfieithwch hi'n gyfan.

Integreiddio diogel â gettext a Babel ar gyfer llinynnau-t Python 3.14+ — mae'r
gwerth yn aros yn ei le, ac mae'r catalog yn gweld y neges gyfan:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Dechrau'r tiwtorial :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Pam llinynnau-t](comparison.md){ .md-button }

Mae'r wefan hon yn ymarfer yr hyn y mae'n ei ddogfennu: mae pob argraffiad
iaith — y llywio, y labeli, a'r adroddiad adeiladu sy'n ymwybodol o ffurfiau
lluosog — yn cael ei rendro o gatalogau PO gan
[`gettext-tstrings` ei hun](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Mae'r catalog yn derbyn y frawddeg gyflawn `Hello {name}`. Caiff cyfieithiad
aildrefnu neu ailadrodd `{name}`; ni chaiff ei ollwng, dyfeisio un newydd, na
chysylltu fformatio o'i ben a'i bastwn ei hun — mae'r llyfrgell hon yn gwirio
hynny, ac mae catalog toredig yn cwympo'n ôl i'r testun ffynhonnell yn lle
chwalu.

!!! note "Gettext yn newydd i chi? Y llif gwaith cyfan mewn pedair brawddeg"

    **gettext** yw'r ffordd safonol y caiff meddalwedd ei chyfieithu, yn Python
    a thu hwnt o lawer. Mae eich cod yn nodi'r llinynnau cyfieithadwy; mae
    *echdynnwr* yn eu casglu i ffeil dempled (`.pot`); mae cyfieithydd — nad yw
    fel arfer yn rhaglennydd — yn llenwi un ffeil gatalog (`.po`) fesul iaith,
    sy'n cael ei chrynhoi'n ffeil ddeuaidd `.mo` y mae eich rhaglen yn ei llwytho
    wrth redeg. Yr enw confensiynol ar y ffwythiant cyfieithu yw `_`, felly mae
    `_(t"Hello {name}")` yn darllen fel "cyfieitha'r frawddeg hon". Mae'r
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

## Y dewis y mae'n ei wneud { #the-choice-it-makes }

- Cyfieithu negeseuon cyflawn, byth darnau o frawddegau.
- Derbyn enwau newidynnau syml yn unig, megis `{name}`.
- Cadw `!r` a `:.2f` dan reolaeth y rhaglen, allan o'r catalog.
- Gadael i gyfieithwyr aildrefnu ac ailadrodd dalwyr lle hysbys — ond nid
  galw priodoleddau, ac nid ychwanegu ymddygiad fformatio.
- Ailddefnyddio ffeiliau POT, PO ac MO cyffredin, a'r offer sydd eisoes yn eu
  darllen.

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

Mae tri math o ddarllenydd yn cyrraedd yma: rhywun sy'n cyfieithu ei raglen
gyntaf, rhywun sy'n gwifrau cyfieithu i mewn i brosiect go iawn, a rhywun sydd
am wybod yn union pam y mae'r peiriannau ar y siâp hwn. Mae gan bob un ei
lwybr.

**Ei ddysgu** — heb dybio unrhyw brofiad o gettext:

<div class="grid cards" markdown>

- **[Tiwtorial](tutorial.md)** — dechreuwch yma: o gyfeiriadur gwag i
  gyfieithiad Japaneg sy'n rhedeg mewn pum cam, pob gorchymyn wedi'i ddangos
  gyda'i allbwn.
- **[Pam llinynnau-t](comparison.md)** — yr un neges wedi'i hysgrifennu mewn
  pedair ffordd, a'r hyn y mae `%(name)s`, `.format()` a llinynnau `$` yn ei
  drosglwyddo i'r catalog.
- **[Cefndir](background.md)** — pam y mae'r llyfrgell hon yn bodoli: deng
  mlynedd ar hugain o gettext, dau PEP, a'r drafodaeth am y llyfrgell safonol
  a gaeodd heb ateb.

</div>

**Ei ddefnyddio o ddifrif** — y cyfeirlyfrau gwaith:

<div class="grid cards" markdown>

- **[Canllaw](guide.md)** — yr API rhedeg: ffurfiau lluosog, ieithoedd fesul
  cais, llinynnau gohiriedig, a beth sy'n digwydd pan fo catalog yn anghywir.
- **[Echdynnu](extraction.md)** — y cyfeirlyfr `pybabel`: ffurfweddu, enwau
  ffwythiannau pwrpasol, a sut y mae offer sy'n bodoli eisoes yn dilysu'r
  catalogau hyn am ddim.
- **[Mewn cynhyrchu](workflow.md)** — y ddolen fel y mae tîm yn ei rhedeg: y
  cylch diweddaru, cofnodion fuzzy, gatiau CI, llwyfannau cyfieithu, ac
  ieithoedd fesul cais mewn rhaglen we.
- **[API](api.md)** — popeth y mae'r pecyn yn ei allforio, ar un dudalen.

</div>

**Ei ddeall** — o'r egwyddorion at y gweithredu:

<div class="grid cards" markdown>

- **[Sut mae'n gweithio](internals.md)** — o wrthrych templed PEP 750 at y
  llinyn wedi'i rendro, a'r cachau sy'n gwneud y gwirio'n rhad.
- **[Manyleb](spec.md)** — y confensiwn llinyn-t ↔ msgid fel contract sefydlog
  â fersiwn, gyda chyfres gydymffurfio y gall peiriant ei darllen.

</div>

## Statws { #status }

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
