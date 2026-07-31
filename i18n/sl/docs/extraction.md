---
description: "Ekstrakcija sporočil iz t-nizov s pybabelom in kako msgfmt ter priloženi Babelov preverjevalnik preverita kataloge."
---

# Ekstrakcija

Ekstrakcija je korak, ki vsako označeno sporočilo iz vaše izvorne kode zbere v
predlogo `.pot` za prevajalce — korak 3 zanke iz [vadnice](tutorial.md). Ta
stran je referenca za ta korak: konfiguracija, lastna imena funkcij, strogi
način za CI in preverjanja, ki vaše kataloge varujejo zatem.

Ekstrakcija potrebuje dodatek `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Delovni proces { #the-workflow }

Ustvarite `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Nato uporabite običajne Babelove ukaze:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` teče enkrat na jezik; po tem `pybabel update` vsako svežo predlogo
zloži v obstoječe kataloge. Ta ponavljajoči se cikel — in kaj njegovi vnosi
`fuzzy` pomenijo za izdajo — je prehojen v
[V produkciji](workflow.md#the-cycle-after-the-first-translation).

Ekstraktor `gettext_tstrings` obdela tudi običajne klice `_()`, `gettext()` in
`ngettext()`, tako da ena preslikava pokrije mešano kodno zbirko. Prepozna
`_()`, štiri standardna imena gettexta, vzdevka `tr()` / `ntr()` in odložena
`lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Komentarje za prevajalce vklopite s `-c`"

    `pybabel extract` zbere komentarje za prevajalce le, kadar podate
    `-c "Translators:"`, natanko tako kot pri običajnih klicih gettexta. Če
    ga izpustite, ekstrakcija še vedno deluje — komentarji le nikoli ne
    pridejo v katalog, kjer so [najcenejši vzvod kakovosti](workflow.md#working-with-translators-and-platforms)
    v vsem delovnem procesu.

## Registracija lastnih imen funkcij { #registering-your-own-function-names }

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

Datoteka ini da en niz, preslikava TOML da seznam, znotraj niza pa imena ločuje
bodisi presledek bodisi vejica. Vse štiri zapise delujejo.

Možnosti so `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` in `npgettext_functions`.

!!! danger "`-k` ne seže do t-niza"

    Lasten pomočnik, kot je `mytr(t"…")`, mora biti poimenovan v eni od
    zgornjih možnosti. Babelovo strojevje `--keyword` ne zna prebrati
    dobesednega t-niza, zato `pybabel extract -k mytr` ne najde ničesar in ne
    pove ničesar — sporočil v POT preprosto ni. `-k` še naprej deluje za
    običajne klice gettexta, izvlečene ob njih.

    Podprt je samo standardni vrstni red argumentov: najprej sporočilo, pri
    `pgettext` kontekst in nato sporočilo, pri `npgettext` kontekst, nato
    ednina, nato množina.

## Prizanesljivo lokalno, strogo v CI { #lenient-locally-strict-in-ci }

Privzeto ena slaba datoteka ne konča teka:

- T-niz, ki ga ekstraktor zavrne — dostop do atributa, izraz, napačen
  argument —, se javi kot opozorilo in preskoči.
- Datoteka, ki se ne razčleni, se preskoči enako.
- Prav tako datoteka, ki jo zavrne le `tokenize`, medtem ko jo `ast` sprejme in
  na kateri bi Babelov lastni prehod sicer klonil.

To je udobno, dokler urejate, in nevarno, kadar ne. Preskočeno sporočilo je
preprosto **odsotno iz POT**, zato ni nikoli prevedeno in tega nič ne pove.
Povsod, kjer ekstrakcije ne opazuje človek, v možnostih preslikave nastavite
`strict = true`:

=== "babel.cfg"

    ```ini
    [gettext_tstrings: **.py]
    encoding = utf-8
    strict = true
    ```

=== "babel.toml"

    ```toml
    [[mappings]]
    method = "gettext_tstrings"
    pattern = "**.py"
    strict = true
    ```

Vsako zgornje opozorilo tedaj postane trda odpoved. To imejte za produkcijsko
nastavitev, privzeto pa za lokalno.

## Vaša obstoječa orodna veriga te kataloge preveri { #your-existing-toolchain-validates-these-catalogs }

Babel vsako izvlečeno sporočilo označi s standardno zastavico in prav ta ena
vrstica je tisto, kar v orodjih, ki jih že poganjate, vklopi preverjanje ograd:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Prevedite ga kot `こんにちは {nombre}` in napaka bo ujeta brez sleherne
nastavitve:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate isto preverjanje dokumentira kot [Python brace format][weblate-checks],
komercialne platforme pa imajo svoj nadzor kakovosti ograd, vezan na isto
zastavico. Vedenje vsake platforme je njena lastna stvar; spodnji orodji sta
tisti, ki sta preverjeni tukaj.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Vrh tega paket registrira Babelov **preverjevalnik**, tako da `pybabel compile`
uporabi pravila specifikacije za vsako sporočilo, ki nosi označevalni komentar
`gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Pri množinskem sporočilu kazalec poimenuje obliko, saj je številka vrstice, ki
jo javi Babel, številka msgida, ruski blok pa ima pod njim tri vnose `msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` `.mo` vseeno zapiše"

    Zgornja napaka je javljena, izhodno stanje je `1` — pokvarjen katalog pa se
    vseeno kompilira. Samo to izhodno stanje lahko cevovodu prepreči, da bi ga
    odpremil; [Kaj zapira CI](workflow.md#what-ci-gates) prikaže gradbeni
    korak, ki mu to omogoči.

Preverjanji nista odveč. Preverjevalnik iz paketa je strožji vsaj v dveh
primerih:

- Msgid, katerega edini zaviti oklepaji so ubežno zapisani
  (`Config {{raw}} only`), zastavice `python-brace-format` nikoli ne dobi, zato
  ga nobeno zunanje orodje sploh ne preveri.
- Množinske oblike se preverjajo eno po eno. `msgfmt --check-format` prebere
  natanko zgornjo datoteko in se konča z `0`; oblika, ki izpusti ogrado, ki jo
  njene sestre ohranijo, je tam sprejeta, tukaj pa zavrnjena.

`msgfmt` preveri le tista imena ograd, ki jih zna razčleniti kot Pythonov
format z zavitimi oklepaji, zato imena v ASCII ohranijo zmožnost vsakega orodja
v verigi, da sporočilo preveri. Knjižnica sama sprejme vsako ime, za katero
velja `str.isidentifier()`.

## Predloge in druga orodja { #templates-and-other-tools }

T-nizi so pythonska sintaksa, zato ta knjižnica pokriva pythonsko izvorno kodo.
Predlogni jeziki naprej uporabljajo svoj i18n — Jinja2 `{% trans %}`,
Djangove predlogne značke — in Babelove ekstraktorje zanje. Vse se steka v isti
katalog PO, tako da en sam prevajalski proces še vedno pokrije mešano kodno
zbirko.

`pygettext` t-nizov danes ne zna razčleniti, zato ekstrakcija poteka prek
Babela. Dogovor je zapisan v [specifikaciji](spec.md), tako da ga lahko drug
ekstraktor ali prihodnji `pygettext` vzame za cilj.
