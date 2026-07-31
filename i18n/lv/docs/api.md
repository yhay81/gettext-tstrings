---
description: "Katrs nosaukums, ko eksportē gettext_tstrings: funkcijas, Translator, konteksta piesaiste, atliktās virknes un kļūdas."
---

# API

Viss zemāk esošais tiek eksportēts no `gettext_tstrings`. Nekas cits nav
publisks. Šī lapa ir signatūru uzziņa; izstrādātus katras funkcijas piemērus
skatiet [ceļvedī](guide.md).

## Tulkošana { #translating }

Katra funkcija ņem savu t-virkni pozicionāli un pieņem divus atslēgvārdu
argumentus: `translations` (atkāpjoties uz konteksta piesaisti un tad uz
standarta bibliotēkas globālajām funkcijām) un `strict` (skatiet
[Ceļvedi](guide.md#what-happens-when-a-catalog-is-wrong)).

| Funkcija | Signatūra |
| --- | --- |
| `gettext` | `(template, /, *, translations=None, strict=False) -> str` |
| `ngettext` | `(singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `pgettext` | `(context, template, /, *, translations=None, strict=False) -> str` |
| `npgettext` | `(context, singular, plural, n, /, *, translations=None, strict=False) -> str` |
| `tr` | `gettext` aizstājvārds |
| `ntr` | `ngettext` aizstājvārds |

### `Translator`

Iesaldēta dataclass, kas piesaista vienu tulkojumu objektu, lai izsaukuma
vietām tas nebūtu jāatkārto.

```python
Translator(translations, strict=False)
```

Tā ir izsaucama (`_(t"…")`) un nes `gettext`, `ngettext`, `pgettext`,
`npgettext` un `tr` / `ntr` aizstājvārdus.

## Konteksta piesaiste { #context-binding }

| Nosaukums | Nolūks |
| --- | --- |
| `use_translations(translations)` | Piesaista uz `with` bloka laiku, tad atjauno iepriekšējo. |
| `set_translations(translations)` | Piesaista bez bloka — ietvara pārvaldītiem dzīves cikliem. |
| `get_translations()` | Nolasa tekošo piesaisti vai `None`. |

Piesaiste ir `ContextVar`, tāpēc tā ir konteksta robežās un droša
vienlaicīgumā.

## Atliktās virknes { #deferred-strings }

| Nosaukums | Nolūks |
| --- | --- |
| `lazy_gettext(template, /, *, strict=False)` | Atliek tulkojumu līdz pirmajai lietošanai. |
| `lazy_pgettext(context, template, /, *, strict=False)` | Kontekstuālā forma. |
| `LazyString` | Tas, ko abas atgriež. Renderējas caur `str()` un `format()`, salīdzinājumā ir vienāda ar savu tekstu un ir apzināti nehešojama. |

## Zemāka līmeņa { #lower-level }

### `compile_template(template, /) -> CompiledTemplate`

Kompilē t-virkni, atkārtoti izmantojot tās kešoto statisko plānu.

### `CompiledTemplate`

| Loceklis | Nozīme |
| --- | --- |
| `.msgid` | Stabilais gettext ziņojuma identifikators. |
| `.placeholders` | Vietturu nosaukumi pirmās parādīšanās secībā. |
| `.render(pattern)` | Validē vienu rakstu un renderē to. Neatbilstības gadījumā **vienmēr izraisa kļūdu**. |

## Tipi un kļūdas { #types-and-errors }

### `Translations`

`runtime_checkable` `Protocol` četrām standarta metodēm, visas tikai
pozicionālas:

```python
class Translations(Protocol):
    def gettext(self, message: str, /) -> str: ...
    def ngettext(self, singular: str, plural: str, n: int, /) -> str: ...
    def pgettext(self, context: str, message: str, /) -> str: ...
    def npgettext(self, context: str, singular: str, plural: str, n: int, /) -> str: ...
```

`gettext.NullTranslations`, `gettext.GNUTranslations` un Babel `Translations`
visi to apmierina.

### Izņēmumi

| Klase | Tiek izraisīts, kad |
| --- | --- |
| `TStringError` | Bāzes klase abiem zemāk esošajiem. |
| `InvalidTemplateError` | Konvenciju lauž **avota** t-virkne — sarežģīta interpolācija vai atkārtots nosaukums ar atšķirīgu formatējumu. |
| `InvalidTranslationError` | To dara **tulkojums**. Noklusējuma iecietīgajā režīmā tas tiek ierakstīts žurnālā un tā vietā tiek renderēts avota teksts. |

## Ekstrakcijas ieejas punkti { #extraction-entry-points }

Tiek reģistrēti automātiski instalēšanas laikā; uz tiem atsaucas pēc nosaukuma,
nevis ar importu.

| Grupa | Nosaukums | Lieto |
| --- | --- | --- |
| `babel.extractors` | `gettext_tstrings` | `method` failā `babel.cfg`. |
| `babel.checkers` | `gettext_tstrings` | `pybabel compile`, automātiski. |

## Veiktspēja { #performance }

Pilnais stāsts — kas tiek kešots, uz ko kešatmiņas balsta atslēgas un kādi ir
izmērītie skaitļi — ir [Karstais ceļš](internals.md#the-hot-path). Īsā versija:
validācija tiek kešota, nekad neizlaista, un visa renderēšana maksā
mikrosekundes daļu. Palaidiet mērījumu uz savas mērķa vides:

```console
uv run python benchmarks/runtime.py
```
