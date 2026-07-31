---
description: "Trzydzieści lat gettext, dwa PEP-y w odstępie dziesięciu lat i dyskusja o bibliotece standardowej zamknięta jako „not planned": dlaczego ta biblioteka istnieje, z odnośnikami do źródeł."
---

# Geneza

Ta biblioteka leży w punkcie przecięcia dwóch długich historii — jednej o tym,
jak tłumaczy się oprogramowanie, i drugiej o tym, jak Python interpoluje
łańcuchy — które w końcu zeszły się w 2025 roku i utknęły dokładnie tam,
gdzie potrzebna była mała, staranna konwencja. Ta strona opowiada obie
historie z odnośnikami do źródeł, bo decyzje projektowe na tej witrynie
łatwiej ocenić, gdy widać pytania, na które odpowiadają.

## Ekosystem gettext { #the-gettext-ecosystem }

[GNU gettext] jest sposobem tłumaczenia wolnego oprogramowania od połowy lat
90.: oznacz łańcuchy w kodzie, wyodrębnij je do szablonu, daj tłumaczom po
jednym pliku katalogu na język, skompiluj, wczytaj w czasie działania. Wokół
tej pętli wyrósł cały ekosystem — edytory PO, przepływy recenzji i platformy
tłumaczeniowe mówiące tym samym formatem plików — a Python od ponad dwóch
dekad dostarcza w bibliotece standardowej
[moduł `gettext`][stdlib-gettext]. Wykonawcza połowa tłumaczenia nigdy nie
była problemem.

