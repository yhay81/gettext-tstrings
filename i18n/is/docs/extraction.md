---
description: "Að draga t-string-skilaboð út með pybabel, og hvernig msgfmt og meðfylgjandi Babel-athugari staðfesta þýðingaskrárnar."
---

# Útdráttur

Útdráttur er skrefið sem safnar hverjum merktum skilaboðum úr frumkóðanum
þínum í `.pot`-sniðmát fyrir þýðendur — skref 3 í hringrás
[kennsluefnisins](tutorial.md). Þessi síða er uppflettiritið um það skref:
stillingar, eigin fallanöfn, strangur CI-hamur og athuganirnar sem gæta
þýðingaskránna þinna á eftir.

Útdráttur þarf `babel`-aukapakkann:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Hringrásin { #the-workflow }

Búðu til `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Notaðu svo venjulegu Babel-skipanirnar:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` keyrir einu sinni fyrir hvert tungumál; eftir það fellir
`pybabel update` hvert nýtt sniðmát inn í þýðingaskrárnar sem fyrir eru. Það
endurtekna ferli — og hvað `fuzzy`-færslur þess þýða fyrir útgáfu — er gengið
gegnum í [Í rekstri](workflow.md#the-cycle-after-the-first-translation).

Útdráttartólið `gettext_tstrings` ræður líka við venjuleg köll á `_()`,
`gettext()` og `ngettext()`, svo ein vörpun dugar fyrir blandaðan kóðagrunn.
Það þekkir `_()`, gettext-nöfnin fjögur, samheitin `tr()` / `ntr()` og
frestuðu `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "`-c` er ekki valfrjálst"

    `pybabel extract` safnar athugasemdum til þýðenda aðeins þegar þú gefur
    `-c "Translators:"`, nákvæmlega eins og það gerir fyrir venjuleg
    gettext-köll.

## Að skrá þín eigin fallanöfn { #registering-your-own-function-names }

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

Ini-skrá gefur einn streng, TOML-vörpun gefur lista, og innan strengs skilja
annaðhvort bil eða kommur nöfnin að. Allar fjórar ritmyndirnar virka.

Valkostirnir eru `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` og `npgettext_functions`.

!!! danger "`-k` nær ekki til t-strengs"

    Eigin hjálparfall á borð við `mytr(t"…")` verður að nefna í einum
    valkostanna hér að ofan. `--keyword`-vélbúnaður Babel getur ekki lesið
    t-strengsfasta, svo `pybabel extract -k mytr` finnur ekkert og segir
    ekkert — skilaboðin eru einfaldlega fjarverandi úr POT-skránni. `-k`
    virkar áfram fyrir venjulegu gettext-köllin sem eru dregin út samhliða.

    Aðeins staðlaða viðfangaröðin er studd: skilaboð fyrst, samhengi og svo
    skilaboð fyrir `pgettext`, samhengi og svo eintala og svo fleirtala
    fyrir `npgettext`.

## Þolið sjálfgefið { #robust-by-default }

Ein léleg skrá bindur ekki enda á keyrsluna:

- t-strengur sem útdráttartólið hafnar — aðgangur að eigindi, segð, rangt
  viðfang — er tilkynntur sem viðvörun og honum sleppt.
- Skrá sem lætur ekki þátta sig fær sömu meðferð.
- Sömuleiðis skrá sem aðeins `tokenize` hafnar meðan `ast` tekur við henni,
  en á henni myndi eigin yfirferð Babel annars stöðvast.

Settu `strict = true` í valkosti vörpunarinnar til að breyta hverju og einu
þessara í harða bilun í staðinn, sem er það sem þú vilt í CI.

## Tólakeðjan sem þú átt fyrir staðfestir þessar þýðingaskrár { #your-existing-toolchain-validates-these-catalogs }

Babel merkir hver útdregin skilaboð með stöðluðu flaggi, og sú eina lína er
það sem virkjar athugun staðgengla í tólunum sem þú keyrir nú þegar:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Þýddu það sem `こんにちは {nombre}` og mistökin nást án nokkurra stillinga:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate skjalfestir sömu athugun sem [Python brace format][weblate-checks], og
viðskiptavettvangarnir eru með sína eigin gæðaathugun á staðgenglum sem er
lyklað á sama flagg. Hegðun þeirra er þeirra mál; tólin tvö hér að neðan eru
þau sem hafa verið staðfest hér.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Ofan á það skráir pakkinn **athugara** hjá Babel, svo að `pybabel compile`
beitir reglum forskriftarinnar á hver þau skilaboð sem bera
`gettext-tstrings`-merkiathugasemdina:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Fyrir fleirtöluskilaboð nefnir vísirinn myndina, því línunúmerið sem Babel
tilkynnir er línunúmer msgid-sins og rússnesk blokk hefur þrjú `msgstr` þar
fyrir neðan:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` skrifar `.mo`-skrána eftir sem áður"

    Villan hér að ofan er tilkynnt, lokastaðan er `1` — og bilaða
    þýðingaskráin er vistþýdd hvort eð er. Aðeins sú lokastaða getur stöðvað
    keðju frá því að senda hana frá sér;
    [Hvað CI stöðvar](workflow.md#what-ci-gates) sýnir byggingarskrefið sem
    leyfir það.

Athuganirnar tvær eru ekki óþarfa endurtekning. Meðfylgjandi athugarinn er
strangari aðilinn á að minnsta kosti tveimur stöðum:

- Msgid þar sem einu slaufusvigarnir eru escape-ritaðir
  (`Config {{raw}} only`) fær aldrei `python-brace-format`-flaggið, svo að
  ekkert utanaðkomandi tól staðfestir það yfirleitt.
- Fleirtölumyndir eru athugaðar hver fyrir sig. `msgfmt --check-format` les
  einmitt skrána hér að ofan og lýkur með `0`; mynd sem sleppir staðgengli
  sem systkini hennar halda er samþykkt þar og hafnað hér.

`msgfmt` athugar aðeins nöfn staðgengla sem það getur þáttað sem
brace-snið Pythons, svo að ASCII-nöfn halda hverju tóli í keðjunni færu um að
staðfesta skilaboðin. Safnið sjálft tekur við hvaða nafni sem er þar sem
`str.isidentifier()` er satt.

## Sniðmát og önnur tól { #templates-and-other-tools }

t-strengir eru málskipan Pythons, svo þetta safn nær yfir Python-frumkóða.
Sniðmátsmál nota áfram sína eigin i18n — `{% trans %}` í Jinja2, sniðmátsmerki
Django — og útdráttartól Babel fyrir þau. Allt rennur í sömu PO-þýðingaskrána,
svo ein þýðingahringrás nær áfram yfir blandaðan kóðagrunn.

`pygettext` getur ekki þáttað t-strengi í dag, og þess vegna fer útdráttur
gegnum Babel. Venjan er skrifuð niður í [forskriftinni](spec.md) svo að annað
útdráttartól, eða `pygettext` framtíðarinnar, geti miðað við hana.
