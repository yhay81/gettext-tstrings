---
description: "Þýddu heil t-string-skilaboð gegnum gettext og Babel, með gildunum og sniðinu haldið utan þýðingaskrárinnar."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Þýddu heil skilaboð,<br>ekki strengjabúta.

`gettext-tstrings` tengir t-strengi í Python 3.14+ við staðlaðar
gettext-þýðingaskrár og Babel-tólakeðjuna. Gildi og snið haldast í
forritskóðanum; þýðingaskráin geymir heil skilaboð með einföldum
`{name}`-staðgenglum:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Byrjaðu á kennsluefninu :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Berðu saman valkostina](comparison.md){ .md-button }

Alfa · Python 3.14+ · venjulegar PO/MO-þýðingaskrár · engar háðar einingar á
keyrslutíma
{ .home-facts }

Þessi vefur fer sjálfur eftir því sem hann kennir: hver einasta
tungumálaútgáfa — leiðarkerfi, merkingar og byggingarskýrslan sem kann
fleirtölu — er birt úr PO-þýðingaskrám af
[`gettext-tstrings` sjálfu](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Er þetta fyrir þig? { #is-this-for-you }

**Það passar í dag þegar** forritið þitt keyrir á Python 3.14 eða nýrri; þú
notar nú þegar gettext og Babel, eða vilt taka upp PO/MO-hringrás þeirra; og
þú vilt t-strengjamálskipan með nefndum staðgenglum sem eru athugaðir áður en
þeir birtast.

**Það passar ekki enn þegar** þú þarft Python 3.13 eða eldri; þú krefst
stöðugs Python-viðmóts — þetta er alfa og [forskriftin](spec.md) er sá hluti
þess sem hefur sest; eða nánast allur þýðanlegur texti þinn býr í
sniðmátsmáli fremur en í Python-frumkóða.

Áttu þýðingaskrár nú þegar? Þær halda áfram að virka.
`_("Hello {name}").format(name=name)` og `tr(t"Hello {name}")` framleiða sama
msgid, svo að núverandi þýðingar lifa skiptin af —
[Yfirfærsla](migration.md) gengur gegnum alla færsluna.

## Hvað þýðingaskráin má segja { #what-the-catalog-may-say }

Þýðingaskráin tekur við heilum skilaboðum, `Hello {name}`. Þýðing má víxla
`{name}` til eða endurtaka hann, og má umskrifa hvert annað orð í kringum
hann. Hún má ekki sleppa staðgenglinum, búa til nýjan, seilast gegnum hann inn
í hlutina þína eða hengja við sitt eigið snið.

Það er allt loforðið: **þýðing getur ekki breytt gerð þeirra skilaboða sem hún
þýðir.** Safnið athugar það á leiðinni inn — þegar þýðingaskrár eru vistþýddar
— og aftur við birtingu; biluð færsla sem kemst engu að síður í rekstur skráir
viðvörun og birtir frumtextaskilaboðin í stað þess að hrynja.

!!! note "Nýliði í gettext? Öll hringrásin í fjórum setningum"

    **gettext** er staðlaða leiðin til að þýða hugbúnað, í Python og langt
    þar út fyrir. Kóðinn þinn merkir þýðanleg skilaboð; *útdráttartól* safnar
    þeim í sniðmátsskrá (`.pot`); þýðandi — sjaldnast forritari — fyllir út
    eina þýðingaskrá (`.po`) fyrir hvert tungumál, sem er vistþýdd í tvíundar-
    `.mo` sem forritið þitt les inn á keyrslutíma. Venjubundna nafnið á
    þýðingarfallinu er `_`, svo `_(t"Hello {name}")` les sem „þýddu þessi
    skilaboð“. **[Kennsluefnið](tutorial.md)** gengur alla leiðina — merkja,
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

## Hönnunarreglurnar { #the-design-rules }

- Þýða heil skilaboð, aldrei setningarbúta.
- Taka aðeins við einföldum breytunöfnum á borð við `{name}`.
- Halda `!r` og `:.2f` undir stjórn forritsins, utan þýðingaskrárinnar.
- Leyfa þýðingum að víxla og endurtaka þekkta staðgengla, en koma um leið í
  veg fyrir að þær nái til eiginda eða bæti við sniði.
- Endurnýta venjulegar POT-, PO- og MO-skrár, og tólin sem lesa þær nú þegar.

Og samsvarandi listi yfir það sem það lætur af ásettu ráði í friði: það
staðfærir ekki tölur, gjaldmiðla eða dagsetningar —
[sníddu þau fyrst](guide.md#locale-aware-values), með Babel; það escape-ritar
ekki birt úttak fyrir HTML, skel eða skjáhermi; og það getur ekki dæmt um
hvort þýðing sé *rétt*, aðeins hvort staðgenglar hennar séu heilir.

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

**Byrjaðu hér** — engrar gettext-reynslu krafist:

<div class="grid cards" markdown>

- **[Kennsluefni](tutorial.md)** — úr tómri möppu í keyrandi japanska þýðingu
  í fimm skrefum, hver skipun sýnd með úttaki sínu.
- **[Hvers vegna t-strings](comparison.md)** — sömu skilaboðin rituð á fjóra
  vegu, og hvað `%(name)s`, `.format()` og `$`-strengir rétta hver um sig
  þýðingaskránni.

</div>

**Notaðu það** — vinnuheimildirnar:

<div class="grid cards" markdown>

- **[Handbók](guide.md)** — keyrslutíma-API-ið: hvaða aðgangsstað skal nota,
  fleirtala, tungumál eftir beiðni, frestaðir strengir, og hvað gerist þegar
  þýðingaskrá er röng.
- **[Útdráttur](extraction.md)** — `pybabel`-heimildin: stillingar, eigin
  fallanöfn, og hvernig tólin sem þegar eru til staðfesta þessar þýðingaskrár
  án nokkurs aukakostnaðar.
- **[Í rekstri](workflow.md)** — hringrásin eins og teymi keyrir hana:
  uppfærsluferlið, fuzzy-færslur, CI-hlið, þýðingavettvangar og útgáfa.
- **[Yfirfærsla](migration.md)** — að taka þetta upp í verkefni sem hefur nú
  þegar þýðingaskrár, einn köllunarstað í einu.
- **[Fyrir þýðendur](translators.md)** — ein síða til að rétta þeim sem
  ritstýrir `.po`-skránum.

</div>

**Skildu það** — frá sögunni að útfærslunni:

<div class="grid cards" markdown>

- **[Bakgrunnur](background.md)** — hvers vegna þetta safn er til: þrjátíu ár
  af gettext, tveir PEP-ar og umræðan í staðalsafninu sem lokaðist án svars.
- **[Fallgryfjur](pitfalls.md)** — hvað brotnaði í raun við að þýða þennan vef
  á þrjátíu og fimm tungumál, og hvorn helminginn tól getur gripið.
- **[Hvernig þetta virkar](internals.md)** — frá sniðmátshlutnum í PEP 750 að
  birta strengnum, og skyndiminnunum sem gera athugunina ódýra.

</div>

**Uppflettirit** — samningarnir:

<div class="grid cards" markdown>

- **[API](api.md)** — allt sem pakkinn flytur út, á einni síðu.
- **[Forskrift](spec.md)** — venjan t-strengur ↔ msgid sem stöðugur,
  útgáfumerktur samningur, með vélleseinlegum samræmisprófum.

</div>

## Staða { #status }

| | |
| --- | --- |
| Útgáfa pakkans | 0.1.0a7 |
| Stöðugleiki API | alfa — Python-API-ið gæti enn breyst |
| [Forskrift](spec.md) | v1, með [samræmisprófum](spec.md#conformance) |
| Python | 3.14 og nýrra; prófað á 3.14, 3.14t (free-threaded) og 3.15 |
| Babel | 2.18 eða nýrra, og aðeins þar sem `pybabel` keyrir |
| Keyrsluháðir pakkar | engir — `gettext` úr staðalsafninu |
| Snið þýðingaskráa | venjulegar POT-, PO- og MO-skrár |
| Breytingar | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

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
