---
description: "Konwencja t-string do msgid jako mały wersjonowany kontrakt, z maszynowo czytelnym zestawem testów zgodności."
---

# Specyfikacja

Możesz używać tej biblioteki bez czytania tej strony —
[samouczek](tutorial.md) i [przewodnik](guide.md) pokrywają codzienne
użycie. Ta strona jest dla autorów narzędzi: konwencja, którą biblioteka
implementuje, jest spisana jako mały, stabilny kontrakt, tak by inna
implementacja — ekstraktor, IDE, type checker albo przyszły `pygettext` —
mogła obrać ją za cel i współdziałać. Po te same reguły objaśnione wraz z
powodami — i po to, jak wykonuje je implementacja referencyjna — przeczytaj
najpierw [Jak to działa](internals.md).

[Przeczytaj spec v1 :material-arrow-right:](https://github.com/yhay81/gettext-tstrings/blob/main/SPEC.md){ .md-button .md-button--primary }

## Reguły na jednym ekranie { #the-rules-in-one-screen }

**Msgid** to konkatenacja, w kolejności źródłowej, segmentów literalnych i
jednego tokenu `{name}` na interpolację. Literalne nawiasy klamrowe są
escapowane (`{` staje się `{{`). Nazwa musi być prostą nazwą symbolu
zastępczego — `str.isidentifier()` zwraca prawdę i nie jest to słowo
kluczowe Pythona. Konwersje i specyfikacje formatu **nie** są częścią
msgid; pozostają pod kontrolą aplikacji.

| t-string | msgid |
| --- | --- |
| `t"Hello {name}"` | `Hello {name}` |
| `t"Total: {amount:,.2f}"` | `Total: {amount}` |
| `t"Config {{raw}} is {value}"` | `Config {{raw}} is {value}` |
| `t"Hello {user.name}"` | *odrzucone — nie jest prostą nazwą* |

**Tłumaczenie** jest poprawne, gdy zawiera wyłącznie gołe symbole zastępcze
`{name}`, każda wymagana nazwa występuje co najmniej raz i nie występuje
żadna nazwa spoza zbioru dozwolonych. Zmiana kolejności i powtarzanie są
celowo nieograniczone: oba bywają gramatycznie konieczne w języku
docelowym.

Dla liczby mnogiej *dozwolone* to suma nazw obu gałęzi, a *wymagane* — ich
część wspólna. Tak więc `t"One file"` wobec `t"{n} files"` zostawia `n`
dostępne tłumaczowi każdej z form, ale wymagane w żadnej, a reguły liczby
mnogiej języka docelowego mogą różnić się od źródłowych.

**Pusty msgid** nigdy nie jest wyszukiwany, bo gettext rezerwuje go dla
nagłówka metadanych katalogu.

## Zgodność { #conformance }

[`conformance/v1.json`](https://github.com/yhay81/gettext-tstrings/blob/main/conformance/v1.json)
to ten sam dokument w postaci maszynowo czytelnej: przypadki mapujące
statyczną strukturę t-stringa na msgid oraz msgid plus wzorzec z katalogu
na wyrenderowany łańcuch albo odrzucenie.

Implementacja **jest zgodna ze spec v1**, gdy odtwarza każdy przypadek.
Przypadki nazywają wyłącznie to, co definiuje specyfikacja — wyprowadzone
msgid, akceptowane i odrzucane wzorce, wyrenderowany wynik — a nigdy
komunikat błędu ani typ wyjątku, więc implementacja w innym języku może
uruchomić je bez zmian.

Interpolacje są opisywane strukturalnie, nigdy jako źródło w Pythonie:

```json
{
  "spec": "2.2",
  "name": "format spec stays out of the msgid",
  "source": [
    "Total: ",
    {"expression": "amount", "value": 1234.5, "format_spec": ",.2f"}
  ],
  "msgid": "Total: {amount}"
}
```

Implementacja referencyjna uruchamia ten zestaw jako część własnych
testów, więc proza i kod nie mogą po cichu się rozjechać.

## Wersjonowanie { #versioning }

To jest spec v1. Zmiana niekompatybilna wstecz w wyprowadzaniu msgid lub w
walidacji tłumaczeń podnosi wersję i dostarcza nowy `conformance/vN.json`
obok istniejącego. Addytywne doprecyzowania, które nie zmieniają ani
wyprowadzanych msgid, ani akceptowanych wzorców — nie.
