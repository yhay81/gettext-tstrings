---
description: "Ekstrakcja komunikatów t-string za pomocą pybabel oraz to, jak msgfmt i dołączony checker Babel walidują katalogi."
---

# Ekstrakcja

Ekstrakcja to krok, który zbiera każdy oznaczony komunikat z Twojego kodu
źródłowego do szablonu `.pot` dla tłumaczy — krok 3 pętli z
[samouczka](tutorial.md). Ta strona jest dokumentacją tego kroku:
konfiguracja, własne nazwy funkcji, ścisły tryb CI i kontrole, które potem
strzegą Twoich katalogów.

Ekstrakcja wymaga rozszerzenia `babel`:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Przepływ pracy { #the-workflow }

Utwórz `babel.cfg`:

```ini
[gettext_tstrings: **.py]
encoding = utf-8
```

Następnie używaj zwykłych poleceń Babel:

```console
pybabel extract -F babel.cfg -c "Translators:" -o locales/messages.pot .
pybabel init -i locales/messages.pot -d locales -l ja
pybabel compile -d locales
```

`init` uruchamia się raz na język; potem `pybabel update` wtapia każdy świeży
szablon w istniejące katalogi. Ten powracający cykl — i to, co jego wpisy
`fuzzy` znaczą dla wydania — omawia
[W produkcji](workflow.md#the-cycle-after-the-first-translation).

Ekstraktor `gettext_tstrings` obsługuje też zwykłe wywołania `_()`,
`gettext()` i `ngettext()`, więc jedno mapowanie pokrywa mieszaną bazę kodu.
Rozpoznaje `_()`, cztery standardowe nazwy gettext, aliasy `tr()` / `ntr()`
oraz odroczone `lazy_gettext()` / `lazy_pgettext()`.

!!! warning "Włącz komentarze dla tłumaczy przez `-c`"

    `pybabel extract` zbiera komentarze dla tłumaczy tylko wtedy, gdy
    przekażesz `-c "Translators:"`, dokładnie tak samo jak dla zwykłych
    wywołań gettext. Bez tego ekstrakcja nadal działa — komentarze po prostu
    nigdy nie docierają do katalogu, gdzie są [najtańszą dźwignią
    jakości](workflow.md#working-with-translators-and-platforms) w całym
    przepływie pracy.

## Rejestrowanie własnych nazw funkcji { #registering-your-own-function-names }

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

Plik ini podaje jeden łańcuch, mapowanie TOML podaje listę, a wewnątrz
łańcucha nazwy rozdzielają albo białe znaki, albo przecinki. Wszystkie cztery
zapisy działają.

Dostępne opcje to `tr_functions`, `ntr_functions`, `gettext_functions`,
`ngettext_functions`, `pgettext_functions` i `npgettext_functions`.

!!! danger "`-k` nie sięga t-stringa"

    Własny pomocnik taki jak `mytr(t"…")` musi zostać nazwany w jednej z
    powyższych opcji. Mechanizm `--keyword` Babel nie potrafi czytać literału
    t-string, więc `pybabel extract -k mytr` nic nie znajduje i nic nie mówi
    — komunikaty po prostu nie trafiają do POT. `-k` nadal działa dla
    zwykłych wywołań gettext wyodrębnianych obok.

    Wspierana jest tylko standardowa kolejność argumentów: najpierw
    komunikat, kontekst i potem komunikat dla `pgettext`, kontekst, liczba
    pojedyncza i mnoga dla `npgettext`.

## Pobłażliwy lokalnie, rygorystyczny w CI { #lenient-locally-strict-in-ci }

Domyślnie jeden zły plik nie kończy przebiegu:

- T-string, który ekstraktor odrzuca — dostęp do atrybutu, wyrażenie, zły
  argument — jest raportowany jako ostrzeżenie i pomijany.
- Plik, którego nie da się sparsować, jest pomijany tak samo.
- Podobnie plik, który odrzuca tylko `tokenize`, choć `ast` go akceptuje —
  na nim własny przebieg Babel by się przerwał.

To jest wygodne, kiedy właśnie edytujesz kod, i niebezpieczne, kiedy tego nie
robisz: pominięty komunikat jest po prostu **nieobecny w POT**, więc nigdy nie
zostanie przetłumaczony i nic o tym nie powie. Ustaw `strict = true` w opcjach
mapowania wszędzie tam, gdzie nikt nie patrzy na przebieg ekstrakcji:

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

Każde z powyższych ostrzeżeń staje się wtedy twardym niepowodzeniem. Traktuj
to jako ustawienie produkcyjne, a domyślne jako lokalne.

## Twoje istniejące narzędzia walidują te katalogi { #your-existing-toolchain-validates-these-catalogs }

Babel oznacza każdy wyodrębniony komunikat standardową flagą i ta jedna
linia włącza sprawdzanie symboli zastępczych w narzędziach, które już
uruchamiasz:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr ""
```

Przetłumacz go jako `こんにちは {nombre}`, a błąd zostanie wychwycony bez
żadnej konfiguracji:

```console
$ msgfmt --check-format -o /dev/null locales/ja/LC_MESSAGES/messages.po
locales/ja/LC_MESSAGES/messages.po:25: a format specification for argument
'name' doesn't exist in 'msgstr'
msgfmt: found 1 fatal error
```

Weblate dokumentuje tę samą kontrolę jako
[Python brace format][weblate-checks], a platformy komercyjne mają własne QA
symboli zastępczych oparte na tej samej fladze. Zachowanie każdej platformy
jest jej własną sprawą; dwa narzędzia poniżej są tymi zweryfikowanymi tutaj.

  [weblate-checks]: https://docs.weblate.org/en/latest/user/checks.html

Ponadto pakiet rejestruje **checker** Babel, więc `pybabel compile` stosuje
reguły specyfikacji do każdego komunikatu niosącego komentarz znacznikowy
`gettext-tstrings`:

```console
$ pybabel compile -d locales -l ja
error: locales/ja/LC_MESSAGES/messages.po:24: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
1 errors encountered.
```

Dla komunikatu w liczbie mnogiej wskazanie nazywa formę, bo numer linii
raportowany przez Babel jest numerem msgid, a rosyjski blok ma pod nim trzy
`msgstr`:

```console
error: locales/ru/LC_MESSAGES/messages.po:31: msgstr[1]: translation does not
match the source placeholders: {n} is missing
```

!!! danger "`pybabel compile` i tak zapisuje `.mo`"

    Powyższy błąd jest raportowany, status wyjścia to `1` — a uszkodzony
    katalog i tak zostaje skompilowany. Tylko ten status wyjścia może
    powstrzymać potok przed jego wysłaniem;
    [Co bramkuje CI](workflow.md#what-ci-gates) pokazuje krok budowania,
    który mu na to pozwala.

Te dwie kontrole nie są nadmiarowe. Checker z tego pakietu jest surowszy w co
najmniej dwóch przypadkach:

- Msgid, którego jedyne nawiasy klamrowe są escapowane (`Config {{raw}}
  only`), nigdy nie dostaje flagi `python-brace-format`, więc żadne
  zewnętrzne narzędzie w ogóle go nie waliduje.
- Formy liczby mnogiej są sprawdzane jedna po drugiej. `msgfmt
  --check-format` czyta dokładnie ten plik powyżej i wychodzi z kodem `0`;
  forma, która gubi symbol zastępczy zachowany przez jej rodzeństwo, tam
  jest akceptowana, a tu odrzucana.

`msgfmt` sprawdza tylko nazwy symboli zastępczych, które umie sparsować jako
Pythonowy brace format, więc nazwy ASCII utrzymują zdolność każdego
narzędzia w łańcuchu do walidacji komunikatu. Sama biblioteka akceptuje
każdą nazwę spełniającą `str.isidentifier()`.

## Szablony i inne narzędzia { #templates-and-other-tools }

T-stringi to składnia Pythona, więc ta biblioteka pokrywa źródła w Pythonie.
Języki szablonów nadal używają własnego i18n — `{% trans %}` Jinja2,
tagi szablonów Django — i ekstraktorów Babel dla nich. Wszystko zasila ten
sam katalog PO, więc jeden przepływ tłumaczeń nadal pokrywa mieszaną bazę
kodu.

`pygettext` nie potrafi dziś parsować t-stringów, dlatego ekstrakcja idzie
przez Babel. Konwencja jest spisana w [specyfikacji](spec.md), by mógł ją
obrać za cel inny ekstraktor albo przyszły `pygettext`.
