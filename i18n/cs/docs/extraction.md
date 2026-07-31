---
description: "Extrakce zpráv z t-stringů pomocí pybabel a jak msgfmt a přibalený checker pro Babel validují katalogy."
---

# Extrakce

Extrakce je krok, který posbírá každou označenou zprávu z vašeho zdrojového
kódu do šablony `.pot` pro překladatele — krok 3 smyčky z
[tutoriálu](tutorial.md). Tato stránka je referencí pro tento krok:
konfigurace, vlastní jména funkcí, striktní režim pro CI a kontroly, které
potom hlídají vaše katalogy.

Extrakce potřebuje extra `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Pracovní postup { #the-workflow }

Vytvořte `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Pak používejte běžné příkazy Babelu:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` se spouští jednou pro každý jazyk; potom `pybabel update` začlení
každou čerstvou šablonu do existujících katalogů. Tímto opakujícím se
cyklem — a tím, co jeho záznamy `fuzzy` znamenají pro vydání — provází
[V produkci](workflow.md#the-cycle-after-the-first-translation).

Extraktor `gettext_tstrings` zpracovává i běžná volání `_()`, `gettext()` a
`ngettext()`, takže jedno mapování pokryje smíšenou kódovou základnu.
Rozpoznává `_()`, čtyři standardní gettextová jména, aliasy `tr()` / `ntr()`
a odložené `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` není volitelné"

    `pybabel extract` sbírá komentáře pro překladatele jen tehdy, když
    předáte `-c "Translators:"`, přesně tak jako u běžných volání gettextu.

## Registrace vlastních jmen funkcí { #registering-your-own-function-names }

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    tr_functions = tr translate
    ntr_functions = ntr
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    tr_functions = ["tr", "translate"]
    ntr_functions = ["ntr"]
    ```

Soubor ini udává jeden řetězec, mapování v TOML udává seznam a uvnitř
řetězce oddělují jména buď bílé znaky, nebo čárky. Všechny čtyři zápisy
fungují.

Dostupné volby jsou `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` a `npgettext_functions`.

!!! danger "`-k` na t-string nedosáhne"

    Vlastní pomocná funkce jako `mytr(t"…")` musí být uvedena v jedné z voleb
    výše. Mechanismus `--keyword` Babelu neumí přečíst literál t-stringu,
    takže `pybabel extract -k mytr` nic nenajde a nic neřekne — zprávy v POT
    prostě chybějí. `-k` dál funguje pro běžná volání gettextu extrahovaná
    vedle nich.

    Podporováno je jen standardní pořadí argumentů: nejprve zpráva, kontext
    a pak zpráva u `pgettext`, kontext, jednotné číslo a pak množné číslo u
    `npgettext`.

## Ve výchozím stavu odolný { #robust-by-default }

Jeden špatný soubor neukončí celý běh:

- T-string, který extraktor odmítne — přístup k atributu, výraz, špatný
  argument — je nahlášen jako varování a přeskočen.
- Soubor, který nejde naparsovat, je přeskočen stejně.
- A stejně tak soubor, který odmítá jen `tokenize`, zatímco `ast` ho
  přijímá — na něm by se vlastní průchod Babelu jinak přerušil.

Nastavte ve volbách mapování `strict = true`, aby se každý z těchto případů
změnil v tvrdé selhání — což je přesně to, co chcete v CI.

## Vaše stávající sada nástrojů validuje tyto katalogy { #your-existing-toolchain-validates-these-catalogs }

Babel označí každou extrahovanou zprávu standardním příznakem a právě tato
jediná řádka aktivuje kontrolu zástupných symbolů v nástrojích, které už
spouštíte:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Přeložte ji jako `こんにちは {nombre}` a chyba je odhalena bez jakékoli
konfigurace:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate dokumentuje tutéž kontrolu jako
[Python brace format][weblate-checks] a komerční platformy mají vlastní QA
zástupných symbolů navázané na tentýž příznak. Jejich chování je jejich
věcí; dva nástroje níže jsou ty, které jsou ověřeny zde.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Balíček navíc registruje **checker** pro Babel, takže `pybabel compile`
uplatní pravidla specifikace na každou zprávu nesoucí značkovací komentář
`gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

U zprávy v množném čísle ukazatel jmenuje konkrétní tvar, protože číslo
řádku, které Babel hlásí, patří msgid a ruský blok má pod ním tři `msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` přesto zapíše `.mo`"

    Chyba výše je nahlášena, návratový kód je `1` — a poškozený katalog se
    přesto zkompiluje. Jen tento návratový kód může zabránit pipeline v jeho
    vydání; [Co hlídá CI](workflow.md#what-ci-gates) ukazuje krok sestavení,
    který mu to umožní.

Ty dvě kontroly nejsou nadbytečné. Dodaný checker je přísnější stranou
přinejmenším na dvou místech:

- Msgid, jehož jediné složené závorky jsou escapované (`Config {{raw}}
  only`), nikdy nedostane příznak `python-brace-format`, takže ho žádný
  externí nástroj vůbec nevaliduje.
- Množné tvary se kontrolují jeden po druhém. `msgfmt --check-format` přečte
  přesně soubor výše a skončí s kódem `0`; tvar, který ztratí zástupný
  symbol, jejž jeho sourozenci zachovávají, je tam přijat a zde odmítnut.

`msgfmt` kontroluje jen jména zástupných symbolů, která dokáže naparsovat
jako pythonovský brace format, takže jména v ASCII udržují každý nástroj v
řetězci schopný zprávu validovat. Samotná knihovna přijímá jakékoli jméno
splňující `str.isidentifier()`.

## Šablony a další nástroje { #templates-and-other-tools }

T-stringy jsou syntaxe Pythonu, takže tato knihovna pokrývá pythonovské
zdroje. Šablonovací jazyky dál používají vlastní i18n — `{% trans %}` u
Jinja2, šablonové tagy Django — a extraktory Babelu pro ně. Vše plní tentýž
katalog PO, takže jeden překladový postup stále pokrývá smíšenou kódovou
základnu.

`pygettext` dnes t-stringy naparsovat neumí, a proto extrakce vede přes
Babel. Konvence je sepsána ve [specifikaci](spec.md), aby se na ni mohl
zaměřit jiný extraktor nebo budoucí `pygettext`.
