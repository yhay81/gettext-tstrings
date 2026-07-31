---
description: "API czasu działania: wiązanie katalogu, języki na żądanie, odroczone łańcuchy i sposób raportowania uszkodzonego tłumaczenia."
---

# Przewodnik

Ta strona to dokumentacja czasu działania: wszystko, co *kod aplikacji* robi
z tą biblioteką, gdy katalogi już istnieją. Jeśli pełna pętla — oznacz,
wyodrębnij, przetłumacz, skompiluj, uruchom — jest Ci jeszcze obca,
[samouczek](tutorial.md) przechodzi ją raz w pięć minut; tworzenie i
walidację katalogów opisuje [Ekstrakcja](extraction.md), a to, jak zespół
utrzymuje pętlę w ruchu — cykle aktualizacji, CI, platformy tłumaczeniowe —
strona [W produkcji](workflow.md).

## Wiązanie katalogu { #binding-a-catalog }

Zalecany kształt odzwierciedla klasowe użycie gettext: zwiąż standardowy
obiekt tłumaczeń raz i używaj wywoływalnego procesora jako `_`.

```python
import gettext

from gettext_tstrings import Translator

translations = gettext.translation("messages", localedir="locales", languages=["ja"])
_ = Translator(translations)

name = "Ada"
print(_(t"Hello {name}"))  # こんにちは Ada

n = 3
print(_.ngettext(t"One file", t"{n} files", n))  # picks the right plural form for n

filename = "report.txt"
print(_.pgettext("button", t"Open {filename}"))  # "button" disambiguates homonyms
```

Funkcje na poziomie modułu podążają za nazwami z biblioteki standardowej i
jej konwencją argumentów wyłącznie pozycyjnych:

```python
from gettext_tstrings import gettext, ngettext, npgettext, pgettext

gettext(t"Hello {name}", translations=translations)
ngettext(t"One file", t"{n} files", n, translations=translations)
pgettext("button", t"Open {filename}", translations=translations)
npgettext("inbox", t"One message", t"{n} messages", n, translations=translations)
```

`tr` i `ntr` to dokładne aliasy `gettext` i `ngettext`.

## Język na żądanie { #per-request-language }

Framework webowy wybiera język per żądanie. Zwiąż tłumaczenia żądania z
bieżącym kontekstem, a każde wywołanie na poziomie modułu rozwiąże się do tego
języka, bezpiecznie przy współbieżnych żądaniach:

```python
from gettext_tstrings import tr, use_translations


def handle(request):
    translations = load_translations(request.locale)
    with use_translations(translations):
        return render(tr(t"Hello {name}"))
```

