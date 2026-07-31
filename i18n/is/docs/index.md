---
description: "Þýddu heil t-string-skilaboð gegnum gettext og Babel, með sniðið haldið utan þýðingaskrárinnar."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Skrifaðu setninguna einu sinni.<br>Þýddu hana heila.

Örugg samþætting gettext og Babel fyrir t-strings í Python 3.14+ — gildið
helst á sínum stað og þýðingaskráin sér öll skilaboðin:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Byrjaðu á kennsluefninu :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Hvers vegna t-strings](comparison.md){ .md-button }

Þessi vefur fer sjálfur eftir því sem hann kennir: hver einasta
tungumálaútgáfa — leiðarkerfi, merkingar og byggingarskýrslan sem kann
fleirtölu — er birt úr PO-þýðingaskrám af
[`gettext-tstrings` sjálfu](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Þýðingaskráin tekur við heilli setningu, `Hello {name}`. Þýðing má víxla
`{name}` til eða endurtaka hann; hún má ekki sleppa honum, búa einn til eða
hengja við sitt eigið snið — þetta safn athugar það, og biluð þýðingaskrá
fellur aftur í frumtextann í stað þess að hrynja.

!!! note "Nýliði í gettext? Öll hringrásin í fjórum setningum"

    **gettext** er staðlaða leiðin til að þýða hugbúnað, í Python og langt
    þar út fyrir. Kóðinn þinn merkir þýðanlega strengi; *útdráttartól* safnar
    þeim í sniðmátsskrá (`.pot`); þýðandi — sjaldnast forritari — fyllir út
    eina þýðingaskrá (`.po`) fyrir hvert tungumál, sem er vistþýdd í tvíundar-
    `.mo` sem forritið þitt les inn á keyrslutíma. Venjubundna nafnið á
    þýðingarfallinu er `_`, svo `_(t"Hello {name}")` les sem „þýddu þessa
    setningu“. **[Kennsluefnið](tutorial.md)** gengur alla leiðina — merkja,
    draga út, þýða, vistþýða, keyra — á um það bil fimm mínútum.

## Vandinn sem það leysir { #the-problem-it-solves }

f-strengur er þegar innskeyttur um leið og nokkurt safn fær að sjá hann —
`f"Hello {name}"` er orðinn `"Hello Ada"`, og að þýða bútana kringum gildi
brýtur málfræði flestra tungumála. t-strengur ([PEP 750]) heldur föstum
textanum, útreiknuðum gildum, frumsegðunum, umbreytingunum og
sniðlýsingunum aðskildum — sem er einmitt sú skipting sem skilaboðaskrá
þarf.
[Hverju það breytir](comparison.md), borið saman við `%(name)s`, `.format()`
og `$`-strengi.

Ekkert í gettext eða Babel segir samt hvernig t-strengur verður að
skilaboðum. Þetta safn tekur þá ákvörðun, skrifar hana niður sem
[útgáfumerkta forskrift](spec.md) og lætur
[samræmisprófin](spec.md#conformance) fylgja með til að athuga hana.

## Valið sem það tekur { #the-choice-it-makes }

- Þýða heil skilaboð, aldrei setningarbúta.
- Taka aðeins við einföldum breytunöfnum á borð við `{name}`.
- Halda `!r` og `:.2f` undir stjórn forritsins, utan þýðingaskrárinnar.
- Leyfa þýðendum að víxla og endurtaka þekkta staðgengla — en ekki kalla á
  eigindi og ekki bæta við sniðhegðun.
- Endurnýta venjulegar POT-, PO- og MO-skrár, og tólin sem lesa þær nú þegar.

## Uppsetning { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 eða nýrri. **Birting hefur engar háðar einingar** — hún notar
`gettext` úr staðalsafninu og ekkert annað.

Útdráttur og athugun þýðingaskráa fer gegnum [Babel], svo settu þann
aukapakka upp alls staðar þar sem `pybabel` keyrir, sem er yfirleitt
þróunar- eða CI-umhverfi fremur en rekstrarímynd:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Hvert skal halda næst { #where-to-go-next }

Þrenns konar lesendur koma hingað: sá sem er að þýða sitt fyrsta forrit, sá
sem er að tengja þýðingar inn í raunverulegt verkefni, og sá sem vill vita
nákvæmlega hvers vegna vélbúnaðurinn er lagaður svona. Hver hefur sína leið.

**Að læra það** — engrar gettext-reynslu krafist:

<div class="grid cards" markdown>

- **[Kennsluefni](tutorial.md)** — byrjaðu hér: úr tómri möppu í keyrandi
  japanska þýðingu í fimm skrefum, hver skipun sýnd með úttaki sínu.
- **[Hvers vegna t-strings](comparison.md)** — sömu skilaboðin rituð á fjóra
  vegu, og hvað `%(name)s`, `.format()` og `$`-strengir rétta hver um sig
  þýðingaskránni.
- **[Bakgrunnur](background.md)** — hvers vegna þetta safn er til: þrjátíu ár
  af gettext, tveir PEP-ar og umræðan í staðalsafninu sem lokaðist án svars.

</div>

**Að nota það í alvöru** — vinnuheimildirnar:

<div class="grid cards" markdown>

- **[Handbók](guide.md)** — keyrslutíma-API-ið: fleirtala, tungumál eftir
  beiðni, frestaðir strengir, og hvað gerist þegar þýðingaskrá er röng.
- **[Útdráttur](extraction.md)** — `pybabel`-heimildin: stillingar, eigin
  fallanöfn, og hvernig tólin sem þegar eru til staðfesta þessar þýðingaskrár
  án nokkurs aukakostnaðar.
- **[Í rekstri](workflow.md)** — hringrásin eins og teymi keyrir hana:
  uppfærsluferlið, fuzzy-færslur, CI-hlið, þýðingavettvangar og tungumál
  eftir beiðni í vefforriti.
- **[API](api.md)** — allt sem pakkinn flytur út, á einni síðu.

</div>

**Að skilja það** — frá grunnreglum að útfærslu:

<div class="grid cards" markdown>

- **[Hvernig þetta virkar](internals.md)** — frá sniðmátshlutnum í PEP 750 að
  birta strengnum, og skyndiminnunum sem gera athugunina ódýra.
- **[Forskrift](spec.md)** — venjan t-strengur ↔ msgid sem stöðugur,
  útgáfumerktur samningur, með vélleseinlegum samræmisprófum.

</div>

## Staða { #status }

Alfa-útgáfa. Samningurinn er lítill af ásettu ráði og
[forskriftin](spec.md) er stöðugi hluti hans; Python-API-ið gæti enn hreyfst.
Fyrir stöðuga útgáfu þarf þetta breiðari tungumálagögn, samfellda mælingu á
afköstum, API-yfirlestur frá fólki sem notar gettext og Babel í alvöru, og
samhæfnisprófanir yfir hverja studda Python- og Babel-útgáfu.

[Mál og breytingabeiðnir](https://github.com/yhay81/gettext-tstrings/issues)
eru vel þegnar — alfa er einmitt tíminn þegar viðmótið er enn þess virði að
deila um.

## Gakktu í samfélagið { #join-the-community }

- Veldu þér
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  fyrir afmarkað framlag.
- Spurðu um notkun í
  [Q&A Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Komdu með gettext-hringrásir úr rekstri og API-hugmyndir í
  [Ideas Discussions](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Lestu
  [leiðbeiningar um framlög](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md)
  áður en þú opnar breytingabeiðni.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
