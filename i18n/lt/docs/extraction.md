---
description: "T-eilučių pranešimų ištraukimas su pybabel ir tai, kaip msgfmt bei pridedamas Babel tikrintuvas patikrina katalogus."
---

# Ištraukimas

Ištraukimas yra tas žingsnis, kuris surenka kiekvieną pažymėtą pranešimą iš
jūsų pirminio kodo į `.pot` šabloną vertėjams — 3-iasis
[pamokos](tutorial.md) ciklo žingsnis. Šis puslapis yra to žingsnio žinynas:
konfigūracija, savi funkcijų vardai, griežtas CI režimas ir patikros, kurios
paskui saugo jūsų katalogus.

Ištraukimui reikia `babel` priedo:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Darbo eiga { #the-workflow }

Sukurkite `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Tada naudokite įprastas Babel komandas:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` paleidžiama po kartą kiekvienai kalbai; po to `pybabel update` įpina
kiekvieną šviežią šabloną į jau esamus katalogus. Tas pasikartojantis ciklas —
ir ką jo `fuzzy` įrašai reiškia leidimui — pereitas puslapyje
[Realioje aplinkoje](workflow.md#the-cycle-after-the-first-translation).

`gettext_tstrings` ištraukiklis taip pat tvarko įprastus `_()`, `gettext()` ir
`ngettext()` iškvietimus, todėl vienas atvaizdis dengia mišrią kodo bazę. Jis
atpažįsta `_()`, keturis standartinius gettext vardus, `tr()` / `ntr()`
sinonimus ir atidėtuosius `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Vertėjų komentarus įjunkite su `-c`"

    `pybabel extract` surenka vertėjų komentarus tik tada, kai perduodate
    `-c "Translators:"` — lygiai kaip ir įprastiems gettext iškvietimams. Jo
    nepridėjus, ištraukimas vis tiek veikia — tiesiog komentarai niekada
    nepasiekia katalogo, kuriame jie yra [pigiausia kokybės
    svirtis](workflow.md#working-with-translators-and-platforms) visoje darbo
    eigoje.

## Savų funkcijų vardų registravimas { #registering-your-own-function-names }

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

Ini failas duoda vieną eilutę, TOML atvaizdis duoda sąrašą, o eilutės viduje
vardus skiria arba tarpai, arba kableliai. Veikia visi keturi užrašymo būdai.

Galimos parinktys: `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` ir `npgettext_functions`.

!!! danger "`-k` t-eilutės nepasiekia"

    Savas pagalbininkas, toks kaip `mytr(t"…")`, turi būti įvardytas vienoje iš
    aukščiau nurodytų parinkčių. Babel `--keyword` mechanika negali perskaityti
    t-eilutės literalo, todėl `pybabel extract -k mytr` neranda nieko ir nieko
    nesako — pranešimų POT faile tiesiog nėra. `-k` toliau veikia įprastiems
    gettext iškvietimams, ištraukiamiems kartu.

    Palaikoma tik standartinė argumentų tvarka: pirma pranešimas, `pgettext`
    atveju kontekstas ir tada pranešimas, `npgettext` atveju kontekstas, tada
    vienaskaita, tada daugiskaita.

## Pakanti vietoje, griežta CI aplinkoje { #lenient-locally-strict-in-ci }

Pagal nutylėjimą vienas blogas failas nenutraukia viso paleidimo:

- T-eilutė, kurią ištraukiklis atmeta — prieiga prie atributo, reiškinys,
  netinkamas argumentas — pranešama kaip įspėjimas ir praleidžiama.
- Failas, kurio nepavyksta išanalizuoti, praleidžiamas taip pat.
- Taip pat ir failas, kurio atsisako tik `tokenize`, o `ast` jį priima — nuo
  tokio paties Babel praėjimas šiaip nutrūktų.

Redaguojant tai patogu, o neredaguojant — pavojinga: praleistas pranešimas
paprasčiausiai **nepatenka į POT**, tad jis niekada neišverčiamas ir niekas apie
tai nepraneša. Nustatykite `strict = true` atvaizdžio parinktyse visur, kur
ištraukimo nestebi žmogus:

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

Tada kiekvienas aukščiau minėtas įspėjimas tampa kieta klaida. Laikykite tai
produkcine nuostata, o numatytąją — vietine.

## Jūsų turimi įrankiai patikrina šiuos katalogus { #your-existing-toolchain-validates-these-catalogs }

Babel kiekvieną ištrauktą pranešimą pažymi standartine žyma, ir būtent ta viena
eilutė įjungia vietaženklių tikrinimą įrankiuose, kuriuos jau naudojate:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Išverskite jį kaip `こんにちは {nombre}` ir klaida bus pagauta be jokios
konfigūracijos:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate tą pačią patikrą dokumentuoja kaip [Python brace format][weblate-checks],
o komercinės platformos turi savo vietaženklių kokybės kontrolę, paremtą ta
pačia žyma. Kiekvienos platformos elgsena yra jos pačios reikalas; du žemiau
aprašyti įrankiai yra tie, kurie čia patikrinti.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Be to, paketas užregistruoja Babel **tikrintuvą**, todėl `pybabel compile`
pritaiko specifikacijos taisykles kiekvienam pranešimui, nešančiam
`gettext-tstrings` žymos komentarą:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Daugiskaitos pranešimui rodyklė įvardija formą, nes Babel praneštas eilutės
numeris yra msgid'o, o po rusišku bloku yra trys `msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` vis tiek įrašo `.mo`"

    Apie aukščiau esančią klaidą pranešama, išėjimo būsena yra `1` — o
    sugadintas katalogas vis tiek sukompiliuojamas. Tik ta išėjimo būsena gali
    sustabdyti konvejerį, kad jo neišsiųstų;
    [Ką tikrina CI](workflow.md#what-ci-gates) parodo tai leidžiantį kūrimo
    žingsnį.

Šios dvi patikros nėra perteklinės. Paketo tikrintuvas yra griežtesnis
mažiausiai dviem atvejais:

- Msgid, kurio vieninteliai riestiniai skliaustai yra ekranuoti
  (`Config {{raw}} only`), niekada negauna `python-brace-format` žymos, todėl
  jokia išorinė priemonė jo apskritai netikrina.
- Daugiskaitos formos tikrinamos po vieną. `msgfmt --check-format` perskaito
  būtent tą patį failą ir baigia darbą su `0`; forma, praradusi vietaženklį,
  kurį jos seserys išlaiko, ten priimama, o čia atmetama.

`msgfmt` tikrina tik tuos vietaženklių vardus, kuriuos sugeba išanalizuoti kaip
Python riestinių skliaustų formatą, todėl ASCII vardai palaiko kiekvieno
grandinės įrankio gebėjimą tikrinti pranešimą. Pati biblioteka priima bet kurį
`str.isidentifier()` vardą.

## Šablonai ir kiti įrankiai { #templates-and-other-tools }

T-eilutės yra Python sintaksė, todėl ši biblioteka dengia Python pirminį kodą.
Šablonų kalbos toliau naudoja savo i18n — Jinja2 `{% trans %}`, Django šablonų
žymes — ir Babel ištraukiklius joms. Viskas suplaukia į tą patį PO katalogą,
todėl viena vertimo darbo eiga vis tiek dengia mišrią kodo bazę.

`pygettext` šiandien negali išanalizuoti t-eilučių, todėl ištraukimas eina per
Babel. Susitarimas surašytas [specifikacijoje](spec.md), kad į jį galėtų
taikytis kitas ištraukiklis arba būsimas `pygettext`.
