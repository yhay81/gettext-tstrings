---
description: "Tłumacz kompletne komunikaty t-string przez gettext i Babel, trzymając wartości i formatowanie poza katalogiem."
title: "gettext-tstrings"
hide:
  - navigation
  - toc
---

<div class="home-hero" markdown>

# Tłumacz kompletne komunikaty<br>z t-stringami Pythona

`gettext-tstrings` łączy t-stringi Pythona 3.14+ ze standardowymi katalogami
gettext i narzędziami Babel. Wartości i formatowanie zostają w kodzie
aplikacji; tłumacze pracują z kompletnymi komunikatami i prostymi symbolami
zastępczymi `{name}`:

```python
import gettext

from gettext_tstrings import Translator

_ = Translator(gettext.translation("messages", localedir="locales"))
name = "Ada"
print(_(t"Hello {name}"))  # with a Japanese catalog: こんにちは Ada
```

Katalog zawiera `Hello {name}`. Tłumaczenie może przenieść `{name}` albo je
powtórzyć. Jeśli usunie, przemianuje lub przeformatuje symbol zastępczy,
walidacja katalogu zgłosi błąd. Jeśli błędny wpis mimo to trafi na produkcję,
biblioteka loguje ostrzeżenie i renderuje komunikat źródłowy zamiast powodować
awarię.

[Rozpocznij pięciominutowy samouczek :material-arrow-right:](tutorial.md){ .md-button .md-button--primary }
[Porównaj alternatywy](comparison.md){ .md-button }

Alfa · Python 3.14+ · standardowe katalogi PO/MO · brak zewnętrznych zależności w czasie działania
{ .home-facts }

