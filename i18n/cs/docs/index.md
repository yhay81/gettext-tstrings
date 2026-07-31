---
description: "Překládejte kompletní zprávy z t-stringů přes gettext a Babel, s hodnotami i formátováním drženými mimo katalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Překládejte celé zprávy,<br>ne útržky řetězců.

`gettext-tstrings` propojuje t-stringy Pythonu 3.14+ se standardními
katalogy gettextu a s nástroji Babelu. Hodnoty i formátování zůstávají
v kódu aplikace; katalog drží kompletní zprávu s jednoduchými zástupnými
symboly `{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Začněte tutoriálem :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Porovnejte si alternativy](comparison.md){ .md-button }

Alfa · Python 3.14+ · obyčejné katalogy PO/MO · žádné běhové závislosti
{ .home-facts }

Tento web praktikuje to, co dokumentuje: každá jazyková edice —
navigace, popisky i sestavovací report zohledňující množné číslo — se
vykresluje z katalogů PO pomocí
[samotného `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Je to pro vás? { #is-this-for-you }

**Sedne vám to dnes, pokud** vaše aplikace běží na Pythonu 3.14 nebo novějším;
už používáte gettext a Babel, nebo chcete jejich postup s PO/MO převzít; a
chcete syntaxi t-stringů s pojmenovanými zástupnými symboly, které se
kontrolují dřív, než se vykreslí.

**Zatím vám to nesedne, pokud** potřebujete Python 3.13 nebo starší; vyžadujete
stabilní pythonovské API — tohle je alfa a [specifikace](spec.md) je ta část,
která se usadila —; nebo pokud téměř všechen váš přeložitelný text žije
v šablonovacím jazyce, a ne v pythonovském zdroji.

Už katalogy máte? Fungují dál. `_("Hello {name}").format(name=name)` a
`tr(t"Hello {name}")` produkují týž msgid, takže stávající překlady přechod
přežijí — [Migrace](migration.md) provází celým přesunem.

## Co smí katalog říct { #what-the-catalog-may-say }

Katalog dostává kompletní zprávu `Hello {name}`. Překlad smí `{name}`
přeuspořádat nebo zopakovat a smí přepsat každé ostatní slovo kolem něj.
Nesmí zástupný symbol vypustit, vymyslet si nový, sahat skrz něj do vašich
objektů ani k němu připojit vlastní formátování.

To je celý ten slib: **překlad nemůže změnit strukturu zprávy, kterou
překládá.** Knihovna to kontroluje na vstupu — při kompilaci katalogů — a
znovu při vykreslování; rozbitý záznam, který se přesto dostane do produkce,
zaloguje varování a vykreslí zdrojovou zprávu, místo aby způsobil pád.

!!! note "gettext je pro vás novinka? Celý pracovní postup ve čtyřech větách"

    **gettext** je standardní způsob, jakým se software překládá, v Pythonu i
    daleko za ním. Váš kód označí přeložitelné zprávy; *extraktor* je posbírá
    do souboru šablony (`.pot`); překladatel — obvykle nikoli programátor —
    vyplní jeden katalogový soubor (`.po`) na jazyk, který se zkompiluje do
    binárního `.mo`, jejž vaše aplikace načítá za běhu. Konvenční jméno
    překládací funkce je `_`, takže `_(t"Hello {name}")` se čte jako „přelož
    tuto zprávu“. **[Tutoriál](tutorial.md)** projde celou cestu — označit,
    extrahovat, přeložit, zkompilovat, spustit — přibližně za pět minut.

## Problém, který řeší { #the-problem-it-solves }

F-string je v okamžiku, kdy ho jakákoli knihovna uvidí, už interpolovaný —
z `f"Hello {name}"` se stalo `"Hello Ada"` a překládání útržků kolem hodnoty
láme gramatiku většiny jazyků. T-string ([PEP 750]) drží statický text,
vyhodnocené hodnoty, zdrojové výrazy, konverze a formátovací specifikace
odděleně — a to je přesně to rozdělení, které katalog zpráv potřebuje.
[Co to mění](comparison.md) ve srovnání s `%(name)s`, `.format()` a
`$`-stringy.

Nic v gettextu ani v Babelu ovšem neříká, jak se t-string stane zprávou. Tato
knihovna tu volbu činí, zapisuje ji jako [verzovanou specifikaci](spec.md) a
dodává [sadu testů konformity](spec.md#conformance), která ji ověřuje.

## Návrhová pravidla { #the-design-rules }

- Překládat kompletní zprávy, nikdy útržky vět.
- Přijímat jen jednoduchá jména proměnných, jako je `{name}`.
- Držet `!r` a `:.2f` pod kontrolou aplikace, mimo katalog.
- Nechat překlady přeuspořádávat a opakovat známé zástupné symboly, ale
  zabránit jim v tom, aby sahaly na atributy nebo přidávaly formátování.
- Používat obyčejné soubory POT, PO a MO a nástroje, které je už umějí číst.

A k tomu odpovídající seznam toho, co záměrně nechává na pokoji: nelokalizuje
čísla, měny ani data — [naformátujte je nejdřív](guide.md#locale-aware-values)
Babelem; neescapuje vykreslený výstup pro HTML, shell ani terminál; a neumí
posoudit, zda je překlad *správný*, jen zda jsou jeho zástupné symboly
nedotčené.

## Instalace { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 nebo novější. **Vykreslování nemá žádné závislosti** — používá
`gettext` ze standardní knihovny a nic jiného.

Extrakce a validace katalogů běží přes [Babel], nainstalujte tedy toto extra
všude, kde běží `pybabel`, což je obvykle vývojové nebo CI prostředí, nikoli
produkční obraz:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Kam dál { #where-to-go-next }

**Začněte tady** — bez předpokladu zkušeností s gettextem:

<div class="grid cards" markdown>

- **[Tutoriál](tutorial.md)** — od prázdného adresáře k běžícímu japonskému
  překladu v pěti krocích, každý příkaz ukázaný i s výstupem.
- **[Proč t-stringy](comparison.md)** — tatáž zpráva zapsaná čtyřmi způsoby a
  to, co `%(name)s`, `.format()` a `$`-stringy každý předávají katalogu.

</div>

**Používejte to** — pracovní reference:

<div class="grid cards" markdown>

- **[Průvodce](guide.md)** — běhové API: který vstupní bod použít, množná
  čísla, jazyky podle požadavku, odložené řetězce a co se stane, když je
  katalog špatně.
- **[Extrakce](extraction.md)** — reference `pybabel`: konfigurace, vlastní
  jména funkcí a to, jak existující nástroje validují tyto katalogy zdarma.
- **[V produkci](workflow.md)** — smyčka tak, jak ji provozuje tým: cyklus
  aktualizací, fuzzy záznamy, brány v CI, překladatelské platformy a nasazení.
- **[Migrace](migration.md)** — zavádění v projektu, který už katalogy má,
  jedno místo volání po druhém.
- **[Pro překladatele](translators.md)** — jediná stránka, kterou předáte
  tomu, kdo upravuje soubory `.po`.

</div>

**Porozumějte tomu** — od historie k implementaci:

<div class="grid cards" markdown>

- **[Pozadí](background.md)** — proč tato knihovna existuje: třicet let
  gettextu, dva PEPy a diskuse o standardní knihovně uzavřená bez odpovědi.
- **[Úskalí](pitfalls.md)** — co se při překladu tohoto webu do pětatřiceti
  jazyků skutečně rozbilo a kterou půlku z toho nástroj zachytí.
- **[Jak to funguje](internals.md)** — od objektu šablony z PEP 750 po
  vykreslený řetězec a keše, díky nimž je kontrola levná.

</div>

**Reference** — kontrakty:

<div class="grid cards" markdown>

- **[API](api.md)** — všechno, co balíček exportuje, na jedné stránce.
- **[Specifikace](spec.md)** — konvence t-string ↔ msgid jako stabilní,
  verzovaný kontrakt se strojově čitelnou sadou testů konformity.

</div>

## Stav { #status }

| | |
| --- | --- |
| Verze balíčku | 0.1.0a7 |
| Stabilita API | alfa — pythonovské API se ještě může měnit |
| [Specifikace](spec.md) | v1, se [sadou testů konformity](spec.md#conformance) |
| Python | 3.14 a novější; testováno na 3.14, 3.14t (free-threaded) a 3.15 |
| Babel | 2.18 nebo novější, a jen tam, kde běží `pybabel` |
| Běhové závislosti | žádné — `gettext` ze standardní knihovny |
| Formát katalogu | běžné POT, PO a MO |
| Změny | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

Alfa. Kontrakt je záměrně malý a [specifikace](spec.md) je jeho stabilní
částí; pythonovské API se ještě může hýbat. Před stabilním vydáním to
potřebuje širší jazykové fixtury, soustavné sledování výkonu, revizi API od
lidí, kteří gettext a Babel používají doopravdy, a testy kompatibility napříč
všemi podporovanými verzemi Pythonu a Babelu.

[Issues a pull requesty](https://github.com/yhay81/gettext-tstrings/issues)
jsou vítány — alfa je přesně ta chvíle, kdy se o rozhraní ještě vyplatí
přít.

## Přidejte se ke komunitě { #join-the-community }

- Vyberte si
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  jako ohraničený první příspěvek.
- Ptejte se na použití v
  [diskusích Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Přineste produkční pracovní postupy s gettextem a nápady na API do
  [diskusí Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Přečtěte si
  [průvodce přispěvatele](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md),
  než otevřete pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
