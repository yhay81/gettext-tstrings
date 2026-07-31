---
description: "Zavedení t-stringů v projektu, který už gettextové katalogy má: co přežije bez dotyku, co zfuzzyví a jak se dá přesouvat jedno místo volání po druhém."
---

# Migrace

Pokud váš projekt gettext už používá, jsou otázky, které rozhodují o tom, zda
je tato knihovna přijatelná, poměrně úzké: znehodnotí katalogy, které máte,
umí koexistovat s kódem, který zatím měnit nechcete, a jak velká část přesunu
musí proběhnout naráz? Odpovědi, od nejkratší:

| Otázka | Odpověď |
| --- | --- |
| Fungují stávající soubory `.po` a `.mo` dál? | Ano. Tytéž soubory, tytéž nástroje. |
| Můžou stará a nová volání žít v jednom souboru? | Ano, a jedno mapování extraktoru pokryje obojí. |
| Změní se msgid? | Z `.format()` ne. Z `%`-formátu ano. |
| Musí se celý projekt přesunout naráz? | Ne. Jedno místo volání je platná změna. |
| A co Jinja, šablony Django, JavaScript? | Nedotčené, tytéž katalogy. |

Zbytek této stránky jsou podrobnosti ke každé z nich.

## Z `.format()`: msgid se nemění { #from-format-the-msgid-does-not-change }