`set_translations(translations)` wiąże bez bloku `with`, dla frameworków,
które same zarządzają cyklem życia żądania; `get_translations()` odczytuje
bieżące wiązanie. Jawny argument `translations=` zawsze wygrywa z kontekstem,
a niezwiązany kontekst wraca do globalnie zainstalowanych funkcji gettext z
biblioteki standardowej. Opracowane przykłady dla Flaska i middleware ASGI
znajdują się na stronie
[W produkcji](workflow.md#binding-a-language-at-runtime).

## Tłumaczenie odroczone { #deferred-translation }

T-string przechwytuje swoje wartości zachłannie, co jest złe dla łańcucha
zdefiniowanego w czasie importu — etykiety formularza, wartości enuma, stałej
modułu — który musi wyrenderować się w języku aktywnym w chwili jego
*użycia*.

```python
from gettext_tstrings import lazy_gettext, lazy_pgettext, use_translations

SAVE = lazy_gettext(t"Save changes")  # defined once, at import
OPEN = lazy_pgettext("button", t"Open file")

with use_translations(japanese):
    assert str(SAVE) == "変更を保存"  # rendered here, in this language
```

`LazyString` renderuje się przez `str()`, `format()` i f-stringi oraz jest
równy swojemu wyrenderowanemu tekstowi.

!!! note "Celowo niehashowalny"

    Tekst `LazyString` zależy od aktywnego języka, więc hash zmieniałby się
    przy przełączeniu języka i po cichu psuł każdy zbiór lub słownik, który
    go przechowuje. Jeśli potrzebujesz klucza, najpierw wywołaj `str()`.

O `strict` decyduje się tam, gdzie komunikat jest zapisany, a nie tam, gdzie
się renderuje:

```python
SAVE = lazy_gettext(t"Save changes", strict=True)
```

Łańcuch odroczony renderuje się tam, gdzie zostanie ostatecznie użyty — w
szablonie, w formularzu, w linii logu — a to miejsce rzadko wie, czy jest to
przebieg testowy, czy produkcja. Przekazanie `strict=True` przy definicji
pozwala zastosować ten sam wybór [głośno w CI, łagodnie w
produkcji](#what-happens-when-a-catalog-is-wrong) do łańcucha, który nie
renderuje się w miejscu swojego wywołania.

Formy liczby mnogiej zależą od licznika znanego w czasie działania, więc
renderuj je zachłannie przez `ngettext` tam, gdzie licznik jest znany.

## Co się dzieje, gdy katalog jest błędny { #what-happens-when-a-catalog-is-wrong }

Jeśli symbole zastępcze tłumaczenia nie pasują do źródła — brakujące,
nieznane albo przeformatowane pole, które prześlizgnęło się przez walidację,
z ręcznie edytowanego MO, katalogu od dostawcy albo potoku pomijającego
checker — domyślnym zachowaniem jest odtworzenie tekstu źródłowego, a nie
zgłoszenie wyjątku. To odzwierciedla kontrakt samego gettext, że zły katalog
nigdy nie psuje aplikacji.

Przy `Hello {name}` przetłumaczonym jako `こんにちは {nombre}` renderowanie
się udaje, a do loggera `gettext_tstrings` trafia jedno ostrzeżenie:

```text
WARNING gettext_tstrings: invalid translation for msgid 'Hello {name}'; using
source text: translation does not match the source placeholders: {name} is
missing; {nombre} is not in the source message
```

```pycon
>>> _(t"Hello {name}")
'Hello Ada'
```

Ostrzeżenie pojawia się raz na komunikat i wzorzec, nie raz na renderowanie,
więc uszkodzony wpis katalogu nie zalewa loga.

Do testów i CI możesz włączyć głośne niepowodzenia:

```python
strict = Translator(translations, strict=True)
tr(t"Hello {name}", translations=translations, strict=True)
```

To samo wyszukanie wtedy zgłasza wyjątek, niosący to samo zdanie bez połowy
„using source text":

```pycon
>>> strict(t"Hello {name}")
Traceback (most recent call last):
  ...
gettext_tstrings.errors.InvalidTranslationError: translation does not match the
source placeholders: {name} is missing; {nombre} is not in the source message
```

## Czytanie komunikatu o błędzie { #reading-a-failure-message }

Te komunikaty są pisane dla tego, kto może na nie zareagować, a przy
problemie z katalogiem jest to częściej tłumacz niż programista. Zgłoszenie
tylko tego, że brakuje `{name}`, jest ślepą uliczką, gdy czytelnik widzi te
znaki przed sobą — więc tam, gdzie symbol zastępczy wygląda na obecny, a nie
jest, komunikat mówi dlaczego. Względem źródła `Hello {name}` każdy z
poniższych przypadków jest raportowany pod
`translation does not match the source placeholders:`

| Tłumaczenie mówi | Podany powód |
| --- | --- |
| `こんにちは ｛name｝` | `{name}` is missing (the braces around it are not the ASCII `{` and `}`) |
| `こんにちは {{name}}` | `{name}` is missing (it is written `{{name}}`, which is how a literal brace is escaped) |
| `こんにちは name` | `{name}` is missing (the name appears, but not inside braces) |
| `こんにちは {名前}` | `{name}` is missing; `{名前}` is not in the source message |

Znaki, których nie widać, dostają osobne traktowanie. Twarda spacja wewnątrz
nawiasów klamrowych to coś, co produkuje metoda wprowadzania i czego nie
pokazuje żaden edytor, więc komunikat wypisuje ją jako punkt kodowy, zamiast
nazywać znak, którego czytelnik nie znajdzie:

```text
placeholder {<U+00A0>name} has a space inside the braces; write {name}
```

Nazwa, której litery mieszają systemy pisma — przypadek homoglifów, gdzie
cyrylickie `а` jest nieodróżnialne od łacińskiego — jest pokazywana dwa razy,
raz czytelnie i raz w formie z sekwencją ucieczki, jedynej, która je
rozróżnia:

```text
translation does not match the source placeholders: {name} is missing;
{nаme} (n\u0430me) is not in the source message
```

To samo rozróżnienie stosuje się, gdy grecka lub cyrylicka nazwa zapisana w
całości jednym pismem koliduje z ASCII nazwą źródłową, w tym w
jednoliterowym przypadku łacińskiego `a` i cyrylickiego `а`.

## Renderowanie wzorca bez katalogu { #rendering-a-pattern-without-a-catalog }

`compile_template` udostępnia tę samą maszynerię poziom niżej: zamienia
t-string na jego msgid plus związany zestaw wartości i renderuje dowolny
wzorzec, który mu podasz.

```python
from gettext_tstrings import compile_template

name = "Ada"
compiled = compile_template(t"Hello {name}")

compiled.msgid  # "Hello {name}"
compiled.placeholders  # ("name",)
compiled.render("こんにちは {name}")  # "こんにちは Ada"
```

`render` waliduje według tych samych reguł i przy niedopasowaniu **zawsze
zgłasza wyjątek**. Nie ma tu trybu łagodnego: łagodność istnieje po to, by
wyszukanie w *katalogu* mogło zdegradować się do tekstu źródłowego, a
wzorzec, który przekazujesz samodzielnie, nie ma z czego się degradować.

## Bezpieczeństwo i zakres { #safety-and-scope }

To jest poprawne:

```python
tr(t"Hello {name}")
```

Te są odrzucane celowo:

```python
tr(t"Hello {user.name}")  # attribute access
tr(t"Hello {display_name()}")  # a call
```

Najpierw oblicz znaczącą wartość:

```python
name = user.display_name()
tr(t"Hello {name}")
```

Ograniczenie daje stabilne klucze katalogu, daje tłumaczom użyteczne nazwy i
powstrzymuje przetłumaczony łańcuch przed staniem się językiem wyrażeń.

Gwarancja dotyczy *struktury i formatowania*: tłumaczenie nigdy nie jest
wykonywane i nigdy nie może dodać dostępu do atrybutów, wywołań, konwersji
ani specyfikacji formatu. Dwie rzeczy pozostają odpowiedzialnością
wywołującego, dokładnie tak jak przy stdlibowym gettext — **escapowanie**
wyrenderowanego wyniku dla jego celu (HTML, powłoka, terminal) oraz
**integralność katalogu**, bo wrogi katalog może powtarzać symbol zastępczy,
by zwielokrotnić rozmiar wyniku, co jest nieodłączne dla każdego i18n
opartego na symbolach zastępczych.
