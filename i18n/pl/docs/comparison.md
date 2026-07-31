---
description: "Ten sam przetłumaczalny komunikat zapisany z %-formatem, .format(), $-stringami flufl.i18n i t-stringiem, wraz z tym, jak każdy z nich wiąże wartości i traktuje uszkodzony katalog."
---

# Dlaczego t-stringi

Cztery sposoby wstawienia wartości do przetłumaczalnego komunikatu, porównane
na tym samym zdaniu. Wersja skrócona:

- Przy **%-formacie** jedna litera usunięta przez tłumacza staje się awarią
  na produkcji.
- Przy **str.format** tłumaczenie może czytać atrybuty obiektów, które
  przekazuje Twój kod — łącznie z sekretami.
- Przy **$-stringach** (flufl.i18n) wartości są pobierane niejawnie ze
  zmiennych funkcji wywołującej, a symbole zastępcze z kropką sięgają także
  atrybutów.
- Przy **t-stringach** formatowanie zostaje w Twoim kodzie, tłumaczenia są
  sprawdzane w czasie działania, a uszkodzony katalog wraca do tekstu
  źródłowego zamiast powodować awarię.

Reszta tej strony to materiał dowodowy, metoda po metodzie.

!!! note "Każdego przetłumaczonego komunikatu dotykają trzy strony"

    **Katalog** to plik tłumaczeń — `.po`, dopóki edytują go ludzie,
    kompilowany do `.mo`, który wczytuje aplikacja
    ([samouczek](tutorial.md) przechodzi przez oba). Każdego komunikatu
    dotykają trzy strony: **deweloper** pisze łańcuch źródłowy, **tłumacz**
    edytuje katalog — często na zewnętrznej platformie, z dala od
    jakiegokolwiek przeglądu kodu — a **aplikacja** renderuje oba razem w
    czasie działania. Każdy styl formatowania poniżej inaczej odpowiada na to
    samo pytanie: *jak dużą część języka formatowania kontroluje katalog?*
    W przykładach `_` to konwencjonalna nazwa funkcji tłumaczącej, a `tr` to
    nazwa z tej biblioteki.

## %-format { #-format }

```python
_("Hello %(name)s") % {"name": name}
```

Co może pójść nie tak: jedna usunięta litera w tłumaczeniu wywala
renderowanie.

Łańcuch w katalogu niesie składnię printf, łącznie z końcową literą typu —
`s` w `%(name)s` — którą łatwo przeoczyć i łatwo uszkodzić:

```pycon
>>> "Hello %(name)" % {"name": "Ada"}  # the trailing "s" was deleted
Traceback (most recent call last):
  ...
ValueError: incomplete format
```

Jednoznakowa edycja w edytorze PO staje się tracebackiem na produkcji. GNU
`msgfmt --check-format` faktycznie to wychwytuje, ale tylko dla komunikatów
oznaczonych flagą `python-format` i tylko jeśli katalog rzeczywiście
przechodzi przez msgfmt w drodze do Twojej aplikacji.

## str.format { #strformat }

```python
_("Hello {name}").format(name=name)
```

Usuwa końcową literę typu, zachowując nazwany, swobodnie przestawialny symbol
zastępczy. To, co może pójść nie tak, przenosi się na drugą stronę wymiany:
tłumaczenie zyskuje władzę nad Twoimi obiektami.

`str.format` to mały język wyrażeń, a wywołanie go na łańcuchu oznacza
przekazanie temu łańcuchowi prawa do jego użycia:

```pycon
>>> "{name.__class__.__mro__}".format(name="Ada")
"(<class 'str'>, <class 'object'>)"
>>> settings.api_key = "sk-live-…"
>>> "{conf.api_key}".format(conf=settings)
'sk-live-…'
```

