---
description: "Překládejte kompletní zprávy z t-stringů přes gettext a Babel, s formátováním drženým mimo katalog."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Napište větu jednou.<br>Přeložte ji celou.

Bezpečná integrace gettextu a Babelu pro t-stringy Pythonu 3.14+ — hodnota
zůstává na svém místě a katalog vidí celou zprávu:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Začněte tutoriálem :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Proč t-stringy](comparison.md){ .md-button }

Tento web praktikuje to, co dokumentuje: každá jazyková edice —
navigace, popisky i sestavovací report zohledňující množné číslo — se
vykresluje z katalogů PO pomocí
[samotného `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalog dostává kompletní větu `Hello {name}`. Překlad smí `{name}`
přeuspořádat nebo zopakovat; nesmí ho vypustit, vymyslet si nový ani k němu
připojit vlastní formátování — tato knihovna to kontroluje a rozbitý katalog
se vrátí ke zdrojovému textu, místo aby způsobil pád.

!!! note "gettext je pro vás novinka? Celý pracovní postup ve čtyřech větách"

    **gettext** je standardní způsob, jakým se software překládá, v Pythonu i
    daleko za ním. Váš kód označí přeložitelné řetězce; *extraktor* je posbírá
    do souboru šablony (`.pot`); překladatel — obvykle nikoli programátor —
    vyplní jeden katalogový soubor (`.po`) na jazyk, který se zkompiluje do
    binárního `.mo`, jejž vaše aplikace načítá za běhu. Konvenční jméno
    překládací funkce je `_`, takže `_(t"Hello {name}")` se čte jako „přelož
    tuto větu“. **[Tutoriál](tutorial.md)** projde celou cestu — označit,
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

## Volba, kterou činí { #the-choice-it-makes }

- Překládat kompletní zprávy, nikdy útržky vět.
- Přijímat jen jednoduchá jména proměnných, jako je `{name}`.
- Držet `!r` a `:.2f` pod kontrolou aplikace, mimo katalog.
- Nechat překladatele přeuspořádávat a opakovat známé zástupné symboly — ale
  ne volat atributy a ne přidávat formátovací chování.
- Používat obyčejné soubory POT, PO a MO a nástroje, které je už umějí číst.

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

Přicházejí sem tři druhy čtenářů: někdo, kdo překládá svůj první program,
někdo, kdo zapojuje překlady do skutečného projektu, a někdo, kdo chce přesně
vědět, proč má tahle mašinerie právě takový tvar. Každý má svou cestu.

**Učím se to** — bez předpokladu zkušeností s gettextem:

<div class="grid cards" markdown>

- **[Tutoriál](tutorial.md)** — začněte tady: od prázdného adresáře k běžícímu
  japonskému překladu v pěti krocích, každý příkaz ukázaný i s výstupem.
- **[Proč t-stringy](comparison.md)** — tatáž zpráva zapsaná čtyřmi způsoby a
  to, co `%(name)s`, `.format()` a `$`-stringy každý předávají katalogu.
- **[Pozadí](background.md)** — proč tato knihovna existuje: třicet let
  gettextu, dva PEPy a diskuse o standardní knihovně uzavřená bez odpovědi.

</div>

**Používám to doopravdy** — pracovní reference:

<div class="grid cards" markdown>

- **[Průvodce](guide.md)** — běhové API: množná čísla, jazyky per požadavek,
  odložené řetězce a co se stane, když je katalog špatně.
- **[Extrakce](extraction.md)** — reference `pybabel`: konfigurace, vlastní
  jména funkcí a to, jak existující nástroje validují tyto katalogy zdarma.
- **[V produkci](workflow.md)** — smyčka tak, jak ji provozuje tým: cyklus
  aktualizací, fuzzy záznamy, brány v CI, překladatelské platformy a jazyky
  per požadavek ve webové aplikaci.
- **[API](api.md)** — všechno, co balíček exportuje, na jedné stránce.

</div>

**Chci tomu porozumět** — od principů k implementaci:

<div class="grid cards" markdown>

- **[Jak to funguje](internals.md)** — od objektu šablony z PEP 750 po
  vykreslený řetězec a keše, díky nimž je kontrola levná.
- **[Specifikace](spec.md)** — konvence t-string ↔ msgid jako stabilní,
  verzovaný kontrakt se strojově čitelnou sadou testů konformity.

</div>

## Stav { #status }

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
