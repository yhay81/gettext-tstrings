---
description: "Przyjęcie t-stringów w projekcie, który ma już katalogi gettext: co pozostaje nietknięte, co staje się fuzzy i jak przenosić po jednym miejscu wywołania."
---

# Migracja

Jeśli Twój projekt już używa gettext, o możliwości przyjęcia tej biblioteki
decydują wąskie pytania: czy unieważnia katalogi, które masz, czy potrafi
współistnieć z kodem, którego nie jesteś gotów zmienić, i jak dużo przejścia
musi się wydarzyć naraz. Odpowiedzi, od najkrótszej:

| Pytanie | Odpowiedź |
| --- | --- |
| Czy istniejące pliki `.po` i `.mo` nadal działają? | Tak. Te same pliki, te same narzędzia. |
| Czy stare i nowe wywołania mogą żyć w jednym pliku? | Tak, i jedno odwzorowanie ekstraktora obsługuje oba. |
| Czy msgid się zmienia? | Nie przy `.format()`. Tak przy `%`-formacie. |
| Czy cały projekt musi przejść naraz? | Nie. Jedno miejsce wywołania to poprawna zmiana. |
| A co z Jinją, szablonami Django, JavaScriptem? | Nietknięte, te same katalogi. |

Reszta tej strony to szczegóły stojące za każdą z tych odpowiedzi.

## Z `.format()`: msgid się nie zmienia { #from-format-the-msgid-does-not-change }

To przypadek, w którym migracja nie kosztuje prawie nic. Komunikat
`str.format` i komunikat t-stringowy wyprowadzają *ten sam* klucz katalogu, bo
w obu przypadkach kluczem jest tekst z pozostawionym w nim `{name}`:

```python
# Before
_("Hello {name}").format(name=name)

# After — the msgid is still "Hello {name}"
tr(t"Hello {name}")
```

Istniejące tłumaczenie zostaje więc przypięte. Zaczynając od katalogu
zawierającego

```po
#: app.py:6
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

zmień wywołanie, wyodrębnij ponownie i zaktualizuj:

```console
$ pybabel extract -F babel.cfg -o locales/messages.pot .
extracting messages from app.py (encoding="utf-8")
writing PO template file to locales/messages.pot
$ pybabel update -i locales/messages.pot -d locales
updating catalog locales/ja/LC_MESSAGES/messages.po based on locales/messages.pot
```

Wpis, który wraca, różni się dwiema liniami metadanych i niczym więcej —
komentarzem-znacznikiem identyfikującym go jako komunikat t-stringowy oraz
numerem linii źródłowej:

```po
#. gettext-tstrings
#: app.py:4
#, python-brace-format
msgid "Hello {name}"
msgstr "こんにちは {name}"
```

Żadnej flagi `fuzzy`, żadnego ponownego tłumaczenia, w żadnym języku.
Komunikat renderuje się natychmiast:

```console
$ pybabel compile -d locales
compiling catalog locales/ja/LC_MESSAGES/messages.po to locales/ja/LC_MESSAGES/messages.mo
$ python app.py
こんにちは Ada
```

!!! note "`update --check` zgłosi katalogi jako nieaktualne"

    Ten komentarz-znacznik i przesunięte numery linii wystarczą, by
    `pybabel update --check` uznał, że katalog wymaga wygenerowania na nowo,
    bo porównuje cały wpis, a nie tylko tłumaczenie. Uruchom prawdziwe
    `pybabel update` w tym samym commicie co zmiana kodu i zacommituj katalogi
    razem z nią — to ten sam nawyk, o który prosi już
    [bramka CI](workflow.md#what-ci-gates).

## Z `%`-formatu: msgid się zmienia, więc tłumaczenia stają się fuzzy { #from--format-the-msgid-changes-so-translations-go-fuzzy }

Składnia printf mieszka *wewnątrz* komunikatu, więc jej zastąpienie przepisuje
klucz katalogu. Nie da się tego obejść i jest to uczciwy koszt porzucenia
`%(name)s`:

```python
# Before
_("Hello %(name)s") % {"name": name}