Teraz zastąp te literalne łańcuchy tym, co zwraca `_()`. Jeśli tłumaczenie
`Hello {name}` wraca jako `{conf.api_key}`, jego wyrenderowanie wypisuje Twój
klucz API — to katalog, nie Twój kod, zdecydował, co zostało odczytane.
Katalog nie jest kodem, ale podróżuje jak dane: na platformę tłumaczeniową,
przez wiele rąk, z powrotem jako `.po`, skompilowany do `.mo`, czasem
dostarczony spoza Twojego projektu w całości. `.format()` daje każdemu etapowi
tej podróży dostęp do atrybutów obiektów, które przekazujesz.

## `$`-stringi i flufl.i18n { #-strings-and-flufli18n }

```python
from flufl.i18n import initialize

_ = initialize("example")

name = "Ada"
print(_("Hello $name"))  # Hello Ada — the value came from the caller's locals
```

Standardowa biblioteka w [`string.Template`][stdlib-template] dostarcza język
interpolacji `$name`, ale sama nie jest API tłumaczeń.
[`flufl.i18n`][flufl-i18n] łączy ten styl z wyszukiwaniem w katalogach
gettext. Zauważ, że wartość nigdy nie jest przekazywana: flufl.i18n buduje
przestrzeń podstawień z globalnych i lokalnych zmiennych wywołującego —
komunikatowi dostępne są wszystkie zmienne istniejące w miejscu wywołania.
Opcjonalne mapowanie `extras` ma pierwszeństwo przed oboma. Składnia widziana
przez tłumacza nie ma końcowej litery typu ani specyfikatora formatu, a
symbole zastępcze pozostają swobodnie przestawialne.

Niedostępne podstawienie nie zgłasza wyjątku. Przy `name = "Ada"` i braku
`nombre` w przestrzeni nazw wywołującego katalogowe tłumaczenie
`Hello $nombre` renderuje się jako `Hello $nombre`: nierozwiązany symbol
zastępczy pozostaje widoczny. To [udokumentowane zachowanie][documented behavior]
zachowuje resztę przetłumaczonego komunikatu zamiast unieważniać wywołanie.
Wyjątki zgłoszone podczas rozwiązywania atrybutu lub konwersji wartości wciąż
mogą się propagować.

`flufl.i18n` jest w jednym istotnym względzie bardziej zdolny niż goły
`string.Template`. Jego [własny Template][custom Template] akceptuje symbole
zastępcze z kropką, takie jak `$settings.api_key`, a jego
[translator][translator] rozwiązuje te ścieżki względem wartości
wywołującego. Przetłumaczony symbol zastępczy może nazwać dowolną dostępną
zmienną lokalną lub globalną wywołującego i, składnią z kropką, przechodzić
po jej atrybutach. To wygodne, gdy komunikat potrzebuje atrybutu, a
jednocześnie czyni ramkę wywołującego częścią przestrzeni podstawień
katalogu. Porównanie poniżej opisuje `flufl.i18n` 6.0.0, nie każde możliwe
użycie `string.Template`.

Odpowiada też na pytanie, które dwa pozostałe style formatowania zostawiają w
całości aplikacji: *który* język jest bieżący i jak go zmienić.
[Obiekt aplikacji][application object] trzyma stos języków, `_.push(code)` i
`_.pop()` nim poruszają, `with _.using(code):` zagnieżdża, a
[strategia][strategy] znajduje katalog dla kodu języka, więc aplikacja nigdy
sama nie dotyka obiektów katalogu. Serwer, który w jednej jednostce pracy musi
wytworzyć tekst w więcej niż jednym języku — stronę dla czytelnika,
powiadomienie dla kogoś, kto ma ustawiony inny — to właśnie przypadek, dla
którego to istnieje.

Stos żyje na tym obiekcie aplikacji, który współdzieli cały proces. Dwa
nakładające się żądania dzielą więc jeden stos, a bloki, które nie są ściśle
zagnieżdżone *w czasie*, podają sobie nawzajem zły język:

```python
async def greet(code, delay):
    with _.using(code):
        await asyncio.sleep(delay)
        return _("Hello $name")


async def main():
    return await asyncio.gather(greet("fr", 0.01), greet("ja", 0.02))
```

