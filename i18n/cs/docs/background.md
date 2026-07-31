---
description: "Třicet let gettextu, dva PEPy s odstupem deseti let a diskuse o standardní knihovně uzavřená jako „not planned“: proč tato knihovna existuje, s odkazy na zdroje."
---

# Pozadí

Tato knihovna leží v průsečíku dvou dlouhých příběhů — jednoho o tom, jak
se překládá software, a druhého o tom, jak Python interpoluje řetězce —
které se v roce 2025 konečně protnuly a pak uvízly přesně v bodě, kde byla
zapotřebí malá, pečlivá konvence. Tato stránka vypráví oba příběhy
s odkazy na zdroje, protože návrhová rozhodnutí na tomto webu se posuzují
snáze, když vidíte otázky, na které odpovídají.

## Ekosystém gettextu { #the-gettext-ecosystem }

[GNU gettext] je od poloviny 90. let způsobem, jak se překládá svobodný
software: označte řetězce v kódu, extrahujte je do šablony, dejte
překladatelům jeden soubor katalogu na jazyk, zkompilujte, načtěte za
běhu. Kolem této smyčky vyrostl celý ekosystém — editory PO, revizní
workflow a překladatelské platformy, které všechny mluví stejným
souborovým formátem — a Python už více než dvě desetiletí dodává ve
standardní knihovně [modul `gettext`][stdlib-gettext]. Běhová polovina
překladu nikdy nebyla problém.

