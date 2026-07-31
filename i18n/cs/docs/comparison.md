---
description: "Tatáž přeložitelná zpráva zapsaná pomocí %-formátu, .format(), $-stringů flufl.i18n a t-stringu, včetně toho, jak každý z nich váže hodnoty a jak zachází s poškozeným katalogem."
---

# Proč t-stringy

Čtyři způsoby, jak vložit hodnotu do přeložitelné zprávy, porovnané na téže
větě. Stručná verze:

- U **%-formátu** se jedno písmeno smazané překladatelem stane pádem
  v produkci.
- U **str.format** může překlad číst atributy objektů, které váš kód
  předává — včetně tajemství.
- U **$-stringů** (flufl.i18n) se hodnoty berou implicitně z proměnných
  volající funkce a tečkované zástupné symboly dosáhnou i na atributy.
- U **t-stringů** zůstává formátování ve vašem kódu, překlady se kontrolují
  za běhu a poškozený katalog se vrátí ke zdrojovému textu, místo aby
  způsobil pád.

Zbytek této stránky jsou důkazy, metoda po metodě.

!!! note "Každé přeložené zprávy se dotýkají tři strany"

    **Katalog** je soubor s překlady — `.po`, dokud jej upravují lidé,
    zkompilovaný do `.mo`, který načítá aplikace ([tutoriál](tutorial.md)
    projde oběma). Každé zprávy se dotýkají tři strany: **vývojář** píše
    zdrojový řetězec, **překladatel** upravuje katalog — často na externí
    platformě, daleko od jakéhokoli code review — a **aplikace** obojí
    vykresluje dohromady za běhu. Každý styl formátování níže odpovídá na
    tutéž otázku jinak: *jak velkou část formátovacího jazyka smí katalog
    ovládat?* V příkladech je `_` konvenční jméno překládací funkce a `tr`
    je jméno z této knihovny.

## %-formát { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Co se může pokazit: jedno smazané písmeno v překladu shodí vykreslení.

Řetězec v katalogu nese syntaxi printf, včetně koncového písmene typu —
`s` v `%(name)s` — které lze snadno přehlédnout a snadno poškodit:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Jednoznaková úprava v PO editoru se stane tracebackem v produkci. GNU
`msgfmt --check-format` to sice zachytí, ale jen u zpráv označených
příznakem `python-format`, a jen pokud katalog na cestě do vaší aplikace
skutečně projde přes msgfmt.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Odstraňuje koncové písmeno typu a zachovává pojmenovaný, volně
přeuspořádatelný zástupný symbol. To, co se může pokazit, se přesouvá na
druhou stranu výměny: překlad získává moc nad vašimi objekty.

`str.format` je malý výrazový jazyk a jeho zavolání na řetězci znamená
předat tomu řetězci právo jej použít:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Teď ty literální řetězce nahraďte tím, co vrací `_()`. Pokud se překlad
`Hello {name}` vrátí jako `{conf.api_key}`, jeho vykreslení vypíše váš
API klíč — o tom, co se přečetlo, rozhodl katalog, ne váš kód. Katalog
není kód, ale cestuje jako data: na překladatelskou platformu, přes mnoho
rukou, zpět jako `.po`, zkompilovaný do `.mo`, někdy dodaný zcela zvnějšku
vašeho projektu. `.format()` dává každému kroku této cesty přístup
k atributům objektů, které předáváte.

## `$`-stringy a flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Standardní knihovna v [`string.Template`][stdlib-template] poskytuje
interpolační jazyk `$name`, sama však není překladovým API.
[`flufl.i18n`][flufl-i18n] tento styl kombinuje s vyhledáváním v katalozích
gettext. Všimněte si, že hodnota se nikdy nepředává: flufl.i18n sestavuje
substituční prostor jmen z globálních a lokálních proměnných volajícího —
zprávě jsou dostupné všechny proměnné existující v místě volání. Volitelné
mapování `extras` má přednost před oběma. Syntaxe, kterou vidí překladatel,
nemá koncové písmeno typu ani formátovací specifikátor a zástupné symboly
zůstávají volně přeuspořádatelné.

Nedostupná substituce nevyvolá výjimku. Při `name = "Ada"` a bez `nombre`
v prostoru jmen volajícího se katalogový překlad `Hello $nombre` vykreslí
jako `Hello $nombre`: nevyřešený zástupný symbol zůstane viditelný. Toto
[dokumentované chování][documented behavior] zachová zbytek přeložené
zprávy, místo aby volání selhalo. Výjimky vyvolané při řešení atributu
nebo převodu hodnoty se stále mohou šířit dál.

`flufl.i18n` je v jednom podstatném ohledu schopnější než holý
`string.Template`. Jeho [vlastní Template][custom Template] přijímá
tečkované zástupné symboly, jako je `$settings.api_key`, a jeho
[translator][translator] tyto cesty řeší vůči hodnotám volajícího.
Přeložený zástupný symbol může pojmenovat kteroukoli dostupnou lokální
nebo globální proměnnou volajícího a tečkovanou syntaxí procházet její
atributy. To je pohodlné, když zpráva potřebuje atribut, zároveň to však
činí rámec volajícího součástí substitučního prostoru katalogu. Srovnání
níže popisuje `flufl.i18n` 6.0.0, nikoli každé možné použití
`string.Template`.

