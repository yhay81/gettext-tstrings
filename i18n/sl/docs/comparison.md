---
description: "Isto prevedljivo sporočilo, zapisano z %-oblikovanjem, z .format(), z $-nizi iz flufl.i18n in s t-nizom — primerjano po napakah prevajalcev, po oblasti kataloga in po ceni vpeljave."
---

# Zakaj t-nizi

Štirje načini, kako vrednost postaviti v prevedljivo sporočilo, primerjani na
istem sporočilu. Vsi štirje svoje ograde poimenujejo in prevajalcu dovolijo,
da jih prerazporedi; razlikujejo se v tem, kaj se zgodi, kadar je prevod
napačen, koliko vašega programa lahko doseže katalog in koliko stane njihova
vpeljava.

Tabele so na začetku, da lahko poiščete vrstico, ki vas zanima, in preberete
le razdelek za njo.

!!! note "Vsakega prevedenega sporočila se dotaknejo trije"

    **Katalog** je datoteka s prevodi — `.po`, dokler ga urejajo ljudje, in
    kompiliran v `.mo`, da ga naloži aplikacija ([vadnica](tutorial.md) prehodi
    oboje). Vsakega sporočila se dotaknejo trije: **razvijalec** napiše izvorni
    niz, **prevajalec** ureja katalog — pogosto na zunanji platformi, daleč od
    vsakršnega pregleda kode — **aplikacija** pa oboje med izvajanjem izriše
    skupaj. Vsak spodnji slog oblikovanja na isto vprašanje odgovori drugače:
    *kolikšen del formatnega jezika sme nadzorovati katalog?* V primerih je `_`
    običajno ime prevajalne funkcije, `tr` pa je ime iz te knjižnice.

## Drug ob drugem { #side-by-side }