```pycon
>>> asyncio.run(main())  # "fr" entered first and left first, so it read "ja" off the top
['こんにちは Ada', 'Bonjour Ada']
```

Ta biblioteka zachowuje tę samą możliwość — wiązania zagnieżdżają się i
rozwijają tak samo — ale w `ContextVar`, a nie na współdzielonym stosie, więc
powyższe przeplecenie rozwiązuje się osobno dla każdego zadania. Odpowiedniki
znajdziesz na stronie
[Kilka języków naraz](guide.md#several-languages-at-once). Czego biblioteka nie
dostarcza, to wyszukania katalogu po kodzie języka: przekazujesz obiekt
tłumaczeń, którym w typowym przypadku jest jedno wywołanie
`gettext.translation()`, a biblioteka standardowa buforuje sparsowany katalog.

## t-stringi { #t-strings }

```python
tr(t"Hello {name}")
```

Katalog nadal widzi `Hello {name}` i pozostaje zwykłym katalogiem PO/MO.
Różnica polega na tym, co tłumaczeniu *wolno powiedzieć* i kto to sprawdza.

Ta biblioteka waliduje każde tłumaczenie względem symboli zastępczych
komunikatu źródłowego przed renderowaniem i akceptuje gołe nazwy — i nic
poza tym. Względem `t"Hello {name}"`:

| Tłumaczenie zawierające | jest odrzucane z komunikatem |
| --- | --- |
| `{name.__class__.__mro__}` | placeholder `{name.__class__.__mro__}` must be a plain name, copied from the source message unchanged |
| `{name!r}` | placeholder `{name}` adds formatting; write `{name}` on its own, because the source message decides how the value is formatted |
| `{0}` | placeholder `{0}` must be a plain name, copied from the source message unchanged |
| `{nombre}` | translation does not match the source placeholders: `{name}` is missing; `{nombre}` is not in the source message |

Odrzucone nie znaczy zawieszone: domyślnie biblioteka loguje ostrzeżenie i
renderuje tekst źródłowy, więc zły katalog nigdy nie kładzie aplikacji —
[ten sam kontrakt, którego dotrzymuje sam gettext](guide.md#what-happens-when-a-catalog-is-wrong).

Formatowanie zostaje tam, gdzie zostało napisane, w kodzie:

```python
amount = 1234.5
tr(t"Total: {amount:,.2f}")  # msgid is "Total: {amount}"
```

`:,.2f` nigdy nie dociera do katalogu, więc żadne tłumaczenie nie może go
zmienić i żaden tłumacz nie musi na nie patrzeć.

Jeszcze jedna różnica to narzędzia: t-stringi to nowa składnia, więc
wyodrębnianie ich do `.pot` wymaga obecnie ekstraktora świadomego
t-stringów, takiego jak ten, który ten pakiet
[dostarcza dla Babel](extraction.md).

## Obok siebie { #side-by-side }

| | `%(name)s` | `.format()` | `flufl.i18n` `$name` | `t"…"` |
| --- | --- | --- | --- | --- |
| Czy symbol zastępczy jest nazwany? | tak | tak | tak | tak |
| Czy tłumacz może przestawiać symbole zastępcze? | tak | tak | tak | tak |
| Skąd pochodzą wartości? | jawne mapowanie | jawne argumenty | zmienne lokalne i globalne wywołującego, plus opcjonalne `extras` | wartości przechwycone wewnątrz t-stringa |
| Czy katalog może zmienić sposób formatowania wartości? | tak | tak | nie | nie |
| Czy katalog może sięgać do obiektów (dostęp do atrybutów)? | nie | tak | tak, nazwami z kropką | nie |
| Tłumaczenie *gubi* symbol zastępczy — co się renderuje? | wartość znika po cichu | wartość znika po cichu | wartość znika po cichu | tekst źródłowy, z ostrzeżeniem ([domyślnie](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Tłumaczenie *dodaje* nieznany symbol zastępczy — co się renderuje? | wyjątek | wyjątek | symbol zastępczy pozostaje widoczny jako tekst | tekst źródłowy, z ostrzeżeniem ([domyślnie](guide.md#what-happens-when-a-catalog-is-wrong)) |
| Czy symbole zastępcze są sprawdzane w czasie renderowania? | nie | nie | nie | tak (patrz niżej) |
| Jaką flagę PO wywnioskuje Babel, by istniejące narzędzia walidowały? | `python-format` | `python-brace-format` | brak | `python-brace-format` |
| Używa zwykłych katalogów PO/MO? | tak | tak | tak | tak |
| Potrzebuje własnego ekstraktora źródeł? | nie | nie | nie | tak, na razie |
| Gdzie mieszka „bieżący język"? | tam, gdzie umieści go aplikacja | tam, gdzie umieści go aplikacja | stos kodów języków na współdzielonym obiekcie aplikacji | `ContextVar`, osobno dla zadania lub żądania |

O kontroli w czasie renderowania: komunikaty w liczbie pojedynczej są
sprawdzane pod kątem dokładnego dopasowania symboli zastępczych. Komunikaty w
liczbie mnogiej też — względem
[reguły sumy i części wspólnej](spec.md), która pozwala formom liczby mnogiej
języka docelowego różnić się od źródłowych; surowsza kontrola per forma
działa przy kompilacji katalogów ([Ekstrakcja](extraction.md)).

Wiersz o fladze formatu dotyczy walidacji świadomej symboli zastępczych, nie
zgodności katalogów. `brak` oznacza, że standardowe narzędzia gettext nadal
czytają i kompilują komunikat, ale `msgfmt --check-format` nie ma gramatyki
symboli `$`, którą mógłby zastosować.

## Ile to kosztuje { #what-it-costs }

F-stringa nie da się tak użyć w ogóle — zanim jakakolwiek biblioteka go
zobaczy, jest już gotowym łańcuchem, więc tłumaczenie go oznacza tłumaczenie
fragmentu. T-stringi ([PEP 750]) trzymają tekst statyczny i wartości osobno,
zachowując składnię podobną do f-stringów i jawne wiązanie wartości.
`$`-stringi już dziś oferują zwięzłą alternatywę z innym modelem wiązania i
błędów. `flufl.i18n` to dojrzały pakiet działający na Pythonie 3.10 i
nowszych; `gettext-tstrings` jest obecnie w wersji alfa, a ponieważ
t-stringi to nowa składnia, wymaga Pythona 3.14 lub nowszego.

Drugim kosztem jest samo ograniczenie: interpolacja musi być prostą nazwą.

```python
tr(t"Hello {user.name}")  # raises InvalidTemplateError at the call site
```

```python
name = user.name  # compute it first
tr(t"Hello {name}")
```

To realne ograniczenie. Razem z wiązaniem wartości po stronie źródła i
sprawdzaniem symboli zastępczych w czasie działania zapobiega temu, by
łańcuchy z katalogu wykonywały wyrażenia, i utrzymuje znaczące nazwy symboli
zastępczych.

Jak Python doszedł do tego rozdroża — dwa PEP-y w odstępie dziesięciu lat i
dyskusja o bibliotece standardowej zamknięta bez odpowiedzi — opowiada ze
źródłami strona [Geneza](background.md).

  [PEP 750]: https://peps.python.org/pep-0750/
  [stdlib-template]: https://docs.python.org/3/library/string.html#template-strings
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [documented behavior]: https://flufli18n.readthedocs.io/en/stable/using.html#substitutions-and-placeholders
  [custom Template]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_substitute.py
  [translator]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_translator.py
  [application object]: https://gitlab.com/flufl/flufl.i18n/-/blob/6.0.0/src/flufl/i18n/_application.py
  [strategy]: https://flufli18n.readthedocs.io/en/stable/strategies.html
