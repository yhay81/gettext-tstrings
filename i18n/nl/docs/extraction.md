---
description: "t-string-berichten extraheren met pybabel, en hoe msgfmt en de meegeleverde Babel-checker de catalogi valideren."
---

# Extractie

Extractie is de stap die elk gemarkeerd bericht uit je broncode verzamelt in
een `.pot`-sjabloon voor vertalers — stap 3 van de lus uit de
[tutorial](tutorial.md). Deze pagina is de referentie voor die stap:
configuratie, eigen functienamen, strikte CI-modus, en de controles die je
catalogi daarna bewaken.

Extractie heeft de `babel`-extra nodig:

```console
python -m pip install "gettext-tstrings[babel]"
```

## De workflow { #the-workflow }

Maak `babel.cfg` aan:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Gebruik vervolgens de gewone Babel-commando's:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` draait één keer per taal; daarna vouwt `pybabel update` elk vers
sjabloon in de bestaande catalogi. Die terugkerende cyclus — en wat zijn
`fuzzy`-entries voor een release betekenen — wordt doorgelopen in
[In productie](workflow.md#the-cycle-after-the-first-translation).

De `gettext_tstrings`-extractor verwerkt ook gewone `_()`-, `gettext()`- en
`ngettext()`-aanroepen, zodat één mapping een gemengde codebase dekt. Hij
herkent `_()`, de vier standaard gettext-namen, de `tr()`- / `ntr()`-aliassen
en de uitgestelde `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` is niet optioneel"

    `pybabel extract` verzamelt vertalerscommentaren alleen wanneer je
    `-c "Translators:"` meegeeft, precies zoals bij gewone gettext-aanroepen.

## Je eigen functienamen registreren { #registering-your-own-function-names }

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

Een ini-bestand geeft één string, een TOML-mapping geeft een lijst, en binnen
een string scheiden witruimte of komma's de namen. Alle vier de spellingen
werken.

De opties zijn `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` en `npgettext_functions`.

!!! danger "`-k` bereikt een t-string niet"

    Een eigen helper zoals `mytr(t"…")` moet in een van de bovenstaande
    opties worden benoemd. Babels `--keyword`-machinerie kan een
    t-string-literal niet lezen, dus `pybabel extract -k mytr` vindt niets en
    zegt niets — de berichten ontbreken simpelweg in de POT. `-k` blijft
    werken voor de gewone gettext-aanroepen die ernaast worden geëxtraheerd.

    Alleen de standaard argumentvolgorde wordt ondersteund: bericht eerst,
    context dan bericht voor `pgettext`, context dan enkelvoud dan meervoud
    voor `npgettext`.

## Robuust als standaard { #robust-by-default }

Eén slecht bestand beëindigt de run niet:

- Een t-string die de extractor afwijst — attribuuttoegang, een expressie,
  een verkeerd argument — wordt als waarschuwing gerapporteerd en
  overgeslagen.
- Een bestand dat niet parseert wordt op dezelfde manier overgeslagen.
- Net als een bestand dat alleen `tokenize` weigert terwijl `ast` het
  accepteert, waarop Babels eigen doorloop anders zou afbreken.

Zet `strict = true` in de mapping-opties om elk van die gevallen in een harde
fout te veranderen, wat je in CI wilt.

## Je bestaande toolchain valideert deze catalogi { #your-existing-toolchain-validates-these-catalogs }

Babel markeert elk geëxtraheerd bericht met een standaardvlag, en die ene
regel is wat placeholdercontrole activeert in de tools die je al draait:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Vertaal het als `こんにちは {nombre}` en de fout wordt zonder enige
configuratie gevangen:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate documenteert dezelfde controle als
[Python brace format][weblate-checks], en de commerciële platforms hebben hun
eigen placeholder-QA op dezelfde vlag. Hun gedrag is het hunne; de twee tools
hieronder zijn degene die hier geverifieerd zijn.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Daarbovenop registreert het pakket een Babel-**checker**, zodat
`pybabel compile` de regels van de specificatie toepast op elk bericht dat
het markeringscommentaar `gettext-tstrings` draagt:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Voor een meervoudsbericht benoemt de aanwijzer de vorm, omdat het
regelnummer dat Babel rapporteert dat van de msgid is en een Russisch blok er
drie `msgstr` onder heeft staan:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` schrijft de `.mo` toch"

    De fout hierboven wordt gerapporteerd, de exitstatus is `1` — en de
    kapotte catalogus wordt evengoed gecompileerd. Alleen die exitstatus kan
    een pipeline tegenhouden hem uit te leveren;
    [Wat CI bewaakt](workflow.md#what-ci-gates) toont de buildstap die dat
    laat gebeuren.

De twee controles zijn niet redundant. De meegeleverde checker is op minstens
twee plekken de striktere partij:

- Een msgid waarvan de enige accolades geëscaped zijn (`Config {{raw}} only`)
  krijgt nooit de vlag `python-brace-format`, dus geen enkele externe tool
  valideert hem überhaupt.
- Meervoudsvormen worden één voor één gecontroleerd.
  `msgfmt --check-format` leest precies dat bestand hierboven en eindigt met
  `0`; een vorm die een placeholder laat vallen die zijn broers behouden,
  wordt daar geaccepteerd en hier afgewezen.

`msgfmt` controleert alleen placeholdernamen die het als Python-brace-format
kan parseren, dus ASCII-namen houden elke tool in de keten in staat het
bericht te valideren. De bibliotheek zelf accepteert elke
`str.isidentifier()`-naam.

## Sjablonen en andere tools { #templates-and-other-tools }

t-strings zijn Python-syntaxis, dus deze bibliotheek dekt Python-broncode.
Sjabloontalen blijven hun eigen i18n gebruiken — Jinja2's `{% trans %}`,
Django's template-tags — en Babels extractors daarvoor. Alles voedt dezelfde
PO-catalogus, dus één vertaalworkflow dekt nog steeds een gemengde codebase.

`pygettext` kan vandaag geen t-strings parseren, en daarom loopt extractie
via Babel. De conventie is vastgelegd in de [specificatie](spec.md), zodat
een andere extractor, of een toekomstige `pygettext`, haar kan
implementeren.