Ta strona praktykuje to, co dokumentuje: każda wersja językowa —
nawigacja, etykiety i raport z budowania świadomy form liczby mnogiej — jest
renderowana z katalogów PO przez
[sam `gettext-tstrings`](https://github.com/yhay81/gettext-tstrings/blob/main/scripts/build_multilingual_docs.py).
{ .home-hero-note }

</div>

## Czy to jest dla Ciebie? { #is-this-for-you }

**Pasuje już dziś, gdy** Twoja aplikacja działa na Pythonie 3.14 lub nowszym;
używasz już gettext i Babel albo chcesz przyjąć ich przepływ pracy z plikami
PO/MO; i chcesz składni t-stringów z nazwanymi symbolami zastępczymi, które są
sprawdzane, zanim się wyrenderują.

**Jeszcze nie pasuje, gdy** potrzebujesz Pythona 3.13 lub starszego; wymagasz
stabilnego API Pythona — to jest wersja alfa, a [specyfikacja](spec.md) jest tą
jej częścią, która się ustaliła; albo prawie cały Twój tekst do przetłumaczenia
mieszka w języku szablonów, a nie w źródłach Pythona.

Masz już katalogi? Działają dalej. `_("Hello {name}").format(name=name)` i
`tr(t"Hello {name}")` dają ten sam msgid, więc istniejące tłumaczenia przetrwają
zmianę — [Migracja](migration.md) prowadzi przez całe przejście.

## Co wolno powiedzieć katalogowi { #what-the-catalog-may-say }

**Tłumaczenie nie może zmienić struktury komunikatu, który tłumaczy.** Na tym
polega cała obietnica, a reszta tej strony z niej wynika. Tłumaczenie może
zmieniać kolejność `{name}` albo je powtarzać i może przepisać każde inne słowo
wokół niego. Nie może pominąć symbolu zastępczego, wymyślić nowego, sięgnąć
przez niego do Twoich obiektów ani dołączyć własnego formatowania.

Biblioteka sprawdza to na wejściu — przy kompilacji katalogów — i ponownie w
czasie renderowania, a to właśnie różnica między błędem znalezionym w przeglądzie
a błędem znalezionym przez użytkownika.

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

## Zasady projektowe { #the-design-rules }

- Tłumacz kompletne komunikaty, nigdy fragmenty zdań.
- Akceptuj wyłącznie proste nazwy zmiennych, takie jak `{name}`.
- Trzymaj `!r` i `:.2f` pod kontrolą aplikacji, poza katalogiem.
- Pozwól tłumaczeniom zmieniać kolejność i powtarzać znane symbole zastępcze,
  nie pozwalając im sięgać do atrybutów ani dodawać formatowania.
- Używaj zwykłych plików POT, PO i MO oraz narzędzi, które już je czytają.

A do tego pasująca lista tego, czego biblioteka celowo nie dotyka: nie
lokalizuje liczb, walut ani dat — [sformatuj je wcześniej](guide.md#locale-aware-values),
Bablem; nie escape'uje wyrenderowanego wyjścia dla HTML-a, powłoki ani
terminala; i nie potrafi ocenić, czy tłumaczenie jest *poprawne* — tylko czy
jego symbole zastępcze są nienaruszone.

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

**Zacznij tutaj** — bez zakładania doświadczenia z gettext:

<div class="grid cards" markdown>

- **[Samouczek](tutorial.md)** — od pustego katalogu do działającego
  japońskiego tłumaczenia w pięciu krokach, każde polecenie pokazane z jego
  wynikiem.
- **[Dlaczego t-stringi](comparison.md)** — ten sam komunikat zapisany na
  cztery sposoby i to, co `%(name)s`, `.format()` oraz `$`-stringi oddają
  katalogowi.

</div>

**Używanie** — robocze materiały odniesienia:

<div class="grid cards" markdown>

- **[Przewodnik](guide.md)** — API czasu działania: którego punktu wejścia
  użyć, liczba mnoga, języki na żądanie, odroczone łańcuchy i to, co się
  dzieje, gdy katalog jest błędny.
- **[Ekstrakcja](extraction.md)** — dokumentacja `pybabel`: konfiguracja,
  własne nazwy funkcji i to, jak istniejące narzędzia walidują te katalogi za
  darmo.
- **[W produkcji](workflow.md)** — pętla tak, jak prowadzi ją zespół: cykl
  aktualizacji, wpisy fuzzy, bramki CI, platformy tłumaczeniowe i wysyłka.
- **[Migracja](migration.md)** — przyjęcie tego w projekcie, który ma już
  katalogi, jedno miejsce wywołania naraz.
- **[Dla tłumaczy](translators.md)** — jedna strona do przekazania temu, kto
  edytuje pliki `.po`.

</div>

**Zrozumienie** — od historii do implementacji:

<div class="grid cards" markdown>

- **[Geneza](background.md)** — dlaczego ta biblioteka istnieje: trzydzieści
  lat gettext, dwa PEP-y i dyskusja o bibliotece standardowej zamknięta bez
  odpowiedzi.
- **[Pułapki](pitfalls.md)** — co naprawdę zepsuło się przy tłumaczeniu tej
  strony na trzydzieści pięć języków i którą połowę potrafi wychwycić
  narzędzie.
- **[Jak to działa](internals.md)** — od obiektu szablonu z PEP 750 do
  wyrenderowanego łańcucha oraz pamięci podręczne, które czynią sprawdzanie
  tanim.

</div>

**Referencja** — kontrakty:

<div class="grid cards" markdown>

- **[API](api.md)** — wszystko, co eksportuje pakiet, na jednej stronie.
- **[Specyfikacja](spec.md)** — konwencja t-string ↔ msgid jako stabilny,
  wersjonowany kontrakt z maszynowo czytelnym zestawem testów zgodności.

</div>

## Status { #status }

| | |
| --- | --- |
| Wersja pakietu | 0.1.0a8 |
| Stabilność API | alfa — API Pythona może się jeszcze zmieniać |
| [Specyfikacja](spec.md) | v1, z [zestawem testów zgodności](spec.md#conformance) |
| Python | 3.14 i nowsze; testowane na 3.14, 3.14t (free-threaded) i 3.15 |
| Babel | 2.18 lub nowszy, i tylko tam, gdzie działa `pybabel` |
| Zależności w czasie działania | brak — moduł `gettext` biblioteki standardowej |
| Format katalogów | zwykłe POT, PO i MO |
| Zmiany | [CHANGELOG](https://github.com/yhay81/gettext-tstrings/blob/main/CHANGELOG.md) |

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