# After — a different msgid
tr(t"Hello {name}")
```

`pybabel update` rozpoznaje nowy komunikat jako bliskiego krewnego usuniętego
i przenosi stare tłumaczenie, oznaczając je jako fuzzy:

```po
#. gettext-tstrings
#: app.py:4
#, fuzzy, python-brace-format, python-format
msgid "Hello {name}"
msgstr "こんにちは %(name)s"
```

O tym stanie trzeba wiedzieć trzy rzeczy:

- **Nic nie psuje się w czasie działania.** Wpisy fuzzy są wyłączane ze
  skompilowanego `.mo`, więc aplikacja renderuje tekst źródłowy, dopóki
  człowiek nie potwierdzi pary — [ta sama degradacja](workflow.md#the-cycle-after-the-first-translation),
  przez którą przechodzi każdy przeredagowany komunikat.
- **CI pozostaje zielone, dopóki są fuzzy.** Kontroler symboli zastępczych
  pomija wpisy fuzzy, dokładnie tak jak `msgfmt --check-format`, bo wpis, który
  nie może dotrzeć do czasu działania, nie powinien wywalać budowania. W chwili,
  gdy tłumacz zdejmie flagę, wpis jest sprawdzany jak każdy inny — więc
  `%(name)s` pozostawione w potwierdzonym tłumaczeniu zostaje wychwycone
  właśnie wtedy, czyli w momencie, w którym zaczęłoby się renderować.
- **Stara flaga `python-format` jedzie razem** i powinna zostać usunięta wraz z
  flagą `fuzzy`, inaczej `msgfmt --check-format` będzie dalej stosował reguły
  printf do komunikatu w formacie klamrowym.

Dla nazwanych symboli printf edycja jest mechaniczna — `%(name)s` staje się
`{name}` i nic więcej się nie zmienia — więc duży katalog to skryptowe
przejście, po którym następuje przegląd tłumacza, a nie ponowne tłumaczenie.
Pozycyjne `%s` mechaniczne nie jest: nie ma nazwy do przeniesienia, a jej wybór
jest właśnie sensem tej zmiany.

Migracja może więc postępować w tempie, na jakie pozwala przegląd:
nieprzekonwertowany wpis fuzzy to widoczny kawałek pracy w katalogu, a nie
zepsute budowanie.

## Stare i nowe wywołania współistnieją { #old-and-new-calls-coexist }

Ekstraktor, który czyta t-stringi, czyta też zwykłe wywołania gettext, więc
jedno odwzorowanie obsługuje plik w trakcie migracji:

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

Oba komunikaty lądują w tym samym szablonie i tylko ten t-stringowy niesie
komentarz-znacznik włączający dodatkowe sprawdzanie tej biblioteki:

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

Rozpoznaje `_()`, cztery standardowe nazwy gettext, aliasy `tr()` / `ntr()`
oraz odroczone `lazy_gettext()` / `lazy_pgettext()`. Własną funkcję pomocniczą
trzeba [nazwać w odwzorowaniu](extraction.md#registering-your-own-function-names).

W czasie działania oba style są tak samo niezależne: `gettext.translation()`
zwraca jeden obiekt tłumaczeń, a zarówno `_`, jak i punkty wejścia tej
biblioteki czytają z niego.

## Co się nie przenosi { #what-does-not-move }

- **Języki szablonów.** `{% trans %}` Jinji2, tagi szablonów Django i ich
  ekstraktory Babel działają dalej bez zmian i dalej zasilają te same katalogi
  PO. T-stringi to składnia Pythona; dotyczą źródeł Pythona.
- **Twoje pliki katalogów.** Żadnej zmiany formatu, żadnego nowego pliku,
  żadnego kroku konwersji.
- **Twoja platforma tłumaczeniowa.** Wymiana `.po` jest identyczna, a flaga
  `python-brace-format`, którą niesie komunikat t-stringowy, to ta sama flaga,
  którą niesie komunikat `.format()` — więc kontrola jakości symboli
  zastępczych działa dalej.
- **Kod spoza Pythona.** Katalog JavaScriptu czy C w tym samym projekcie
  pozostaje nietknięty.

## Lista kontrolna migracji { #a-migration-checklist }

1. Dodaj rozszerzenie `babel` tam, gdzie działa `pybabel`, i zmień odwzorowanie
   `python` w `babel.cfg` na metodę `gettext_tstrings` — jedno odwzorowanie
   obsłuży wtedy oba style, a `-k` dalej działa dla zwykłych wywołań.
2. Przekonwertuj najpierw miejsca wywołań `.format()`. Wyodrębnij ponownie,
   uruchom `pybabel update` i zacommituj katalogi razem z kodem; nie spodziewaj
   się wpisów fuzzy.
3. Konwertuj miejsca wywołań `%`-formatu partiami, które da się przejrzeć,
   przepisując przeniesione symbole zastępcze i zdejmując flagi `fuzzy` oraz
   `python-format`.
4. Napraw to, co odrzuca ograniczenie: interpolacja musi być prostą nazwą, więc
   `t"Hello {user.name}"` staje się najpierw zmienną lokalną. To edycja miejsca
   wywołania, nie katalogu.
5. Włącz `strict = true` w odwzorowaniu ekstraktora, gdy przejście się skończy,
   tak by komunikat, którego nie da się wyodrębnić, wywalał
   [budowanie](extraction.md#lenient-locally-strict-in-ci), zamiast znikać z
   szablonu.
6. Dodaj kontrolę czasu działania z [W produkcji](workflow.md#what-ci-gates):
   wyrenderuj jeden komunikat na każdy wysyłany język przez ścisły
   `Translator`.

Kroki 2 i 3 to zwykłe commity. Nic na tej liście nie wymaga dnia przełomu.