**Kadar prevajalec naredi napako.** Katalog gre skozi mnogo rok in večina
tega, kar se v njem zalomi, je nenamerna:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Prevod ogrado *izpusti* — kaj se izriše? | vrednost tiho izgine | vrednost tiho izgine | vrednost tiho izgine | izvorno sporočilo z opozorilom ([privzeto](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Prevod *doda* neznano ogrado — kaj se izriše? | izjema | izjema | ograda ostane vidna kot besedilo | izvorno sporočilo z opozorilom ([privzeto](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Prevod ogrado *preoblikuje* — kaj se izriše? | to, kar je zahteval katalog, ali izjema, če črka za tip vrednosti ne ustreza več | to, kar je zahteval katalog | v `$`-nizih ni izrazljivo | izvorno sporočilo z opozorilom |
| So ograde preverjene ob izrisu? | ne | ne | ne | da (glejte spodaj) |

**Kolikšno oblast ima katalog.** Prevod so podatki od zunaj vašega
repozitorija in vsak slog mu izroči drugačno mero moči:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Od kod pridejo vrednosti? | iz izrecne preslikave | iz izrecnih argumentov | iz lokalnih in globalnih spremenljivk klicatelja, poleg neobveznega `extras` | iz vrednosti, ujetih znotraj t-niza |
| Sme katalog spremeniti oblikovanje vrednosti? | da | da | ne | ne |
| Sme katalog seči v objekte (dostop do atributov)? | ne | da | da, z imeni s piko | ne |
| Kje živi »trenutni jezik«? | kamor ga postavi aplikacija | kamor ga postavi aplikacija | v skladu jezikovnih oznak na deljenem aplikacijskem objektu | v `ContextVar`, za vsako opravilo ali zahtevo posebej |

**Koliko stane vpeljava.** Vse zgornje je zastonj, če se orodje ujame; tu se
morda ne:

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Najmanjši Python | kateri koli | kateri koli | 3.10 | **3.14** |
| Zrelost | standardna knjižnica | standardna knjižnica | stabilna izdaja | **alfa** |
| Uporablja običajne kataloge PO/MO? | da | da | da | da |
| Potrebuje lasten ekstraktor izvorne kode? | ne | ne | ne | da, zaenkrat |
| Katero zastavico PO izpelje Babel, da jo obstoječa orodja preverijo? | `python-format` | `python-brace-format` | nobene | `python-brace-format` |

O preverjanju ob izrisu: pri ednini se zahteva natančno ujemanje ograd.
Preverjajo se tudi množinska sporočila, in sicer po
[pravilu unije in preseka](spec.md), ki dovoli, da se množinske oblike ciljnega
jezika razlikujejo od izvornih; strožje preverjanje posamezne oblike steče ob
kompilaciji katalogov ([Ekstrakcija](extraction.md)).

Vrstica o formatni zastavici govori o preverjanju, ki pozna ograde, ne o
združljivosti kataloga. `nobene` pomeni, da standardna orodja gettext sporočilo
še vedno berejo in kompilirajo, le da `msgfmt --check-format` nima slovnice
`$`-ograd, ki bi jo lahko uporabil.

## Združljivost in zrelost { #compatibility-and-maturity }

Prvi dve vrstici zadnje tabele sta tisti, ki odločata o prevzemu, zato ju je
vredno povedati naravnost in ne kot celici v tabeli.

`%`-oblikovanje in `.format()` sta vgrajena v Python in ne potrebujeta nobene
odvisnosti. [`flufl.i18n`][flufl-i18n] je zrel paket, izdan in v produkcijski
rabi, ki teče na Pythonu 3.10 in novejšem. `gettext-tstrings` je **alfa** in
zahteva **Python 3.14 ali novejši**, ker so t-nizi nova sintaksa v 3.14 —
vzvratne prenosljivke ni in je ne more biti. Njegova
[specifikacija](spec.md) je njen stabilni del; pythonski API se pred 1.0 še
lahko premakne.

Česar ne stane nobeden od njih, je združljivost katalogov. Vsi štirje
proizvedejo običajne datoteke POT/PO/MO, ki jih vsak urejevalnik PO, vsaka
prevajalska platforma in vsako orodje GNU gettext že berejo, zato je spodnja
izbira povratna na način, kot menjava *formata* katalogov ne bi bila.
[Migracija](migration.md) pokriva selitev obstoječega projekta.

Spodnji razdelki vsako izmed teh tehtanj prikažejo podrobno, en način za
drugim.

## %-oblikovanje { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Kaj gre lahko narobe: en sam izbrisan znak v prevodu sesuje izris.

Niz v katalogu nosi sintakso printf, vključno s končno črko za tip — `s` v
`%(name)s` —, ki jo je zlahka spregledati in zlahka pokvariti:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Popravek enega znaka v urejevalniku PO postane izjema med izvajanjem, razen če
ga prej ujame preverjanje katalogov. GNU-jev `msgfmt --check-format` tega
sicer ujame, a le pri sporočilih z zastavico `python-format` in le, če katalog
na poti do vaše aplikacije res gre skozi msgfmt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Odpravi končno črko za tip, ograda pa ostane imenovana in prosto
prerazporedljiva. Tisto, kar gre lahko narobe, se preseli na drugo stran
menjave: prevod dobi oblast nad vašimi objekti.

`str.format` je majhen izrazni jezik in klicati ga nad nizom pomeni temu nizu
izročiti pravico, da ga uporabi:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Zdaj te dobesedne nize zamenjajte s tem, kar vrne `_()`. Če se prevod niza
`Hello {name}` vrne kot `{conf.api_key}`, njegov izris izpiše vaš ključ API —
kaj se prebere, je odločil katalog, ne vaša koda. Katalog ni koda, potuje pa
kot podatki: ven na prevajalsko platformo, skozi več rok, nazaj kot `.po`,
kompiliran v `.mo`, včasih v celoti prevzet od zunaj vašega projekta.
`.format()` vsakemu koraku te poti podeli dostop do atributov objektov, ki jih
izročite.

## `$`-nizi in flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Interpolacijski jezik `$name` prispeva [`string.Template`][stdlib-template] iz
standardne knjižnice, ki pa sam po sebi ni prevajalski API.
[`flufl.i18n`][flufl-i18n] ta slog združi z iskanjem po gettextovem katalogu.
Bodite pozorni: vrednost se nikoli ne izroči — flufl.i18n imenski prostor za
zamenjave zgradi iz globalnih in lokalnih spremenljivk klicatelja; sporočilu je
na voljo, kar koli obstaja na klicnem mestu. Neobvezna preslikava `extras` ima
prednost pred obojim. Sintaksa, ki jo vidi prevajalec, nima ne končne črke za
tip ne formatne specifikacije, ograde pa ostajajo prosto prerazporedljive.

Nedosegljiva zamenjava ne sproži izjeme. Pri `name = "Ada"` in brez `nombre` v
imenskem prostoru klicatelja se katalogov prevod `Hello $nombre` izriše kot
`Hello $nombre`: nerazrešena ograda ostane vidna. To [dokumentirano vedenje]
ohrani preostanek prevedenega sporočila, namesto da bi klic spodletel. Izjeme,
sprožene med razreševanjem atributa ali pretvarjanjem vrednosti, se še vedno
lahko razširijo navzgor.

`flufl.i18n` je od golega `string.Template` zmogljivejši v eni pomembni točki.
Njegov [lastni Template] sprejema ograde s piko, kot je `$settings.api_key`,
njegov [prevajalnik] pa te poti razreši glede na vrednosti klicatelja. Prevedena ograda lahko poimenuje katero koli
razpoložljivo lokalno ali globalno spremenljivko klicatelja in s piko prehodi
njene atribute. To je priročno, kadar sporočilo potrebuje atribut, hkrati pa
naredi klicateljev okvir za del imenskega prostora zamenjav, ki ga vidi
katalog. Primerjava tukaj opisuje `flufl.i18n` 6.0.0, ne pa vsake možne rabe
`string.Template`.

Odgovarja tudi na vprašanje, ki ga druga dva sloga oblikovanja v celoti
prepustita aplikaciji: *kateri* jezik je trenutno dejaven in kako ga zamenjati.
[Aplikacijski objekt][application object] hrani sklad jezikov, `_.push(code)` in
`_.pop()` ga premikata, `with _.using(code):` se gnezdi, [strategija][strategy]
pa za jezikovno oznako poišče katalog, tako da aplikaciji nikoli ni treba sami
ravnati s katalognimi objekti. Prav strežnik, ki mora med eno samo enoto dela
ustvariti besedilo v več kot enem jeziku — stran za bralca, obvestilo za nekoga,
čigar račun je nastavljen drugače —, je primer, zaradi katerega vse to obstaja.

Sklad živi na tem aplikacijskem objektu, ki si ga deli celoten proces. Dve
prekrivajoči se zahtevi si zato delita en sam sklad, bloki, ki niso strogo
gnezdeni *v času*, pa drug drugemu izročijo napačen jezik:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Ta knjižnica ohranja isto zmožnost — vezave se gnezdijo in odvijajo enako —, le
da jo hrani v `ContextVar` namesto v deljenem skladu, zato se zgornje
prepletanje razreši za vsako opravilo posebej. Ustreznice so na strani
[Več jezikov hkrati](guide.md#several-languages-at-once). Česar ne ponuja, je
iskanje kataloga po jezikovni oznaki: izročite prevodni objekt, ki je v
običajnem primeru en sam klic `gettext.translation()`, razčlenjeni katalog pa
predpomni standardna knjižnica.

## t-nizi { #t-strings }

```python
tr(t"Hello {name}")
```

Katalog še vedno vidi `Hello {name}` in ostaja običajen katalog PO/MO. Razlika
je v tem, kaj prevod *sme povedati* in kdo to preveri.

Ta knjižnica pred izrisom vsak prevod preveri glede na ograde izvornega
sporočila in sprejme gola imena in nič drugega. Za `t"Hello {name}"`:

| Prevod, ki vsebuje | je zavrnjen z |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Zavrnjeno ne pomeni sesuto: knjižnica privzeto zabeleži opozorilo in izriše
izvorno sporočilo, tako da slab katalog nikoli ne podre aplikacije —
[isti dogovor, kot ga drži gettext sam](guide.md#what-happens-when-a-catalog-is-wrong).

Oblikovanje ostane tam, kjer je bilo zapisano, v kodi:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nikoli ne pride do kataloga, zato ga noben prevod ne more spremeniti in
nobenemu prevajalcu ga ni treba gledati. Vendar je to *nespremenljivo*
oblikovanje, ne lokalizirano — izbira števk in ločil za vsak jezik je
[Babelova naloga, pred klicem](guide.md#locale-aware-values).

Še ena razlika je orodje: t-nizi so nova sintaksa, zato njihova ekstrakcija v
`.pot` trenutno potrebuje ekstraktor, ki t-nize pozna — na primer tistega, ki
ga ta paket [ponuja za Babel](extraction.md).

## Cena omejitve { #the-cost-of-the-restriction }

Poleg zahteve po Pythonu je cena vsega tega eno samo pravilo: interpolacija
mora biti preprosto ime.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

To je resnična omejitev in prav ista omejitev proizvede zgornja jamstva.
Skupaj z vezavo vrednosti na izvorni strani in preverjanjem ograd med
izvajanjem prepreči, da bi nizi iz kataloga vrednotili izraze, in ohrani imena
ograd smiselna za osebo, ki jih prevaja.

F-niza na ta način sploh ni mogoče uporabiti — ko ga zagleda katera koli
knjižnica, je že dokončan niz, zato bi njegovo prevajanje pomenilo prevajanje
drobca. T-nizi ([PEP 750]) hranijo statično besedilo in vrednosti ločeno, pri
tem pa ohranjajo f-nizom podobno sintakso in izrecno vezavo vrednosti.

Kako je Python prišel na to razpotje — dva PEP-a z desetletjem vmes in razprava
o standardni knjižnici, ki se je zaključila brez odgovora — je z viri
povedano v [Ozadju](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [dokumentirano vedenje]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [lastni Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [prevajalnik]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
