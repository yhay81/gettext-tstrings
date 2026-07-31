---
description: "Tłumacz kompletne komunikaty t-string przez gettext i Babel, trzymając formatowanie poza katalogiem."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Napisz zdanie raz.<br>Przetłumacz je w całości.

Bezpieczna integracja gettext i Babel dla t-stringów Pythona 3.14+ — wartość
zostaje na swoim miejscu, a katalog widzi cały komunikat:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

[Rozpocznij samouczek :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Dlaczego t-stringi](comparison.md){ .md-button }

Ta strona praktykuje to, co dokumentuje: każda wersja językowa —
nawigacja, etykiety i raport z budowania świadomy form liczby mnogiej — jest
renderowana z katalogów PO przez
[sam `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

Katalog otrzymuje kompletne zdanie `Hello {name}`. Tłumaczenie może zmieniać
kolejność `{name}` albo je powtarzać; nie może go pominąć, wymyślić nowego ani
dołączyć własnego formatowania — ta biblioteka to sprawdza, a uszkodzony katalog
wraca do tekstu źródłowego zamiast powodować awarię.

!!! note "gettext to dla Ciebie nowość? Cały przepływ pracy w czterech zdaniach"

    **gettext** to standardowy sposób tłumaczenia oprogramowania, w Pythonie i
    daleko poza nim. Twój kod oznacza łańcuchy do przetłumaczenia; *ekstraktor*
    zbiera je do pliku szablonu (`.pot`); tłumacz — zwykle nie programista —
    wypełnia po jednym pliku katalogu (`.po`) na język, kompilowanym do
    binarnego `.mo`, który aplikacja wczytuje w czasie działania. Konwencjonalna
    nazwa funkcji tłumaczącej to `_`, więc `_(t"Hello {name}")` czyta się jako
    „przetłumacz to zdanie". **[Samouczek](tutorial.md)** przechodzi całą
    ścieżkę — oznacz, wyodrębnij, przetłumacz, skompiluj, uruchom — w około
    pięć minut.

## Problem, który rozwiązuje { #the-problem-it-solves }

F-string jest już zinterpolowany, zanim zobaczy go jakakolwiek biblioteka —
`f"Hello {name}"` stał się `"Hello Ada"`, a tłumaczenie fragmentów wokół
wartości łamie gramatykę większości języków. T-string ([PEP 750]) utrzymuje
osobno tekst statyczny, obliczone wartości, wyrażenia źródłowe, konwersje i
specyfikacje formatu — a to dokładnie ten podział, którego potrzebuje katalog
komunikatów.
[Co to zmienia](comparison.md) w porównaniu z `%(name)s`, `.format()` i
`$`-stringami.

Nic w gettext ani w Babel nie mówi jednak, jak t-string ma stać się
komunikatem. Ta biblioteka dokonuje tego wyboru, spisuje go jako
[wersjonowaną specyfikację](spec.md) i dostarcza
[zestaw testów zgodności](spec.md#conformance), który go sprawdza.

## Wybór, którego dokonuje { #the-choice-it-makes }

- Tłumacz kompletne komunikaty, nigdy fragmenty zdań.
- Akceptuj wyłącznie proste nazwy zmiennych, takie jak `{name}`.
- Trzymaj `!r` i `:.2f` pod kontrolą aplikacji, poza katalogiem.
- Pozwól tłumaczom zmieniać kolejność i powtarzać znane symbole zastępcze —
  ale nie wywoływać atrybutów ani nie dodawać zachowań formatujących.
- Używaj zwykłych plików POT, PO i MO oraz narzędzi, które już je czytają.

## Instalacja { #install }

```console
python -m pip install gettext-tstrings
```

Python 3.14 lub nowszy. **Renderowanie nie ma zależności** — korzysta z
modułu `gettext` biblioteki standardowej i z niczego więcej.

Ekstrakcja i walidacja katalogów przechodzą przez [Babel], zainstaluj więc to
rozszerzenie tam, gdzie działa `pybabel`, czyli zwykle w środowisku
deweloperskim lub CI, a nie w obrazie produkcyjnym:

```console
python -m pip install "gettext-tstrings[babel]"
```

## Dokąd dalej { #where-to-go-next }

Trafiają tu trzy rodzaje czytelników: ktoś, kto tłumaczy swój pierwszy
program, ktoś, kto wpina tłumaczenia w prawdziwy projekt, i ktoś, kto chce
dokładnie wiedzieć, dlaczego ta maszyneria ma taki kształt. Każdy ma swoją
ścieżkę.

**Nauka** — bez zakładania doświadczenia z gettext:

<div class="grid cards" markdown>

- **[Samouczek](tutorial.md)** — zacznij tutaj: od pustego katalogu do
  działającego japońskiego tłumaczenia w pięciu krokach, każde polecenie
  pokazane z jego wynikiem.
- **[Dlaczego t-stringi](comparison.md)** — ten sam komunikat zapisany na
  cztery sposoby i to, co `%(name)s`, `.format()` oraz `$`-stringi oddają
  katalogowi.
- **[Geneza](background.md)** — dlaczego ta biblioteka istnieje: trzydzieści
  lat gettext, dwa PEP-y i dyskusja o bibliotece standardowej zamknięta bez
  odpowiedzi.

</div>

**Poważne użycie** — robocze materiały odniesienia:

<div class="grid cards" markdown>

- **[Przewodnik](guide.md)** — API czasu działania: liczba mnoga, języki na
  żądanie, odroczone łańcuchy i to, co się dzieje, gdy katalog jest błędny.
- **[Ekstrakcja](extraction.md)** — dokumentacja `pybabel`: konfiguracja,
  własne nazwy funkcji i to, jak istniejące narzędzia walidują te katalogi za
  darmo.
- **[W produkcji](workflow.md)** — pętla tak, jak prowadzi ją zespół: cykl
  aktualizacji, wpisy fuzzy, bramki CI, platformy tłumaczeniowe i języki na
  żądanie w aplikacji webowej.
- **[API](api.md)** — wszystko, co eksportuje pakiet, na jednej stronie.

</div>

**Zrozumienie** — od zasad do implementacji:

<div class="grid cards" markdown>

- **[Jak to działa](internals.md)** — od obiektu szablonu z PEP 750 do
  wyrenderowanego łańcucha oraz pamięci podręczne, które czynią sprawdzanie
  tanim.
- **[Specyfikacja](spec.md)** — konwencja t-string ↔ msgid jako stabilny,
  wersjonowany kontrakt z maszynowo czytelnym zestawem testów zgodności.

</div>

## Status { #status }

Wersja alfa. Kontrakt jest celowo mały, a [specyfikacja](spec.md) jest jego
stabilną częścią; API Pythona może się jeszcze zmieniać. Przed stabilnym
wydaniem potrzebne są szersze zestawy testowe dla języków, stałe śledzenie
wydajności, przegląd API przez osoby używające gettext i Babel na poważnie
oraz testy zgodności z każdą wspieraną wersją Pythona i Babel.

[Zgłoszenia i pull requesty](https://github.com/yhay81/gettext-tstrings/issues)
są mile widziane — alfa to dokładnie ten moment, w którym o interfejs wciąż
warto się spierać.

## Dołącz do społeczności { #join-the-community }

- Wybierz
  [good first issue](https://github.com/yhay81/gettext-tstrings/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  na ograniczony, pierwszy wkład.
- Zadawaj pytania o użycie w
  [dyskusjach Q&A](https://github.com/yhay81/gettext-tstrings/discussions/categories/q-a).
- Przynieś produkcyjne przepływy gettext i pomysły na API do
  [dyskusji Ideas](https://github.com/yhay81/gettext-tstrings/discussions/categories/ideas).
- Przeczytaj
  [przewodnik dla współtwórców](https://github.com/yhay81/gettext-tstrings/blob/main/CONTRIBUTING.md),
  zanim otworzysz pull request.

  [PEP 750]: https://peps.python.org/pep-0750/
  [Babel]: https://babel.pocoo.org/
