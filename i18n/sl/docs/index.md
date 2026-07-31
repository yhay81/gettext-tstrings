---
description: "Prevajajte celotna sporočila iz t-nizov prek gettexta in Babela, z vrednostmi in oblikovanjem, ki ostanejo zunaj kataloga."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Prevajajte celotna sporočila<br>s pythonskimi t-nizi

`gettext-tstrings` poveže t-nize iz Pythona 3.14+ s standardnimi katalogi
gettexta in orodji Babela. Vrednosti in oblikovanje ostanejo v kodi
aplikacije; prevajalci delajo s celotnimi sporočili in preprostimi ogradami
`{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Katalog vsebuje `Hello {name}`. Prevod sme `{name}` prestaviti ali ponoviti.
Če ogrado izpusti, preimenuje ali ji spremeni obliko, preverjanje kataloga
napako sporoči. Če neveljaven vnos kljub temu pride v produkcijo, knjižnica
zabeleži opozorilo in izriše izvorno sporočilo, namesto da bi se sesul.

[Začnite petminutno vadnico :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Primerjajte možnosti](comparison.md){ .md-button }

Alfa · Python 3.14+ · standardni katalogi PO/MO · brez odvisnosti tretjih oseb med izvajanjem
{ .home-facts }

Ta stran uresničuje to, kar dokumentira: vsaka jezikovna različica —
navigacija, oznake in poročilo o gradnji, ki upošteva množinske oblike — se
izriše iz katalogov PO s
[knjižnico `gettext-tstrings` samo](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Je to za vas? { #is-this-for-you }

**Danes se ujame, kadar** vaša aplikacija teče na Pythonu 3.14 ali novejšem;
gettext in Babel že uporabljate ali pa želite prevzeti njun delovni proces
PO/MO; in želite sintakso t-nizov s poimenovanimi ogradami, ki so preverjene,
še preden se izrišejo.

**Še se ne ujame, kadar** potrebujete Python 3.13 ali starejši; kadar
potrebujete stabilen pythonski API — to je alfa in [specifikacija](spec.md) je
tisti njen del, ki se je ustalil; ali kadar skoraj vse vaše prevedljivo
besedilo živi v predlognem jeziku in ne v pythonski izvorni kodi.

Kataloge že imate? Delovali bodo naprej. `_("Hello {name}").format(name=name)`
in `tr(t"Hello {name}")` proizvedeta isti msgid, zato obstoječi prevodi
preklop preživijo — [Migracija](migration.md) prehodi celotno selitev.

## Kaj sme katalog povedati { #what-the-catalog-may-say }

**Prevod ne more spremeniti zgradbe sporočila, ki ga prevaja.** To je celotna
obljuba in iz nje sledi vse drugo na tem spletišču. Prevod sme `{name}`
prestaviti ali ponoviti in sme prepisati vsako drugo besedo okoli njega. Ne sme
pa ograde izpustiti, si izmisliti nove, skoznjo seči v vaše objekte ali ji
dodati lastnega oblikovanja.

Knjižnica to preveri na poti noter — ob kompilaciji katalogov — in znova ob
izrisu, in prav v tem je razlika med napako, ki jo najde pregled, in napako, ki
jo najde uporabnik.

!!! note "Vam je gettext nov? Celoten delovni proces v štirih povedih"

    **gettext** je standardni način prevajanja programske opreme, v Pythonu in
    daleč zunaj njega. Vaša koda označi prevedljiva sporočila; *ekstraktor* jih zbere
    v datoteko predloge (`.pot`); prevajalec — običajno ne programer — izpolni
    po eno katalogno datoteko (`.po`) za vsak jezik, ta pa se prevede v binarno
    datoteko `.mo`, ki jo vaša aplikacija naloži med izvajanjem. Uveljavljeno
    ime prevajalske funkcije je `_`, zato se `_(t"Hello {name}")` bere kot
    »prevedi to sporočilo«. **[Vadnica](tutorial.md)** prehodi celotno pot —
    označevanje, ekstrakcija, prevajanje, kompilacija, zagon — v približno petih
    minutah.

## Problem, ki ga rešuje { #the-problem-it-solves }

F-niz je v trenutku, ko ga zagleda katera koli knjižnica, že interpoliran —
iz `f"Hello {name}"` je nastalo `"Hello Ada"`, prevajanje drobcev okoli
vrednosti pa poruši slovnico večine jezikov. T-niz ([PEP 750]) hrani statično
besedilo, ovrednotene vrednosti, izvorne izraze, pretvorbe in formatne
specifikacije ločeno — in prav to je delitev, ki jo katalog sporočil potrebuje.
[Kaj to spremeni](comparison.md) v primerjavi z `%(name)s`, `.format()` in
`$`-nizi.

Toda ne gettext ne Babel ne povesta, kako t-niz postane sporočilo. Ta knjižnica
to izbiro naredi, jo zapiše kot [verzionirano specifikacijo](spec.md) in
priloži [zbirko testov skladnosti](spec.md#conformance) za njeno preverjanje.

## Pravila zasnove { #the-design-rules }

- Prevajati celotna sporočila, nikoli drobcev povedi.
- Sprejemati le preprosta imena spremenljivk, kot je `{name}`.
- `!r` in `:.2f` ohraniti pod nadzorom aplikacije, zunaj kataloga.
- Prevodom dopustiti prerazporejanje in ponavljanje znanih ograd, hkrati pa
  jim preprečiti seganje po atributih ali dodajanje oblikovanja.
- Ponovno uporabiti običajne datoteke POT, PO in MO ter orodja, ki jih znajo
  brati že danes.

In pripadajoči seznam tega, česar se namenoma ne dotika: ne lokalizira števil,
valut ali datumov — [ta oblikujte prej](guide.md#locale-aware-values), z
Babelom; izrisanega izpisa ne ubeži za HTML, lupino ali terminal; in ne more
presoditi, ali je prevod *pravilen*, ampak le, ali so njegove ograde
nedotaknjene.

## Namestitev { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 ali novejši. **Izris nima nobenih odvisnosti** — uporablja
`gettext` iz standardne knjižnice in nič drugega.

Ekstrakcija in preverjanje katalogov potekata prek orodja [Babel], zato ta
dodatek namestite povsod, kjer teče `pybabel`, kar je običajno razvojno ali CI
okolje in ne produkcijska slika:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Kam naprej { #where-to-go-next }

**Začnite tukaj** — brez predpostavljenih izkušenj z gettextom:

<div class="grid cards" markdown>

- **[Vadnica](tutorial.md)** — od praznega imenika do delujočega japonskega
  prevoda v petih korakih, vsak ukaz prikazan skupaj z izpisom.
- **[Zakaj t-nizi](comparison.md)** — isto sporočilo, zapisano na štiri načine,
  in kaj katalogu izročijo `%(name)s`, `.format()` in `$`-nizi.

</div>

**Uporaba** — delovne reference:

<div class="grid cards" markdown>

- **[Vodnik](guide.md)** — API med izvajanjem: katero vstopno točko uporabiti,
  množinske oblike, jezik na zahtevo, odloženi nizi in kaj se zgodi, kadar je
  katalog napačen.
- **[Ekstrakcija](extraction.md)** — referenca za `pybabel`: konfiguracija,
  lastna imena funkcij in kako obstoječa orodja te kataloge preverijo zastonj.
- **[V produkciji](workflow.md)** — zanka, kakor jo poganja ekipa: cikel
  posodobitev, ohlapni (`fuzzy`) vnosi, zaščite v CI, prevajalske platforme in
  odprema.
- **[Migracija](migration.md)** — prevzemanje tega v projektu, ki kataloge že
  ima, po eno klicno mesto naenkrat.
- **[Za prevajalce](translators.md)** — ena stran, ki jo izročite tistemu, ki
  ureja datoteke `.po`.

</div>

**Razumevanje** — od zgodovine do izvedbe:

<div class="grid cards" markdown>

- **[Ozadje](background.md)** — zakaj ta knjižnica obstaja: trideset let
  gettexta, dva PEP-a in razprava o standardni knjižnici, ki se je zaključila
  brez odgovora.
- **[Pasti](pitfalls.md)** — kaj se je ob prevajanju tega spletišča v
  petintrideset jezikov v resnici polomilo in katero polovico tega orodje
  lahko ujame.
- **[Kako deluje](internals.md)** — od objekta predloge iz PEP 750 do izrisanega
  niza in predpomnilnikov, zaradi katerih je preverjanje poceni.

</div>

**Referenca** — pogodbe:

<div class="grid cards" markdown>

- **[API](api.md)** — vse, kar paket izvaža, na eni strani.
- **[Specifikacija](spec.md)** — dogovor t-niz ↔ msgid kot stabilna,
  verzionirana pogodba s strojno berljivo zbirko testov skladnosti.

</div>

## Stanje { #status }

| | |
| --- | --- |
| Različica paketa | 0.1.0a7 |
| Stabilnost API-ja | alfa — Pythonov API se še lahko spremeni |
| [Specifikacija](spec.md) | v1, z [zbirko testov skladnosti](spec.md#conformance) |
| Python | 3.14 in novejši; testirano na 3.14, 3.14t (prostonitni) in 3.15 |
| Babel | 2.18 ali novejši, in le tam, kjer teče `pybabel` |
| Odvisnosti med izvajanjem | brez — `gettext` iz standardne knjižnice |
| Oblika kataloga | običajni POT, PO in MO |
| Spremembe | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Alfa. Pogodba je namerno majhna in [specifikacija](spec.md) je njen stabilni
del; Pythonov API se še lahko premakne. Pred stabilno izdajo potrebuje širši
nabor jezikovnih testnih podatkov, vztrajno spremljanje zmogljivosti, pregled
API-ja s strani ljudi, ki gettext in Babel uporabljajo zares, ter preverjanje
združljivosti z vsemi podprtimi izdajami Pythona in Babela.

[Prijave težav in pull requesti](https://github.com/yhay81/gettext-tstrings/issues)
so dobrodošli — alfa je natanko tisti čas, ko se je o vmesniku še vredno
prerekati.

## Pridružite se skupnosti { #join-the-community }

- Izberite si
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  za omejen prvi prispevek.
- Vprašanja o uporabi zastavite v
  [razpravah Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Produkcijske delovne procese z gettextom in zamisli za API prinesite v
  [razprave Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Preden odprete pull request, preberite
  [vodnik za prispevanje](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
