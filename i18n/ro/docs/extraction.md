---
description: "Extragerea mesajelor t-string cu pybabel, și felul în care msgfmt și verificatorul Babel inclus validează cataloagele."
---

# Extragere

Extragerea este pasul care adună fiecare mesaj marcat din codul tău sursă
într-un șablon `.pot` pentru traducători — pasul 3 din bucla
[tutorialului](tutorial.md). Pagina de față este referința pentru acel pas:
configurare, nume proprii de funcții, modul strict pentru CI și verificările
care îți păzesc cataloagele după aceea.

Extragerea are nevoie de extraul `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Fluxul de lucru { #the-workflow }

Creează `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Apoi folosește comenzile Babel obișnuite:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` se rulează o dată pe limbă; după aceea, `pybabel update` pliază fiecare
șablon proaspăt peste cataloagele existente. Acel ciclu recurent — și ce
înseamnă intrările lui `fuzzy` pentru o lansare — este parcurs în
[În producție](workflow.md#the-cycle-after-the-first-translation).

Extractorul `gettext_tstrings` tratează și apelurile obișnuite `_()`,
`gettext()` și `ngettext()`, așa că o singură mapare acoperă o bază de cod
mixtă. Recunoaște `_()`, cele patru nume gettext standard, aliasurile `tr()` /
`ntr()` și `lazy_gettext()` / `lazy_pgettext()` amânate.

!!! warning "Activează comentariile pentru traducători cu `-c`"

    `pybabel extract` adună comentariile pentru traducători numai când îi
    transmiți `-c "Translators:"`, exact așa cum face și pentru apelurile
    gettext obișnuite. Lasă-l deoparte și extragerea funcționează în
    continuare — doar că acele comentarii nu ajung niciodată în catalog, unde
    sunt [cea mai ieftină pârghie de calitate](workflow.md#working-with-translators-and-platforms)
    din tot fluxul.

## Înregistrarea propriilor nume de funcții { #registering-your-own-function-names }

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

Un fișier ini dă un singur șir, o mapare TOML dă o listă, iar în interiorul unui
șir numele sunt separate fie de spații albe, fie de virgule. Toate cele patru
scrieri funcționează.

Opțiunile sunt `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` și `npgettext_functions`.

!!! danger "`-k` nu ajunge la un t-string"

    Un ajutor propriu precum `mytr(t"…")` trebuie numit în una dintre opțiunile
    de mai sus. Mecanismul `--keyword` al lui Babel nu poate citi un literal
    t-string, așa că `pybabel extract -k mytr` nu găsește nimic și nu spune
    nimic — mesajele lipsesc pur și simplu din POT. `-k` continuă să
    funcționeze pentru apelurile gettext obișnuite extrase alături.

    Este suportată numai ordinea standard a argumentelor: mai întâi mesajul,
    contextul apoi mesajul pentru `pgettext`, contextul apoi singularul apoi
    pluralul pentru `npgettext`.

## Îngăduitor local, strict în CI { #lenient-locally-strict-in-ci }

În mod implicit, un singur fișier prost nu încheie rularea:

- Un t-string pe care extractorul îl respinge — acces la atribut, o expresie,
  un argument greșit — este raportat ca avertisment și sărit.
- Un fișier care nu se poate parsa este sărit în același fel.
- La fel și un fișier pe care doar `tokenize` îl refuză, în timp ce `ast` îl
  acceptă — un fișier pe care trecerea proprie a lui Babel ar aborta altfel.

Asta este comod cât timp editezi și primejdios cât timp nu o faci: un mesaj
sărit este pur și simplu **absent din POT**, așa că nu este tradus niciodată și
nimic nu o spune. Pune `strict = true` în opțiunile mapării oriunde extragerea
nu este privită de un om:

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

Fiecare avertisment de mai sus devine atunci un eșec dur. Tratează asta drept
setarea de producție, iar valoarea implicită drept cea locală.

## Lanțul tău de unelte existent validează aceste cataloage { #your-existing-toolchain-validates-these-catalogs }

Babel marchează fiecare mesaj extras cu un flag standard, iar acea singură linie
este ceea ce activează verificarea substituenților în uneltele pe care le
rulezi deja:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Tradu-l ca `こんにちは {nombre}` și greșeala este prinsă fără nicio
configurare:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate documentează aceeași verificare sub numele
[Python brace format][weblate-checks], iar platformele comerciale au propriul
lor QA de substituenți legat de același flag. Comportamentul fiecărei platforme
este al ei; cele două unelte de mai jos sunt cele verificate aici.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Pe deasupra, pachetul înregistrează un **verificator** Babel, așa că
`pybabel compile` aplică regulile specificației fiecărui mesaj care poartă
comentariul-marcaj `gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Pentru un mesaj la plural, indicatorul numește forma, pentru că numărul de
linie raportat de Babel este cel al msgid-ului, iar un bloc rusesc are trei
`msgstr` sub el:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` scrie oricum fișierul `.mo`"

    Eroarea de mai sus este raportată, starea de ieșire este `1` — iar
    catalogul stricat este compilat oricum. Numai acea stare de ieșire poate
    opri o conductă să îl livreze;
    [Ce anume păzește CI-ul](workflow.md#what-ci-gates) arată pasul de build
    care îi permite asta.

Cele două verificări nu sunt redundante. Verificatorul pachetului este mai
strict în cel puțin două cazuri:

- Un msgid ale cărui singure acolade sunt escapate (`Config {{raw}} only`) nu
  primește niciodată flagul `python-brace-format`, așa că nicio unealtă externă
  nu îl validează deloc.
- Formele de plural sunt verificate una câte una. `msgfmt --check-format`
  citește chiar fișierul de mai sus și iese cu `0`; o formă care pierde un
  substituent pe care surorile ei îl păstrează este acceptată acolo și respinsă
  aici.

`msgfmt` verifică numai numele de substituenți pe care le poate parsa ca format
Python cu acolade, așa că numele ASCII păstrează fiecare unealtă din lanț
capabilă să valideze mesajul. Biblioteca însăși acceptă orice nume pentru care
`str.isidentifier()` este adevărat.

## Șabloane și alte unelte { #templates-and-other-tools }

T-stringurile sunt sintaxă Python, așa că biblioteca de față acoperă sursa
Python. Limbajele de șabloane își folosesc mai departe propriul i18n —
`{% trans %}` din Jinja2, tagurile de șablon din Django — și extractoarele
Babel pentru ele. Totul se varsă în același catalog PO, așa că un singur flux
de traducere acoperă și acum o bază de cod mixtă.

`pygettext` nu poate parsa t-stringuri astăzi, motiv pentru care extragerea
trece prin Babel. Convenția este consemnată în [specificație](spec.md) tocmai
pentru ca un alt extractor, sau un viitor `pygettext`, să o poată ținti.