Nevyřešenou polovinou vždy bylo, *jak vypadá řetězec v katalogu*. Zpráva
`%(name)s` vkládá překladatelům do rukou syntaxi printf, kterou jedno
smazané písmeno promění v pád na produkci; zpráva `.format()` dává
katalogu přístup k atributům živých objektů. ([Proč
t-stringy](comparison.md) probírá obojí, s předvedenými selháními.)
A f-stringy — syntaxe, kterou dnes většina pythonního kódu preferuje — se
nemohou účastnit vůbec: než je jakákoli knihovna spatří, jsou už hotovým
řetězcem. Lidé to přesto zkoušejí, a to dost často na to, aby issue
tracker Babelu tyto pokusy sbíral ([#594][babel-594], [#715][babel-715]);
selhání je strukturální, nejde o chybějící funkci.

## Dva PEPy, deset let od sebe { #two-peps-ten-years-apart }

V roce 2015 napsali Alyssa Coghlan a Nick Humrich [PEP 501], navrhující
interpolační šablony, jejichž první deklarovanou motivací bylo i18n —
„providing a cleaner syntax for i18n translation“, jak to formuluje sám
PEP. Návrh byl odložen, zčásti proto, že diskuse ukázala, že případ i18n
nese významné dodatečné komplikace, které jednodušší případy užití
neměly.

O deset let později [PEP 750] — od Jima Bakera, Guida van Rossuma, Paula
Everitta, Koudaie Aona, Lysandrose Nikolaoua a Davea Pecka — oživil tuto
myšlenku jako t-stringy, byl [přijat v dubnu 2025][sc-resolution] a vyšel
v [Pythonu 3.14][Python 3.14] v říjnu 2025. PEP 501 byl poté stažen v jeho
prospěch. Jeden detail je pro tuto stránku důležitý: i18n *nepatří* mezi
deklarované motivace PEP 750. PEP mechanismus zobecnil — typ šablony,
který může konzumovat libovolná knihovna — a nechal otázku překladu
přesně tam, kde ji PEP 501 před deseti lety zaparkoval: otevřenou.

Od Pythonu 3.14 tedy jazyk měl přesně tu datovou strukturu, kterou katalog
zpráv potřebuje, a žádnou konvenci, jak ji v této roli používat.

## Diskuse o standardní knihovně { #the-stdlib-discussion }

Dva měsíce před vydáním 3.14 navrhl Adrian Mönnich (ThiefMaster, správce
projektu Indico) uzavřít tuto mezeru přímo ve standardní knihovně: vlákno
[Support t-strings in gettext][discuss-thread] na discuss.python.org,
otevřené v srpnu 2025, přišlo s funkčním [pull requestem][cpython-pr]
přidávajícím podporu t-stringů jak do `gettext`, tak do `pygettext`.

Vlákno stojí za přečtení celé, protože vynáší na povrch každou těžkou
otázku, na kterou tato knihovna musela později odpovědět:

- **Čím smí interpolace být?** Pouze prostým jménem, nebo i atributy a
  voláními s odvozeným jménem zástupného symbolu? Každá odpověď směňuje
  pohodlí za stabilitu msgid a bezpečnost katalogu.
- **Co vyžadují tvary množného čísla,** když se systém množného čísla
  cílového jazyka liší od zdrojového?
- **Je gettext vůbec ten správný cíl?** Barry Warsaw — který během vývoje
  PEP 750 argumentoval, že t-stringy se pro i18n dobře nehodí — ukazoval
  na svůj [`flufl.i18n`][flufl-i18n] a jeho styl `$`-stringů jako
  přívětivější nástroj; jiní se přimlouvali za úplné opuštění gettextu ve
  prospěch novějších systémů, jako je [Fluent].
- **A metaotázka:** ať už standardní knihovna dodá cokoli, v podstatě to
  už nikdy nelze změnit. Konvence s tolika otevřenými volbami je riskantní
  věc na zmrazení na první pokus.

Konsenzus se nevytvořil. Issue v CPythonu bylo
[uzavřeno jako „not planned“][cpython-issue] a pull request byl uzavřen
bez sloučení v říjnu 2025, pár dní po vydání 3.14. Schopnost v jazyce
existovala; konvence neměla domov.

## Proč nejdřív balíček { #why-a-package-first }

To je mezera, kterou se tento projekt rozhodl vyplnit mimo standardní
knihovnu, na základě záměrné sázky: konvence dozrává rychleji tam, kde
může svobodně verzovat a získávat adopci případ od případu, a standardní
knihovna — která musí být správně napoprvé — je místem, kde by konvence
měla *skončit*, ne kde by se měla vypracovávat.

Konkrétně: každá sporná otázka z vlákna tu má sepsanou odpověď, každá na
vlastní stránce:

- Interpolace jsou **pouze prostá jména**, takže msgid zůstávají stabilní
  a smysluplná — [průvodce](guide.md#safety-and-scope) ukazuje pravidlo,
  [Jak to funguje](internals.md#from-template-to-msgid) jeho důvody.
- **Formátování zůstává zcela mimo katalog**
  ([Proč t-stringy](comparison.md)).
- **Množná čísla** se řídí pravidlem sjednocení a průniku, které dovoluje,
  aby se systém množného čísla cílového jazyka lišil od zdrojového
  ([spec §4](spec.md)).
- Poškozený katalog **se vrací ke zdrojovému textu, místo aby padal**,
  a dodržuje tak vlastní kontrakt gettextu
  ([průvodce](guide.md#what-happens-when-a-catalog-is-wrong)).
- A celá konvence je [verzovanou specifikací](spec.md) se strojově
  čitelnou sadou testů konformity — napsanou tak, aby ji jiná
  implementace, včetně budoucí implementace ve standardní knihovně, mohla
  převzít beze změn a spolupracovat s ní.

Diskuse neskončila a tento projekt je jejím účastníkem, nikoli verdiktem
nad ní. Máte-li produkční zkušenost s gettextem, která se těchto voleb
týká, [totéž vlákno][discuss-thread] a [Discussions][gh-discussions]
tohoto repozitáře jsou místa, kde se o nich vede spor.

## Časová osa { #timeline }

| Kdy | Co se stalo |
| --- | --- |
| polovina 90. let | GNU gettext ustavuje workflow PO/POT/MO, kterým překladatelé a platformy mluví dodnes. |
| 2015 | [PEP 501] navrhuje interpolační šablony s i18n jako první motivací; odložen. |
| 2016 | f-stringy vycházejí v Pythonu 3.6 — interpolace dostává svou syntaxi a překlad ji nemůže použít. |
| čvc 2024 | [PEP 750] navrhuje t-stringy. |
| dub 2025 | PEP 750 [přijat][sc-resolution]; PEP 501 stažen v jeho prospěch. |
| srp 2025 | Otevírá se vlákno [Support t-strings in gettext][discuss-thread], s [pull requestem][cpython-pr] pro stdlib. |
| říj 2025 | [Python 3.14] dodává t-stringy; issue ve stdlib se uzavírá jako [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` vychází jako alfa, se [spec v1](spec.md) a její sadou testů konformity. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