## t-stringy { #t-strings }

```python
tr(t"Hello {name}")
```

Katalog stále vidí `Hello {name}` a zůstává obyčejným katalogem PO/MO.
Rozdíl je v tom, co překlad *smí říct* a kdo to kontroluje.

Tato knihovna validuje každý překlad vůči zástupným symbolům zdrojové
zprávy před vykreslením a přijímá holá jména — a nic jiného. Vůči
`t"Hello {name}"`:

| Překlad obsahující | je odmítnut se zprávou |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Odmítnutý neznamená spadlý: ve výchozím nastavení knihovna zaloguje
varování a vykreslí zdrojový text, takže špatný katalog nikdy nepoloží
aplikaci —
[tentýž kontrakt, který dodržuje sám gettext](guide.md#what-happens-when-a-catalog-is-wrong).

Formátování zůstává tam, kde bylo napsáno, v kódu:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` se do katalogu nikdy nedostane, takže jej žádný překlad nemůže
změnit a žádný překladatel se na něj nemusí dívat.

Ještě jeden rozdíl jsou nástroje: t-stringy jsou nová syntaxe, takže
jejich extrakce do `.pot` v současnosti vyžaduje extraktor, který
t-stringům rozumí, například ten, který tento balíček
[poskytuje pro Babel](extraction.md).

## Vedle sebe { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Je zástupný symbol pojmenovaný? | ano | ano | ano | ano |
| Může překladatel zástupné symboly přeuspořádat? | ano | ano | ano | ano |
| Odkud pocházejí hodnoty? | explicitní mapování | explicitní argumenty | lokální a globální proměnné volajícího, plus volitelné `extras` | hodnoty zachycené uvnitř t-stringu |
| Může katalog změnit způsob formátování hodnoty? | ano | ano | ne | ne |
| Může katalog sahat do objektů (přístup k atributům)? | ne | ano | ano, tečkovanými jmény | ne |
| Překlad zástupný symbol *vypustí* — co se vykreslí? | hodnota tiše zmizí | hodnota tiše zmizí | hodnota tiše zmizí | zdrojový text, s varováním ([ve výchozím nastavení](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Překlad *přidá* neznámý zástupný symbol — co se vykreslí? | výjimka | výjimka | zástupný symbol zůstane viditelný jako text | zdrojový text, s varováním ([ve výchozím nastavení](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Kontrolují se zástupné symboly při vykreslování? | ne | ne | ne | ano (viz níže) |
| Jaký PO příznak odvodí Babel, aby existující nástroje validovaly? | `python-format` | `python-brace-format` | žádný | `python-brace-format` |
| Používá obyčejné katalogy PO/MO? | ano | ano | ano | ano |
| Potřebuje vlastní extraktor zdrojů? | ne | ne | ne | ano, zatím |

Ke kontrole při vykreslování: zprávy v jednotném čísle se kontrolují na
přesnou shodu zástupných symbolů. Zprávy v množném čísle také — vůči
[pravidlu sjednocení a průniku](spec.md), které dovoluje, aby se tvary
množného čísla cílového jazyka lišily od zdrojových; přísnější kontrola
po jednotlivých tvarech běží při kompilaci katalogů
([Extrakce](extraction.md)).

Řádek o formátovacím příznaku se týká validace znalé zástupných symbolů,
nikoli kompatibility katalogů. `žádný` znamená, že standardní nástroje
gettext zprávu stále přečtou a zkompilují, ale `msgfmt --check-format`
nemá žádnou gramatiku `$`-symbolů, kterou by mohl uplatnit.

## Co to stojí { #what-it-costs }

F-string se takto použít vůbec nedá — než jej jakákoli knihovna uvidí, je
už hotovým řetězcem, takže jeho překlad znamená překládat fragment.
T-stringy ([PEP 750]) drží statický text a hodnoty odděleně a přitom
zachovávají syntaxi podobnou f-stringům a explicitní vázání hodnot.
`$`-stringy už dnes nabízejí stručnou alternativu s jiným modelem vázání
a selhání. `flufl.i18n` je zralý balíček běžící na Pythonu 3.10 a novějším;
`gettext-tstrings` je v současnosti alfa, a protože t-stringy jsou nová
syntaxe, vyžaduje Python 3.14 nebo novější.

Druhou cenou je samo omezení: interpolace musí být prosté jméno.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

To je skutečné omezení. Spolu s vázáním hodnot na straně zdroje a
kontrolou zástupných symbolů za běhu brání tomu, aby řetězce z katalogu
vyhodnocovaly výrazy, a udržuje jména zástupných symbolů smysluplná.

Jak Python dospěl k této křižovatce — dva PEPy s odstupem deseti let a
diskuse o standardní knihovně uzavřená bez odpovědi — vypráví s prameny
stránka [Pozadí](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