Tohle je případ, kdy migrace nestojí téměř nic. Zpráva psaná přes `str.format`
a zpráva z t-stringu odvozují *týž* klíč katalogu, protože klíčem je tak jako
tak text s ponechaným `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Stávající překlad tedy zůstane připojený. Vyjdeme-li z katalogu, který
obsahuje

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

změňte volání, znovu extrahujte a aktualizujte:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Záznam, který se vrátí, se liší ve dvou řádcích metadat a v ničem jiném —
ve značkovacím komentáři, který jej označuje za zprávu z t-stringu, a v čísle
řádku ve zdroji:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Žádný příznak `fuzzy`, žádné překládání znovu, v žádném jazyce. Zpráva se
vykreslí okamžitě:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` katalogy nahlásí jako zastaralé"

    Onen značkovací komentář a posunutá čísla řádků stačí na to, aby
    `pybabel update --check` prohlásil katalog za potřebující přegenerovat —
    porovnává totiž celý záznam, nejen překlad. Spusťte skutečný
    `pybabel update` v témž commitu jako změnu kódu a katalogy s ní
    commitněte; je to tentýž návyk, jaký si žádá už
    [brána v CI](workflow.md#what-ci-gates).

## Z `%`-formátu: msgid se mění, takže překlady zfuzzyví { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Syntaxe printf žije *uvnitř* zprávy, takže její nahrazení přepíše klíč
katalogu. Nedá se to obejít a je to poctivá cena za opuštění `%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` rozpozná v nové zprávě blízkou příbuznou té odstraněné a
starý překlad přenese, označený jako fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

O tomto stavu je dobré vědět tři věci:

- **Za běhu se nic nerozbije.** Fuzzy záznamy jsou ze zkompilovaného `.mo`
  vyloučené, takže aplikace vykresluje zdrojovou zprávu, dokud dvojici
  nepotvrdí člověk — [tatáž degradace](workflow.md#the-cycle-after-the-first-translation),
  jakou prochází každá přeformulovaná zpráva.
- **CI zůstává zelené, dokud jsou fuzzy.** Checker zástupných symbolů fuzzy
  záznamy přeskakuje, přesně jako to dělá `msgfmt --check-format`, protože
  záznam, který se nemůže dostat do běhu, by neměl shazovat build. Jakmile
  překladatel příznak odstraní, kontroluje se záznam jako každý jiný — takže
  `%(name)s` ponechané v potvrzeném překladu se odhalí právě tehdy, tedy ve
  chvíli, kdy by se jinak začalo vykreslovat.
- **Starý příznak `python-format` jede s sebou** a měl by se smazat spolu
  s příznakem `fuzzy`, jinak bude `msgfmt --check-format` dál uplatňovat
  pravidla printf na zprávu ve formátu brace.

U pojmenovaných zástupných symbolů printf je úprava mechanická — `%(name)s`
se stane `{name}` a nic jiného se nehýbe —, takže velký katalog znamená
skriptovaný průchod a po něm revizi překladatele, nikoli překlad znovu.
Poziční `%s` mechanické není: nemá jméno, které by se dalo přenést, a jeho
volba je právě podstatou té změny.

Migrace tedy může postupovat tempem, jaké dovolí revize: nepřevedený fuzzy
záznam je viditelný kus práce v katalogu, ne rozbitý build.

## Stará a nová volání koexistují { #old-and-new-calls-coexist }

Extraktor, který čte t-stringy, čte i běžná volání gettextu, takže jedno
mapování pokryje soubor uprostřed migrace:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

```python
from gettext_tstrings import tr
from myapp.i18n import _

name = "Ada"
print(_("Save changes"))
print(tr(t"Hello {name}"))
```

Obě zprávy skončí v téže šabloně a jen ta z t-stringu nese značkovací
komentář, který zapíná kontroly navíc z této knihovny:

```po
#: app.py:5
msgid "Save changes"
msgstr ""

#. gettext-tstrings
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Rozpoznává `_()`, čtyři standardní gettextová jména, aliasy `tr()` / `ntr()`
a odložené `lazy_gettext()` / `lazy_pgettext()`. Vlastní pomocná funkce musí
být [uvedena v mapování](extraction.md#registering-your-own-function-names).

Za běhu jsou oba styly stejně nezávislé: `gettext.translation()` vrátí jeden
objekt s překlady a čtou z něj jak `_`, tak vstupní body této knihovny.

## Co se nehýbe { #what-does-not-move }

- **Šablonovací jazyky.** `{% trans %}` u Jinja2, šablonové tagy Django a
  jejich extraktory pro Babel fungují beze změny dál a dál plní tytéž
  katalogy PO. T-stringy jsou syntaxe Pythonu; platí pro pythonovské zdroje.
- **Vaše katalogové soubory.** Žádná změna formátu, žádný nový soubor, žádný
  krok konverze.
- **Vaše překladatelská platforma.** Výměna přes `.po` je identická a příznak
  `python-brace-format`, který zpráva z t-stringu nese, je tentýž příznak,
  jaký nese zpráva z `.format()` — takže QA zástupných symbolů funguje dál.
- **Kód mimo Python.** Katalog pro JavaScript nebo C v témž projektu zůstává
  nedotčen.

## Kontrolní seznam migrace { #a-migration-checklist }

1. Přidejte extra `babel` tam, kde běží `pybabel`, a v `babel.cfg` změňte
   mapování `python` na metodu `gettext_tstrings` — jedno mapování pak
   pokrývá oba styly a `-k` u běžných volání funguje dál.
2. Převeďte nejdřív místa volání s `.format()`. Znovu extrahujte, spusťte
   `pybabel update` a katalogy commitněte spolu s kódem; žádné fuzzy záznamy
   nečekejte.
3. Převádějte místa volání s `%`-formátem po dávkách, které dokážete nechat
   zrevidovat, přepisujte přenesené zástupné symboly a mažte příznaky `fuzzy`
   a `python-format`.
4. Opravte to, co omezení odmítne: interpolace musí být prosté jméno, takže
   z `t"Hello {user.name}"` se nejdřív musí stát lokální proměnná. Je to
   úprava v místě volání, ne v katalogu.
5. Jakmile je průchod hotový, zapněte ve volbách mapování `strict = true`,
   aby zpráva, kterou nelze extrahovat, shodila
   [build](extraction.md#lenient-locally-strict-in-ci), místo aby ze šablony
   zmizela.
6. Přidejte běhovou kontrolu z [V produkci](workflow.md#what-ci-gates):
   vykreslete jednu zprávu za každý dodávaný jazyk přes striktní
   `Translator`.

Kroky 2 a 3 jsou obyčejné commity. Nic v tomto seznamu nepotřebuje den `D`.