Nierozstrzygniętą połową zawsze było to, *jak wygląda łańcuch w katalogu*.
Komunikat `%(name)s` wręcza tłumaczom składnię printf, którą jedna usunięta
litera zamienia w awarię na produkcji; komunikat `.format()` daje katalogowi
dostęp do atrybutów żywych obiektów. ([Dlaczego t-stringi](comparison.md)
omawia oba przypadki, z pokazanymi błędami.) A f-stringi — składnia, którą
większość kodu w Pythonie dziś preferuje — nie mogą uczestniczyć w ogóle:
zanim zobaczy je jakakolwiek biblioteka, są już gotowym łańcuchem. Ludzie i
tak próbują, na tyle często, że tracker Babel zbiera te próby
([#594][babel-594], [#715][babel-715]); porażka jest strukturalna, a nie
wynika z brakującej funkcji.

## Dwa PEP-y, dziesięć lat różnicy { #two-peps-ten-years-apart }

W 2015 roku Alyssa Coghlan i Nick Humrich napisali [PEP 501], proponując
szablony interpolacji, których pierwszą deklarowaną motywacją było i18n —
„providing a cleaner syntax for i18n translation", jak ujmuje to sam PEP.
Propozycję odroczono, po części dlatego, że dyskusja pokazała, iż przypadek
i18n niesie istotne dodatkowe komplikacje, których prostsze zastosowania nie
miały.

Dekadę później [PEP 750] — autorstwa Jima Bakera, Guido van Rossuma, Paula
Everitta, Koudaia Aono, Lysandrosa Nikolaou i Dave'a Pecka — wskrzesił pomysł
jako t-stringi, został [przyjęty w kwietniu 2025][sc-resolution] i trafił do
[Pythona 3.14] w październiku 2025. PEP 501 został wtedy wycofany na jego
rzecz. Jeden szczegół ma znaczenie dla tej strony: i18n *nie* należy do
deklarowanych motywacji PEP 750. PEP uogólnił mechanizm — typ szablonu,
który może konsumować dowolna biblioteka — i zostawił kwestię tłumaczeń
dokładnie tam, gdzie PEP 501 zaparkował ją dziesięć lat wcześniej: otwartą.

Tak więc od Pythona 3.14 język miał dokładnie tę strukturę danych, której
potrzebuje katalog komunikatów, i żadnej konwencji używania jej w tej roli.

## Dyskusja o bibliotece standardowej { #the-stdlib-discussion }

Dwa miesiące przed wydaniem 3.14 Adrian Mönnich (ThiefMaster, opiekun
projektu Indico) zaproponował zamknięcie tej luki w samej bibliotece
standardowej: wątek [Support t-strings in gettext][discuss-thread] na
discuss.python.org, otwarty w sierpniu 2025, przyszedł z działającym
[pull requestem][cpython-pr] dodającym obsługę t-stringów zarówno do
`gettext`, jak i do `pygettext`.

Wątek wart jest przeczytania w całości, bo wydobywa każde trudne pytanie, na
które ta biblioteka musiała później odpowiedzieć:

- **Czym może być interpolacja?** Tylko prostą nazwą, czy także atrybutami i
  wywołaniami z wyprowadzoną nazwą symbolu zastępczego? Każda odpowiedź
  wymienia wygodę na stabilność msgid i bezpieczeństwo katalogu.
- **Czego wymagają formy liczby mnogiej,** gdy system liczby mnogiej języka
  docelowego różni się od źródłowego?
- **Czy gettext jest w ogóle właściwym celem?** Barry Warsaw — który podczas
  prac nad PEP 750 przekonywał, że t-stringi nie nadają się dobrze do i18n —
  wskazywał na swój [`flufl.i18n`][flufl-i18n] i jego styl `$`-stringów jako
  przyjaźniejsze narzędzie; inni argumentowali za porzuceniem gettext w
  ogóle na rzecz nowszych systemów, takich jak [Fluent].
- **I metapytanie:** cokolwiek trafi do biblioteki standardowej, w zasadzie
  nigdy nie może się zmienić. Konwencja z tyloma otwartymi wyborami to
  ryzykowna rzecz do zamrożenia za pierwszym podejściem.

Konsensus się nie uformował. Zgłoszenie w CPythonie zostało
[zamknięte jako „not planned"][cpython-issue], a pull request zamknięto bez
scalenia w październiku 2025, kilka dni po wydaniu 3.14. Możliwość istniała
w języku; konwencja nie miała domu.

## Dlaczego najpierw pakiet { #why-a-package-first }

To jest luka, którą ten projekt postanowił wypełnić spoza biblioteki
standardowej, w oparciu o świadomy zakład: konwencja dojrzewa szybciej tam,
gdzie może swobodnie wersjonować i zdobywać adopcję przypadek po przypadku, a
biblioteka standardowa — która musi trafić za pierwszym razem — jest
miejscem, w którym konwencja powinna *wylądować*, a nie miejscem, w którym
się ją wypracowuje.

Konkretnie: każde sporne pytanie z wątku ma tu spisaną odpowiedź, każda na
własnej stronie:

- Interpolacje to **wyłącznie proste nazwy**, więc msgid pozostają stabilne
  i znaczące — [przewodnik](guide.md#safety-and-scope) pokazuje regułę,
  [Jak to działa](internals.md#from-template-to-msgid) jej powody.
- **Formatowanie zostaje całkowicie poza katalogiem**
  ([Dlaczego t-stringi](comparison.md)).
- **Liczba mnoga** kieruje się regułą sumy i części wspólnej, która pozwala
  systemowi liczby mnogiej języka docelowego różnić się od źródłowego
  ([spec §4](spec.md)).
- Uszkodzony katalog **wraca do tekstu źródłowego zamiast powodować awarię**,
  dotrzymując kontraktu samego gettext
  ([przewodnik](guide.md#what-happens-when-a-catalog-is-wrong)).
- A cała konwencja jest [wersjonowaną specyfikacją](spec.md) z maszynowo
  czytelnym zestawem testów zgodności — napisaną tak, by inna implementacja,
  w tym przyszła z biblioteki standardowej, mogła przyjąć ją bez zmian i
  współdziałać.

Dyskusja się nie skończyła, a ten projekt jest jej uczestnikiem, nie
werdyktem. Jeśli masz produkcyjne doświadczenie z gettext, które dotyczy tych
wyborów, [ten sam wątek][discuss-thread] i [Discussions][gh-discussions] w
tym repozytorium są miejscem, gdzie się o nie spiera.

## Oś czasu { #timeline }

| Kiedy | Co się wydarzyło |
| --- | --- |
| połowa lat 90. | GNU gettext ustanawia przepływ PO/POT/MO, którym tłumacze i platformy mówią do dziś. |
| 2015 | [PEP 501] proponuje szablony interpolacji z i18n jako pierwszą motywacją; odroczony. |
| 2016 | f-stringi trafiają do Pythona 3.6 — interpolacja dostaje składnię, a tłumaczenia nie mogą jej użyć. |
| lip 2024 | [PEP 750] proponuje t-stringi. |
| kwi 2025 | PEP 750 [przyjęty][sc-resolution]; PEP 501 wycofany na jego rzecz. |
| sie 2025 | Otwiera się wątek [Support t-strings in gettext][discuss-thread], ze stdlibowym [pull requestem][cpython-pr]. |
| paź 2025 | [Python 3.14] dostarcza t-stringi; zgłoszenie stdlib zamyka się jako [not planned][cpython-issue]. |
| 2026 | `gettext-tstrings` wychodzi jako alfa, ze [spec v1](spec.md) i jej zestawem testów zgodności. |

  [GNU gettext]: https://www.gnu.org/software/gettext/
  [stdlib-gettext]: https://docs.python.org/3/library/gettext.html
  [babel-594]: https://github.com/python-babel/babel/issues/594
  [babel-715]: https://github.com/python-babel/babel/issues/715
  [PEP 501]: https://peps.python.org/pep-0501/
  [PEP 750]: https://peps.python.org/pep-0750/
  [sc-resolution]: https://github.com/python/steering-council/issues/275
  [Python 3.14]: https://docs.python.org/3.14/whatsnew/3.14.html
  [discuss-thread]: https://discuss.python.org/t/support-t-strings-in-gettext/101109
  [cpython-pr]: https://github.com/python/cpython/pull/137354
  [cpython-issue]: https://github.com/python/cpython/issues/137353
  [flufl-i18n]: https://flufli18n.readthedocs.io/en/stable/
  [Fluent]: https://projectfluent.org/
  [gh-discussions]: https://github.com/yhay81/gettext-tstrings/discussions
